import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from occasion.engine.cli import main
from occasion.engine.telegram import TelegramClient, TelegramError
from occasion.engine.pipeline import PipelineError
from occasion.tests.test_telegram import package_fixture

class EventDayTests(unittest.TestCase):
    def test_event_day_reuses_art_and_has_independent_resumable_receipts(self):
        calls = []
        def transport(method, fields, file):
            calls.append((method, fields, file))
            return {'ok': True, 'result': {'message_id': len(calls)}}
        with tempfile.TemporaryDirectory() as tmp:
            package = package_fixture(Path(tmp))
            original = package.read_bytes()
            client = TelegramClient(token='fake', chat_id='test', transport=transport, today=lambda: date(2026, 10, 20))
            client.deliver(package)
            first_count = len(calls)
            client.deliver(package, purpose='event-day', as_of=date(2026, 10, 20))
            self.assertEqual(len(calls), first_count * 2)
            self.assertIn('READY TO POST TODAY', calls[first_count][1]['caption'])
            client.deliver(package, purpose='event-day', as_of=date(2026, 10, 20))
            self.assertEqual(len(calls), first_count * 2)
            self.assertEqual(package.read_bytes(), original)
            self.assertTrue(package.with_suffix('.event-day.telegram.json').exists())
            with self.assertRaisesRegex(TelegramError, 'event date'):
                client.deliver(package, purpose='event-day', as_of=date(2026, 10, 21))
            historical = TelegramClient(token='fake', chat_id='test', transport=transport, today=lambda: date(2026, 10, 21))
            with self.assertRaisesRegex(TelegramError, 'event date'):
                historical.deliver(package, purpose='event-day', as_of=date(2026, 10, 20))

    def test_reminder_cli_is_zero_provider_calls_on_non_event_day(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as tmp, patch('occasion.engine.cli.ist_today', return_value=date(2026, 10, 19)), \
             patch('occasion.engine.cli._telegram_from_environment') as telegram:
            self.assertEqual(main(['remind', '--date', '2026-10-19', '--repo-root', str(root),
                            '--state-root', tmp, '--output-root', tmp]), 0)
            telegram.assert_not_called()

    def test_cli_reminder_resumes_without_generation_and_preserves_owner_holds(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            production = folder / 'production'; production.mkdir()
            package_fixture(production)
            state = folder / 'state'; state.mkdir()
            marker = state / 'dussehra-2026-metaldock.json'
            original_marker = {'schemaVersion': 2, 'jobKey': 'dussehra:2026:metaldock',
                'status': 'delivered', 'package': 'package.json', 'deliveredAt': '2026-09-27T09:52:59+00:00'}
            marker.write_text(json.dumps(original_marker))
            raw = json.loads((root / 'occasion/registry.json').read_text())
            event = next(e for e in raw['events'] if e['id'] == 'dussehra')
            event['brandIds'] = ['metaldock']
            registry = folder / 'registry.json'; registry.write_text(json.dumps(raw))
            calls = []
            def transport(method, fields, file):
                calls.append(method)
                if len(calls) == 2: return {'ok': False, 'description': 'refused'}
                return {'ok': True, 'result': {'message_id': len(calls)}}
            client = TelegramClient(token='fake', chat_id='test', transport=transport, today=lambda: date(2026, 10, 20))
            args = ['remind', '--date', '2026-10-20', '--repo-root', str(root), '--registry', str(registry),
                    '--state-root', str(state), '--output-root', str(production)]
            with patch('occasion.engine.cli.ist_today', return_value=date(2026, 10, 20)), \
                 patch('occasion.engine.cli._telegram_from_environment', return_value=client), \
                 patch('occasion.engine.cli.GeminiDrafter') as drafter, patch('occasion.engine.cli.HiggsfieldProvider') as images:
                with self.assertRaises(PipelineError): main(args)
                self.assertEqual(main(args), 0)
                self.assertEqual(main(args), 0)
                drafter.assert_not_called(); images.assert_not_called()
            self.assertEqual(calls, ['sendPhoto', 'sendMessage', 'sendMessage', 'sendMessage', 'sendMessage'])
            self.assertEqual(json.loads(marker.read_text()), original_marker)
            # Reuse the same prepared package, but current policy always wins.
            for policy in ('hold', 'disabled', 'cancelled', 'delivered-today'):
                current = json.loads(json.dumps(raw))
                if policy == 'hold': next(e for e in current['events'] if e['id'] == 'dussehra')['sensitivity'] = 'approval-required'
                if policy == 'disabled': next(b for b in current['brands'] if b['id'] == 'metaldock')['enabled'] = False
                if policy == 'cancelled': next(o for o in current['occurrences'] if o['eventId'] == 'dussehra')['status'] = 'cancelled'
                registry.write_text(json.dumps(current))
                marker.write_text(json.dumps({**original_marker, **({'deliveredAt': '2026-10-20T00:00:00+00:00'} if policy == 'delivered-today' else {})}))
                with patch('occasion.engine.cli.ist_today', return_value=date(2026, 10, 20)), patch('occasion.engine.cli._telegram_from_environment') as factory:
                    self.assertEqual(main(args), 0)
                    factory.assert_not_called()

if __name__ == '__main__': unittest.main()
