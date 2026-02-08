from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from textwrap import dedent
from typing import AsyncGenerator

from core import settings, templates
import aiosmtplib


class EmailManager:
    def __init__(
        self,
        host: str = settings.mail.host,
        post: int = settings.mail.port,
        username: str = settings.mail.username,
        password: str = settings.mail.password,
        start_tls: bool = False,
    ):
        self._host = host
        self._post = post
        self._username = username
        self._password = password
        self._start_tls = start_tls

    async def _send_email(
        self, recipient: str, subject: str, plain_content: str, html_content: str = ""
    ):
        message = MIMEMultipart("alternative")
        message["From"] = settings.mail.from_email
        message["To"] = recipient
        message["Subject"] = subject

        message.attach(MIMEText(plain_content, "plain", "utf-8"))

        if html_content:
            message.attach(MIMEText(html_content, "html", "utf-8"))

        try:
            await aiosmtplib.send(
                message,
                hostname=self._host,
                port=self._post,
                username=self._username,
                password=self._password,
                start_tls=self._start_tls,
            )
        except aiosmtplib.SMTPException as e:
            # print(f"Email send failed: {e}")
            raise

    async def send_email_reset_pass(
        self, email_recipient: str, reset_token: str, reset_url: str = ""
    ):
        subject = "Reset password"

        plain_content = dedent(f"""\
            Dear {email_recipient},
            
            Please follow the link to reset your password to {reset_url}
            
            Use this token to reset your password: 
            {reset_token}         
            
            Your site admin
            ℗ 2026.   
            """)

        template = templates.get_template("mailing/reset-password-request.html")
        context = {
            "email": email_recipient,
            "reset_url": reset_url,
            "reset_token": reset_token,
        }
        html_content = template.render(context)
        await self._send_email(
            recipient=email_recipient,
            subject=subject,
            plain_content=plain_content,
            html_content=html_content,
        )


async def get_email_manager() -> AsyncGenerator[EmailManager, None]:
    manager = EmailManager()
    yield manager
