"""Bounded external-provider adapters for Gemini and Higgsfield."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib import request

from PIL import Image

from . import GenerationBudget, Job, build_higgsfield_command, parse_higgsfield_result
from .pipeline import Draft, PipelineError

GeminiTransport = Callable[[dict[str, Any]], str]
CommandRunner = Callable[[list[str]], Any]
Downloader = Callable[[str], bytes]


def _gemini_text(payload: Mapping[str, Any]) -> str:
    blocked = payload.get("promptFeedback", {}).get("blockReason") if isinstance(payload.get("promptFeedback"), dict) else None
    if blocked:
        raise PipelineError(f"Gemini blocked the request: {blocked}")
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise PipelineError("Gemini returned no candidates")
    content = candidates[0].get("content", {}) if isinstance(candidates[0], dict) else {}
    parts = content.get("parts", []) if isinstance(content, dict) else []
    text = "\n".join(
        part.get("text", "") for part in parts if isinstance(part, dict) and part.get("text")
    ).strip()
    if not text:
        raise PipelineError("Gemini returned no text")
    return text


class GeminiDrafter:
    """One grounded research call plus at most two structured drafting calls."""

    def __init__(
        self,
        *,
        transport: GeminiTransport | None = None,
        api_key: str | None = None,
        model: str = "gemini-3.5-flash-lite",
        timeout_seconds: int = 120,
    ) -> None:
        self.model = model
        self.timeout_seconds = timeout_seconds
        if transport is not None:
            self._transport = transport
        else:
            if not api_key:
                raise PipelineError("GEMINI_API_KEY is not configured")
            self._transport = self._http_transport(api_key)

    def _http_transport(self, api_key: str) -> GeminiTransport:
        endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + self.model
            + ":generateContent"
        )

        def send(body: dict[str, Any]) -> str:
            encoded = json.dumps(body).encode("utf-8")
            req = request.Request(
                endpoint,
                data=encoded,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": api_key,
                },
            )
            try:
                with request.urlopen(req, timeout=self.timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except Exception as exc:
                raise PipelineError(f"Gemini request failed: {exc}") from exc
            if not isinstance(payload, dict):
                raise PipelineError("Gemini response was not an object")
            return _gemini_text(payload)

        return send

    @staticmethod
    def _research_prompt(job: Job) -> str:
        sources = "\n".join(f"- {url}" for url in job.occurrence.sources)
        return f"""Research one occasion for a production social post.

Event: {job.event.name}
Confirmed occurrence date: {job.publish_date.isoformat()}
Tradition and regional interpretation: {job.event.tradition}
Brand: {job.brand.name}
Category: {job.event.category}
Locked date sources:
{sources}

Use Google Search to verify the date, tradition, meaning, and culturally safe visual details.
Prefer governments, official institutions, religious authorities, and primary organizers.
Clearly distinguish verified facts from interpretation. Do not change the locked date. Return a
concise research packet with source URLs. Do not draft marketing copy yet."""

    @staticmethod
    def _draft_prompt(job: Job, research: str, correction: str | None = None) -> str:
        channels = ", ".join(job.brand.channels)
        correction_text = f"\nThe previous draft failed validation: {correction}\nCorrect only those fields." if correction else ""
        return f"""Create the final structured content package using only the research packet.

EVENT: {job.event.name}
DATE: {job.publish_date.isoformat()}
BRAND: {job.brand.name}
BRAND CHANNELS: {channels}
BRAND-SPECIFIC ANGLE AND VISUAL DIRECTION: {job.event.image_direction}

RESEARCH PACKET:
{research}

Return exactly one JSON object with:
- eyebrow: date/occasion label, maximum 56 characters
- greeting: image headline, maximum 150 characters and no generic sales claim
- tagline: restrained closing line, maximum 90 characters
- imagePrompt: a photorealistic, culturally accurate background prompt; it must request no text,
  letters, logos, watermark, UI, border, or invented sacred symbolism
- captions: one caption for every requested channel, using the exact channel names

The X caption must have no URL and must be at most 260 characters. Other captions must be at most
2200 characters. Do not put hashtags into the image. The renderer, logo, typography, colours, and
geometry are locked and are not part of this response.{correction_text}"""

    def draft(self, job: Job) -> Draft:
        research_body = {
            "contents": [{"role": "user", "parts": [{"text": self._research_prompt(job)}]}],
            "tools": [{"google_search": {}}],
            "generationConfig": {"temperature": 0.15},
        }
        research = self._transport(research_body)
        correction: str | None = None
        for _ in range(2):
            draft_body = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": self._draft_prompt(job, research, correction)}],
                    }
                ],
                "generationConfig": {
                    "temperature": 0.25,
                    "responseMimeType": "application/json",
                },
            }
            raw = self._transport(draft_body)
            try:
                parsed = json.loads(raw)
                return Draft.from_payload(parsed, channels=job.brand.channels)
            except (json.JSONDecodeError, PipelineError) as exc:
                correction = str(exc)
        raise PipelineError("Gemini failed local validation after two drafting attempts")


def _default_run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def _default_download(url: str) -> bytes:
    req = request.Request(url, headers={"User-Agent": "DockContentEngine/1.0"})
    with request.urlopen(req, timeout=180) as response:
        return response.read()


def _find_credit_balance(value: Any) -> float | None:
    if isinstance(value, dict):
        direct = value.get("credits")
        if isinstance(direct, (int, float)) and not isinstance(direct, bool):
            return float(direct)
        for child in value.values():
            found = _find_credit_balance(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_credit_balance(child)
            if found is not None:
                return found
    return None


class HiggsfieldProvider:
    """Persistent-session Higgsfield CLI adapter with a hard attempt budget."""

    def __init__(
        self,
        *,
        run_command: CommandRunner = _default_run,
        download: Downloader = _default_download,
        budget: GenerationBudget,
        model: str = "nano_banana_2",
        resolution: str = "2k",
    ) -> None:
        self.run_command = run_command
        self.download = download
        self.budget = budget
        self.model = model
        self.resolution = resolution
        self._preflight_complete = False

    def _preflight(self) -> None:
        if self._preflight_complete:
            return
        result = self.run_command(["higgsfield", "account", "status", "--json", "--no-color"])
        if getattr(result, "returncode", 1) != 0:
            detail = (getattr(result, "stderr", "") or getattr(result, "stdout", "")).strip()
            if "auth" in detail.lower() or "session" in detail.lower():
                raise PipelineError(
                    "Higgsfield authentication is unavailable; run higgsfield auth login once on the VPS"
                )
            raise PipelineError(f"Higgsfield account preflight failed: {detail or 'unknown error'}")
        try:
            payload = json.loads(getattr(result, "stdout", ""))
        except json.JSONDecodeError as exc:
            raise PipelineError("Higgsfield account status was not valid JSON") from exc
        credits = _find_credit_balance(payload)
        if credits is not None and credits <= 0:
            raise PipelineError("Higgsfield account has no generation credits remaining")
        self._preflight_complete = True

    def generate(self, *, prompt: str, destination: Path, job_key: str) -> Path:
        self._preflight()
        self.budget.record_attempt(job_key)
        command = build_higgsfield_command(
            model=self.model,
            prompt=prompt,
            aspect_ratio="4:5",
            resolution=self.resolution,
        )
        result = self.run_command(command)
        if getattr(result, "returncode", 1) != 0:
            detail = (getattr(result, "stderr", "") or getattr(result, "stdout", "")).strip()
            raise PipelineError(f"Higgsfield generation failed: {detail or 'unknown error'}")
        try:
            url = parse_higgsfield_result(getattr(result, "stdout", ""))
            image_bytes = self.download(url)
        except PipelineError:
            raise
        except Exception as exc:
            raise PipelineError(f"Higgsfield result download failed: {exc}") from exc
        if not image_bytes:
            raise PipelineError("Higgsfield returned an empty image")
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_bytes(image_bytes)
        try:
            with Image.open(temporary) as image:
                image.verify()
            with Image.open(temporary) as image:
                if image.width < 800 or image.height < 800:
                    raise PipelineError(
                        f"Higgsfield image is too small: {image.width}x{image.height}"
                    )
        except PipelineError:
            temporary.unlink(missing_ok=True)
            raise
        except Exception as exc:
            temporary.unlink(missing_ok=True)
            raise PipelineError(f"Higgsfield result is not a valid image: {exc}") from exc
        temporary.replace(destination)
        return destination


__all__ = ["GeminiDrafter", "HiggsfieldProvider"]
