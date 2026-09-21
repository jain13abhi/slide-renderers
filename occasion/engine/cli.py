"""Command line entry point for planning, production, delivery, and failure alerts."""

from __future__ import annotations

import argparse
import json
import os
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Iterator, Sequence

from . import GenerationBudget, Job, load_registry, plan_jobs
from .pipeline import PipelineError, run_job
from .providers import GeminiDrafter, HiggsfieldProvider
from .state import load_state, mark_delivered, pending_delivery
from .telegram import TelegramClient


@contextmanager
def _working_directory(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _write_manifest(path: Path, *, planned: list[Job], produced: list[str], errors: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schemaVersion": 1,
        "planned": [
            {
                "jobKey": job.key,
                "event": job.event.name,
                "brand": job.brand.name,
                "date": job.publish_date.isoformat(),
            }
            for job in planned
        ],
        "produced": produced,
        "errors": errors,
    }
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def _telegram_from_environment() -> TelegramClient:
    return TelegramClient(
        token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        chat_id=os.environ.get("TELEGRAM_CHAT_ID", ""),
    )


def _produce(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    registry_path = Path(args.registry)
    if not registry_path.is_absolute():
        registry_path = repo_root / registry_path
    state_root = Path(args.state_root)
    manifest = Path(args.manifest)
    if not state_root.is_absolute():
        state_root = repo_root / state_root
    if not manifest.is_absolute():
        manifest = repo_root / manifest
    with _working_directory(repo_root):
        registry = load_registry(registry_path, asset_root=repo_root)
        snapshot = load_state(state_root)
        jobs = plan_jobs(
            registry,
            as_of=date.fromisoformat(args.date),
            completed=snapshot.produced,
        )
        if len(jobs) > args.max_jobs:
            raise RuntimeError(
                f"occasion job limit exceeded: {len(jobs)} planned, maximum {args.max_jobs}"
            )
        if args.dry_run or not jobs:
            _write_manifest(manifest, planned=jobs, produced=[], errors=[])
            print(f"Occasion plan: {len(jobs)} job(s); no external calls made.")
            return 0

        drafter = GeminiDrafter(
            api_key=os.environ.get("GEMINI_API_KEY"),
            model=os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite"),
        )
        image_provider = HiggsfieldProvider(
            budget=GenerationBudget(max_attempts=registry.max_image_attempts),
            model=os.environ.get("HIGGSFIELD_MODEL", "nano_banana_2"),
            resolution=os.environ.get("HIGGSFIELD_RESOLUTION", "2k"),
        )
        output_root = Path(args.output_root)
        produced: list[str] = []
        errors: list[str] = []
        for job in jobs:
            try:
                run_job(
                    job,
                    drafter=drafter,
                    image_provider=image_provider,
                    output_root=output_root,
                    state_root=state_root,
                )
                produced.append(job.key)
                print(f"Produced {job.key}")
            except Exception as exc:
                errors.append(f"{job.key}: {exc}")
        _write_manifest(manifest, planned=jobs, produced=produced, errors=errors)
        if errors:
            raise PipelineError("; ".join(errors))
        return 0


def _deliver(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    state_root = Path(args.state_root)
    if not state_root.is_absolute():
        state_root = repo_root / state_root
    with _working_directory(repo_root):
        snapshot = load_state(state_root)
        pending = pending_delivery(snapshot)
        if not pending:
            print("Occasion delivery: nothing pending.")
            return 0
        telegram = _telegram_from_environment()
        errors: list[str] = []
        for job_key, package in pending:
            try:
                telegram.deliver(package)
                mark_delivered(snapshot.markers[job_key])
                print(f"Delivered {job_key}")
            except Exception as exc:
                errors.append(f"{job_key}: {exc}")
        if errors:
            raise PipelineError("; ".join(errors))
        return 0


def _notify_failure(args: argparse.Namespace) -> int:
    detail = args.detail
    if args.detail_file:
        detail = Path(args.detail_file).read_text(encoding="utf-8", errors="replace")
    _telegram_from_environment().send_failure(stage=args.stage, detail=detail)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dock Group occasion production engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    default_repo = str(Path(__file__).resolve().parents[2])
    produce = subparsers.add_parser("produce", help="plan and generate due occasion packages")
    produce.add_argument("--date", default=date.today().isoformat())
    produce.add_argument("--repo-root", default=default_repo)
    produce.add_argument("--registry", default="occasion/registry.json")
    produce.add_argument("--state-root", default="occasion/state")
    produce.add_argument("--output-root", default="occasion/production")
    produce.add_argument("--manifest", default="occasion/production/manifest.json")
    produce.add_argument("--max-jobs", type=int, default=6)
    produce.add_argument("--dry-run", action="store_true")
    produce.set_defaults(handler=_produce)

    deliver = subparsers.add_parser("deliver", help="send generated packages to Telegram")
    deliver.add_argument("--repo-root", default=default_repo)
    deliver.add_argument("--state-root", default="occasion/state")
    deliver.set_defaults(handler=_deliver)

    failure = subparsers.add_parser("notify-failure", help="send a failure to Telegram")
    failure.add_argument("--stage", required=True)
    failure.add_argument("--detail", default="No error detail was captured.")
    failure.add_argument("--detail-file")
    failure.set_defaults(handler=_notify_failure)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if getattr(args, "max_jobs", 1) < 1:
        raise RuntimeError("max-jobs must be positive")
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
