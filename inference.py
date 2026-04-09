"""
inference.py — Baseline inference script for Email Triage OpenEnv.

Usage:
    # Option A — Groq
    export API_BASE_URL="https://api.groq.com/openai/v1"
    export MODEL_NAME="llama-3.3-70b-versatile"
    export HF_TOKEN="<your_groq_api_key>"

    # Option B — OpenRouter
    export API_BASE_URL="https://openrouter.ai/api/v1"
    export MODEL_NAME="meta-llama/llama-3.3-70b-instruct"
    export HF_TOKEN="<your_openrouter_api_key>"

    python inference.py

Environment variables:
    API_BASE_URL     — OpenAI-compatible LLM API endpoint
    MODEL_NAME       — model identifier string
    HF_TOKEN         — API key for the chosen provider
    LOCAL_IMAGE_NAME — optional, used when running via from_docker_image()
"""
import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

import httpx
from openai import OpenAI

# ---------------------------------------------------------------------------
# Configuration — reads from environment variables
# API_BASE_URL and MODEL_NAME have sensible defaults
# HF_TOKEN has NO default (judges must supply their own key)
# ---------------------------------------------------------------------------
API_BASE_URL     = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME       = os.getenv("MODEL_NAME",   "llama-3.3-70b-versatile")
HF_TOKEN         = os.getenv("HF_TOKEN", "")
LOCAL_IMAGE_NAME = os.getenv("LOCAL_IMAGE_NAME")

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
if "openrouter.ai" in API_BASE_URL:
    API_KEY = OPENROUTER_KEY or HF_TOKEN
else:
    API_KEY = HF_TOKEN or OPENROUTER_KEY

# No sys.exit — always run and print structured output
if not API_KEY:
    API_KEY = "dummy"

ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:7860")
TEMPERATURE = 0.0
MAX_TOKENS  = 512
MAX_STEPS   = 12

TASKS     = ["easy", "medium", "hard"]
BENCHMARK = "email-triage-openenv"

# ---------------------------------------------------------------------------
# Structured log helpers — plain text format required by Scaler
# ---------------------------------------------------------------------------

def log_start(task, env, model):
    print(f"[START] task={task}", flush=True)

def log_step(step, action, reward, done, error):
    print(f"[STEP] step={step} reward={reward}", flush=True)

def log_end(task, success, steps, score, rewards):
    print(f"[END] task={task} score={score} steps={steps}", flush=True)


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """You are an expert email triage specialist.
For each email you receive, output a JSON object with exactly these fields:
{
  "priority": "<urgent|high|normal|low>",
  "category": "<bug_report|feature_request|billing|general_inquiry|spam|internal|security>",
  "response_draft": "<1-3 sentence professional reply draft>",
  "reasoning": "<1-2 sentence explanation of your priority and category choice>"
}

Priority guidelines:
- urgent: Requires immediate action (production down, security breach, legal, media)
- high: Important, should be handled today (enterprise clients, renewals, data issues)
- normal: Standard business email, handle within 1-2 days
- low: Newsletters, low-stakes inquiries, spam

Category guidelines:
- bug_report: Technical issues, errors, crashes
- feature_request: Product suggestions or enhancement requests
- billing: Payment, pricing, subscription, invoice
- general_inquiry: General questions, newsletters, misc
- spam: Promotional junk, scams, irrelevant mass mail
- internal: From your own company (employees, team comms)
- security: Security alerts, vulnerabilities, data breaches

Output ONLY valid JSON. No preamble, no markdown, no explanation outside the JSON."""


def get_agent_action(client, obs, step, history):
    email = obs.get("current_email") or {}
    user_content = f"""Task: {obs.get("task_description", "")}

Current email (step {step}):
From: {email.get("sender", "unknown")}
Subject: {email.get("subject", "")}
Body: {email.get("body", "")}
Time: {email.get("timestamp", "")}

Feedback from last action: {obs.get("last_action_feedback", "")}
Emails remaining: {obs.get("inbox_size", 0) - obs.get("processed_count", 0)}

Triage this email. Output JSON only."""

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        text = (completion.choices[0].message.content or "").strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as exc:
        print(f"[DEBUG] LLM error at step {step}: {exc}", flush=True)
        return {
            "priority": "normal",
            "category": "general_inquiry",
            "response_draft": "Thank you for your email. We will get back to you shortly.",
            "reasoning": "Fallback action due to parsing error.",
        }


def run_task(task):
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    http = httpx.Client(base_url=ENV_BASE_URL, timeout=30.0)
    rewards = []
    steps_taken = 0
    log_start(task=task, env=BENCHMARK, model=MODEL_NAME)
    try:
        resp = http.post("/reset", json={"task": task})
        resp.raise_for_status()
        obs = resp.json()["observation"]
        done = False
        history = []
        for step in range(1, MAX_STEPS + 1):
            if done:
                break
            action = get_agent_action(client, obs, step, history)
            steps_taken = step
            step_resp = http.post("/step", json=action)
            step_resp.raise_for_status()
            step_data = step_resp.json()
            reward = step_data.get("reward", 0.0)
            done = step_data.get("done", False)
            obs = step_data.get("observation", obs)
            rewards.append(reward)
            history.append(
                f"Step {step}: priority={action.get('priority')}, "
                f"category={action.get('category')}, reward={reward:.3f}"
            )
            log_step(step=step, action=action, reward=reward, done=done, error=None)
            if done:
                break
    except Exception as e:
        print(f"[DEBUG] Episode error: {e}", flush=True)
        log_step(step=steps_taken + 1, action={}, reward=0.0, done=True, error=str(e))
    finally:
        http.close()
    score = min(max(sum(rewards) / len(rewards) if rewards else 0.0, 0.0), 1.0)
    success = score >= 0.6
    log_end(task=task, success=success, steps=steps_taken, score=score, rewards=rewards)
    return {"task": task, "score": score, "steps": steps_taken, "success": success}


def main():
    start_time = time.time()
    print(f"\n{'='*60}", flush=True)
    print(f"Email Triage OpenEnv — Baseline Inference", flush=True)
    print(f"Model: {MODEL_NAME}", flush=True)
    print(f"Environment: {ENV_BASE_URL}", flush=True)
    print(f"{'='*60}\n", flush=True)
    results = []
    for task in TASKS:
        print(f"\n--- Running task: {task.upper()} ---\n", flush=True)
        result = run_task(task)
        results.append(result)
        print(
            f"\n>>> Task '{task}' score: {result['score']:.4f} | success: {result['success']}\n",
            flush=True,
        )
    print(f"\n{'='*60}", flush=True)
    print("FINAL RESULTS:", flush=True)
    overall = sum(r["score"] for r in results) / len(results)
    for r in results:
        status = "PASS" if r["success"] else "FAIL"
        print(f"  {status} {r['task']:8s}  score={r['score']:.4f}  steps={r['steps']}", flush=True)
    print(f"\n  Overall mean score: {overall:.4f}", flush=True)
    total_time = time.time() - start_time
    print(f"  Total time taken: {total_time:.2f} seconds", flush=True)
    print(f"{'='*60}\n", flush=True)


if __name__ == "__main__":
    main()