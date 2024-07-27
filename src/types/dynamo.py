from types_aiobotocore_dynamodb import type_defs as aiodyno_defs
import typing as t

DynoItem = t.Mapping[str, aiodyno_defs.TableAttributeValueTypeDef]
