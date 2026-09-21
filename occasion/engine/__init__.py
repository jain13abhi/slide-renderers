"""Validated planning and provider contracts for occasion production."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import urlparse


class ConfigurationError(ValueError):
    """Raised before any external service is called when configuration is unsafe."""


@dataclass(frozen=True)
class RendererProfile:
    accent: str
    text: str
    overlay: str


@dataclass(frozen=True)
class Brand:
    id: str
    name: str
    enabled: bool
    logo: Path
    renderer_profile: RendererProfile
    channels: tuple[str, ...]


@dataclass(frozen=True)
class Event:
    id: str
    name: str
    category: str
    tradition: str
    brand_ids: tuple[str, ...]
    image_direction: str
    sensitivity: str


@dataclass(frozen=True)
class Occurrence:
    event_id: str
    publish_date: date
    status: str
    verified_at: date
    sources: tuple[str, ...]
    lead_days: int | None = None


@dataclass(frozen=True)
class Registry:
    version: int
    lead_days: int
    max_image_attempts: int
    brands: Mapping[str, Brand]
    events: Mapping[str, Event]
    occurrences: tuple[Occurrence, ...]


@dataclass(frozen=True)
class Job:
    key: str
    event: Event
    occurrence: Occurrence
    brand: Brand

    @property
    def publish_date(self) -> date:
        return self.occurrence.publish_date


def _required_string(block: Mapping[str, Any], key: str, context: str) -> str:
    value = block.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"{context}.{key} must be a non-empty string")
    return value.strip()


def _identifier(value: str, context: str) -> str:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise ConfigurationError(f"{context} must be a lowercase kebab-case identifier")
    return value


def _positive_int(value: Any, context: str, *, maximum: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1 or value > maximum:
        raise ConfigurationError(f"{context} must be an integer from 1 to {maximum}")
    return value


def _iso_date(value: Any, context: str) -> date:
    if not isinstance(value, str):
        raise ConfigurationError(f"{context} must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ConfigurationError(f"{context} must be a real YYYY-MM-DD date") from exc


def _https_url(value: Any, context: str) -> str:
    if not isinstance(value, str):
        raise ConfigurationError(f"{context} must be an HTTPS URL")
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ConfigurationError(f"{context} must be an HTTPS URL")
    return value


def load_registry(path: str | Path, *, asset_root: str | Path | None = None) -> Registry:
    """Load and fully validate the registry before any paid or quota-bound call."""

    registry_path = Path(path)
    root = Path(asset_root) if asset_root is not None else registry_path.parent.parent
    try:
        raw = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError(f"cannot read registry {registry_path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigurationError("registry root must be an object")
    version = raw.get("version")
    if version != 1:
        raise ConfigurationError("registry.version must be 1")

    defaults = raw.get("defaults")
    if not isinstance(defaults, dict):
        raise ConfigurationError("registry.defaults must be an object")
    lead_days = _positive_int(defaults.get("leadDays"), "defaults.leadDays", maximum=90)
    max_attempts = _positive_int(
        defaults.get("maxImageAttempts"), "defaults.maxImageAttempts", maximum=2
    )

    brand_rows = raw.get("brands")
    if not isinstance(brand_rows, list) or not brand_rows:
        raise ConfigurationError("registry.brands must contain at least one brand")
    brands: dict[str, Brand] = {}
    for index, row in enumerate(brand_rows):
        context = f"brands[{index}]"
        if not isinstance(row, dict):
            raise ConfigurationError(f"{context} must be an object")
        brand_id = _identifier(_required_string(row, "id", context), f"{context}.id")
        if brand_id in brands:
            raise ConfigurationError(f"duplicate brand id: {brand_id}")
        enabled = row.get("enabled")
        if not isinstance(enabled, bool):
            raise ConfigurationError(f"{context}.enabled must be boolean")
        logo = root / _required_string(row, "logo", context)
        if enabled and not logo.is_file():
            raise ConfigurationError(f"{context}.logo does not exist: {logo}")
        profile = row.get("rendererProfile")
        if not isinstance(profile, dict):
            raise ConfigurationError(f"{context}.rendererProfile must be an object")
        renderer_profile = RendererProfile(
            accent=_required_string(profile, "accent", f"{context}.rendererProfile"),
            text=_required_string(profile, "text", f"{context}.rendererProfile"),
            overlay=_required_string(profile, "overlay", f"{context}.rendererProfile"),
        )
        channels = row.get("channels")
        if not isinstance(channels, list) or not channels or not all(
            isinstance(channel, str) and channel.strip() for channel in channels
        ):
            raise ConfigurationError(f"{context}.channels must contain channel names")
        brands[brand_id] = Brand(
            id=brand_id,
            name=_required_string(row, "name", context),
            enabled=enabled,
            logo=logo,
            renderer_profile=renderer_profile,
            channels=tuple(channel.strip() for channel in channels),
        )

    event_rows = raw.get("events")
    if not isinstance(event_rows, list) or not event_rows:
        raise ConfigurationError("registry.events must contain at least one event")
    events: dict[str, Event] = {}
    for index, row in enumerate(event_rows):
        context = f"events[{index}]"
        if not isinstance(row, dict):
            raise ConfigurationError(f"{context} must be an object")
        event_id = _identifier(_required_string(row, "id", context), f"{context}.id")
        if event_id in events:
            raise ConfigurationError(f"duplicate event id: {event_id}")
        brand_ids = row.get("brandIds")
        if not isinstance(brand_ids, list) or not all(isinstance(item, str) for item in brand_ids):
            raise ConfigurationError(f"{context}.brandIds must be a list")
        unknown = sorted(set(brand_ids) - brands.keys())
        if unknown:
            raise ConfigurationError(f"{context}.brandIds contains unknown brands: {unknown}")
        sensitivity = _required_string(row, "sensitivity", context)
        if sensitivity not in {"standard", "approval-required", "blocked"}:
            raise ConfigurationError(
                f"{context}.sensitivity must be standard, approval-required, or blocked"
            )
        events[event_id] = Event(
            id=event_id,
            name=_required_string(row, "name", context),
            category=_required_string(row, "category", context),
            tradition=_required_string(row, "tradition", context),
            brand_ids=tuple(brand_ids),
            image_direction=_required_string(row, "imageDirection", context),
            sensitivity=sensitivity,
        )

    occurrence_rows = raw.get("occurrences")
    if not isinstance(occurrence_rows, list):
        raise ConfigurationError("registry.occurrences must be a list")
    occurrences: list[Occurrence] = []
    seen_occurrences: set[tuple[str, date]] = set()
    for index, row in enumerate(occurrence_rows):
        context = f"occurrences[{index}]"
        if not isinstance(row, dict):
            raise ConfigurationError(f"{context} must be an object")
        event_id = _required_string(row, "eventId", context)
        if event_id not in events:
            raise ConfigurationError(f"{context}.eventId references an unknown event")
        publish_date = _iso_date(row.get("date"), f"{context}.date")
        identity = (event_id, publish_date)
        if identity in seen_occurrences:
            raise ConfigurationError(f"duplicate occurrence: {event_id} on {publish_date}")
        seen_occurrences.add(identity)
        status = _required_string(row, "status", context)
        if status not in {"proposed", "verified", "locked", "cancelled"}:
            raise ConfigurationError(f"{context}.status is not recognised")
        verified_at = _iso_date(row.get("verifiedAt"), f"{context}.verifiedAt")
        source_rows = row.get("sources")
        if not isinstance(source_rows, list) or not source_rows:
            raise ConfigurationError(f"{context}.sources must contain at least one source")
        sources = tuple(
            _https_url(source, f"{context}.sources[{source_index}]")
            for source_index, source in enumerate(source_rows)
        )
        occurrence_lead = row.get("leadDays")
        if occurrence_lead is not None:
            occurrence_lead = _positive_int(
                occurrence_lead, f"{context}.leadDays", maximum=90
            )
        occurrences.append(
            Occurrence(
                event_id=event_id,
                publish_date=publish_date,
                status=status,
                verified_at=verified_at,
                sources=sources,
                lead_days=occurrence_lead,
            )
        )

    return Registry(
        version=version,
        lead_days=lead_days,
        max_image_attempts=max_attempts,
        brands=brands,
        events=events,
        occurrences=tuple(sorted(occurrences, key=lambda item: item.publish_date)),
    )


def plan_jobs(registry: Registry, *, as_of: date, completed: Iterable[str]) -> list[Job]:
    """Return unattended jobs that are safe and due, with deterministic identities."""

    completed_keys = set(completed)
    jobs: list[Job] = []
    for occurrence in registry.occurrences:
        event = registry.events[occurrence.event_id]
        if occurrence.status != "locked" or event.sensitivity != "standard":
            continue
        lead_days = occurrence.lead_days or registry.lead_days
        if not as_of <= occurrence.publish_date <= as_of + timedelta(days=lead_days):
            continue
        for brand_id in event.brand_ids:
            brand = registry.brands[brand_id]
            if not brand.enabled:
                continue
            key = f"{event.id}:{occurrence.publish_date.year}:{brand.id}"
            if key in completed_keys:
                continue
            jobs.append(
                Job(key=key, event=event, occurrence=occurrence, brand=brand)
            )
    return sorted(jobs, key=lambda item: (item.publish_date, item.event.id, item.brand.id))


def build_higgsfield_command(
    *, model: str, prompt: str, aspect_ratio: str = "4:5", resolution: str = "2k"
) -> list[str]:
    """Build a single-image, noninteractive Higgsfield CLI command."""

    if not model.strip() or not prompt.strip():
        raise ValueError("model and prompt are required")
    safe_prompt = (
        prompt.strip()
        + " Create one image only. The artwork must be text-free: no letters, words, "
        "numbers, logos, watermarks, signatures, borders, or UI elements."
    )
    return [
        "higgsfield",
        "generate",
        "create",
        model.strip(),
        "--prompt",
        safe_prompt,
        "--aspect_ratio",
        aspect_ratio,
        "--resolution",
        resolution,
        "--wait",
        "--json",
        "--no-color",
    ]


def _find_result_url(value: Any) -> str | None:
    if isinstance(value, dict):
        preferred = value.get("result_url") or value.get("resultUrl")
        if isinstance(preferred, str):
            return preferred
        for child in value.values():
            found = _find_result_url(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_result_url(child)
            if found:
                return found
    return None


def _has_completed_status(value: Any) -> bool:
    if isinstance(value, dict):
        if str(value.get("status", "")).lower() in {"completed", "complete", "succeeded"}:
            return True
        return any(_has_completed_status(child) for child in value.values())
    if isinstance(value, list):
        return any(_has_completed_status(child) for child in value)
    return False


def parse_higgsfield_result(output: str) -> str:
    """Extract a completed HTTPS result without accepting queued or unsafe output."""

    try:
        payload = json.loads(output)
    except json.JSONDecodeError as exc:
        raise ValueError("Higgsfield did not return valid JSON") from exc
    url = _find_result_url(payload)
    parsed = urlparse(url) if url else None
    if not _has_completed_status(payload) or not parsed or parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("Higgsfield did not return a completed HTTPS image")
    return url


@dataclass
class GenerationBudget:
    """In-memory hard stop that prevents retries from consuming unlimited credits."""

    max_attempts: int
    attempts: dict[str, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _positive_int(self.max_attempts, "max_attempts", maximum=2)

    def record_attempt(self, key: str) -> int:
        current = self.attempts.get(key, 0)
        if current >= self.max_attempts:
            raise RuntimeError(f"generation budget exhausted for {key}")
        current += 1
        self.attempts[key] = current
        return current


__all__ = [
    "Brand",
    "ConfigurationError",
    "Event",
    "GenerationBudget",
    "Job",
    "Occurrence",
    "Registry",
    "build_higgsfield_command",
    "load_registry",
    "parse_higgsfield_result",
    "plan_jobs",
]
