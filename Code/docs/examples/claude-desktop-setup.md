# Claude Desktop Setup

Add StudyBros to Claude Desktop by editing the configuration file.

## 1. Install StudyBros

```bash
cd /path/to/studybros/Code
pip install -e .
```

## 2. Edit Claude Desktop config

Open your Claude Desktop configuration file:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the `studybros` server:

```json
{
  "mcpServers": {
    "studybros": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "/path/to/studybros/Code"
    }
  }
}
```

Replace `/path/to/studybros/Code` with the actual absolute path to the `Code` directory.

**Windows path example:**

```json
{
  "mcpServers": {
    "studybros": {
      "command": "python",
      "args": ["-m", "mcp_server"],
      "cwd": "C:\\Users\\you\\projects\\studybros\\Code"
    }
  }
}
```

## 3. Restart Claude Desktop

Close and reopen Claude Desktop. The StudyBros server will start automatically.

## 4. Verify

Ask Claude:

> What tools do you have from StudyBros?

You should see all 10 tools listed. Then try:

> Ingest the file at C:\Users\you\notes\chapter1.pdf

## Troubleshooting

**Server not appearing:** Confirm the `cwd` path points to the directory containing `mcp_server/`. The server is launched as `python -m mcp_server` from that directory.

**Python not found:** Use the full path to your Python executable:

```json
{
  "mcpServers": {
    "studybros": {
      "command": "C:\\Users\\you\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
      "args": ["-m", "mcp_server"],
      "cwd": "C:\\Users\\you\\projects\\studybros\\Code"
    }
  }
}
```

**Module not found:** Make sure you ran `pip install -e .` in the `Code` directory using the same Python that Claude Desktop is configured to use.
