"""Versioned cultural scenes. Discovery/LLM metadata cannot approve an image scene."""

import json
from pathlib import Path

from . import Job


class VisualContextError(ValueError):
    pass


OFFICIAL_TRADITIONS = (
    'Official Indian gazetted observance; respectful and non-partisan. No invented rituals or quotations.',
    'Official Delhi central-government holiday wording. Regional traditions may differ; do not rename or conflate festivals.',
)

# These are visual interpretations of the cited cultural context, not calendar dates,
# approved rituals for every community, or permission to override an owner hold.
SUPPLEMENTAL = {
    'maharishi-valmiki-s-birthday': {
        'name': "Maharishi Valmiki's Birthday",
        'scene': 'Maharishi Valmiki Jayanti in an Indian literary-devotional setting: an open traditional manuscript on a low reading lectern, marigolds and one brass diya, a quiet Indian courtyard in warm natural light. Pages seen obliquely with no legible script. No invented portrait of the sage.',
        'source': 'https://www.incredibleindia.gov.in/en/festivals-and-events/valmiki-jayanti',
    },
    'karaka-chaturthi-karwa-chouth': {
        'name': 'Karaka Chaturthi (Karwa Chouth)',
        'scene': 'North Indian Karwa Chauth: a sieve, a small traditional karwa water pot and a restrained puja thali in a contemporary Indian terrace setting under moonlight. Warm diya illumination, accurate polished vessel reflections. Still life only; no invented ritual gestures or fasting health claims.',
        'source': 'https://www.drikpanchang.com/festivals/karwa-chauth/info/karwa-chauth.html?lang=en',
    },
}


def trusted_visual_context(job: Job) -> dict:
    """Match canonical identity and tradition against checked-in curated content."""
    if (not job.brand.enabled or job.brand.id not in job.event.brand_ids
            or job.event.sensitivity != 'standard' or job.occurrence.status != 'locked'
            or job.occurrence.event_id != job.event.id):
        raise VisualContextError('trusted visual brief cannot override disabled brands, owner holds or occurrence identity')
    bundled = Path(__file__).resolve().parents[1] / 'registry.json'
    curated = json.loads(bundled.read_text(encoding='utf-8'))
    event = next((row for row in curated['events'] if row['id'] == job.event.id), None)
    if event is not None:
        if (event['name'], event['tradition'], event['category'], event['sensitivity']) != (
            job.event.name, job.event.tradition, job.event.category, job.event.sensitivity
        ):
            raise VisualContextError('trusted visual brief identity/tradition mismatch')
        scene, provenance = event['imageDirection'], 'occasion/registry.json#' + event['id']
    else:
        brief = SUPPLEMENTAL.get(job.event.id)
        if (not brief or job.event.name != brief['name'] or job.event.tradition not in OFFICIAL_TRADITIONS
                or job.event.category != 'religious' or job.event.sensitivity != 'standard'):
            raise VisualContextError('no trusted visual brief for this canonical event/tradition; review cultural context before generation')
        scene, provenance = brief['scene'], brief['source']
    prompt = (
        f'Occasion: {job.event.name}. Cultural context: {job.event.tradition}\n'
        f'REQUIRED SCENE: {scene}\n'
        'Editorial photograph, portrait 4:5, image-led composition with clear lower area for a separate brand overlay. '
        'Exclude unrelated Christmas, snow-cabin, Western dinner-party or generic celebration imagery. '
        'No text, letters, numbers, logos, watermark, UI, borders, political figures or invented sacred symbols.'
    )
    return dict(canonicalEvent=job.event.id, tradition=job.event.tradition,
                provenance=provenance, providerPrompt=prompt)
