import smtplib
from email.message import EmailMessage
from os import getenv
from dotenv import load_dotenv

class EmailService:
    
    def send_email(self, to_email: str, subject: str, body: str):
        load_dotenv(override=True)
        msg = EmailMessage()
        
        msg["Subject"] = subject
        msg["From"] = getenv("EMAIL_FROM")
        msg["To"] = to_email
        
        msg.set_content(body)
        
        host = getenv("SMTP_HOST")
        port = int(getenv("SMTP_PORT"))
        
        if port == 465:
            server_conn = smtplib.SMTP_SSL(host, port)
        else:
            server_conn = smtplib.SMTP(host, port)
            
        with server_conn as server:
            if port != 465:
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