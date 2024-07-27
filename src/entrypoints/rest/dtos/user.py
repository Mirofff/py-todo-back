import pydantic

from ._base import FromAttributesBaseModel


class UserRegister(FromAttributesBaseModel):
    email: pydantic.EmailStr
    password: str = pydantic.Field(min_length=8, max_length=256)
    first_name: str = pydantic.Field(..., serialization_alias="firstName")
    last_name: str = pydantic.Field(..., serialization_alias="lastName")
