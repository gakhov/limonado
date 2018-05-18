# -*- coding: utf-8 -*-

__all__ = ["SETTINGS"]


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
        "name",
        "id",
        "version",
        "server"
    ]
}
