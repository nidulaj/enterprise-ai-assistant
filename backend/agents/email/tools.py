from services.email_service import EmailService

email_service = EmailService()

def send_email_tool(
    to_email: str,
    subject: str,
    body: str
):
    return email_service.send_email(
        to_email,
        subject,
        body
    )