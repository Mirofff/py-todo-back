import typing as t

from types_aiobotocore_dynamodb import type_defs as aiodyno_defs

DynoItem = t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef]
