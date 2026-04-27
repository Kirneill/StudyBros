"""StudyBros FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import documents, export, gamification, generate, study, study_sets, upload
from study_guide.database.schema import init_db

app = FastAPI(
    title="StudyBros API",
    description="AI-powered study platform with FSRS spaced repetition and gamification",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(study_sets.router, prefix="/api/study-sets", tags=["study-sets"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(generate.router, prefix="/api/generate", tags=["generate"])
app.include_router(study.router, prefix="/api/study", tags=["study"])
app.include_router(gamification.router, prefix="/api/gamification", tags=["gamification"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
