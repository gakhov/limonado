# -*- coding: utf-8 -*-

__all__ = [
    "HEALTH",
    "NO_PARAMS",
    "SETTINGS"
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

SETTINGS = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "minLength": 1
        },
        "id": {
            "type": "string",
            "minLength": 1
        },
        "version": {
            "type": "string",
            "minLength": 1
        },
        "deprecated_versions": {
            "type": "array",
            "items": {
                "type": "string",
                "minLength": 1
            }
        },
        "server": {
            "type": "string",
            "minLength": 1
        },
        "threads": {
            "type": "object",
            "properties": {
                "default": {
                    "type": "integer",
                    "minimum": 1
                }
            },
            "additionalProperties": {
                "type": "integer",
                "minimum": 1
            },
            "required": [
                "default"
            ]
        }
    },
    "required": [
        "name",
        "id",
        "version",
        "deprecated_versions",
        "server",
        "threads"
    ]
}
