"""
Command Line Interface for the Study Guide application.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from study_guide import __version__
from study_guide.config import config
from study_guide.database import init_db, get_session, DatabaseOperations
from study_guide.ingestion import FileScanner, TextChunker, get_extractor
from study_guide.generation import StudyMaterialGenerator
from study_guide.export import get_exporter

# Configure console for Windows compatibility
# Force UTF-8 output on Windows terminals
if sys.platform == "win32":
    console = Console(force_terminal=True, legacy_windows=False)
else:
    console = Console()

# ASCII-friendly symbols for Windows compatibility
CHECK_MARK = "[bold green]OK[/bold green]"
CROSS_MARK = "[bold red]X[/bold red]"


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_success(message: str):
    """Print a success message."""
    console.print(f"{CHECK_MARK} {message}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[bold yellow]Warning:[/bold yellow] {message}")


@click.group()
@click.version_option(version=__version__, prog_name="study-guide")
def cli():
    """
    AI Study Guide - Transform learning materials into study assets.

    Use this CLI to ingest documents, generate flashcards/quizzes, and export
    study materials in various formats.
    """
    pass


@cli.command()
def init():
    """Initialize the database and configuration."""
    config.ensure_directories()
    init_db()
    print_success(f"Database initialized at: {config.DB_PATH}")
    print_success(f"Export directory: {config.EXPORT_DIR}")

    # Validate configuration
    errors = config.validate()
    if errors:
        for error in errors:
            print_warning(error)
        console.print("\n[dim]Copy env.example.txt to .env and configure your API key.[/dim]")


@cli.command()
def status():
    """Show current status and statistics."""
    config.ensure_directories()

    # Check configuration
    errors = config.validate()

    console.print(Panel.fit(
        f"[bold]AI Study Guide[/bold] v{__version__}\n\n"
        f"Database: {config.DB_PATH}\n"
        f"Export Dir: {config.EXPORT_DIR}\n"
        f"Model: {config.GENERATION_MODEL}",
        title="Configuration",
    ))

    if errors:
        console.print("\n[bold yellow]Configuration Issues:[/bold yellow]")
        for error in errors:
            console.print(f"  - {error}")
    else:
        console.print(f"\n{CHECK_MARK} Configuration valid")

    # Show database stats
    try:
        init_db()
        session = get_session()
        ops = DatabaseOperations(session)
        stats = ops.get_stats()
        session.close()

        table = Table(title="\nDatabase Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", justify="right")

        table.add_row("Sources", str(stats["sources"]))
        table.add_row("Documents", str(stats["documents"]))
        table.add_row("Chunks", str(stats["chunks"]))
        table.add_row("Study Sets", str(stats["study_sets"]))
        table.add_row("", "")
        table.add_row("Flashcard Sets", str(stats["study_sets_by_type"]["flashcards"]))
        table.add_row("Quiz Sets", str(stats["study_sets_by_type"]["quiz"]))
        table.add_row("Practice Tests", str(stats["study_sets_by_type"]["practice_test"]))
        table.add_row("Audio Summaries", str(stats["study_sets_by_type"]["audio_summary"]))

        console.print(table)

    except Exception as e:
        print_error(f"Could not read database: {e}")


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--skip-existing", is_flag=True, help="Skip files already ingested")
def ingest(directory: str, skip_existing: bool):
    """
    Ingest files from a directory.

    Processes all supported files (PPTX, PDF, TXT, MD, videos) and stores
    extracted content in the database.
    """
    config.ensure_directories()
    init_db()

    directory_path = Path(directory)
    scanner = FileScanner()
    chunker = TextChunker()

    # Scan for files
    with console.status("[bold blue]Scanning directory..."):
        files = scanner.scan_directory(directory_path)

    if not files:
        print_warning(f"No supported files found in {directory}")
        console.print(f"Supported extensions: {', '.join(scanner.get_supported_extensions())}")
        return

    console.print(f"\nFound [bold]{len(files)}[/bold] supported files")

    session = get_session()
    ops = DatabaseOperations(session)

    processed = 0
    skipped = 0
    failed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Processing files...", total=len(files))

        for scanned_file in files:
            progress.update(task, description=f"Processing: {scanned_file.filename}")

            try:
                # Check for existing file (by hash)
                if skip_existing:
                    file_hash = scanned_file.compute_hash()
                    existing = ops.get_source_by_hash(file_hash)
                    if existing and existing.status == "completed":
                        skipped += 1
                        progress.advance(task)
                        continue

                # Create source record
                source = ops.create_source(
                    filename=scanned_file.filename,
                    filepath=str(scanned_file.path),
                    file_type=scanned_file.file_type,
                    file_hash=scanned_file.compute_hash(),
                    file_size=scanned_file.size,
                )

                ops.update_source_status(source.id, "processing")

                # Get extractor and extract content
                extractor = get_extractor(scanned_file.path)
                if not extractor:
                    ops.update_source_status(
                        source.id, "failed", f"No extractor for {scanned_file.extension}"
                    )
                    failed += 1
                    progress.advance(task)
                    continue

                result = extractor.extract(scanned_file.path)

                if not result.success:
                    ops.update_source_status(source.id, "failed", result.error)
                    failed += 1
                    progress.advance(task)
                    continue

                # Create document
                document = ops.create_document(
                    source_id=source.id,
                    raw_text=result.text,
                    title=result.title,
                )

                # Chunk the content
                chunk_result = chunker.chunk_text(result.text)
                if chunk_result.chunks:
                    ops.create_chunks_batch(document.id, chunk_result.chunks)

                ops.update_source_status(source.id, "completed")
                processed += 1

            except Exception as e:
                failed += 1
                console.print(f"\n[red]Error processing {scanned_file.filename}: {e}[/red]")

            progress.advance(task)

    session.close()

    # Summary
    console.print()
    print_success(f"Processed: {processed} files")
    if skipped:
        console.print(f"[dim]Skipped (already exists): {skipped}[/dim]")
    if failed:
        print_warning(f"Failed: {failed} files")


@cli.group()
def list():
    """List documents, chunks, or study sets."""
    pass


@list.command("documents")
@click.option("--limit", default=20, help="Maximum number of documents to show")
def list_documents(limit: int):
    """List all ingested documents."""
    init_db()
    session = get_session()
    ops = DatabaseOperations(session)

    documents = ops.get_all_documents()[:limit]

    if not documents:
        console.print("[dim]No documents found. Run 'ingest' to add documents.[/dim]")
        session.close()
        return

    table = Table(title="Documents")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Title", style="white", max_width=40)
    table.add_column("Words", justify="right")
    table.add_column("Chunks", justify="right")
    table.add_column("Created", style="dim")

    for doc in documents:
        chunks = ops.get_chunks_for_document(doc.id)
        table.add_row(
            str(doc.id),
            doc.title[:40] if doc.title else "(untitled)",
            str(doc.word_count),
            str(len(chunks)),
            doc.created_at.strftime("%Y-%m-%d %H:%M") if doc.created_at else "",
        )

    console.print(table)
    session.close()


@list.command("chunks")
@click.option("--doc", "doc_id", required=True, type=int, help="Document ID")
@click.option("--limit", default=10, help="Maximum number of chunks to show")
def list_chunks(doc_id: int, limit: int):
    """List chunks for a document."""
    init_db()
    session = get_session()
    ops = DatabaseOperations(session)

    document = ops.get_document(doc_id)
    if not document:
        print_error(f"Document {doc_id} not found")
        session.close()
        return

    chunks = ops.get_chunks_for_document(doc_id)[:limit]

    console.print(f"\n[bold]Document:[/bold] {document.title}")
    console.print(f"[dim]Total chunks: {len(ops.get_chunks_for_document(doc_id))}[/dim]\n")

    table = Table(title="Chunks")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Index", justify="right")
    table.add_column("Preview", max_width=60)
    table.add_column("Chars", justify="right")

    for chunk in chunks:
        preview = chunk.content[:100].replace("\n", " ") + "..."
        table.add_row(
            str(chunk.id),
            str(chunk.chunk_index),
            preview,
            str(chunk.char_count),
        )

    console.print(table)
    session.close()


@list.command("sets")
@click.option("--limit", default=20, help="Maximum number of sets to show")
def list_sets(limit: int):
    """List all generated study sets."""
    init_db()
    session = get_session()
    ops = DatabaseOperations(session)

    sets = ops.get_all_study_sets()[:limit]

    if not sets:
        console.print("[dim]No study sets found. Run 'generate' to create study materials.[/dim]")
        session.close()
        return

    table = Table(title="Study Sets")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Type", style="magenta")
    table.add_column("Title", max_width=30)
    table.add_column("Items", justify="right")
    table.add_column("Doc ID", justify="right", style="dim")
    table.add_column("Created", style="dim")

    for s in sets:
        table.add_row(
            str(s.id),
            s.set_type,
            s.title[:30] if s.title else "(untitled)",
            str(s.item_count),
            str(s.document_id) if s.document_id else "-",
            s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "",
        )

    console.print(table)
    session.close()


@cli.group()
def generate():
    """Generate study materials from documents."""
    pass


@generate.command("flashcards")
@click.option("--doc", "doc_id", required=True, type=int, help="Document ID")
@click.option("--count", default=10, help="Number of flashcards to generate")
def generate_flashcards(doc_id: int, count: int):
    """Generate flashcards from a document."""
    _generate_materials(doc_id, "flashcards", count)


@generate.command("quiz")
@click.option("--doc", "doc_id", required=True, type=int, help="Document ID")
@click.option("--count", default=10, help="Number of questions to generate")
def generate_quiz(doc_id: int, count: int):
    """Generate a quiz from a document."""
    _generate_materials(doc_id, "quiz", count)


@generate.command("test")
@click.option("--doc", "doc_id", required=True, type=int, help="Document ID")
@click.option("--count", default=15, help="Number of questions to generate")
def generate_test(doc_id: int, count: int):
    """Generate a practice test from a document."""
    _generate_materials(doc_id, "practice_test", count)


@generate.command("summary")
@click.option("--doc", "doc_id", required=True, type=int, help="Document ID")
@click.option("--points", default=7, help="Number of main points to include")
def generate_summary(doc_id: int, points: int):
    """Generate an audio-friendly summary from a document."""
    _generate_materials(doc_id, "audio_summary", points)


def _generate_materials(doc_id: int, gen_type: str, count: int):
    """Internal function to generate study materials."""
    # Validate API key
    errors = config.validate()
    if errors:
        for error in errors:
            print_error(error)
        return

    init_db()
    session = get_session()
    ops = DatabaseOperations(session)

    document = ops.get_document(doc_id)
    if not document:
        print_error(f"Document {doc_id} not found")
        session.close()
        return

    chunks = ops.get_chunks_for_document(doc_id)
    if not chunks:
        print_error(f"No chunks found for document {doc_id}")
        session.close()
        return

    console.print(f"\n[bold]Document:[/bold] {document.title}")
    console.print(f"[dim]Using {min(len(chunks), config.MAX_CHUNKS_PER_GENERATION)} of {len(chunks)} chunks[/dim]\n")

    generator = StudyMaterialGenerator()
    chunk_texts = [c.content for c in chunks]

    with console.status(f"[bold blue]Generating {gen_type}..."):
        result = generator.generate_from_chunks(chunk_texts, gen_type, count)

    if not result.success:
        print_error(f"Generation failed: {result.error}")
        session.close()
        return

    # Save to database
    content_dict = result.content.model_dump() if result.content else {}

    study_set = ops.create_study_set(
        set_type=gen_type,
        content=content_dict,
        document_id=doc_id,
        title=f"{document.title} - {gen_type.replace('_', ' ').title()}",
        model_used=result.model,
        tokens_used=result.tokens_used,
    )

    session.close()

    print_success(f"Created {gen_type} set (ID: {study_set.id}) with {study_set.item_count} items")
    console.print(f"[dim]Tokens used: {result.tokens_used}[/dim]")
    console.print(f"\nExport with: [bold]study-guide export {study_set.id} --format json[/bold]")


@cli.command()
@click.argument("set_id", type=int)
@click.option("--format", "fmt", default="json", type=click.Choice(["json", "anki", "markdown"]))
@click.option("--output", "-o", type=click.Path(), help="Output file path (optional)")
def export(set_id: int, fmt: str, output: str | None):
    """
    Export a study set to a file.

    SET_ID is the ID of the study set to export.
    """
    init_db()
    session = get_session()
    ops = DatabaseOperations(session)

    study_set = ops.get_study_set(set_id)
    if not study_set:
        print_error(f"Study set {set_id} not found")
        session.close()
        return

    content = ops.get_study_set_content(set_id)
    if not content:
        print_error("Could not parse study set content")
        session.close()
        return

    exporter = get_exporter(fmt)
    if not exporter:
        print_error(f"Unknown export format: {fmt}")
        session.close()
        return

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        config.ensure_directories()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = (study_set.title or "export").replace(" ", "_")[:30]
        filename = f"{safe_title}_{timestamp}{exporter.get_file_extension()}"
        output_path = config.EXPORT_DIR / filename

    result = exporter.export(content, output_path, study_set.title)
    session.close()

    if result.success:
        print_success(f"Exported {result.item_count} items to: {result.filepath}")
    else:
        print_error(f"Export failed: {result.error}")


@cli.command()
@click.argument("set_id", type=int)
def show(set_id: int):
    """Show the content of a study set."""
    init_db()
    session = get_session()
    ops = DatabaseOperations(session)

    study_set = ops.get_study_set(set_id)
    if not study_set:
        print_error(f"Study set {set_id} not found")
        session.close()
        return

    content = ops.get_study_set_content(set_id)
    session.close()

    console.print(Panel.fit(
        f"[bold]{study_set.title}[/bold]\n\n"
        f"Type: {study_set.set_type}\n"
        f"Items: {study_set.item_count}\n"
        f"Created: {study_set.created_at.strftime('%Y-%m-%d %H:%M') if study_set.created_at else 'N/A'}",
        title=f"Study Set #{set_id}",
    ))

    console.print("\n[bold]Content:[/bold]")
    console.print_json(json.dumps(content, indent=2))


if __name__ == "__main__":
    cli()
