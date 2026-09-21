"""Telegram delivery of the exact card and copy-ready platform captions."""

from __future__ import annotations

import json
import mimetypes
import uuid
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib import parse, request


class TelegramError(RuntimeError):
    """Telegram rejected or could not receive a production result."""


Transport = Callable[[str, dict[str, str], Path | None], Mapping[str, Any]]


def _chunks(value: str, size: int = 3900) -> list[str]:
    if len(value) <= size:
        return [value]
    chunks: list[str] = []
    remaining = value
    while remaining:
        if len(remaining) <= size:
            chunks.append(remaining)
            break
        split_at = remaining.rfind("\n", 0, size)
        if split_at < size // 2:
            split_at = remaining.rfind(" ", 0, size)
        if split_at < size // 2:
            split_at = size
        chunks.append(remaining[:split_at].rstrip())
        remaining = remaining[split_at:].lstrip()
    return chunks


def delivery_messages(package: Mapping[str, Any]) -> list[str]:
    draft = package.get("draft")
    captions = draft.get("captions") if isinstance(draft, Mapping) else None
    if not isinstance(captions, Mapping) or not captions:
        raise TelegramError("package has no platform captions")
    messages: list[str] = []
    for channel, caption in captions.items():
        if not isinstance(channel, str) or not isinstance(caption, str) or not caption.strip():
            raise TelegramError("package contains an invalid platform caption")
        heading = channel.replace("-", " ").upper()
        messages.extend(_chunks(f"{heading}\n\n{caption.strip()}"))
    return messages


def _multipart(fields: Mapping[str, str], file: Path) -> tuple[bytes, str]:
    boundary = "----DockContent" + uuid.uuid4().hex
    body = bytearray()
    for name, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.extend(value.encode("utf-8"))
        body.extend(b"\r\n")
    mime = mimetypes.guess_type(file.name)[0] or "application/octet-stream"
    body.extend(f"--{boundary}\r\n".encode())
    body.extend(
        f'Content-Disposition: form-data; name="photo"; filename="{file.name}"\r\n'.encode()
    )
    body.extend(f"Content-Type: {mime}\r\n\r\n".encode())
    body.extend(file.read_bytes())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())
    return bytes(body), f"multipart/form-data; boundary={boundary}"


class TelegramClient:
    def __init__(
        self,
        *,
        token: str,
        chat_id: str,
        transport: Transport | None = None,
        timeout_seconds: int = 120,
    ) -> None:
        if not token or not chat_id:
            raise TelegramError("Telegram token and chat id are required")
        self.chat_id = chat_id
        self.timeout_seconds = timeout_seconds
        self.transport = transport or self._http_transport(token)

    def _http_transport(self, token: str) -> Transport:
        api_root = f"https://api.telegram.org/bot{token}/"

        def send(method: str, fields: dict[str, str], file: Path | None) -> Mapping[str, Any]:
            if file is None:
                data = parse.urlencode(fields).encode("utf-8")
                req = request.Request(
                    api_root + method,
                    data=data,
                    method="POST",
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
            else:
                data, content_type = _multipart(fields, file)
                req = request.Request(
                    api_root + method,
                    data=data,
                    method="POST",
                    headers={"Content-Type": content_type},
                )
            try:
                with request.urlopen(req, timeout=self.timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except Exception as exc:
                raise TelegramError(f"Telegram request failed: {exc}") from exc
            if not isinstance(payload, Mapping):
                raise TelegramError("Telegram response was not an object")
            return payload

        return send

    @staticmethod
    def _check(payload: Mapping[str, Any]) -> None:
        if payload.get("ok") is not True:
            raise TelegramError(str(payload.get("description") or "Telegram rejected the request"))

    def send_message(self, message: str) -> None:
        for chunk in _chunks(message):
            self._check(
                self.transport(
                    "sendMessage",
                    {"chat_id": self.chat_id, "text": chunk, "disable_web_page_preview": "true"},
                    None,
                )
            )

    def deliver(self, package_path: str | Path) -> None:
        package_path = Path(package_path)
        try:
            package = json.loads(package_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TelegramError(f"cannot read delivery package {package_path}: {exc}") from exc
        event = package.get("event")
        brand = package.get("brand")
        artifacts = package.get("artifacts")
        if not all(isinstance(item, Mapping) for item in (event, brand, artifacts)):
            raise TelegramError("delivery package metadata is incomplete")
        card_value = artifacts.get("card")
        card = Path(card_value) if isinstance(card_value, str) else None
        if card is None or not card.is_file():
            raise TelegramError("delivery card is missing")
        caption = f"{brand.get('name')} · {event.get('name')} · {event.get('date')}"
        self._check(
            self.transport(
                "sendPhoto", {"chat_id": self.chat_id, "caption": caption[:1024]}, card
            )
        )
        for message in delivery_messages(package):
            self.send_message(message)

    def send_failure(self, *, stage: str, detail: str) -> None:
        self.send_message(f"OCCASION PIPELINE FAILED\n\nStage: {stage}\n\n{detail[:3500]}")


__all__ = ["TelegramClient", "TelegramError", "delivery_messages"]
