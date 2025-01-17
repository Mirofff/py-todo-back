import pydantic
import abc


class FromAttributesBaseModel(abc.ABC, pydantic.BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
