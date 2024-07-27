"""
! TODO: Logging
"""

import logging

import fastapi

from src.entrypoints.rest.depends import repositories as repositories_depends
from src.entrypoints.rest.dtos import auth as auth_dtos, user as user_dtos
from src.exceptions import user as user_exception
from src.handlers import auth as auth_handlers, user as user_handlers
from src.models import user as user_models

router = fastapi.APIRouter(prefix="/auth", tags=["Auth"])

_logger = logging.getLogger(__name__)


@router.post("/register", status_code=fastapi.status.HTTP_201_CREATED)
async def register_user(dyno: repositories_depends.DynoDepends, user_register_dto: user_dtos.UserRegister):
    """
    Register new user endpoint.
    """
    public_user = user_models.UserPublic.create(
        user_register_dto.email, user_register_dto.first_name, user_register_dto.last_name
    )

    if public_user is not None:
        try:
            await user_handlers.register_new_user(dyno, public_user, user_register_dto.password)
        except user_exception.UserAlreadyExistException as e:
            _logger.error(e)
            raise fastapi.HTTPException(
                fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"User with email: {user_register_dto.email}, already exist.",
            )
        except user_exception.UserException as e:
            _logger.error(e)
            raise fastapi.HTTPException(
                fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR, "Unknown error in user creation..."
            )


@router.post("/token", response_model=auth_dtos.AuthSuccess)
async def login_user(
    dyno: repositories_depends.DynoDepends, credentials: auth_dtos.AuthCredentialsFormDepends, req: fastapi.Request
):
    """
    Login user endpoint. Return access and refresh token on success.
    """
    user = await user_handlers.login_user(dyno, credentials.username, credentials.password)
    if user:
        access, refresh = auth_handlers.generate_access_refresh(user)
        return auth_dtos.AuthSuccess(access_token=access.jwt, refresh_token=refresh.jwt, expires_in=access.exp)

    _logger.warn(f"Wrong authenticate try: {req.client=}, username: {credentials.username}")
    raise fastapi.HTTPException(fastapi.status.HTTP_401_UNAUTHORIZED, "Email or password is incorrect")


# ! TODO: implement refresh access token and revoke token endpoints
