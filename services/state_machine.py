"""Asset state transition enforcement — see docs/data-model.md."""

TRANSITIONS: dict[str, list[str]] = {
    "planned": ["ordered", "installed"],
    "ordered": ["delivered", "planned"],
    "delivered": ["installed"],
    "installed": ["in_service"],
    "in_service": ["moved", "removed", "retired"],
    "moved": ["in_service", "removed"],
    "removed": ["stored", "in_service", "retired"],
    "stored": ["in_service", "installed", "sold", "disposed"],
    "retired": ["stored", "sold", "disposed"],
    "sold": [],
    "disposed": [],
}


def validate_transition(current: str, new: str) -> None:
    if new not in TRANSITIONS.get(current, []):
        raise ValueError(f"Invalid transition: {current} -> {new}")
