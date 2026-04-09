---
title: Email Triage OpenEnv
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 📬 Email Triage AI — OpenEnv Environment

> A real-world AI environment where agents learn to triage emails like a professional support specialist — assigning priority, category, and drafting replies across 3 difficulty levels.

**Built for Scaler x Meta x PyTorch OpenEnv Hackathon — Round 1**

🔗 **Live Demo:** [huggingface.co/spaces/Hari15prasad/email-triage-openenv](https://huggingface.co/spaces/Hari15prasad/email-triage-openenv)

---

## 🚨 Problem

Every company receives hundreds of emails daily. Support teams waste hours manually:
- Deciding which emails are **urgent vs low priority**
- Routing emails to the **right department**
- Drafting **professional replies** under time pressure

**Result:** Slow response times, missed critical issues, revenue loss.

---

## 💡 Solution

An OpenEnv-compliant RL environment that trains AI agents to:
1. **Read** incoming emails
2. **Classify** priority (urgent / high / normal / low)
3. **Categorize** type (bug_report / billing / security / spam / etc.)
4. **Draft** a professional reply (required on hard tasks)

Agents receive **partial credit rewards** at every step — enabling continuous learning, not just binary success/failure.

---

## 🏆 Baseline Scores

| Model | Easy | Medium | Hard | Overall |
|---|---|---|---|---|
| llama-3.3-70b-versatile | **1.00** | **0.89** | **0.84** | **0.91** 🥇 |
| llama-3.1-8b-instant | 0.84 | 0.53 | 0.69 | 0.69 |

---

## ⚙️ Architecture

```
Agent (LLM)
    │
    ▼
inference.py  ──── POST /reset ────▶  EmailTriageEnv
    │          ◀── Observation ──────      │
    │                                      │
    ├── GET agent action (LLM call)        ├── dataset.py  (23 real emails)
    │                                      ├── graders.py  (deterministic scoring)
    └── POST /step ────────────────▶       └── models.py   (Pydantic types)
        ◀── reward, done, info ──────
```

```
User Request
    │
    ▼
FastAPI Server (port 7860)
    ├── GET  /health    → status check
    ├── GET  /tasks     → list 3 tasks
    ├── POST /reset     → start episode
    ├── POST /step      → submit action
    ├── GET  /state     → current state
    └── GET  /score     → episode score
```

---

## 🎯 Key Features

- **3 difficulty levels** — Easy (5 emails) → Medium (8 emails) → Hard (10 emails)
- **Partial credit rewards** — priority is an ordered scale, near-misses get partial score
- **23 curated real-world emails** — spam, security alerts, legal notices, production outages
- **Deterministic graders** — same input always produces same score
- **Ground-truth hidden** — agent never sees labels, only the email content
- **Response drafts evaluated** — hard task requires professional reply drafts
- **Full OpenEnv spec** — step() / reset() / state() / openenv.yaml

---

## 🤖 AI Stack

```
LLM Provider:     Groq (OpenAI-compatible API)
Model:            meta-llama/llama-3.3-70b (via llama-3.3-70b-versatile)
Embeddings:       None — pure zero-shot prompting
Classification:   LLM JSON output → deterministic grader
Reward Signal:    Partial credit (priority distance + category match + response quality)
Framework:        OpenEnv by Meta & Hugging Face
```

**Why this works:** The LLM reads email context and reasons about urgency signals, sender patterns, and business impact — exactly like a trained support specialist would.

---

## 📊 Task Design

### Easy Task (5 emails)
Clear, unambiguous signals:
- 🎉 Obvious spam (FREE iPhone scam)
- 📢 CEO all-hands mandatory meeting
- 💳 Standard pricing inquiry
- 🔥 Production outage (500 users down)
- 📰 Tech newsletter

### Medium Task (8 emails)
Requires careful reading:
- AWS security alert (security vs. general?)
- Contractor delay (internal vs. bug?)
- API rate limit (feature vs. billing?)
- Cold outreach (spam vs. general?)

### Hard Task (10 emails)
Overlapping signals + mandatory response drafts:
- Legal copyright notice
- Bug bounty disclosure
- Press inquiry about data breach
- CTO escalation with board deadline
- Payment failure with account suspension threat

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| Environment API | FastAPI + Uvicorn |
| Data Models | Pydantic v2 |
| LLM Client | OpenAI SDK (compatible with Groq, OpenRouter) |
| HTTP Client | httpx |
| Deployment | Hugging Face Spaces (Docker) |
| Package Manager | uv |
| Language | Python 3.11 |

---

## 📁 Project Structure

```
email-triage-openenv/
├── email_triage_env/
│   ├── __init__.py        # Package exports
│   ├── models.py          # Pydantic: Observation, Action, Reward
│   ├── dataset.py         # 23 curated real-world emails
│   ├── graders.py         # Deterministic graders (easy/medium/hard)
│   ├── env.py             # EmailTriageEnv: reset/step/state
│   └── server.py          # FastAPI HTTP server
├── server/
│   └── app.py             # Server entry point
├── tests/
│   └── test_env.py        # Unit + integration tests
├── inference.py           # Baseline agent script
├── validate.py            # Pre-submission validator
├── pyproject.toml         # Project metadata
├── uv.lock                # Locked dependencies
├── openenv.yaml           # OpenEnv spec
├── Dockerfile             # Container definition
└── README.md
```

---

## 🚀 Quick Start

```bash
# Clone
git clone https://huggingface.co/spaces/Hari15prasad/email-triage-openenv
cd email-triage-openenv

# Install
pip install -r requirements.txt

# Start server
uvicorn email_triage_env.server:app --host 0.0.0.0 --port 7860

# Run agent (in another terminal)
export HF_TOKEN="your-groq-api-key"
export API_BASE_URL="https://api.groq.com/openai/v1"
export MODEL_NAME="llama-3.3-70b-versatile"
python inference.py
```

### Docker
```bash
docker build -t email-triage-openenv .
docker run -p 7860:7860 email-triage-openenv
```

---

## 🔌 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/health` | GET | Health check → `{"status":"ok"}` |
| `/tasks` | GET | List all 3 tasks |
| `/reset` | POST | Start new episode `{"task": "easy"}` |
| `/step` | POST | Submit action, get reward |
| `/state` | GET | Full internal state |
| `/score` | GET | Current episode score |
| `/docs` | GET | Interactive API explorer |

---

## 🌱 Future Scope

```
Phase 1 (Current): OpenEnv RL training environment ✅
Phase 2: Gmail/Outlook plugin for real inbox triage
Phase 3: Auto task creation in Jira/Asana from emails
Phase 4: Smart SLA deadline detection and escalation
Phase 5: Multi-agent system (triage + responder + escalator)
Phase 6: Fine-tuned small model (replace 70B with 7B)
Phase 7: Enterprise deployment with audit trails
```

This environment is the **foundation layer** for building production-grade email automation systems. The reward function and graders can be directly used to fine-tune smaller, cheaper models for deployment.

---

## 📈 Reward Function Design

```python
# Priority: ordered scale with partial credit
PRIORITY_ORDER = ["low", "normal", "high", "urgent"]
PARTIAL_CREDIT = {0: 1.0, 1: 0.4, 2: 0.1, 3: 0.0}

# Category: exact match only
category_score = 1.0 if predicted == ground_truth else 0.0

# Response quality (hard task):
# +0.4 base, +0.2 length, +0.2 professional tone, +0.2 relevance

# Final reward (hard task):
reward = 0.35 * priority + 0.40 * category + 0.25 * response
```

---

## 👤 Author

**Hari Prasad R** — [Hari15prasad on HuggingFace](https://huggingface.co/Hari15prasad)

*Scaler x Meta x PyTorch OpenEnv Hackathon — Round 1, April 2026*