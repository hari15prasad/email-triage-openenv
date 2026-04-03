"""
Email Triage Environment — Full OpenEnv implementation.

Simulates a real-world email inbox management task where an AI agent must:
  1. Read incoming emails one by one
  2. Assign a priority level (urgent / high / normal / low)
  3. Assign a category (bug_report / feature_request / billing / general_inquiry / spam / internal / security)
  4. (Hard task) Draft a short reply

The environment cycles through the inbox until all emails are processed.
"""
from typing import Any, Dict, List, Optional
import copy

from email_triage_env.models import (
    Email,
    EmailTriageAction,
    EmailTriageObservation,
    EmailTriageReward,
    StepResult,
)
from email_triage_env.dataset import EASY_EMAILS, MEDIUM_EMAILS, HARD_EMAILS
from email_triage_env.graders import GRADERS


TASK_DESCRIPTIONS = {
    "easy": (
        "EASY TASK: Triage a small inbox of 5 clearly distinct emails. "
        "For each email, assign the correct priority (urgent/high/normal/low) "
        "and category (bug_report/feature_request/billing/general_inquiry/spam/internal/security). "
        "The emails have clear, unambiguous signals."
    ),
    "medium": (
        "MEDIUM TASK: Triage a mixed inbox of 8 emails with more nuanced signals. "
        "Priorities and categories require careful reading. "
        "A short response draft (1-3 sentences) is encouraged and will boost your score."
    ),
    "hard": (
        "HARD TASK: Triage a complex inbox of 10 emails with overlapping signals, "
        "legal/security urgency, and ambiguous categories. "
        "A professional response draft (1-3 sentences) is REQUIRED for each email. "
        "Accuracy of priority + category + response quality all matter."
    ),
}


class EmailTriageEnv:
    """
    OpenEnv-compliant environment for email triage.

    Usage:
        env = EmailTriageEnv(task="easy")
        obs = env.reset()
        while not done:
            action = EmailTriageAction(priority="urgent", category="bug_report")
            result = env.step(action)
            obs, reward, done = result.observation, result.reward, result.done
    """

    def __init__(self, task: str = "easy"):
        if task not in ("easy", "medium", "hard"):
            raise ValueError(f"task must be 'easy', 'medium', or 'hard'. Got: {task!r}")

        self.task = task
        self._email_pool: List[Email] = {
            "easy": EASY_EMAILS,
            "medium": MEDIUM_EMAILS,
            "hard": HARD_EMAILS,
        }[task]

        self._inbox: List[Email] = []
        self._current_idx: int = 0
        self._step_number: int = 0
        self._episode_rewards: List[float] = []
        self._last_feedback: str = ""
        self._done: bool = False

    # ------------------------------------------------------------------
    # OpenEnv core interface
    # ------------------------------------------------------------------

    def reset(self) -> EmailTriageObservation:
        """Reset the environment and return the initial observation."""
        self._inbox = copy.deepcopy(self._email_pool)
        self._current_idx = 0
        self._step_number = 0
        self._episode_rewards = []
        self._last_feedback = "Environment reset. Triage the incoming emails."
        self._done = False

        return self._make_observation()

    def step(self, action: EmailTriageAction) -> StepResult:
        """
        Process the agent's action for the current email.
        Returns (observation, reward, done, info).
        """
        if self._done:
            raise RuntimeError("Episode is done. Call reset() to start a new episode.")
        if self._current_idx >= len(self._inbox):
            raise RuntimeError("No more emails to process. Episode should be done.")

        current_email = self._inbox[self._current_idx]
        self._step_number += 1

        # Grade the action
        grader = GRADERS[self.task]
        reward_obj: EmailTriageReward = grader(action, current_email)

        self._episode_rewards.append(reward_obj.total)
        self._last_feedback = reward_obj.feedback
        self._current_idx += 1

        done = self._current_idx >= len(self._inbox)
        self._done = done

        obs = self._make_observation()

        info = {
            "email_id": current_email.id,
            "ground_truth_priority": current_email.priority_label,
            "ground_truth_category": current_email.category_label,
            "reward_breakdown": reward_obj.dict(),
            "episode_mean_reward": (
                sum(self._episode_rewards) / len(self._episode_rewards)
                if self._episode_rewards else 0.0
            ),
        }

        return StepResult(
            observation=obs,
            reward=reward_obj.total,
            done=done,
            info=info,
        )

    def state(self) -> Dict[str, Any]:
        """Return the full internal state (for debugging / checkpointing)."""
        return {
            "task": self.task,
            "step_number": self._step_number,
            "current_idx": self._current_idx,
            "inbox_size": len(self._inbox),
            "processed_count": self._current_idx,
            "episode_rewards": list(self._episode_rewards),
            "done": self._done,
            "current_email_id": (
                self._inbox[self._current_idx].id
                if self._current_idx < len(self._inbox)
                else None
            ),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_observation(self) -> EmailTriageObservation:
        current_email: Optional[Email] = None
        if self._current_idx < len(self._inbox):
            # Strip ground-truth labels before giving to agent
            raw = self._inbox[self._current_idx]
            current_email = Email(
                id=raw.id,
                sender=raw.sender,
                subject=raw.subject,
                body=raw.body,
                timestamp=raw.timestamp,
                # priority_label and category_label intentionally omitted
            )

        return EmailTriageObservation(
            current_email=current_email,
            inbox_size=len(self._inbox),
            processed_count=self._current_idx,
            last_action_feedback=self._last_feedback,
            task_name=self.task,
            task_description=TASK_DESCRIPTIONS[self.task],
            step_number=self._step_number,
        )

    def score(self) -> float:
        """Return normalized episode score in [0, 1]."""
        if not self._episode_rewards:
            return 0.0
        return sum(self._episode_rewards) / len(self._episode_rewards)
