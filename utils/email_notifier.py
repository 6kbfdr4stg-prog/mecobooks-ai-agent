import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

class EmailNotifier:
    def __init__(self):
        self.sender_email = os.environ.get("EMAIL_SENDER")
        self.sender_password = os.environ.get("EMAIL_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.logger = logging.getLogger("email_notifier")

    def send_report(self, subject, body_html, to_email=None):
        """
        Sends an email report. If to_email is not provided, sends to self (User).
        """
        if not self.sender_email or not self.sender_password:
            self.logger.warning("❌ [Email Notifier] Missing EMAIL_SENDER or EMAIL_PASSWORD. Email skipped.")
            return

        recipient = to_email or self.sender_email  # Default to sending to self

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = recipient
            msg['Subject'] = subject

            msg.attach(MIMEText(body_html, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, recipient, text)
            server.quit()
            print(f"📧 [Email Notifier] Report sent to {recipient}: {subject}")
        except Exception as e:
            print(f"❌ [Email Notifier] Failed to send email: {e}")
