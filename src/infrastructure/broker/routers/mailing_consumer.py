from faststream.rabbit import RabbitRouter
from faststream import Depends

from schemas.auth_schemas import ResetPasswordEmailPayloadBroker
from infrastructure import EmailManager, get_email_manager
from typing import Annotated
from core import settings

mailing_router = RabbitRouter()


@mailing_router.subscriber(queue="password-reset-request")
async def password_reset_request_notifications(
    data: ResetPasswordEmailPayloadBroker,
    email_manager: Annotated["EmailManager", Depends(get_email_manager)],
):
    await email_manager.send_email_reset_pass(
        email_recipient=data.email,
        reset_token=data.token,
        reset_url=settings.fron.reset_password_url,
    )
