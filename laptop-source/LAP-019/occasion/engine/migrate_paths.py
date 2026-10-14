"""Opt-in migration of legacy occasion state paths to schema version 2."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from .portable_paths import (
    CURRENT_PATH_SCHEMA,
    PortablePathError,
    portable_relative,
    resolve_persisted_path,
)


class MigrationError(RuntimeError):
    """Legacy state cannot be migrated safely."""


@dataclass(frozen=True)
class MigrationResult:
    inspected: int
    changed: int
    written: bool


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError(f"cannot read {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise MigrationError(f"{path} is not a JSON object")
    return payload


def _write_json_atomic(path: Path, payload: Mapping[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def _resolve(
    value: Any,
    *,
    schema_version: int,
    production_root: Path,
    legacy_root: Path,
    label: str,
) -> Path:
    if not isinstance(value, str) or not value:
        raise MigrationError(f"{label} is missing")
    try:
        return resolve_persisted_path(
            value,
            schema_version=schema_version,
            production_root=production_root,
            legacy_root=legacy_root,
        )
    except PortablePathError as exc:
        raise MigrationError(f"{label} is invalid: {exc}") from exc


def migrate_paths(
    *,
    state_root: str | Path,
    production_root: str | Path,
    legacy_root: str | Path,
    write: bool = False,
) -> MigrationResult:
    """Preview or write an idempotent schema-v2 path migration."""

    state_root = Path(state_root)
    production_root = Path(production_root).resolve()
    legacy_root = Path(legacy_root).resolve()
    inspected = 0
    changed = 0

    for marker_path in sorted(state_root.glob("*.json")):
        inspected += 1
        marker = _read_json(marker_path)
        marker_schema = marker.get("schemaVersion", 1)
        if not isinstance(marker_schema, int):
            raise MigrationError(f"{marker_path.name} has invalid schemaVersion")
        package_path = _resolve(
            marker.get("package"),
            schema_version=marker_schema,
            production_root=production_root,
            legacy_root=legacy_root,
            label=f"{marker_path.name}.package",
        )
        if not package_path.is_file():
            raise MigrationError(f"{marker_path.name} references missing package {package_path}")
        package = _read_json(package_path)
        package_schema = package.get("schemaVersion", 1)
        if not isinstance(package_schema, int):
            raise MigrationError(f"{package_path.name} has invalid schemaVersion")
        artifacts = package.get("artifacts")
        if not isinstance(artifacts, dict):
            raise MigrationError(f"{package_path.name}.artifacts is missing")

        migrated_package = dict(package)
        migrated_artifacts = dict(artifacts)
        for field in ("background", "card"):
            if field not in migrated_artifacts:
                continue
            artifact_path = _resolve(
                migrated_artifacts[field],
                schema_version=package_schema,
                production_root=production_root,
                legacy_root=legacy_root,
                label=f"{package_path.name}.artifacts.{field}",
            )
            if not artifact_path.is_file():
                raise MigrationError(
                    f"{package_path.name}.artifacts.{field} is missing: {artifact_path}"
                )
            migrated_artifacts[field] = portable_relative(
                artifact_path, root=production_root
            )
        migrated_package["schemaVersion"] = CURRENT_PATH_SCHEMA
        migrated_package["artifacts"] = migrated_artifacts

        migrated_marker = dict(marker)
        migrated_marker["schemaVersion"] = CURRENT_PATH_SCHEMA
        migrated_marker["package"] = portable_relative(
            package_path, root=production_root
        )

        package_changed = migrated_package != package
        marker_changed = migrated_marker != marker
        if package_changed or marker_changed:
            changed += 1
            if write:
                if package_changed:
                    _write_json_atomic(package_path, migrated_package)
                if marker_changed:
                    _write_json_atomic(marker_path, migrated_marker)

    return MigrationResult(inspected=inspected, changed=changed, written=write)


__all__ = ["MigrationError", "MigrationResult", "migrate_paths"]
