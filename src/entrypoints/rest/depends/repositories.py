import typing as t

import fastapi

from src.database.dynamo import connection as dyno_connection


async def _get_app_dyno_connection(req: fastapi.Request) -> dyno_connection.DynoConnection:
    dyno: dyno_connection.DynoConnection = req.state.dynamo_connection
    return dyno


DynoDepends = t.Annotated[dyno_connection.DynoConnection, fastapi.Depends(_get_app_dyno_connection)]
