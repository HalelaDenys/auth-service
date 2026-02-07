from faststream.rabbit import RabbitBroker
from core import settings
from faststream import FastStream
from infrastructure.broker.routers.mailing_consumer import mailing_router

broker = RabbitBroker(
    url=settings.br.rabbit_url,
)

app = FastStream(broker)


broker.include_router(mailing_router)
