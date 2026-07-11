"""SQLAlchemy 2.0 Core table definitions — full schema per docs/data-model.md.

Columns tagged with a milestone comment are nullable at M1 and activated by
later milestones. No migrations are needed when those milestones land.
"""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    JSON,
    MetaData,
    String,
    Table,
    Text,
)
from sqlalchemy.sql import func

metadata = MetaData()

ASSET_STATES = (
    "wishlist",
    "planned",
    "ordered",
    "delivered",
    "installed",
    "in_service",
    "moved",
    "removed",
    "stored",
    "retired",
    "sold",
    "disposed",
)

EVENT_TYPES = (
    "purchased",
    "delivered",
    "installed",
    "reallocated",
    "removed",
    "noted",
    "stored",
    "sold",
    "disposed",
    "attachment_added",
    "warranty_claimed",
    "rma_opened",
    "rma_resolved",
    "maintained",
    "repasted",
    "dust_cleaned",
    "firmware_updated",
    "bios_updated",
    "smart_tested",
    "benchmark_run",
    "photo_added",
)

ATTACHMENT_TYPES = ("invoice", "receipt", "photo", "manual", "other")

projects = Table(
    "projects",
    metadata,
    # Composite identity: `type` is a free-text category (not limited to any
    # fixed set — "PC Build", "HomeLab", "Laptop", "Server", etc.); `key` only
    # needs to be unique within its type, not globally.
    Column("type", String, primary_key=True),
    Column("key", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("date_started", Date),
    Column("budget", Float),
    Column("notes", Text),
    Column("is_active", Boolean, default=True),
)

assets = Table(
    "assets",
    metadata,
    # Identity
    Column("part_uid", String, primary_key=True),
    Column("name", String, nullable=False),
    Column("category", String, nullable=False),
    Column("manufacturer", String, nullable=True),  # [M2]
    Column("model_number", String, nullable=True),  # [M2]
    Column("serial_number", String, nullable=True),  # [M2]
    # Ownership — bought_for/used_by are paired columns (composite FK to
    # projects' composite PK), not single-column references.
    Column("bought_for_type", String, nullable=True),
    Column("bought_for_key", String, nullable=True),
    Column("used_by_type", String, nullable=True),
    Column("used_by_key", String, nullable=True),
    Column("location_id", Integer, ForeignKey("locations.id"), nullable=True),  # [M2]
    Column("parent_asset_uid", String, ForeignKey("assets.part_uid"), nullable=True),  # [M2]
    # Purchase
    Column("amount", Float),
    Column("purchase_date", Date),
    Column("retailer", String),
    Column("invoice_ref", String, nullable=True),  # [M2]
    Column("link", String),
    Column("is_consumable", Boolean, default=False),
    # State
    Column("state", Enum(*ASSET_STATES, name="asset_state"), nullable=False, default="planned"),
    # Warranty [M2]
    Column("warranty_months", Integer, nullable=True),
    Column("warranty_expiry", Date, nullable=True),
    Column("rma_number", String, nullable=True),
    # Meta
    Column("notes", Text),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
    ForeignKeyConstraint(["bought_for_type", "bought_for_key"], ["projects.type", "projects.key"]),
    ForeignKeyConstraint(["used_by_type", "used_by_key"], ["projects.type", "projects.key"]),
)

specs = Table(
    "specs",
    metadata,
    Column("part_uid", String, ForeignKey("assets.part_uid"), primary_key=True),
    # Interface
    Column("socket_interface", String),
    Column("form_factor", String),
    Column("ram_gen", String),
    Column("pcie_gen", String),
    Column("chipset", String),
    # Power
    Column("tdp_watt", Integer),
    Column("idle_watt", Float, nullable=True),  # [M3]
    Column("peak_watt", Float, nullable=True),  # [M3]
    # Physical
    Column("capacity", String),
    Column("slots_used", Integer),
    Column("slots_total", Integer),
    Column("speed_spec", String),
    Column("cooler_height_mm", Integer),
    Column("gpu_length_mm", Integer, nullable=True),  # [M3]
    # Connectivity [M3]
    Column("psu_connectors", String, nullable=True),
    Column("argb_headers", Integer, nullable=True),
    Column("fan_headers", Integer, nullable=True),
    Column("nvme_lanes", Integer, nullable=True),
    # Notes
    Column("compat_notes", Text),
)

events = Table(
    "events",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("part_uid", String, ForeignKey("assets.part_uid"), nullable=False),
    Column("event_type", Enum(*EVENT_TYPES, name="event_type"), nullable=False),
    Column("from_project_type", String, nullable=True),
    Column("from_project_key", String, nullable=True),
    Column("to_project_type", String, nullable=True),
    Column("to_project_key", String, nullable=True),
    Column("from_location", Integer, ForeignKey("locations.id"), nullable=True),  # [M2]
    Column("to_location", Integer, ForeignKey("locations.id"), nullable=True),  # [M2]
    Column("date", DateTime, server_default=func.now(), nullable=False),
    Column("notes", Text),
    Column("event_metadata", JSON, nullable=True),
    ForeignKeyConstraint(["from_project_type", "from_project_key"], ["projects.type", "projects.key"]),
    ForeignKeyConstraint(["to_project_type", "to_project_key"], ["projects.type", "projects.key"]),
)

locations = Table(  # [M2]
    "locations",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("description", Text),
    Column("parent_id", Integer, ForeignKey("locations.id"), nullable=True),
)

attachments = Table(  # [M2]
    "attachments",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("part_uid", String, ForeignKey("assets.part_uid"), nullable=False),
    Column("filename", String, nullable=False),
    Column("filepath", String, nullable=False),
    Column("file_type", Enum(*ATTACHMENT_TYPES, name="attachment_type"), nullable=False),
    Column("description", Text),
    Column("created_at", DateTime, server_default=func.now()),
)

benchmarks = Table(  # [M4]
    "benchmarks",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("part_uid", String, ForeignKey("assets.part_uid"), nullable=False),
    Column("tool", String, nullable=False),
    Column("score", Float),
    Column("metric", String),
    Column("date", Date),
    Column("notes", Text),
    Column("event_id", Integer, ForeignKey("events.id"), nullable=True),
)

settings = Table(
    "settings",
    metadata,
    Column("key", String, primary_key=True),
    Column("value", String),
    Column("description", Text),
)
