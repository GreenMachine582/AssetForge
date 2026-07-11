"""Pluggable compatibility rule registry — see docs/architecture.md #6. [M3]"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum


class CompatStatus(str, Enum):
    OK = "ok"
    FAIL = "fail"
    UNKNOWN = "unknown"


@dataclass
class CompatResult:
    status: CompatStatus
    message: str = ""

    @classmethod
    def ok(cls) -> "CompatResult":
        return cls(CompatStatus.OK)

    @classmethod
    def fail(cls, message: str) -> "CompatResult":
        return cls(CompatStatus.FAIL, message)

    @classmethod
    def unknown(cls, message: str) -> "CompatResult":
        return cls(CompatStatus.UNKNOWN, message)


# Each rule is a function (asset, project) -> CompatResult. Populated in M3.
RULES: list[Callable] = []


def check_asset(asset, project) -> list[CompatResult]:
    return [rule(asset, project) for rule in RULES]
