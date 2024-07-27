import base64
import contextlib
import logging
import re
import typing as t

import asgi_lifespan
import fastapi
import httpx


@contextlib.asynccontextmanager
async def _get_async_httpx_client(**kwargs) -> t.AsyncIterator[httpx.AsyncClient]:
    if kwargs.get("timeout") is None:
        kwargs["timeout"] = float(60)
    async with httpx.AsyncClient(**kwargs) as session:
        yield session


def _is_binary(response) -> bool:
    if not response.headers.get("content-type"):
        return False

    content_type = response.headers["content-type"]
    return any(re.match(re_, content_type) for re_ in (r"image/.*", r"video/.*", r"audio/.*", r".*zip", r".*pdf"))


def _patch_function_response(response: httpx.Response):
    logger.debug(response.__dict__)

    is_binary_ = _is_binary(response)
    if is_binary_:
        body = base64.b64encode(response.content).decode("utf-8")
    else:
        body = response.content.decode()
    return {
        "statusCode": response.status_code,
        "headers": dict(response.headers),
        "body": body,
        "isBase64Encoded": is_binary_,
    }


def _patch_base64_body(event: dict):
    if not event["body"]:
        pass
    elif event["isBase64Encoded"]:
        event["body"] = base64.b64decode(event["body"])
    else:
        event["body"] = event["body"].encode()


class Dispatcher:
    def __init__(self, asgi_app: fastapi.FastAPI):
        self.asgi_app = asgi_app

    async def _invoke_app(self, api_gateway_event: dict):
        logger.debug(api_gateway_event)

        host_url = api_gateway_event["headers"].get("Host", "https://raw-function.net")
        if not host_url.startswith("http"):
            host_url = f"https://{host_url}"
        _patch_base64_body(api_gateway_event)

        async with asgi_lifespan.LifespanManager(
            self.asgi_app, startup_timeout=float(60), shutdown_timeout=float(60)
        ) as lifespan_manager:
            async with _get_async_httpx_client(app=lifespan_manager.app, base_url=host_url) as asgi_app_client:
                logger.debug("Incoming event: ", api_gateway_event)

                request = asgi_app_client.build_request(
                    method=api_gateway_event["httpMethod"],
                    url=api_gateway_event["url"],
                    headers=api_gateway_event["headers"],
                    params=api_gateway_event["multiValueQueryStringParameters"],
                    content=api_gateway_event["body"],
                )
                asgi_app_response = await asgi_app_client.send(request)

                logger.debug(f"Output response: {asgi_app_response}")
                return asgi_app_response

    async def __call__(self, event: dict, context: dict):
        logger.info("DISPATCHER STARTUP")

        if not event:
            return {"statusCode": 500, "body": "got empty event"}
        if "event_metadata" in event:
            return {"statusCode": 200, "body": "ok"}
        response = await self._invoke_app(event)

        logger.info("DISPATCHER SHUTDOWN")
        return _patch_function_response(response)


logger = logging.getLogger("dispatcher")
