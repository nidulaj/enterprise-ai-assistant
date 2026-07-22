import smtplib
from email.message import EmailMessage
from os import getenv

class EmailService:
    
    def send_email(self, to_email: str, subject: str, body: str):
        msg = EmailMessage()
        
        msg["Subject"] = subject
        msg["From"] = getenv("EMAIL_FROM")
        msg["To"] = to_email
        
        msg.set_content(body)
        
        with smtplib.SMTP(
                getenv("SMTP_HOST"), 
                int(getenv("SMTP_PORT"))
            ) as server:
            server.starttls()
            server.login(
                getenv("SMTP_USER"),
                getenv("SMTP_PASSWORD")
            )
            
            server.send_message(msg)
            
        return {
            "success": True,
            "message": "Email sent successfully"
        }