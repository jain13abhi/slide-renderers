"""Versioned, cross-platform paths for committed occasion state."""

from __future__ import annotations

from pathlib import Path, PurePosixPath


CURRENT_PATH_SCHEMA = 2
LEGACY_PATH_SCHEMA = 1


class PortablePathError(ValueError):
    """A persisted path is malformed or escapes its allowed root."""


def portable_relative(path: str | Path, *, root: str | Path) -> str:
    """Serialize a path below root with POSIX separators on every OS."""

    resolved_root = Path(root).resolve()
    resolved_path = Path(path).resolve()
    try:
        relative = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise PortablePathError(f"path is outside production root: {resolved_path}") from exc
    if not relative.parts:
        raise PortablePathError("path must identify a file below production root")
    return PurePosixPath(*relative.parts).as_posix()


def resolve_persisted_path(
    value: str,
    *,
    schema_version: int,
    production_root: str | Path | None,
    legacy_root: str | Path | None,
) -> Path:
    """Resolve schema-v2 paths and tolerate schema-v1 Windows separators."""

    if not isinstance(value, str) or not value.strip():
        raise PortablePathError("persisted path must be a non-empty string")
    if schema_version not in {LEGACY_PATH_SCHEMA, CURRENT_PATH_SCHEMA}:
        raise PortablePathError(f"unsupported path schema version {schema_version!r}")

    normalized = value.replace("\\", "/")
    posix_path = PurePosixPath(normalized)
    if schema_version == CURRENT_PATH_SCHEMA and posix_path.is_absolute():
        raise PortablePathError("portable path must be relative to production root")

    if schema_version == CURRENT_PATH_SCHEMA:
        if production_root is None:
            raise PortablePathError("production root is required for portable paths")
        candidate = Path(production_root).joinpath(*posix_path.parts)
    else:
        native_candidate = Path(normalized)
        if native_candidate.is_absolute():
            candidate = native_candidate
        else:
            base = Path(legacy_root) if legacy_root is not None else Path.cwd()
            candidate = base.joinpath(*posix_path.parts)

    resolved = candidate.resolve()
    if production_root is not None:
        resolved_root = Path(production_root).resolve()
        try:
            resolved.relative_to(resolved_root)
        except ValueError as exc:
            raise PortablePathError(f"path is outside production root: {resolved}") from exc
    return resolved


__all__ = [
    "CURRENT_PATH_SCHEMA",
    "LEGACY_PATH_SCHEMA",
    "PortablePathError",
    "portable_relative",
    "resolve_persisted_path",
]
