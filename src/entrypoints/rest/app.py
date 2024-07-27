import contextlib
import logging

import fastapi
import semver

import settings
from src.database.dynamo import connection as dyno_connection
from src.entrypoints.rest.routers import auth as auth_router, tasks as tasks_router

_logger = logging.getLogger(__name__)


@contextlib.asynccontextmanager
async def _lifespan(_: fastapi.FastAPI):
    _logger.info("REST APPLICATION STARTUP...")
    _logger.info("DYNAMODB CONNECTING...")
    async with dyno_connection.DynoConnection(
        settings.config.DB_ENDPOINT, settings.config.DB_ACCESS_KEY, settings.config.DB_SECRET_KEY
    ) as dyno:
        await dyno.register_main_table(settings.config.DB_TABLE)
        await dyno.register_tokens_table(settings.config.DB_TOKENS_TABLE)

        _logger.info("DYNAMODB CONNECTING - SUCCESS")
        _logger.info("REST APPLICATION STARTUP - SUCCESS")

        yield {"dynamo_connection": dyno}

        _logger.info("DYNAMODB CONNECTING CLOSING...")

    _logger.info("REST APPLICATION SHUTDOWN...")
    _logger.info("REST APPLICATION SHUTDOWN - SUCCESS")


def new_fastapi_app(version: semver.Version) -> fastapi.FastAPI:
    app = fastapi.FastAPI(
        title="TODO Tasks Service",
        description="Simple todos tasks service built with FastAPI and DynamoDB (provide by aioboto3 lib)",
        lifespan=_lifespan,
        version=str(version.finalize_version()),
        root_path=f"/api/v{version.major}",
    )

    app.include_router(tasks_router.router)
    app.include_router(auth_router.router)

    return app
