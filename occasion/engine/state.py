"""Durable two-phase state: generated first, Telegram-delivered second."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class StateError(RuntimeError):
    """State is unreadable, so the engine must stop rather than spend twice."""


@dataclass(frozen=True)
class StateSnapshot:
    produced: set[str]
    delivered: set[str]
    markers: dict[str, Path]
    packages: dict[str, Path]


def _read_marker(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StateError(f"cannot read state marker {path.name}: {exc}") from exc
    if not isinstance(payload, dict):
        raise StateError(f"state marker {path.name} is not an object")
    job_key = payload.get("jobKey")
    status = payload.get("status")
    package = payload.get("package")
    if not isinstance(job_key, str) or not job_key:
        raise StateError(f"state marker {path.name} has no jobKey")
    if status not in {"generated", "delivered"}:
        raise StateError(f"state marker {path.name} has unsupported status {status!r}")
    if not isinstance(package, str) or not package:
        raise StateError(f"state marker {path.name} has no package")
    return payload


def load_state(root: str | Path) -> StateSnapshot:
    state_root = Path(root)
    if not state_root.exists():
        return StateSnapshot(produced=set(), delivered=set(), markers={}, packages={})
    produced: set[str] = set()
    delivered: set[str] = set()
    markers: dict[str, Path] = {}
    packages: dict[str, Path] = {}
    for marker in sorted(state_root.glob("*.json")):
        payload = _read_marker(marker)
        job_key = payload["jobKey"]
        if job_key in markers:
            raise StateError(f"duplicate state marker for {job_key}")
        package = Path(payload["package"])
        if not package.is_file():
            raise StateError(f"state marker {marker.name} references missing package {package}")
        produced.add(job_key)
        if payload["status"] == "delivered":
            delivered.add(job_key)
        markers[job_key] = marker
        packages[job_key] = package
    return StateSnapshot(
        produced=produced, delivered=delivered, markers=markers, packages=packages
    )


def pending_delivery(snapshot: StateSnapshot) -> list[tuple[str, Path]]:
    return sorted(
        (
            (job_key, snapshot.packages[job_key])
            for job_key in snapshot.produced - snapshot.delivered
        ),
        key=lambda item: item[0],
    )


def mark_delivered(marker: str | Path) -> None:
    marker_path = Path(marker)
    payload = _read_marker(marker_path)
    if payload["status"] == "delivered":
        return
    payload["status"] = "delivered"
    payload["deliveredAt"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    temporary = marker_path.with_suffix(marker_path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(marker_path)


__all__ = ["StateError", "StateSnapshot", "load_state", "mark_delivered", "pending_delivery"]
