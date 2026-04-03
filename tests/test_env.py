"""
Tests for the Email Triage OpenEnv environment.
Run with: python -m pytest tests/ -v
"""
import pytest
from email_triage_env.env import EmailTriageEnv
from email_triage_env.models import EmailTriageAction
from email_triage_env.graders import grade_easy, grade_medium, grade_hard
from email_triage_env.dataset import EASY_EMAILS, MEDIUM_EMAILS, HARD_EMAILS


class TestReset:
    def test_reset_returns_observation(self):
        env = EmailTriageEnv(task="easy")
        obs = env.reset()
        assert obs is not None
        assert obs.current_email is not None
        assert obs.inbox_size == 5
        assert obs.processed_count == 0
        assert obs.step_number == 0
        assert obs.task_name == "easy"

    def test_reset_hides_labels(self):
        env = EmailTriageEnv(task="easy")
        obs = env.reset()
        # Agent should not see ground-truth labels
        assert obs.current_email.priority_label is None
        assert obs.current_email.category_label is None

    def test_reset_idempotent(self):
        env = EmailTriageEnv(task="easy")
        obs1 = env.reset()
        env.step(EmailTriageAction(priority="normal", category="spam"))
        obs2 = env.reset()
        assert obs1.inbox_size == obs2.inbox_size
        assert obs2.processed_count == 0


class TestStep:
    def test_step_returns_result(self):
        env = EmailTriageEnv(task="easy")
        env.reset()
        action = EmailTriageAction(priority="urgent", category="bug_report")
        result = env.step(action)
        assert result is not None
        assert 0.0 <= result.reward <= 1.0
        assert isinstance(result.done, bool)
        assert result.observation is not None

    def test_full_easy_episode(self):
        env = EmailTriageEnv(task="easy")
        env.reset()
        results = []
        done = False
        for _ in range(10):
            if done:
                break
            action = EmailTriageAction(priority="normal", category="general_inquiry")
            result = env.step(action)
            results.append(result)
            done = result.done
        assert result.done is True
        assert result.observation.processed_count == 5

    def test_step_after_done_raises(self):
        env = EmailTriageEnv(task="easy")
        env.reset()
        for _ in range(5):
            env.step(EmailTriageAction(priority="low", category="spam"))
        with pytest.raises(RuntimeError):
            env.step(EmailTriageAction(priority="low", category="spam"))

    def test_inbox_size_medium(self):
        env = EmailTriageEnv(task="medium")
        obs = env.reset()
        assert obs.inbox_size == 8

    def test_inbox_size_hard(self):
        env = EmailTriageEnv(task="hard")
        obs = env.reset()
        assert obs.inbox_size == 10

    def test_perfect_score_easy(self):
        """Agent that always gets the right answer should score ~1.0."""
        env = EmailTriageEnv(task="easy")
        env.reset()
        correct_actions = [
            EmailTriageAction(priority="low", category="spam"),
            EmailTriageAction(priority="urgent", category="internal"),
            EmailTriageAction(priority="normal", category="billing"),
            EmailTriageAction(priority="urgent", category="bug_report"),
            EmailTriageAction(priority="low", category="general_inquiry"),
        ]
        rewards = []
        for action in correct_actions:
            result = env.step(action)
            rewards.append(result.reward)
        score = sum(rewards) / len(rewards)
        assert score >= 0.95, f"Expected high score, got {score}"

    def test_wrong_actions_score_low(self):
        """Agent that always gets everything wrong should score low."""
        env = EmailTriageEnv(task="easy")
        env.reset()
        rewards = []
        for _ in range(5):
            result = env.step(EmailTriageAction(priority="urgent", category="spam"))
            rewards.append(result.reward)
        # First email is spam/low — marking as urgent/spam gets wrong priority
        # Score should be below perfect
        score = sum(rewards) / len(rewards)
        assert score < 0.9  # not a perfect score

    def test_info_contains_ground_truth(self):
        env = EmailTriageEnv(task="easy")
        env.reset()
        result = env.step(EmailTriageAction(priority="low", category="spam"))
        assert "ground_truth_priority" in result.info
        assert "ground_truth_category" in result.info
        assert result.info["ground_truth_priority"] == "low"
        assert result.info["ground_truth_category"] == "spam"


class TestState:
    def test_state_after_reset(self):
        env = EmailTriageEnv(task="easy")
        env.reset()
        state = env.state()
        assert state["task"] == "easy"
        assert state["current_idx"] == 0
        assert state["done"] is False

    def test_state_updates_after_step(self):
        env = EmailTriageEnv(task="easy")
        env.reset()
        env.step(EmailTriageAction(priority="low", category="spam"))
        state = env.state()
        assert state["current_idx"] == 1
        assert len(state["episode_rewards"]) == 1


class TestGraders:
    def test_exact_match_priority(self):
        email = EASY_EMAILS[0]  # spam/low
        reward = grade_easy(
            EmailTriageAction(priority="low", category="spam"), email
        )
        assert reward.priority_score == 1.0
        assert reward.category_score == 1.0
        assert reward.total == 1.0

    def test_partial_credit_priority(self):
        email = EASY_EMAILS[0]  # low priority
        # normal is 1 level off from low
        reward = grade_easy(
            EmailTriageAction(priority="normal", category="spam"), email
        )
        assert reward.priority_score == 0.4  # one level off
        assert 0.4 < reward.total < 1.0

    def test_wrong_category_no_credit(self):
        email = EASY_EMAILS[0]  # spam
        reward = grade_easy(
            EmailTriageAction(priority="low", category="bug_report"), email
        )
        assert reward.category_score == 0.0

    def test_invalid_priority_zero_score(self):
        email = EASY_EMAILS[0]
        reward = grade_easy(
            EmailTriageAction(priority="critical", category="spam"), email
        )
        assert reward.priority_score == 0.0

    def test_hard_grader_response_required(self):
        email = HARD_EMAILS[0]
        reward = grade_hard(
            EmailTriageAction(priority="urgent", category="bug_report", response_draft=""),
            email,
        )
        assert reward.response_score == 0.0  # no response penalty

    def test_hard_grader_good_response(self):
        email = HARD_EMAILS[0]
        reward = grade_hard(
            EmailTriageAction(
                priority="urgent",
                category="bug_report",
                response_draft=(
                    "Thank you for escalating this. Our team is investigating the data "
                    "pipeline delay urgently and will schedule a call within the hour."
                ),
            ),
            email,
        )
        assert reward.response_score > 0.5

    def test_reward_always_in_range(self):
        """All graders must return scores in [0, 1]."""
        for email in EASY_EMAILS + MEDIUM_EMAILS + HARD_EMAILS:
            for grader_fn, action in [
                (grade_easy, EmailTriageAction(priority="urgent", category="bug_report")),
                (grade_medium, EmailTriageAction(priority="low", category="spam")),
                (grade_hard, EmailTriageAction(priority="high", category="internal", response_draft="test")),
            ]:
                reward = grader_fn(action, email)
                assert 0.0 <= reward.total <= 1.0, f"Out of range: {reward.total}"
                assert 0.0 <= reward.priority_score <= 1.0
                assert 0.0 <= reward.category_score <= 1.0


class TestInvalidTask:
    def test_invalid_task_raises(self):
        with pytest.raises(ValueError):
            EmailTriageEnv(task="impossible")
