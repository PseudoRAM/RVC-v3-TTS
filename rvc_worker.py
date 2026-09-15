"""Persistent JSON-lines adapter. Stdout is protocol; model logs go to stderr."""
import contextlib
import json
from pathlib import Path
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor' / 'rvc-v3' / 'src'))

def main():
    started = time.perf_counter()
    with contextlib.redirect_stdout(sys.stderr):
        from service import VoiceService
        service = VoiceService()
    print(json.dumps({'ready': True, 'setup_seconds': time.perf_counter()-started}), flush=True)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            with contextlib.redirect_stdout(sys.stderr):
                output = service.convert(**request)
            response = {'path': str(output)}
        except Exception as exc:
            traceback.print_exc(file=sys.stderr)
            response = {'error': str(exc)}
        print(json.dumps(response), flush=True)

if __name__ == '__main__':
    main()
