from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from textwrap import dedent
from typing import AsyncGenerator

from core import settings, templates
import aiosmtplib
import logging

log = logging.getLogger(__name__)


class EmailManager:
    def __init__(
        self,
        host: str = settings.mail.host,
        post: int = settings.mail.port,
        username: str = settings.mail.username,
        password: str = settings.mail.password,
        use_tls: bool = settings.mail.use_tls,
    ):
        self._host = host
        self._post = post
        self._username = username
        self._password = password
        self._use_tls = use_tls

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
                use_tls=self._use_tls,
            )
        except aiosmtplib.SMTPException as e:
            log.error("Email send failed: %s", str(e))
            raise

    async def send_email_reset_pass(
        self, email_recipient: str, reset_token: str, reset_url: str = ""
    ):
        subject = "Reset password"
        full_url = f"{reset_url}?token={reset_token}"

        plain_content = dedent(f"""\
            Dear {email_recipient},
            
            Please follow the link to reset your password to {full_url}
                  
            If you did not request a password reset, you can safely ignore this email.
            
            Your site admin
            ℗ 2026.   
            """)

        template = templates.get_template("mailing/reset-password-request.html")

        context = {
            "email": email_recipient,
            "reset_url": full_url,
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
