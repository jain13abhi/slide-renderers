import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import Mock

from occasion.engine.discovery import SourceDocument, discover_calendar, _Text, BLOCKED_WORDS
from occasion.engine.official_calendar import extract_holiday_rows

CAG = 'https://www.cag.gov.in/defence/new-delhi/en/page-defence-new-delhi-holidaylist'

class OfficialCalendarTests(unittest.TestCase):
    def test_martyrdom_rows_do_not_become_automatic_festive_greetings(self):
        self.assertTrue(BLOCKED_WORDS.search("Guru Tegh Bahadur's Martyrdom Day"))
        self.assertTrue(BLOCKED_WORDS.search("Martyrs' Day"))
    def test_year_scoped_restricted_rows_and_weekday_not_lunar_guess(self):
        rows = (('List of Restricted Holidays during the year 2026',),
                ('24', 'Dussehra (Mahashtami)', 'October 19', 'Monday'),
                ('25', 'Dussehra (Mahanavmi)', 'October 20', 'Tuesday'),
                ('27', 'Karaka Chaturthi (Karwa Chouth)', 'October 29', 'Thursday'),
                ('9', 'Wrong OCR row', 'October 30', 'Monday'))
        facts = extract_holiday_rows(SourceDocument(CAG, '', rows=rows), 2026)
        self.assertEqual([r['date'] for r in facts], ['2026-10-19', '2026-10-20', '2026-10-29'])
        self.assertFalse(extract_holiday_rows(SourceDocument(CAG, '', rows=rows), 2027))
        self.assertNotIn('Ram Navami', str(facts))

    def test_html_rows_preserve_boundaries_and_ignore_scripts(self):
        parser = _Text()
        parser.feed('<table><tr><td><b>2026</b></td></tr><tr><td>A</td><td>October 19</td>'
                    '<td><script>override</script>Monday</td></tr></table>')
        self.assertEqual(parser.rows, [('2026',), ('A', 'October 19', 'Monday')])

    def test_deterministic_regional_source_survives_ai_429_without_search_tool(self):
        root = Path(__file__).resolve().parents[2]
        base = json.loads((root / 'occasion/registry.json').read_text())
        gov = SourceDocument('https://www.surveyofindia.gov.in/UserFiles/files/list%20of%20holidays-2026.pdf',
                             'GAZETTED HOLIDAYS DURING THE YEAR 2026\n14. Dussehra October 20 Asvina 28 Tuesday')
        cag = SourceDocument(CAG, '', rows=(('List of Restricted Holidays during the year 2026',),
                              ('24', 'Dussehra (Mahashtami)', 'October 19', 'Monday')))
        transport = Mock(side_effect=RuntimeError('HTTP 429 quota unavailable'))
        with tempfile.TemporaryDirectory() as tmp:
            result = discover_calendar(base=base, as_of=date(2026, 10, 19), calendar_root=Path(tmp),
                        fetch=lambda url: cag if url == CAG else gov, transport=transport,
                        supplemental_sources=(CAG,))
            registry = json.loads((Path(tmp) / 'registry.json').read_text())
            self.assertTrue(any(o['eventId'] == 'dussehra-mahashtami' for o in registry['occurrences']))
            self.assertEqual(result['coreStatus'], 'healthy')
            self.assertEqual(result['extensionStatus'], 'degraded')
            self.assertNotIn('tools', transport.call_args.args[0])
            self.assertEqual(result['aiAttempts'], 1)

if __name__ == '__main__': unittest.main()
