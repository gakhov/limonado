# -*- coding: utf-8 -*-

__all__ = [
    "HEALTH",
    "NO_PARAMS"
]

HEALTH = {
    "additionalProperties": False,
    "type": "object",
    "properties": {
        "ok": {
            "type": "boolean"
        },
        "ok_as_string": {
            "type": "string",
            "enum": [
                "yes",
                "no"
            ]
        },
        "errors": {
            "type": "array",
            "items": {
                "additionalProperties": False,
                "properties": {
                    "source": {
                        "type": ["null", "string"],
                        "minLength": 1
                    },
                    "reason": {
                        "type": ["null", "string"],
                        "minLength": 1
                    },
                    "exception": {
                        "type": ["null", "string"],
                        "minLength": 1
                    }
                },
                "required": [
                    "source",
                    "reason",
                    "exception"
                ]
            }
        }
    },
    "required": [
        "ok",
        "ok_as_string",
        "errors"
    ]
}

NO_PARAMS = {
    "additionalProperties": False
}
