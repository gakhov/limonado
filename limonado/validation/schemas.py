# -*- coding: utf-8 -*-

__all__ = ["CONFIG"]


CONFIG = {
    "type": "object",
    "properties": {
        "debug": {
            "type": "boolean"
        },
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
        "server": {
            "type": "string",
            "minLength": 1
        },
        "base_path": {
            "type": "string",
            "minLength": 1
        }
    },
    "required": [
        "debug",
        "name",
        "id",
        "version",
        "server"
    ]
}
