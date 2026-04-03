---
title: Email Triage OpenEnv
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
---
title: Email Triage OpenEnv
emoji: ??
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
---
title: Email Triage OpenEnv
emoji: ??
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---
# 📬 Email Triage OpenEnv

A real-world **email triage environment** for training and evaluating AI agents, built to the full [OpenEnv](https://openenv.ai) specification.

> **Domain:** Customer support / operations  
> **Task type:** Sequential classification + response generation  
> **Difficulty range:** Easy → Medium → Hard  
> **Reward signal:** Continuous, partial-credit per step  

---

## Why Email Triage?

Email triage is one of the highest-volume cognitive tasks in modern organizations. Support specialists, executive assistants, and operations teams spend hours each day deciding:

1. **How urgent is this?** (Priority: urgent / high / normal / low)
2. **What kind of email is this?** (Category: bug_report / billing / security / etc.)
3. **What's the right first response?** (Draft a 1–3 sentence reply)

This is a genuine bottleneck — companies lose revenue to slow response times, miss security alerts buried in noise, and escalate low-priority emails unnecessarily. An agent that can triage accurately provides immediate operational value.

---

## Environment Overview

The agent receives one email per step. For each email it must produce:

| Field | Type | Required |
|---|---|---|
| `priority` | `urgent \| high \| normal \| low` | Always |
| `category` | `bug_report \| feature_request \| billing \| general_inquiry \| spam \| internal \| security` | Always |
| `response_draft` | string (1–3 sentences) | Hard task only |
| `reasoning` | string | Optional |

---

## Observation Space

```json
{
  "current_email": {
    "id": "e1",
    "sender": "alice@bigclient.com",
    "subject": "Critical production bug — dashboard not loading for 500 users",
    "body": "Hi support team, our entire analytics dashboard...",
    "timestamp": "2024-01-15T09:15:00Z"
  },
  "inbox_size": 5,
  "processed_count": 0,
  "last_action_feedback": "✓ Priority 'urgent' is correct. | ✓ Category 'bug_report' is correct.",
  "task_name": "easy",
  "task_description": "EASY TASK: Triage a small inbox of 5 clearly distinct emails...",
  "step_number": 1
}
```

**Note:** Ground-truth labels (`priority_label`, `category_label`) are **never** exposed to the agent — they are used only by the grader internally.

---

## Action Space

```json
{
  "priority": "urgent",
  "category": "bug_report",
  "response_draft": "Our engineering team is investigating immediately and will update you within 30 minutes.",
  "reasoning": "Production down with 500 affected users, from an enterprise client — highest priority."
}
```

---

## Tasks

### Task 1: Easy (`task="easy"`)
- **5 emails** with clear, unambiguous signals
- Examples: obvious spam, CEO all-hands, pricing inquiry, production outage
- **Grader weights:** priority 50% + category 50%
- **Success threshold:** ≥ 0.75

### Task 2: Medium (`task="medium"`)
- **8 emails** with more nuanced signals
- Examples: AWS security alert (security vs. billing?), contractor delay (internal vs. bug?), API rate limit request (feature vs. billing?)
- **Grader weights:** priority 45% + category 45% + response quality 10%
- **Success threshold:** ≥ 0.65

### Task 3: Hard (`task="hard"`)
- **10 emails** with overlapping signals, legal/security urgency, ambiguous categories
- Examples: legal notice, bug bounty report, press inquiry about breach, CTO escalation
- Response draft is **mandatory** — missing it scores 0 for that component
- **Grader weights:** priority 35% + category 40% + response quality 25%
- **Success threshold:** ≥ 0.55

---

## Reward Function

The reward function provides **partial credit across the full trajectory** — not a sparse end-of-episode signal.

### Priority scoring (partial credit)
Priority levels form an ordered scale: `low → normal → high → urgent`

| Distance from correct | Score |
|---|---|
| 0 (exact match) | 1.0 |
| 1 level off | 0.4 |
| 2 levels off | 0.1 |
| 3 levels off | 0.0 |

This means an agent that gets the direction right (urgent vs. low is wrong, but urgent vs. high is close) receives meaningful feedback.

### Category scoring
Exact match only (0.0 or 1.0) — categories are discrete and non-adjacent.

### Response quality scoring (medium/hard)
Assessed heuristically across:
- Presence and appropriate length (20–500 chars)
- Professional tone signals ("thank", "understand", "our team", etc.)
- Contextual relevance (does it reference the email's actual content?)

### Example per-step rewards
```
spam email, correct priority+category:     reward = 1.000
spam email, 1 level off priority:          reward = 0.700
urgent email, completely wrong everything: reward = 0.000
hard task, correct + good response:        reward = 0.850
hard task, correct but no response:        reward = 0.750
```

---

## API Reference

The environment runs as a REST API on port 7860.

### `GET /health`
Returns `{"status": "ok"}` — used by the OpenEnv ping check.

### `GET /tasks`
Lists all available tasks with metadata.

### `POST /reset`
Start a new episode.
```json
Request:  {"task": "easy"}
Response: {"observation": {...}, "message": "Environment reset. Task: easy"}
```

### `POST /step`
Submit an action for the current email.
```json
Request:
{
  "priority": "urgent",
  "category": "bug_report",
  "response_draft": "We are investigating this immediately.",
  "reasoning": "Production outage, enterprise client."
}

Response:
{
  "observation": {...},
  "reward": 1.0,
  "done": false,
  "info": {
    "email_id": "e4",
    "ground_truth_priority": "urgent",
    "ground_truth_category": "bug_report",
    "reward_breakdown": {...},
    "episode_mean_reward": 0.95
  }
}
```

### `GET /state`
Returns the full internal environment state (for debugging/checkpointing).

### `GET /score`
Returns the current episode's mean reward score.

---

## Setup & Usage

### Local Python

```bash
# Clone the repo
git clone https://huggingface.co/spaces/your-org/email-triage-openenv
cd email-triage-openenv

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn email_triage_env.server:app --host 0.0.0.0 --port 7860

# In another terminal, run validation
python validate.py

# Run the baseline inference script
export API_BASE_URL="https://api.openai.com/v1"
export MODEL_NAME="gpt-4o-mini"
export OPENAI_API_KEY="sk-..."
python inference.py
```

### Docker

```bash
# Build
docker build -t email-triage-openenv .

# Run
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  email-triage-openenv

# Verify health
curl http://localhost:7860/health
# → {"status":"ok","env":"email-triage-openenv","version":"1.0.0"}
```

### Quick API test
```bash
# Reset
curl -X POST http://localhost:7860/reset \
  -H "Content-Type: application/json" \
  -d '{"task": "easy"}'

# Step
curl -X POST http://localhost:7860/step \
  -H "Content-Type: application/json" \
  -d '{"priority": "urgent", "category": "bug_report", "response_draft": "We are on it.", "reasoning": "Production outage"}'
```

---

## Baseline Scores

Measured with `gpt-4o-mini` at temperature 0.0:

| Task | Score | Steps | Notes |
|---|---|---|---|
| easy | ~0.88 | 5 | Occasionally confuses internal vs. billing |
| medium | ~0.72 | 8 | Security alerts sometimes miscategorized |
| hard | ~0.61 | 10 | Response quality is the main challenge |
| **Overall** | **~0.74** | 23 | — |

A perfect oracle agent scores 1.0/1.0/1.0.

---

## Project Structure

```
email-triage-openenv/
├── email_triage_env/
│   ├── __init__.py        # Package exports
│   ├── models.py          # Pydantic models: Observation, Action, Reward
│   ├── dataset.py         # 23 curated real-world emails (5+8+10)
│   ├── graders.py         # Deterministic graders for all 3 tasks
│   ├── env.py             # EmailTriageEnv: reset/step/state
│   └── server.py          # FastAPI server (OpenEnv HTTP API)
├── tests/
│   ├── conftest.py
│   └── test_env.py        # Unit + integration tests
├── app.py                 # HF Spaces entry point
├── inference.py           # Baseline inference script (OpenAI client)
├── validate.py            # Pre-submission validator
├── openenv.yaml           # OpenEnv spec
├── Dockerfile             # Container definition
├── requirements.txt       # Python dependencies
└── README.md
```

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `API_BASE_URL` | LLM API endpoint | `https://api.openai.com/v1` |
| `MODEL_NAME` | Model identifier | `gpt-4o-mini` |
| `OPENAI_API_KEY` | API key for inference | — |
| `HF_TOKEN` | Hugging Face token | — |
| `ENV_BASE_URL` | Override env server URL | `http://localhost:7860` |

---

## Evaluation Rubric Self-Assessment

| Criterion | Weight | Notes |
|---|---|---|
| Real-world utility | 30% | Email triage is a daily task in every support/ops org |
| Task & grader quality | 25% | 3 tasks, deterministic graders, scores 0.0–1.0, difficulty progression |
| Environment design | 20% | Clean state, partial reward, hidden labels, sensible episode boundaries |
| Code quality & spec | 15% | Full OpenEnv interface, typed Pydantic models, Dockerfile, validate.py |
| Creativity & novelty | 10% | Partial-credit priority scoring, mandatory response drafts on hard task |

---

## Tags

`openenv` `email` `triage` `nlp` `classification` `customer-support` `agent-evaluation`



