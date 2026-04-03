"""
Deterministic graders for each Email Triage task.

Each grader takes the agent's EmailTriageAction and the ground-truth Email,
and returns an EmailTriageReward with a total score in [0.0, 1.0].
"""
from email_triage_env.models import Email, EmailTriageAction, EmailTriageReward

# Priority adjacency — partial credit for near-misses
PRIORITY_ORDER = ["low", "normal", "high", "urgent"]
PRIORITY_PARTIAL = {
    0: 1.0,   # exact match
    1: 0.4,   # one level off
    2: 0.1,   # two levels off
    3: 0.0,   # completely wrong
}

# Category exact-match only (no partial credit — categories are discrete)
VALID_CATEGORIES = {
    "bug_report", "feature_request", "billing",
    "general_inquiry", "spam", "internal", "security"
}


def _priority_score(predicted: str, ground_truth: str) -> tuple[float, str]:
    predicted = predicted.strip().lower()
    ground_truth = ground_truth.strip().lower()

    if predicted not in PRIORITY_ORDER:
        return 0.0, f"Invalid priority '{predicted}'. Must be one of: {PRIORITY_ORDER}"

    pred_idx = PRIORITY_ORDER.index(predicted)
    true_idx = PRIORITY_ORDER.index(ground_truth)
    distance = abs(pred_idx - true_idx)
    score = PRIORITY_PARTIAL[distance]

    if score == 1.0:
        feedback = f"✓ Priority '{predicted}' is correct."
    elif score > 0:
        feedback = f"~ Priority '{predicted}' is off by {distance} level(s) from '{ground_truth}'."
    else:
        feedback = f"✗ Priority '{predicted}' is far from correct (expected '{ground_truth}')."

    return score, feedback


def _category_score(predicted: str, ground_truth: str) -> tuple[float, str]:
    predicted = predicted.strip().lower()
    ground_truth = ground_truth.strip().lower()

    if predicted not in VALID_CATEGORIES:
        return 0.0, f"Invalid category '{predicted}'."

    if predicted == ground_truth:
        return 1.0, f"✓ Category '{predicted}' is correct."
    else:
        return 0.0, f"✗ Category '{predicted}' is wrong (expected '{ground_truth}')."


def _response_quality_score(response: str, email: Email, task_level: str) -> tuple[float, str]:
    """
    Heuristic scoring for response drafts.
    Checks: non-empty, appropriate length, mentions key context.
    """
    if not response or len(response.strip()) < 10:
        if task_level == "hard":
            return 0.0, "✗ Response draft is required for hard task."
        return 0.5, "~ No response draft provided (optional for this task)."

    score = 0.4  # base for having a response
    feedback_parts = []

    # Length check: 20–500 chars is reasonable for a short draft
    length = len(response.strip())
    if 20 <= length <= 500:
        score += 0.2
        feedback_parts.append("appropriate length")
    elif length > 500:
        score += 0.1
        feedback_parts.append("response is quite long")

    # Professionalism signals
    prof_signals = ["thank", "sorry", "understand", "help", "team", "we ", "please", "let us"]
    if any(sig in response.lower() for sig in prof_signals):
        score += 0.2
        feedback_parts.append("professional tone")

    # Relevance: does response mention something from the email?
    email_words = set(email.subject.lower().split() + email.body.lower().split()[:20])
    response_words = set(response.lower().split())
    overlap = len(email_words & response_words)
    if overlap >= 2:
        score += 0.2
        feedback_parts.append("references email context")

    score = min(score, 1.0)
    feedback = f"Response score {score:.2f}: {', '.join(feedback_parts) if feedback_parts else 'basic draft'}."
    return score, feedback


# ---------------------------------------------------------------------------
# Task-level graders
# ---------------------------------------------------------------------------

def grade_easy(action: EmailTriageAction, email: Email) -> EmailTriageReward:
    """
    Easy task: priority + category only. Response not required.
    Weights: priority 50%, category 50%.
    """
    p_score, p_fb = _priority_score(action.priority, email.priority_label)
    c_score, c_fb = _category_score(action.category, email.category_label)
    r_score = 0.5  # not evaluated

    total = 0.5 * p_score + 0.5 * c_score
    feedback = f"{p_fb} | {c_fb}"

    return EmailTriageReward(
        priority_score=p_score,
        category_score=c_score,
        response_score=r_score,
        total=round(total, 4),
        feedback=feedback,
    )


def grade_medium(action: EmailTriageAction, email: Email) -> EmailTriageReward:
    """
    Medium task: priority + category, harder emails, partial credit still applies.
    Response provides small bonus. Weights: priority 45%, category 45%, response 10%.
    """
    p_score, p_fb = _priority_score(action.priority, email.priority_label)
    c_score, c_fb = _category_score(action.category, email.category_label)
    r_score, r_fb = _response_quality_score(action.response_draft, email, "medium")

    total = 0.45 * p_score + 0.45 * c_score + 0.10 * r_score
    feedback = f"{p_fb} | {c_fb} | {r_fb}"

    return EmailTriageReward(
        priority_score=p_score,
        category_score=c_score,
        response_score=r_score,
        total=round(total, 4),
        feedback=feedback,
    )


def grade_hard(action: EmailTriageAction, email: Email) -> EmailTriageReward:
    """
    Hard task: priority + category + mandatory response draft.
    Stricter partial credit on priority. Weights: priority 35%, category 40%, response 25%.
    """
    p_score, p_fb = _priority_score(action.priority, email.priority_label)
    c_score, c_fb = _category_score(action.category, email.category_label)
    r_score, r_fb = _response_quality_score(action.response_draft, email, "hard")

    total = 0.35 * p_score + 0.40 * c_score + 0.25 * r_score
    feedback = f"{p_fb} | {c_fb} | {r_fb}"

    return EmailTriageReward(
        priority_score=p_score,
        category_score=c_score,
        response_score=r_score,
        total=round(total, 4),
        feedback=feedback,
    )


GRADERS = {
    "easy": grade_easy,
    "medium": grade_medium,
    "hard": grade_hard,
}
