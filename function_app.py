import logging

import semver

from packages import dispatcher
from settings import config, init_loggers
from src.entrypoints import rest as app_rest

init_loggers(__name__)

logger = logging.getLogger()

logger.info("FASTAPI APPLICATION CREATION...")

fastapi_app = app_rest.new_fastapi_app(semver.Version.parse(config.VERSION))

logger.info("PASS ASGI APP TO FUNCTION")

handle = dispatcher.Dispatcher(fastapi_app)

logger.info("FUNCTION INVOKE IS END!")
