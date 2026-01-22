"""
Email sender module using Gmail SMTP with App Password
Requires python-dotenv for environment variable management
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class GmailSender:
    """Send emails using Gmail SMTP server with App Password authentication"""
    
    def __init__(self):
        """Initialize Gmail sender with credentials from environment variables"""
        self.sender_email = os.getenv('GMAIL_EMAIL')
        self.app_password = os.getenv('GMAIL_APP_PASSWORD')
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        
        if not self.sender_email or not self.app_password:
            raise ValueError("GMAIL_EMAIL and GMAIL_APP_PASSWORD must be set in .env file")
    
    def send_email(self, recipient_email, subject, body, is_html=False):
        """
        Send an email via Gmail SMTP
        
        Args:
            recipient_email (str): Recipient's email address
            subject (str): Email subject
            body (str): Email body content
            is_html (bool): If True, body is treated as HTML, else plain text
            
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Attach body
            mime_type = "html" if is_html else "plain"
            message.attach(MIMEText(body, mime_type))
            
            # Send email via SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Secure connection
                server.login(self.sender_email, self.app_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
            
            print(f"✓ Email sent successfully to {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("✗ Authentication failed. Check GMAIL_EMAIL and GMAIL_APP_PASSWORD in .env")
            return False
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error occurred: {e}")
            return False
        except Exception as e:
            print(f"✗ Error sending email: {e}")
            return False
    
    def send_bulk_email(self, recipient_emails, subject, body, is_html=False):
        """
        Send the same email to multiple recipients
        
        Args:
            recipient_emails (list): List of recipient email addresses
            subject (str): Email subject
            body (str): Email body content
            is_html (bool): If True, body is treated as HTML, else plain text
            
        Returns:
            dict: Dictionary with success count and failed recipients
        """
        results = {"success": 0, "failed": []}
        
        for email in recipient_emails:
            if self.send_email(email, subject, body, is_html):
                results["success"] += 1
            else:
                results["failed"].append(email)
        
        return results


# Example usage
if __name__ == "__main__":
    try:
        sender = GmailSender()
        
        # Test with HTML
        html_body = """
        <html>
            <body>
                <h1>Gold Price Alert</h1>
                <p>Current gold price: <strong>₹5000/gram</strong></p>
            </body>
        </html>
        """
        sender.send_email(
            recipient_email="nitishm.23it@kongu.edu",
            subject="Gold Price Update",
            body=html_body,
            is_html=True
        )
        
    except ValueError as e:
        print(f"Configuration error: {e}")
