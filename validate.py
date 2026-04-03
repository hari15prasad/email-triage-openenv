"""
validate.py — Pre-submission validation script for Email Triage OpenEnv.

Runs all pre-submission checklist items locally:
  1. OpenEnv spec compliance (openenv.yaml exists, required fields present)
  2. Environment instantiates and resets correctly
  3. Step/state/done cycle works for all 3 tasks
  4. Graders produce scores in [0.0, 1.0]
  5. Reward provides partial progress signal (not purely binary)
  6. 3+ tasks with distinct difficulty

Run with: python validate.py
"""
import sys
import os
import yaml
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PASS = "✓"
FAIL = "✗"
results = []


def check(name: str, condition: bool, detail: str = "") -> bool:
    status = PASS if condition else FAIL
    msg = f"  {status} {name}"
    if detail:
        msg += f"\n       {detail}"
    print(msg)
    results.append(condition)
    return condition


def section(title: str):
    print(f"\n{'─'*55}")
    print(f"  {title}")
    print(f"{'─'*55}")


# ---------------------------------------------------------------------------
# 0. Setup pydantic shim if not installed
# ---------------------------------------------------------------------------
try:
    import pydantic
except ImportError:
    import types

    class _BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def dict(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

    pydantic = types.ModuleType('pydantic')
    pydantic.BaseModel = _BaseModel
    pydantic.Field = lambda *a, **kw: None
    sys.modules['pydantic'] = pydantic


# ---------------------------------------------------------------------------
print("=" * 55)
print("  Email Triage OpenEnv — Pre-Submission Validator")
print("=" * 55)

# ---------------------------------------------------------------------------
section("1. OpenEnv Spec Files")
# ---------------------------------------------------------------------------
check("openenv.yaml exists", os.path.exists("openenv.yaml"))

try:
    with open("openenv.yaml") as f:
        spec = yaml.safe_load(f) if 'yaml' in sys.modules else {}
    required_keys = ["name", "version", "description", "tasks", "observation_space", "action_space", "reward"]
    for key in required_keys:
        check(f"  openenv.yaml has '{key}'", key in spec)
except Exception as e:
    # yaml may not be installed; check file exists at minimum
    check("openenv.yaml is valid YAML", False, str(e))

check("Dockerfile exists", os.path.exists("Dockerfile"))
check("requirements.txt exists", os.path.exists("requirements.txt"))
check("inference.py exists", os.path.exists("inference.py"))
check("app.py (HF Space entry) exists", os.path.exists("app.py"))

# ---------------------------------------------------------------------------
section("2. Environment Import & Instantiation")
# ---------------------------------------------------------------------------
try:
    from email_triage_env.env import EmailTriageEnv
    from email_triage_env.models import EmailTriageAction, EmailTriageObservation, EmailTriageReward
    check("email_triage_env package imports", True)
except Exception as e:
    check("email_triage_env package imports", False, str(e))
    print("\nCannot continue without package. Fix imports first.")
    sys.exit(1)

# ---------------------------------------------------------------------------
section("3. Tasks: 3+ tasks with graders")
# ---------------------------------------------------------------------------
from email_triage_env.graders import GRADERS
check("3+ tasks defined", len(GRADERS) >= 3, f"Found: {list(GRADERS.keys())}")
check("'easy' task exists", "easy" in GRADERS)
check("'medium' task exists", "medium" in GRADERS)
check("'hard' task exists", "hard" in GRADERS)

from email_triage_env.dataset import EASY_EMAILS, MEDIUM_EMAILS, HARD_EMAILS
check("easy task has emails", len(EASY_EMAILS) >= 3, f"Count: {len(EASY_EMAILS)}")
check("medium task has emails", len(MEDIUM_EMAILS) >= 3, f"Count: {len(MEDIUM_EMAILS)}")
check("hard task has emails", len(HARD_EMAILS) >= 3, f"Count: {len(HARD_EMAILS)}")

# ---------------------------------------------------------------------------
section("4. reset() → returns Observation")
# ---------------------------------------------------------------------------
for task in ["easy", "medium", "hard"]:
    try:
        env = EmailTriageEnv(task=task)
        obs = env.reset()
        check(f"reset() works for task='{task}'", obs is not None)
        check(
            f"  observation has current_email",
            obs.current_email is not None,
        )
        check(
            f"  labels hidden from agent",
            obs.current_email.priority_label is None and obs.current_email.category_label is None,
        )
    except Exception as e:
        check(f"reset() works for task='{task}'", False, str(e))

# ---------------------------------------------------------------------------
section("5. step() → reward in [0.0, 1.0], done flag, info")
# ---------------------------------------------------------------------------
env = EmailTriageEnv(task="easy")
env.reset()
action = EmailTriageAction(priority="normal", category="spam", response_draft="", reasoning="")
result = env.step(action)

check("step() returns reward", result.reward is not None)
check("reward in [0.0, 1.0]", 0.0 <= result.reward <= 1.0, f"reward={result.reward}")
check("done is bool", isinstance(result.done, bool))
check("info contains ground_truth", "ground_truth_priority" in result.info)
check("info contains reward_breakdown", "reward_breakdown" in result.info)

# ---------------------------------------------------------------------------
section("6. state() returns dict with required fields")
# ---------------------------------------------------------------------------
state = env.state()
required_state_fields = ["task", "step_number", "current_idx", "done", "episode_rewards"]
for field in required_state_fields:
    check(f"state() has '{field}'", field in state)

# ---------------------------------------------------------------------------
section("7. Reward provides partial progress (not just binary)")
# ---------------------------------------------------------------------------
from email_triage_env.graders import grade_easy
from email_triage_env.dataset import EASY_EMAILS

email = EASY_EMAILS[0]  # low / spam
r_perfect = grade_easy(EmailTriageAction(priority="low", category="spam", response_draft="", reasoning=""), email)
r_partial = grade_easy(EmailTriageAction(priority="normal", category="spam", response_draft="", reasoning=""), email)
r_wrong = grade_easy(EmailTriageAction(priority="urgent", category="bug_report", response_draft="", reasoning=""), email)

check("Partial credit for near-miss priority", r_partial.total > r_wrong.total,
      f"partial={r_partial.total:.3f} > wrong={r_wrong.total:.3f}")
check("Perfect > partial > wrong", r_perfect.total > r_partial.total > r_wrong.total,
      f"perfect={r_perfect.total:.3f}, partial={r_partial.total:.3f}, wrong={r_wrong.total:.3f}")
check("Rewards span full [0, 1] range", r_perfect.total == 1.0 and r_wrong.total == 0.0)

# ---------------------------------------------------------------------------
section("8. Graders deterministic (same input → same output)")
# ---------------------------------------------------------------------------
action_test = EmailTriageAction(priority="high", category="billing", response_draft="test", reasoning="")
r1 = grade_easy(action_test, EASY_EMAILS[2])
r2 = grade_easy(action_test, EASY_EMAILS[2])
check("Graders are deterministic", r1.total == r2.total, f"{r1.total} == {r2.total}")

# ---------------------------------------------------------------------------
section("9. All rewards in [0.0, 1.0] across all emails")
# ---------------------------------------------------------------------------
from email_triage_env.graders import grade_easy, grade_medium, grade_hard

all_in_range = True
for email in EASY_EMAILS + MEDIUM_EMAILS + HARD_EMAILS:
    for grader_fn in [grade_easy, grade_medium, grade_hard]:
        for p in ["urgent", "high", "normal", "low", "invalid"]:
            for c in ["bug_report", "spam", "billing", "nonsense"]:
                try:
                    r = grader_fn(EmailTriageAction(priority=p, category=c, response_draft="test", reasoning=""), email)
                    if not (0.0 <= r.total <= 1.0):
                        all_in_range = False
                        print(f"    OUT OF RANGE: {r.total} for p={p}, c={c}, email={email.id}")
                except Exception as e:
                    all_in_range = False
                    print(f"    ERROR: {e}")

check("All grader outputs in [0.0, 1.0]", all_in_range)

# ---------------------------------------------------------------------------
section("10. Full episode completes without error")
# ---------------------------------------------------------------------------
for task in ["easy", "medium", "hard"]:
    try:
        env = EmailTriageEnv(task=task)
        env.reset()
        done = False
        steps = 0
        while not done and steps < 20:
            result = env.step(EmailTriageAction(
                priority="normal", category="general_inquiry",
                response_draft="Thank you for your message.",
                reasoning="Default action."
            ))
            done = result.done
            steps += 1
        check(f"Full episode completes for '{task}' (steps={steps})", done)
    except Exception as e:
        check(f"Full episode completes for '{task}'", False, str(e))

# ---------------------------------------------------------------------------
print(f"\n{'='*55}")
passed = sum(results)
total = len(results)
all_pass = passed == total
status = "ALL CHECKS PASSED ✓" if all_pass else f"{passed}/{total} PASSED — fix failures before submitting"
print(f"  {status}")
print(f"{'='*55}\n")
sys.exit(0 if all_pass else 1)
