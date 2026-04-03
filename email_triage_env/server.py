"""
FastAPI server exposing the Email Triage environment via OpenEnv HTTP API.

Endpoints:
  POST /reset          — start a new episode
  POST /step           — submit an action
  GET  /state          — get current state
  GET  /health         — health check
  GET  /tasks          — list available tasks
"""
import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from email_triage_env.env import EmailTriageEnv
from email_triage_env.models import EmailTriageAction

app = FastAPI(
    title="Email Triage OpenEnv",
    description="Real-world email triage environment for training and evaluating AI agents.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-memory session store (single-user; extend with session IDs for multi-user)
# ---------------------------------------------------------------------------
_env: Optional[EmailTriageEnv] = None


class ResetRequest(BaseModel):
    task: str = "easy"


class StepRequest(BaseModel):
    priority: str
    category: str
    response_draft: str = ""
    reasoning: str = ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok", "env": "email-triage-openenv", "version": "1.0.0"}


@app.get("/")
def root():
    return {
        "🚀 welcome": "Email Triage OpenEnv is live!",
        "📬 what_is_this": (
            "A real-world AI environment where agents learn to triage emails — "
            "assigning priority, category, and drafting replies across 3 difficulty levels."
        ),
        "📊 tasks": {
            "easy": "5 emails — obvious signals, perfect for warm-up",
            "medium": "8 emails — nuanced, requires careful reading",
            "hard": "10 emails — ambiguous, overlapping signals, response required"
        },
        "🎯 best_score": {
            "model": "llama-3.3-70b-versatile",
            "easy": 0.94,
            "medium": 0.89,
            "hard": 0.83,
            "overall": 0.89
        },
        "🔗 endpoints": {
            "health":  "GET  /health",
            "tasks":   "GET  /tasks",
            "reset":   "POST /reset",
            "step":    "POST /step",
            "state":   "GET  /state",
            "score":   "GET  /score",
            "docs":    "GET  /docs  ← interactive API explorer"
        },
        "📦 built_with": ["FastAPI", "OpenEnv", "Pydantic", "Groq", "HuggingFace Spaces"],
        "👤 author": "Hari15prasad",
        "🏆 hackathon": "Scaler x Meta x PyTorch — OpenEnv Round 1"
    }

@app.get("/tasks")
def list_tasks():
    return {
        "tasks": [
            {
                "id": "easy",
                "description": "5 clearly distinct emails. Priority + category only.",
                "email_count": 5,
                "difficulty": "easy",
            },
            {
                "id": "medium",
                "description": "8 nuanced emails. Priority + category + optional response draft.",
                "email_count": 8,
                "difficulty": "medium",
            },
            {
                "id": "hard",
                "description": "10 complex, ambiguous emails. Priority + category + required response.",
                "email_count": 10,
                "difficulty": "hard",
            },
        ]
    }


@app.post("/reset")
def reset(req: ResetRequest = ResetRequest()):
    global _env
    try:
        _env = EmailTriageEnv(task=req.task)
        obs = _env.reset()
        return {
            "observation": obs.dict(),
            "message": f"Environment reset. Task: {req.task}",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
def step(req: StepRequest):
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Call /reset first.")

    action = EmailTriageAction(
        priority=req.priority,
        category=req.category,
        response_draft=req.response_draft,
        reasoning=req.reasoning,
    )

    try:
        result = _env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "observation": result.observation.dict(),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.get("/state")
def state():
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Call /reset first.")
    return _env.state()


@app.get("/score")
def score():
    global _env
    if _env is None:
        raise HTTPException(status_code=400, detail="Call /reset first.")
    return {"score": _env.score(), "task": _env.task}
