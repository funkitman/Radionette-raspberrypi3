import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
import radio

class Tests(unittest.TestCase):
    def setUp(self):
        self.bands = radio.load_config('config/stations.example.json')
        self.s = self.bands['FM'][0]

    def test_tuning(self):
        self.assertIs(radio.tune([self.s], .25), self.s)
        self.assertIsNone(radio.tune([self.s], .29))
        self.assertIs(radio.tune([self.s], .29, self.s), self.s)
        self.assertIsNone(radio.tune([self.s], .30, self.s))
        self.assertIsNone(radio.tune([], .25, self.s))
        other = dict(self.s, position=.27)
        self.assertIs(radio.tune([self.s, other], .269), other)

    def test_invalid_number(self):
        for value in [float('nan'), float('inf'), -1, 2, True]:
            with self.assertRaises(ValueError):
                radio.number(value, 0, 1)

    @patch('radio.subprocess.Popen')
    @patch('radio.time.monotonic')
    def test_retry_cleanup(self, clock, popen):
        clock.return_value = 10
        first, second = Mock(), Mock()
        first.poll.return_value = None
        second.poll.return_value = None
        popen.side_effect = [first, second]
        p = radio.Player()
        p.set_station(self.s); p.tick(); p.tick()
        self.assertEqual(popen.call_count, 1)
        first.poll.return_value = 1
        p.tick()
        clock.return_value = 14
        p.tick()
        self.assertEqual(popen.call_count, 1)
        clock.return_value = 15
        p.tick()
        self.assertEqual(popen.call_count, 2)
        self.assertEqual(popen.call_args.args[0][-2:], ['--', self.s['url']])
        p.set_station(None)
        second.terminate.assert_called_once()
        second.wait.assert_called_once()

    @patch('radio.subprocess.Popen')
    def test_dry_run(self, popen):
        p = radio.Player(True)
        p.set_station(self.s); p.tick(); p.stop()
        popen.assert_not_called()

    def test_cli(self):
        r = subprocess.run([sys.executable, 'radio.py', '--dry-run'], input='tune .8\nband AM\nband K\nband L\nband FM\ntune nan\ntune .25\nstop\nplay\nquit\n', text=True, capture_output=True, timeout=5)
        self.assertEqual(r.returncode, 0, r.stderr)
        for expected in ['between stations (silent)', 'AM ', 'K ', 'L ', 'Invalid command', 'Local bench test']:
            self.assertIn(expected, r.stdout)

if __name__ == '__main__':
    unittest.main()
