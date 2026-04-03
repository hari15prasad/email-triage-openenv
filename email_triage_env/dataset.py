"""
Curated email dataset for the Email Triage environment.
Each email has a ground-truth priority and category label used by graders.
"""
from email_triage_env.models import Email

# ---------------------------------------------------------------------------
# EASY TASK: 5 clearly distinct emails — obvious priority + category
# ---------------------------------------------------------------------------

EASY_EMAILS = [
    Email(
        id="e1",
        sender="noreply@spampromo.xyz",
        subject="🎉 You WON a FREE iPhone! Click NOW!!!",
        body=(
            "Congratulations! You have been selected as today's winner. "
            "Click the link below to claim your prize: http://scam-link.xyz/claim "
            "This offer expires in 24 hours. Act fast!"
        ),
        timestamp="2024-01-15T09:00:00Z",
        priority_label="low",
        category_label="spam",
    ),
    Email(
        id="e2",
        sender="ceo@ourcompany.com",
        subject="All-hands meeting TOMORROW 9am — mandatory attendance",
        body=(
            "Hi everyone, we have an important company update to share. "
            "Please make sure all team members attend the all-hands tomorrow at 9am sharp. "
            "Dial-in details: meet.google.com/abc-defg-hij. This is mandatory."
        ),
        timestamp="2024-01-15T09:05:00Z",
        priority_label="urgent",
        category_label="internal",
    ),
    Email(
        id="e3",
        sender="john.smith@gmail.com",
        subject="Question about your pricing plans",
        body=(
            "Hello, I'm interested in your Pro plan but I'm not sure what the difference "
            "is between the monthly and annual billing options. "
            "Could you explain the cost savings and any cancellation policy? Thanks!"
        ),
        timestamp="2024-01-15T09:10:00Z",
        priority_label="normal",
        category_label="billing",
    ),
    Email(
        id="e4",
        sender="alice@bigclient.com",
        subject="Critical production bug — dashboard not loading for 500 users",
        body=(
            "Hi support team, our entire analytics dashboard has been down since 8am today. "
            "None of our 500 users can access it. We're losing revenue every minute. "
            "Error message: 503 Service Unavailable. Please escalate immediately. "
            "This is blocking our entire operations team."
        ),
        timestamp="2024-01-15T09:15:00Z",
        priority_label="urgent",
        category_label="bug_report",
    ),
    Email(
        id="e5",
        sender="newsletter@techdigest.com",
        subject="This week in tech: AI roundup, new frameworks, and more",
        body=(
            "Welcome to this week's Tech Digest newsletter! "
            "In this issue: GPT-5 rumors, Rust 2.0 release, "
            "Python performance improvements, and top GitHub repos of the week. "
            "Click to read more at techdigest.com."
        ),
        timestamp="2024-01-15T09:20:00Z",
        priority_label="low",
        category_label="general_inquiry",
    ),
]

# ---------------------------------------------------------------------------
# MEDIUM TASK: 8 emails — more nuanced, requires reasoning to prioritize
# ---------------------------------------------------------------------------

MEDIUM_EMAILS = [
    Email(
        id="m1",
        sender="dev@contractor.io",
        subject="Re: Sprint 4 deliverable — slight delay",
        body=(
            "Hey, just wanted to give you a heads-up that the authentication module "
            "will be delayed by 2 days due to an unexpected dependency conflict. "
            "I've already opened a ticket and have a workaround in progress. "
            "Should be ready by Thursday. Let me know if that's a blocker."
        ),
        timestamp="2024-01-16T08:30:00Z",
        priority_label="high",
        category_label="internal",
    ),
    Email(
        id="m2",
        sender="sarah.j@enterprise-client.com",
        subject="Renewal quote request — contract expires Feb 1",
        body=(
            "Hi, our annual contract with you expires on February 1st and we'd like "
            "to discuss renewal terms. We're currently paying $24,000/year and would "
            "like to explore the enterprise tier. Could someone from sales reach out? "
            "We have budget approval to move forward quickly."
        ),
        timestamp="2024-01-16T08:35:00Z",
        priority_label="high",
        category_label="billing",
    ),
    Email(
        id="m3",
        sender="security-alerts@aws.com",
        subject="Unusual sign-in activity detected on your AWS account",
        body=(
            "We detected a sign-in to your AWS account from an unrecognized device "
            "in Singapore (IP: 103.21.244.0) at 2024-01-16 03:14 UTC. "
            "If this was you, no action is needed. If not, secure your account "
            "immediately at console.aws.amazon.com/iam/. "
            "This notification was sent to the account root email."
        ),
        timestamp="2024-01-16T08:40:00Z",
        priority_label="urgent",
        category_label="security",
    ),
    Email(
        id="m4",
        sender="feedback@surveymonkey.com",
        subject="Customer satisfaction survey — share your experience",
        body=(
            "You recently interacted with our support team. "
            "We'd love to hear your feedback! "
            "Take our 2-minute survey: sm.link/feedback123. "
            "Your responses help us improve."
        ),
        timestamp="2024-01-16T08:45:00Z",
        priority_label="low",
        category_label="general_inquiry",
    ),
    Email(
        id="m5",
        sender="user1234@gmail.com",
        subject="App crashes when uploading files larger than 10MB",
        body=(
            "I keep getting a crash whenever I try to upload files over 10MB. "
            "The app just freezes and I have to force-close it. "
            "I'm on iOS 17.2, app version 4.1.3. "
            "This has happened 5 times this week. Very frustrating."
        ),
        timestamp="2024-01-16T08:50:00Z",
        priority_label="high",
        category_label="bug_report",
    ),
    Email(
        id="m6",
        sender="intern@ourcompany.com",
        subject="Can I get access to the staging environment?",
        body=(
            "Hi, I'm the new intern starting this week. "
            "My manager Alex said I should email IT to get staging environment access. "
            "My employee ID is EMP-4421. Please let me know what I need to do. Thanks!"
        ),
        timestamp="2024-01-16T08:55:00Z",
        priority_label="normal",
        category_label="internal",
    ),
    Email(
        id="m7",
        sender="partner@integrate.co",
        subject="API rate limit increase request for production integration",
        body=(
            "Hi team, we're a paying partner building a production integration "
            "and we're currently hitting the 1000 requests/hour rate limit. "
            "Our usage patterns show we need approximately 5000 req/hour during peak. "
            "We're on the Business plan. Could you increase our limit or point us "
            "to the enterprise upgrade path?"
        ),
        timestamp="2024-01-16T09:00:00Z",
        priority_label="high",
        category_label="feature_request",
    ),
    Email(
        id="m8",
        sender="marketing@competitor.com",
        subject="Partnership opportunity — let's grow together!",
        body=(
            "Hi there! I'm reaching out from CompetitorCo's marketing team. "
            "We think there's a great opportunity for a cross-promotion partnership. "
            "Would you be open to a 30-minute call to explore? "
            "Best, Jamie"
        ),
        timestamp="2024-01-16T09:05:00Z",
        priority_label="low",
        category_label="general_inquiry",
    ),
]

# ---------------------------------------------------------------------------
# HARD TASK: 10 emails — ambiguous, overlapping signals, requires response drafts
# ---------------------------------------------------------------------------

HARD_EMAILS = [
    Email(
        id="h1",
        sender="cto@majorpartner.com",
        subject="Re: Re: Re: Data pipeline issue — now affecting our clients",
        body=(
            "We've been going back and forth on this for a week. "
            "The data sync delays are now causing our end customers to see stale reports. "
            "We have a board presentation Friday where we're demoing this integration. "
            "I need someone technical to jump on a call with me today. "
            "This is becoming a reputational issue for both companies."
        ),
        timestamp="2024-01-17T07:45:00Z",
        priority_label="urgent",
        category_label="bug_report",
    ),
    Email(
        id="h2",
        sender="anon-user@protonmail.com",
        subject="I found a way to access other users' data",
        body=(
            "Hello, I'm a security researcher and I've found what appears to be "
            "an IDOR vulnerability in your API. By modifying the user_id parameter "
            "in GET /api/v2/profile/{user_id}, I can view any user's private profile data. "
            "I have NOT exploited this beyond basic testing. "
            "Please respond so I can share the full PoC responsibly."
        ),
        timestamp="2024-01-17T08:00:00Z",
        priority_label="urgent",
        category_label="security",
    ),
    Email(
        id="h3",
        sender="legal@lawfirm.com",
        subject="Notice of potential copyright infringement claim — response required",
        body=(
            "On behalf of our client MediaCorp Ltd, we are writing to notify you "
            "that content hosted on your platform may constitute copyright infringement. "
            "Please preserve all relevant server logs and content. "
            "A formal demand letter will follow within 10 business days. "
            "Please direct all correspondence to our office."
        ),
        timestamp="2024-01-17T08:15:00Z",
        priority_label="urgent",
        category_label="general_inquiry",
    ),
    Email(
        id="h4",
        sender="poweruser@gmail.com",
        subject="Feature request: bulk export + several other ideas",
        body=(
            "Love the product! A few things that would make it 10x better: "
            "1) Bulk CSV export of all records 2) Dark mode 3) Keyboard shortcuts "
            "4) API webhooks for real-time updates 5) Mobile app. "
            "I use this 8 hours a day and these would save me so much time. "
            "The export one especially — right now I have to do it one by one."
        ),
        timestamp="2024-01-17T08:30:00Z",
        priority_label="normal",
        category_label="feature_request",
    ),
    Email(
        id="h5",
        sender="billing-dept@enterprise.org",
        subject="Invoice #INV-2024-0089 — payment failed, account at risk",
        body=(
            "Your payment of $8,400 for invoice INV-2024-0089 failed on Jan 15. "
            "We have attempted to charge the card on file 3 times. "
            "If payment is not received within 5 business days, "
            "your account will be suspended and data export will be locked. "
            "Please update your payment method at billing.ourservice.com."
        ),
        timestamp="2024-01-17T08:45:00Z",
        priority_label="urgent",
        category_label="billing",
    ),
    Email(
        id="h6",
        sender="hr@ourcompany.com",
        subject="Reminder: mandatory compliance training due by Jan 31",
        body=(
            "This is a reminder that all employees must complete the annual "
            "data privacy and security compliance training by January 31. "
            "You have not yet completed Module 3: Data Handling. "
            "Failure to complete will be noted in your performance review. "
            "Access the training at: training.ourcompany.com"
        ),
        timestamp="2024-01-17T09:00:00Z",
        priority_label="high",
        category_label="internal",
    ),
    Email(
        id="h7",
        sender="ops@datacenter-provider.com",
        subject="Scheduled maintenance window: Jan 20 02:00-06:00 UTC",
        body=(
            "This is advance notice of a scheduled maintenance window for "
            "network infrastructure upgrades. Expected impact: brief connectivity "
            "interruptions of 2-5 minutes during the 4-hour window. "
            "No data loss expected. Please plan accordingly and notify your users. "
            "Contact us if you have concerns about this window."
        ),
        timestamp="2024-01-17T09:15:00Z",
        priority_label="high",
        category_label="general_inquiry",
    ),
    Email(
        id="h8",
        sender="user9900@yahoo.com",
        subject="Account locked — please help",
        body=(
            "Hi I can't log into my account. It says 'account suspended' but I don't "
            "know why. I've been a customer for 3 years and I have a lot of important "
            "data in there. My username is user9900. Please help asap. "
            "I have a client presentation in 2 hours and I need to access my files."
        ),
        timestamp="2024-01-17T09:20:00Z",
        priority_label="high",
        category_label="billing",
    ),
    Email(
        id="h9",
        sender="dev@oss-project.github.io",
        subject="Your SDK has a memory leak in async context managers",
        body=(
            "Found a memory leak in your Python SDK v2.3.1. "
            "When using async context managers in a loop, the client connection "
            "pool never releases. Reproduced on Python 3.11 + aiohttp 3.9. "
            "Minimal repro: gist.github.com/dev/abc123. "
            "Happy to submit a PR if you can confirm."
        ),
        timestamp="2024-01-17T09:30:00Z",
        priority_label="high",
        category_label="bug_report",
    ),
    Email(
        id="h10",
        sender="press@techcrunch-pr.com",
        subject="TechCrunch story request — comment on recent data breach reports",
        body=(
            "Hi, I'm a reporter at TechCrunch working on a story about "
            "a reported data breach affecting multiple SaaS companies. "
            "Your company's name has come up in our investigation. "
            "Could you provide an official comment or statement by 5pm today? "
            "We're publishing with or without your response. "
            "This is a time-sensitive media inquiry."
        ),
        timestamp="2024-01-17T09:35:00Z",
        priority_label="urgent",
        category_label="security",
    ),
]
