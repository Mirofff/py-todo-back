import logging

import coloredlogs
import pydantic
import pydantic_settings


def _get_log_level(str_log_level: str) -> int:
    return getattr(logging, str_log_level)


class Settings(pydantic_settings.BaseSettings):
    DB_ENDPOINT: pydantic.HttpUrl = pydantic.Field()
    DB_ACCESS_KEY: str = pydantic.Field()
    DB_SECRET_KEY: str = pydantic.Field()
    DB_TABLE: str = pydantic.Field()
    DB_TOKENS_TABLE: str = pydantic.Field("tokens")

    SIGNING_KEY: str = pydantic.Field()
    ACCESS_TOKEN_EXPIRATION: int = pydantic.Field(60)  # * minutes
    REFRESH_TOKEN_EXPIRATION: int = pydantic.Field(168)  # * hours

    VERSION: str = pydantic.Field()

    LOG_LEVEL: str = pydantic.Field("DEBUG")
    LOG_FORMATTER: str = pydantic.Field("{asctime} {levelname:8s} ({pathname}:{lineno}) {message:50s}")

    model_config = pydantic_settings.SettingsConfigDict(case_sensitive=True)


config = Settings()  # type: ignore


def init_loggers(project_root: str, log_level=_get_log_level(config.LOG_LEVEL)) -> logging.Logger:
    # console_log_stream = logging.StreamHandler()
    # console_log_stream.setFormatter(coloredlogs.ColoredFormatter(config.LOG_FORMATTER, style="{"))

    logger = logging.getLogger(project_root)
    logger.setLevel(log_level)
    # logger.addHandler(console_log_stream)
    logger.propagate = False

    coloredlogs.install(logger=logger, style="{", fmt=config.LOG_FORMATTER)

    return logger
