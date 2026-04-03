"""
app.py — Hugging Face Spaces entry point.

This file is the HF Space application entrypoint.
It starts the FastAPI server on port 7860 so the Space
can respond to OpenEnv reset() / step() / state() calls.
"""
import uvicorn
from email_triage_env.server import app  # noqa: F401 — imported for uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "email_triage_env.server:app",
        host="0.0.0.0",
        port=7860,
        workers=1,
        log_level="info",
    )
