"""Create a source-only archive using an explicit allowlist."""
from pathlib import Path
import zipfile
import argparse

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = ['emotion.py', 'expressive.py', 'expressive_worker.py', 'requirements-expressive.txt', 'requirements-expressive-windows.lock', 'docs/EMOTION.md', '.gitignore', '.dockerignore', 'README.md', 'RESEARCH.md', 'LICENSE',
              'benchmark.py', 'cli.py', 'pipeline.py', 'rvc_worker.py', 'kokoro_adapter.py',
              'predict.py', 'cog.yaml', 'requirements.txt', 'requirements-rvc.txt',
              'requirements-tts-windows.lock', 'examples/README.md', 'examples/licenses/APACHE-2.0.txt', 'examples/licenses/VCTK-CC-BY-4.0.txt', 'examples/licenses/VCTK-model-card.md',
              'examples/manifest.json', 'docs/ASSET_PERMISSIONS.md', 
              'docs/voice-record.template.json', 'docs/TTS_GOGGINS_BENCHMARK.md', 'docs/benchmarks/goggins-20260916.json', 'vendor/rvc-v3/UPSTREAM.md', 'vendor/rvc-v3/LICENSE', 'vendor/KOKORO-ONNX-LICENSE']
EXAMPLE_FILES = ['examples/audio/'+name+'.wav' for name in ('vctk226-source','vctk226-speech','vctk231-source','vctk231-speech')]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--include-examples', action='store_true')
    args = parser.parse_args()
    output = ROOT/('dist/rvc-v3-tts-with-examples.zip' if args.include_examples else 'dist/rvc-v3-tts-source.zip')
    output.parent.mkdir(exist_ok=True)
    files = [ROOT/f for f in ROOT_FILES]
    if args.include_examples:
        files.extend(ROOT/f for f in EXAMPLE_FILES)
    for directory in ('scripts', 'tests', 'vendor/rvc-v3/src'):
        files.extend((ROOT/directory).rglob('*.py'))
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(set(files)):
            archive.write(path, path.relative_to(ROOT).as_posix())
    print(output)

if __name__ == '__main__': main()
