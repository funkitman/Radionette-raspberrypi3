#!/usr/bin/env python3
"""Bench radio: standard-library controller and replaceable mpv backend."""
import argparse
import json
import math
from pathlib import Path
import select
import shutil
import signal
import subprocess
import sys
import time
from urllib.parse import urlparse

BANDS = ('FM', 'AM', 'K', 'L')


def number(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'Expected finite number {low}..{high}: {value!r}')
    return value


def load_config(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or not isinstance(data.get('bands'), dict):
        raise ValueError('Configuration must contain a bands object')
    bands = data['bands']
    if set(bands) != set(BANDS):
        raise ValueError('Exactly FM, AM, K and L are required')
    for stations in bands.values():
        if not isinstance(stations, list):
            raise ValueError('Each band must be a list')
        for s in stations:
            if not isinstance(s, dict):
                raise ValueError('Station must be an object')
            if not isinstance(s['name'], str) or not s['name'].strip():
                raise ValueError('Station name is required')
            url = urlparse(s['url'])
            if url.scheme not in ('http', 'https') or not url.hostname:
                raise ValueError('Station URL must be HTTP(S)')
            number(s['position'], 0, 1)
            number(s['capture_width'], 0.001, 0.5)
    return bands


def tune(stations, position, current=None):
    number(position, 0, 1)
    # Retain the captured station through small movements at the edge.
    if current in stations and current is not None:
        if abs(current['position'] - position) <= current['capture_width'] + 0.01:
            return current
    candidates = [s for s in stations if abs(s['position'] - position) <= s['capture_width']]
    return min(candidates, key=lambda s: abs(s['position'] - position), default=None)


class Player:
    def __init__(self, dry_run=False, volume=30):
        self.dry_run, self.volume = dry_run, volume
        self.process = None
        self.url = None
        self.retry_at = 0

    def stop(self):
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait()
            self.process = None

    def set_station(self, station):
        url = station['url'] if station else None
        if url != self.url:
            self.stop()
            self.url, self.retry_at = url, 0

    def tick(self):
        if self.dry_run or self.url is None:
            return
        if self.process is not None:
            if self.process.poll() is None:
                return
            print(f'Player exited ({self.process.returncode}); retry in 5s', flush=True)
            self.process = None
            self.retry_at = time.monotonic() + 5
        if time.monotonic() >= self.retry_at:
            self.process = subprocess.Popen([
                'mpv', '--no-config', '--no-video', '--no-terminal',
                '--input-terminal=no', '--network-timeout=10',
                f'--volume={self.volume}', '--', self.url], stdin=subprocess.DEVNULL)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default=str(Path(__file__).parent / 'config/stations.example.json'))
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--band', choices=BANDS, default='FM')
    parser.add_argument('--position', type=float, default=0.25)
    parser.add_argument('--volume', type=int, default=30)
    parser.add_argument('--headless', action='store_true', help='Stay on initial band/position, without stdin')
    args = parser.parse_args(argv)
    try:
        bands = load_config(args.config)
        number(args.position, 0, 1)
        number(args.volume, 0, 100)
        if not args.dry_run and not shutil.which('mpv'):
            raise ValueError('mpv missing: install mpv or use --dry-run')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.error(str(exc))
    player = Player(args.dry_run, args.volume)
    band, position, station = args.band, args.position, None
    running = True

    def shutdown(*_):
        nonlocal running
        running = False

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    def update():
        nonlocal station
        station = tune(bands[band], position, station)
        player.set_station(station)
        print(f'{band} {position:.3f}: {station["name"] if station else "between stations (silent)"}', flush=True)

    update()
    if not args.headless:
        print('Commands: band FM|AM|K|L, tune 0..1, stop, play, quit', flush=True)
    try:
        while running:
            player.tick()
            if args.headless:
                time.sleep(0.1)
                continue
            if not select.select([sys.stdin], [], [], 0.1)[0]:
                continue
            line = sys.stdin.readline()
            if not line:
                break
            parts = line.split()
            try:
                if parts == ['quit']:
                    break
                elif parts == ['stop']:
                    player.set_station(None)
                elif parts == ['play']:
                    update()
                elif len(parts) == 2 and parts[0] == 'band' and parts[1] in BANDS:
                    band, station = parts[1], None
                    update()
                elif len(parts) == 2 and parts[0] == 'tune':
                    position = number(float(parts[1]), 0, 1)
                    update()
                else:
                    print('Invalid command', flush=True)
            except ValueError as exc:
                print(f'Invalid command: {exc}', flush=True)
    finally:
        player.stop()
    return 0


if __name__ == '__main__':
    sys.exit(main())
