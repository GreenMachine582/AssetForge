"""Pydantic request/response models — M1 subset only."""

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    type: str
    key: str
    name: str
    date_started: date | None = None
    budget: float | None = None
    notes: str | None = None
    is_active: bool = True


class ProjectOut(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)


class AssetCreate(BaseModel):
    part_uid: str
    name: str
    category: str
    bought_for_type: str | None = None
    bought_for_key: str | None = None
    used_by_type: str | None = None
    used_by_key: str | None = None
    amount: float | None = None
    purchase_date: date | None = None
    retailer: str | None = None
    link: str | None = None
    is_consumable: bool = False
    state: str = "planned"
    notes: str | None = None


class AssetUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    bought_for_type: str | None = None
    bought_for_key: str | None = None
    used_by_type: str | None = None
    used_by_key: str | None = None
    amount: float | None = None
    purchase_date: date | None = None
    retailer: str | None = None
    link: str | None = None
    is_consumable: bool | None = None
    notes: str | None = None


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    part_uid: str
    name: str
    category: str
    bought_for_type: str | None
    bought_for_key: str | None
    used_by_type: str | None
    used_by_key: str | None
    amount: float | None
    purchase_date: date | None
    retailer: str | None
    link: str | None
    is_consumable: bool
    state: str
    notes: str | None
    created_at: datetime | None
    updated_at: datetime | None


class TransitionRequest(BaseModel):
    new_state: str
    notes: str | None = None


class SpecOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    part_uid: str
    socket_interface: str | None
    form_factor: str | None
    ram_gen: str | None
    pcie_gen: str | None
    chipset: str | None
    tdp_watt: int | None
    capacity: str | None
    slots_used: int | None
    slots_total: int | None
    speed_spec: str | None
    cooler_height_mm: int | None
    compat_notes: str | None


class SpecUpdate(BaseModel):
    socket_interface: str | None = None
    form_factor: str | None = None
    ram_gen: str | None = None
    pcie_gen: str | None = None
    chipset: str | None = None
    tdp_watt: int | None = None
    capacity: str | None = None
    slots_used: int | None = None
    slots_total: int | None = None
    speed_spec: str | None = None
    cooler_height_mm: int | None = None
    compat_notes: str | None = None


class EventCreate(BaseModel):
    part_uid: str
    event_type: str
    from_project_type: str | None = None
    from_project_key: str | None = None
    to_project_type: str | None = None
    to_project_key: str | None = None
    notes: str | None = None
    event_metadata: dict[str, Any] | None = None


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    part_uid: str
    event_type: str
    from_project_type: str | None
    from_project_key: str | None
    to_project_type: str | None
    to_project_key: str | None
    date: datetime
    notes: str | None
    event_metadata: dict[str, Any] | None


class SettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    key: str
    value: str | None
    description: str | None


class SettingUpdate(BaseModel):
    value: str
