"""Transactional production of one occasion package."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol

from . import Job
from .renderer import RenderError, render_card


class PipelineError(RuntimeError):
    """A safe, Telegram-reportable production failure."""


class Drafter(Protocol):
    def draft(self, job: Job) -> "Draft": ...


class ImageProvider(Protocol):
    def generate(self, *, prompt: str, destination: Path, job_key: str) -> Path: ...


def _copy(payload: Mapping[str, Any], field: str, *, maximum: int) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        raise PipelineError(f"draft.{field} must be a non-empty string")
    value = value.strip()
    if len(value) > maximum:
        raise PipelineError(f"draft.{field} exceeds {maximum} characters")
    return value


@dataclass(frozen=True)
class Draft:
    eyebrow: str
    greeting: str
    tagline: str
    image_prompt: str
    captions: Mapping[str, str]

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any], *, channels: tuple[str, ...]) -> "Draft":
        if not isinstance(payload, Mapping):
            raise PipelineError("draft must be an object")
        captions_raw = payload.get("captions")
        if not isinstance(captions_raw, Mapping):
            raise PipelineError("draft.captions must be an object")
        captions: dict[str, str] = {}
        for channel in channels:
            value = captions_raw.get(channel)
            if not isinstance(value, str) or not value.strip():
                raise PipelineError(f"draft.captions.{channel} is required")
            value = value.strip()
            if len(value) > 2200:
                raise PipelineError(f"draft.captions.{channel} exceeds 2200 characters")
            captions[channel] = value
        x_caption = captions.get("x")
        if x_caption and re.search(r"(?:https?://|www\.)", x_caption, flags=re.IGNORECASE):
            raise PipelineError("draft.captions.x must not contain a URL")
        if x_caption and len(x_caption) > 260:
            raise PipelineError("draft.captions.x exceeds 260 characters")
        return cls(
            eyebrow=_copy(payload, "eyebrow", maximum=56),
            greeting=_copy(payload, "greeting", maximum=150),
            tagline=_copy(payload, "tagline", maximum=90),
            image_prompt=_copy(payload, "imagePrompt", maximum=1800),
            captions=captions,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "eyebrow": self.eyebrow,
            "greeting": self.greeting,
            "tagline": self.tagline,
            "imagePrompt": self.image_prompt,
            "captions": dict(self.captions),
        }


@dataclass(frozen=True)
class JobResult:
    job_key: str
    background: Path
    card: Path
    package: Path
    marker: Path


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def run_job(
    job: Job,
    *,
    drafter: Drafter,
    image_provider: ImageProvider,
    output_root: str | Path,
    state_root: str | Path,
) -> JobResult:
    """Produce all durable artifacts, then and only then write the completion marker."""

    output_root = Path(output_root)
    state_root = Path(state_root)
    file_key = job.key.replace(":", "-")
    event_root = output_root / f"{job.event.id}-{job.publish_date.year}"
    background = event_root / "backgrounds" / f"{job.brand.id}.png"
    card = event_root / "cards" / f"{job.brand.id}.png"
    package = event_root / "packages" / f"{job.brand.id}.json"
    marker = state_root / f"{file_key}.json"

    try:
        draft = drafter.draft(job)
        background.parent.mkdir(parents=True, exist_ok=True)
        generated = image_provider.generate(
            prompt=f"{job.event.image_direction}\n\n{draft.image_prompt}",
            destination=background,
            job_key=job.key,
        )
        if Path(generated).resolve() != background.resolve():
            raise PipelineError("image provider returned an unexpected destination")
        if not background.is_file() or background.stat().st_size == 0:
            raise PipelineError("image provider did not produce a background")
        metrics = render_card(
            background=background,
            output=card,
            brand=job.brand,
            eyebrow=draft.eyebrow,
            greeting=draft.greeting,
            tagline=draft.tagline,
        )
    except PipelineError:
        raise
    except RenderError as exc:
        raise PipelineError(f"locked renderer rejected the draft: {exc}") from exc
    except Exception as exc:
        raise PipelineError(f"occasion production failed: {exc}") from exc

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    package_payload = {
        "schemaVersion": 1,
        "jobKey": job.key,
        "event": {
            "id": job.event.id,
            "name": job.event.name,
            "category": job.event.category,
            "tradition": job.event.tradition,
            "date": job.publish_date.isoformat(),
        },
        "brand": {"id": job.brand.id, "name": job.brand.name},
        "sources": list(job.occurrence.sources),
        "draft": draft.as_dict(),
        "artifacts": {
            "background": str(background),
            "card": str(card),
            "renderMetrics": metrics,
        },
        "generatedAt": generated_at,
    }
    _write_json_atomic(package, package_payload)
    marker_payload = {
        "schemaVersion": 1,
        "jobKey": job.key,
        "status": "completed",
        "package": str(package),
        "completedAt": generated_at,
    }
    _write_json_atomic(marker, marker_payload)
    return JobResult(
        job_key=job.key,
        background=background,
        card=card,
        package=package,
        marker=marker,
    )


__all__ = ["Draft", "JobResult", "PipelineError", "run_job"]
