"""
Theres no base64 to python function - it's unsafe
"""

import base64
import json
import typing as t


def python_to_base64(obj: t.Any) -> str:
    return base64.b64encode(json.dumps(obj).encode()).decode()


def base64_to_dict(encoded_obj: str | None) -> t.Any:
    # TODO: right exception handler
    if encoded_obj is not None:
        try:
            return json.loads(base64.b64decode(encoded_obj, validate=True))
        except Exception:
            return None
