import logging
from packages import dispatcher
from src.entrypoints import rest as app_rest
from settings import config, init_loggers

init_loggers(__name__)

logger = logging.getLogger()

logger.info("FASTAPI APPLICATION CREATION...")

fastapi_app = app_rest.new_fastapi_app(config.VERSION)

logger.info("PASS ASGI APP TO FUNCTION")

handle = dispatcher.Dispatcher(fastapi_app)

logger.info("FUNCTION INVOKE IS END!")
