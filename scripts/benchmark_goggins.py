"""Generate local TTS/RVC listening pairs and separate stage timings.

Provision the requested voice checkpoint and index before running. Audio stays
under ignored demos/; this script does not upload or redistribute model weights.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import statistics
import sys
import time

STARTED = time.perf_counter()
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import Pipeline, Request

SHORT = 'Start with one small task. Give it your full attention, finish it properly, and then take the next step.'
MEDIUM = ('When a plan feels overwhelming, make the next step smaller. Choose one useful thing you can finish today. '
          'Put your phone aside, take a breath, and give yourself ten focused minutes. Progress does not need to be dramatic. '
          'It needs to be something you can repeat tomorrow.')
LONG = ('Some days, everything feels easy. On other days, even getting started takes effort. That is when a simple routine helps. '
        'Decide what matters, prepare your space, and begin before you feel completely ready.\n'
        'You do not have to solve the whole problem in one sitting. Work through the first part, check what you have learned, '
        'and adjust your approach. If you make a mistake, use it as information rather than a reason to stop.\n'
        'At the end of the day, look back at the work you actually completed. Keep what helped, change what did not, '
        'and leave yourself a clear starting point for tomorrow.')
CASES = [('short-michael', 'Short / Michael', SHORT, 'am_michael'),
         ('medium-michael', 'Medium / Michael', MEDIUM, 'am_michael'),
         ('long-michael', 'Long / Michael', LONG, 'am_michael'),
         ('medium-adam', 'Medium / Adam', MEDIUM, 'am_adam')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voice', default='DavidGoggins')
    parser.add_argument('--runs', type=int, default=3)
    parser.add_argument('--rvc-python')
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    if args.runs < 2:
        parser.error('At least two runs are needed to separate first requests and warm repeats')
    folder = args.output_dir or ROOT / 'demos' / ('goggins-' + time.strftime('%Y%m%d-%H%M%S'))
    folder = folder.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    report = {'scope': 'Local text -> Kokoro CPU ONNX -> RVC GPU, not a hosted or machine-cold benchmark',
              'platform': platform.platform(), 'tts_python': sys.version,
              'tts_provider': 'CPUExecutionProvider', 'tts_threads': 4,
              'runs_per_case': args.runs, 'case_order': [case[0] for case in CASES],
              'notes': 'First means first request for that case in one persistent process. Warm median excludes that request. No audio response cache.',
              'cases': []}
    with Pipeline(args.rvc_python) as pipeline:
        report.update(setup_seconds=pipeline.setup_seconds, tts_setup_seconds=pipeline.tts_setup_seconds,
                      rvc_worker_setup_seconds=pipeline.rvc_setup_seconds,
                      startup_including_imports_seconds=time.perf_counter() - STARTED)
        for slug, title, text, source_voice in CASES:
            request = Request(text=text, voice=args.voice, source_voice=source_voice)
            runs = []
            for iteration in range(args.runs):
                output, metrics = pipeline.run(request, folder / f'{slug}-{iteration}')
                runs.append(metrics)
                print(json.dumps({'case': slug, 'run': iteration, 'total_seconds': metrics['total_seconds'],
                                  'tts_seconds': metrics['tts_seconds'], 'rvc_seconds': metrics['rvc_and_copy_seconds']}), flush=True)
            row = {'slug': slug, 'title': title, 'request': asdict(request), 'runs': runs,
                   'first_seconds': runs[0]['total_seconds'],
                   'warm_median_seconds': statistics.median(run['total_seconds'] for run in runs[1:]),
                   'warm_tts_median_seconds': statistics.median(run['tts_seconds'] for run in runs[1:]),
                   'warm_rvc_median_seconds': statistics.median(run['rvc_and_copy_seconds'] for run in runs[1:]),
                   'duration_seconds': runs[0]['duration_seconds'],
                   'warm_median_rtf': statistics.median(run['rtf'] for run in runs[1:]),
                   'audio': {}}
            for kind in ('source', 'speech'):
                audio = folder / f'{slug}-0' / f'{kind}.wav'
                row['audio'][kind] = {'path': audio.relative_to(folder).as_posix(),
                                      'sha256': hashlib.sha256(audio.read_bytes()).hexdigest()}
            report['cases'].append(row)
            (folder / 'results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    voice_dir = ROOT / 'vendor/rvc-v3/rvc_models' / args.voice
    report['model_assets'] = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in voice_dir.iterdir() if path.suffix in ('.pth', '.index')}
    report['setup_plus_first_request_seconds'] = report['setup_seconds'] + report['cases'][0]['first_seconds']
    (folder / 'results.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({'results': str(folder / 'results.json'), 'setup_seconds': report['setup_seconds']}, indent=2))


if __name__ == '__main__':
    main()
