"""Deterministic official holiday adapters; no model or lunar-date inference.

The CAG calendar is for Delhi central-government offices, not a claim that all
regional religious traditions follow one tithi. Keep the source's full name.
"""
from datetime import date
import re

CAG_CALENDAR = 'https://www.cag.gov.in/defence/new-delhi/en/page-defence-new-delhi-holidaylist'
MONTHS = {name.lower(): index for index, name in enumerate(
    ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
     'September', 'October', 'November', 'December'), 1)}


def extract_holiday_rows(document, year):
    facts = []
    active = False
    for cells in document.rows:
        header = ' '.join(cells)
        if re.search(r'List of (?:Gazetted|Restricted) Holidays during the year', header, re.I):
            active = bool(re.search(r'\byear\s+' + str(year) + r'\b', header, re.I))
            continue
        if not active or len(cells) != 4 or not cells[0].strip().isdigit():
            continue
        _, name, when, weekday = cells
        match = re.fullmatch(r'([A-Za-z]+)\s+(\d{1,2})', when.strip())
        if not match or match[1].lower() not in MONTHS:
            continue
        try:
            day = date(year, MONTHS[match[1].lower()], int(match[2]))
        except ValueError:
            continue
        if day.strftime('%A').casefold() != weekday.strip().casefold():
            continue
        facts.append({'name': name.strip(), 'date': day.isoformat(),
                      'sourceUrl': document.url, 'evidence': header})
    return facts
