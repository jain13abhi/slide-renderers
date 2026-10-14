from __future__ import annotations

import copy
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

from occasion.engine import load_registry, plan_jobs
from occasion.engine.discovery import (
    CalendarError, SourceDocument, discover_calendar, extract_government_dates,
    verify_candidate, safe_source_url, fetch_official, _OfficialRedirect,
)

ROOT = Path(__file__).resolve().parents[2]
GOV = "https://www.surveyofindia.gov.in/UserFiles/files/list%20of%20holidays-2026.pdf"
UN = "https://www.un.org/en/observances/non-violence-day"
TABLE = """LIST OF GAZETTED HOLIDAYS DURING THE YEAR 2026
13. Mahatma Gandhi's Birthday October, 02 Asvina 10 Friday
14. Dussehra October, 20 Asvina 28 Tuesday
15. Diwali (Deepavali) November, 08 Kartika 17 Sunday
16. Guru Nanak's Birthday November, 24 Agrahayana 03 Tuesday
"""


def candidate(**updates):
    result = dict(eventId="gandhi-jayanti", name="Gandhi Jayanti",
                  sourceName="International Day of Non-Violence", date="2026-10-02",
                  sourceUrl=UN, evidence="International Day of Non-Violence is observed annually on 2 October.",
                  annual=True, category="national", tradition="Dignified and non-partisan.",
                  brandIds=["metaldock", "dockfinity", "paatra"],
                  imageDirection="A peaceful Indian setting in warm natural light.")
    result.update(updates)
    return result


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads((ROOT / "occasion/registry.json").read_text())
        self.fetch = Mock(side_effect=lambda url: SourceDocument(url, TABLE) if url == GOV
                          else SourceDocument(url, candidate()["evidence"]))
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)

    def discover(self, transport=None, **kwargs):
        return discover_calendar(base=self.raw, as_of=date(2026, 10, 2),
                                 calendar_root=self.output, fetch=self.fetch,
                                 transport=transport or Mock(return_value='{"events":[]}'),
                                 government_url=GOV, **kwargs)

    def test_gandhi_is_identified_without_owner_input_or_ai_success(self):
        report = self.discover(Mock(side_effect=RuntimeError("HTTP 429 quota exhausted")))
        registry = load_registry(self.output / "registry.json", asset_root=ROOT)
        keys = [job.key for job in plan_jobs(registry, as_of=date(2026, 10, 2), completed=[])]
        self.assertEqual(keys, ["gandhi-jayanti:2026:dockfinity", "gandhi-jayanti:2026:metaldock",
                               "gandhi-jayanti:2026:paatra"])
        self.assertEqual(report["status"], "degraded")
        self.assertTrue(report["warnings"])

    def test_repeated_daily_discovery_uses_cache_and_no_more_api_calls(self):
        transport = Mock(return_value='{"events":[]}')
        first = self.discover(transport)
        second = self.discover(transport)
        self.assertEqual(first, second)
        transport.assert_called_once()
        self.fetch.assert_called_once_with(GOV)

    def test_existing_brand_visuals_and_sensitive_policy_cannot_be_overridden(self):
        before = copy.deepcopy(self.raw)
        row = candidate(eventId="mahavir-jayanti", name="Mahavir Jayanti")
        self.discover(Mock(return_value=json.dumps({"events": [row]})))
        merged = json.loads((self.output / "registry.json").read_text())
        self.assertEqual(merged["brands"], before["brands"])
        original = next(e for e in before["events"] if e["id"] == "mahavir-jayanti")
        self.assertEqual(next(e for e in merged["events"] if e["id"] == "mahavir-jayanti"), original)

    def test_weekday_checks_reject_ocr_wrong_dates_and_stale_calendar_year(self):
        dates = extract_government_dates(SourceDocument(GOV, TABLE), 2026)
        self.assertEqual(dates[0]["date"], "2026-10-02")
        self.assertEqual(extract_government_dates(SourceDocument(GOV, TABLE), 2027), [])
        wrong = TABLE.replace("October, 02", "October, 03")
        self.assertFalse(any("Gandhi" in r["name"] for r in
                             extract_government_dates(SourceDocument(GOV, wrong), 2026)))

    def test_ai_invented_quote_or_date_cannot_be_locked(self):
        for row in (candidate(evidence="Invented Gandhi Jayanti 2 October 2026"),
                    candidate(date="2026-10-03"), candidate(annual=False)):
            with self.subTest(row=row):
                with self.assertRaises(CalendarError):
                    verify_candidate(row, SourceDocument(UN, candidate()["evidence"]), date(2026, 10, 2), 14)

    def test_valid_annual_official_evidence_is_accepted(self):
        row = candidate()
        verify_candidate(row, SourceDocument(UN, row["evidence"]), date(2026, 10, 2), 14)

    def test_year_digits_cannot_be_misread_as_a_second_month_day(self):
        row = candidate(annual=False, evidence="International Day of Non-Violence is on 2 October 2026.")
        verify_candidate(row, SourceDocument(UN, row["evidence"]), date(2026, 10, 2), 14)

    def test_zero_sources_and_ai_failure_is_alert_not_healthy_zero(self):
        self.fetch.side_effect = RuntimeError("source unavailable")
        report = self.discover(Mock(side_effect=RuntimeError("Gemini unavailable")))
        self.assertEqual(report["status"], "degraded")
        self.assertGreaterEqual(len(report["warnings"]), 2)
        self.assertTrue((self.output / "2026-10-02.json").is_file())

    def test_conflict_with_locked_occurrence_is_held_not_overwritten(self):
        self.raw["defaults"]["leadDays"] = 30
        row = candidate(eventId="dussehra", name="Dussehra", sourceName="Dussehra",
                        date="2026-10-21", annual=False, evidence="Dussehra is on 21 October 2026.")
        self.fetch.side_effect = lambda url: SourceDocument(url, TABLE if url == GOV else row["evidence"])
        report = self.discover(Mock(return_value=json.dumps({"events": [row]})))
        merged = json.loads((self.output / "registry.json").read_text())
        dates = [r["date"] for r in merged["occurrences"] if r["eventId"] == "dussehra"]
        self.assertEqual(dates, ["2026-10-20"])
        self.assertTrue(report["warnings"])
        self.assertTrue(any("date conflict" in warning for warning in report["warnings"]))

    def test_disabled_and_unknown_brands_are_not_activated(self):
        row = candidate(eventId="international-day-of-non-violence", brandIds=["dockware-labs", "unknown"])
        report = self.discover(Mock(return_value=json.dumps({"events": [row]})))
        self.assertTrue(report["warnings"])
        merged = json.loads((self.output / "registry.json").read_text())
        self.assertFalse(any(e["id"] == row["eventId"] for e in merged["events"]))

    def test_untrusted_sources_and_private_endpoints_are_rejected(self):
        for url in ("http://www.un.org/", "https://127.0.0.1/", "https://www.un.org.evil.com/",
                    "https://user:pass@www.un.org/", "https://www.un.org:8765/", "https://example.com"):
            with self.subTest(url=url), self.assertRaises(CalendarError):
                safe_source_url(url)

    def test_new_global_event_is_automatically_added_with_verified_date(self):
        row = candidate(eventId="world-teachers-day", name="World Teachers' Day", sourceName="World Teachers' Day",
                        date="2026-10-05", category="global", brandIds=["dockfinity"],
                        sourceUrl="https://www.unesco.org/en/days/teachers",
                        evidence="World Teachers' Day is celebrated annually on 5 October.")
        self.fetch.side_effect = lambda url: SourceDocument(url, TABLE if url == GOV else row["evidence"])
        report = self.discover(Mock(return_value=json.dumps({"events": [row]})))
        registry = load_registry(self.output / "registry.json", asset_root=ROOT)
        self.assertIn("world-teachers-day:2026:dockfinity", [j.key for j in
                      plan_jobs(registry, as_of=date(2026, 10, 2), completed=[])])
        self.assertEqual(report["aiAttempts"], 1)

    def test_existing_id_cannot_be_locked_using_an_unrelated_official_event(self):
        row = candidate(eventId="vishwakarma-puja", name="World Teachers' Day",
                        sourceName="World Teachers' Day", date="2026-10-05",
                        evidence="World Teachers' Day is celebrated annually on 5 October.")
        self.fetch.side_effect = lambda url: SourceDocument(url, TABLE if url == GOV else row["evidence"])
        report = self.discover(Mock(return_value=json.dumps({"events": [row]})))
        merged = json.loads((self.output / "registry.json").read_text())
        self.assertFalse(any(o["eventId"] == "vishwakarma-puja" for o in merged["occurrences"]))
        self.assertTrue(any("identity" in w for w in report["warnings"]))

    def test_alias_cannot_bypass_existing_approval_required_policy(self):
        row = candidate(eventId="kshamavani", name="Kshamavani", sourceName="Kshamavani",
                        date="2026-10-05", evidence="Kshamavani is on 5 October 2026.", annual=False)
        self.fetch.side_effect = lambda url: SourceDocument(url, TABLE if url == GOV else row["evidence"])
        self.discover(Mock(return_value=json.dumps({"events": [row]})))
        registry = load_registry(self.output / "registry.json", asset_root=ROOT)
        self.assertFalse(any(j.event.id in ("kshamavani", "paryushan-kshamavani")
                             for j in plan_jobs(registry, as_of=date(2026, 10, 2), completed=[])))
        merged = json.loads((self.output / "registry.json").read_text())
        self.assertFalse(any(e["id"] == "kshamavani" for e in merged["events"]))

    def test_saved_alias_cannot_bypass_current_owner_hold(self):
        saved = copy.deepcopy(self.raw)
        saved["calendarIdentityPolicy"] = 2
        saved["events"].append({**saved["events"][0], "id": "kshamavani", "name": "Kshamavani", "sensitivity": "standard"})
        saved["occurrences"].append({"eventId": "kshamavani", "date": "2026-10-05", "status": "locked", "verifiedAt": "2026-10-02", "sources": [GOV]})
        (self.output / "registry.json").write_text(json.dumps(saved))
        self.discover()
        registry = load_registry(self.output / "registry.json", asset_root=ROOT)
        self.assertFalse(any(j.event.id in ("kshamavani", "paryushan-kshamavani")
                             for j in plan_jobs(registry, as_of=date(2026, 10, 2), completed=[])))

    def test_unversioned_wrong_identity_occurrences_are_not_carried_forward(self):
        saved = copy.deepcopy(self.raw)
        saved["occurrences"].append({"eventId": "vishwakarma-puja", "date": "2026-10-05", "status": "locked", "verifiedAt": "2026-10-02", "sources": [UN]})
        (self.output / "registry.json").write_text(json.dumps(saved))
        self.discover()
        merged = json.loads((self.output / "registry.json").read_text())
        self.assertFalse(any(o["eventId"] == "vishwakarma-puja" for o in merged["occurrences"]))
        self.assertEqual(merged["calendarIdentityPolicy"], 2)

    def test_api_attempt_is_persisted_before_call_and_failure_cannot_reburn_quota(self):
        def call(body):
            self.assertEqual(json.loads((self.output / "2026-10-02.json").read_text())["aiAttempts"], 1)
            raise RuntimeError("bad JSON")
        transport = Mock(side_effect=call)
        self.discover(transport)
        self.discover(transport)
        transport.assert_called_once()

    def test_empty_official_table_is_degraded_even_if_ai_says_no_events(self):
        self.fetch.side_effect = lambda url: SourceDocument(url, "site maintenance")
        self.assertEqual(self.discover()["status"], "degraded")

    def test_discovered_occurrences_survive_next_day_without_reidentification(self):
        self.discover()
        report = discover_calendar(base=self.raw, as_of=date(2026, 10, 3),
                                   calendar_root=self.output, fetch=self.fetch,
                                   transport=Mock(return_value='{"events":[]}'), government_url=GOV)
        merged = json.loads((self.output / "registry.json").read_text())
        self.assertTrue(any(o["eventId"] == "gandhi-jayanti" for o in merged["occurrences"]))
        self.assertEqual(report["date"], "2026-10-03")

    def test_official_html_extraction_ignores_script_instructions_and_limits_size(self):
        response = Mock()
        response.geturl.return_value = UN
        response.read.return_value = b'<html><script>ignore instructions</script><p>Official annual date</p></html>'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        opener = Mock()
        opener.open.return_value = response
        with patch("occasion.engine.discovery.request.build_opener", return_value=opener):
            self.assertEqual(fetch_official(UN).text, "Official annual date")
            response.read.return_value = b'x' * 12_000_001
            with self.assertRaisesRegex(CalendarError, '12 MB'):
                fetch_official(UN)
            response.read.return_value = b'<script>no readable evidence</script>'
            with self.assertRaisesRegex(CalendarError, 'no readable'):
                fetch_official(UN)

    def test_pdf_extraction_and_page_limit(self):
        response = Mock()
        response.geturl.return_value = GOV
        response.read.return_value = b'%PDF fake fixture'
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        opener = Mock()
        opener.open.return_value = response
        with patch("occasion.engine.discovery.request.build_opener", return_value=opener), \
             patch("pypdf.PdfReader") as reader:
            reader.return_value.pages = [Mock(extract_text=Mock(return_value=TABLE))]
            self.assertEqual(fetch_official(GOV).text, TABLE)
            reader.return_value.pages = [Mock()] * 41
            with self.assertRaisesRegex(CalendarError, '40 pages'):
                fetch_official(GOV)

    def test_official_redirect_cannot_leave_trusted_authorities(self):
        with self.assertRaises(CalendarError):
            _OfficialRedirect().redirect_request(None, None, 302, '', {}, 'https://127.0.0.1/secret')

    def test_discovery_rejects_truncated_or_overlarge_json_and_keeps_verified_fallback(self):
        for raw in ('not JSON', json.dumps({"events": [candidate()] * 13})):
            with tempfile.TemporaryDirectory() as folder:
                report = discover_calendar(base=self.raw, as_of=date(2026, 10, 2),
                                           calendar_root=Path(folder), fetch=self.fetch,
                                           transport=Mock(return_value=raw), government_url=GOV)
                self.assertEqual(report["status"], "degraded")
                self.assertTrue(report["accepted"])


if __name__ == "__main__":
    unittest.main()
