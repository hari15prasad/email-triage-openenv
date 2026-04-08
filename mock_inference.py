# mock_inference.py
# A rule-based agent that runs without any API keys or internet.
import json
import httpx
import time

ENV_BASE_URL = "http://localhost:7860"
TASKS = ["easy", "medium", "hard"]

def get_mock_action(obs):
    email = obs.get("current_email", {})
    body = email.get("body", "").lower()
    subject = email.get("subject", "").lower()

    # Simple keyword-based triage
    if any(k in body or k in subject for k in ["urgent", "broken", "critical", "down"]):
        priority, category = "urgent", "bug_report"
    elif any(k in body or k in subject for k in ["billing", "invoice", "pay"]):
        priority, category = "high", "billing"
    elif any(k in body or k in subject for k in ["spam", "win", "offer"]):
        priority, category = "low", "spam"
    else:
        priority, category = "normal", "general_inquiry"

    return {
        "priority": priority,
        "category": category,
        "response_draft": "This is a mock response created by the rule-based agent.",
        "reasoning": "Determined via keyword matching (Offline mode)."
    }

def run_task(task):
    print(f"\n--- Running Task: {task.upper()} ---")
    with httpx.Client(base_url=ENV_BASE_URL, timeout=10.0) as http:
        resp = http.post("/reset", json={"task": task})
        obs = resp.json()["observation"]
        done = False
        steps = 0
        total_reward = 0
        
        print(f"[START] task={task}")
        while not done:
            action = get_mock_action(obs)
            steps += 1
            step_resp = http.post("/step", json=action)
            data = step_resp.json()
            reward = data.get("reward", 0.0)
            done = data.get("done", False)
            obs = data.get("observation", obs)
            total_reward += reward
            print(f"[STEP] step={steps} reward={reward:.2f}")
        
        score = total_reward / steps if steps > 0 else 0
        print(f"[END] task={task} score={score:.4f} steps={steps}")

if __name__ == "__main__":
    print("🚀 Running Offline Mock Inference...")
    try:
        # Check if server is running
        httpx.get(f"{ENV_BASE_URL}/health")
        for task in TASKS:
            run_task(task)
    except Exception:
        print(f"❌ Error: Server not found at {ENV_BASE_URL}. Run 'python app.py' first!")
