EMAIL_CLASSIFIER_PROMPT = """
Determine the email action.

Possible actions:

1. SEND_EMAIL
2. DRAFT_EMAIL
3. MEETING_INVITATION

Return only the action.
"""