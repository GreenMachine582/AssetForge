"""Shared JSON serialization helper for embedding query results into
templates and file exports."""

from datetime import datetime


def json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)
