"""Resumable direct official-model download when the native transfer stalls."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import time
import requests

ROOT = Path(__file__).resolve().parents[1] / 'models' / 'qwen3-tts-customvoice'
REV = '0c0e3051f131929182e2c023b9537f8b1c68adfe'
BASE = 'https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice'
metadata = requests.get('https://huggingface.co/api/models/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice/revision/' + REV, params={'blobs': 'true'}, timeout=30).json()
files = [f for f in metadata['siblings'] if f['rfilename'].endswith('.safetensors')]
print(json.dumps([{'file': f['rfilename'], 'size': f['size'], 'sha256': f['lfs']['sha256']} for f in files]), flush=True)
CHUNK = 8 * 1024 * 1024
jobs = []
for f in files:
    parts = ROOT / '.parts' / f['rfilename'].replace('/', '_')
    parts.mkdir(parents=True, exist_ok=True)
    for start in range(0, f['size'], CHUNK):
        end = min(start + CHUNK, f['size']) - 1
        jobs.append((f, start, end, parts / str(start)))

def download(job):
    f, start, end, part = job
    size = end - start + 1
    if part.exists() and part.stat().st_size == size:
        return size
    for attempt in range(5):
        try:
            url = BASE + '/resolve/' + REV + '/' + f['rfilename']
            with requests.get(url, params={'download': 'true', 'part': str(start), 'attempt': str(attempt)},
                              headers={'Range': f'bytes={start}-{end}'}, stream=True, timeout=(30, 90)) as response:
                response.raise_for_status()
                assert response.status_code == 206 and response.headers['Content-Range'].startswith(f'bytes {start}-{end}/')
                with part.open('wb') as out:
                    for block in response.iter_content(1024 * 1024):
                        out.write(block)
            assert part.stat().st_size == size
            return size
        except Exception as error:
            print(json.dumps({'retry_file': f['rfilename'], 'start':start, 'attempt':attempt+1, 'error_type':type(error).__name__}),flush=True)
            if attempt == 4:
                raise
            time.sleep(2 + attempt)

started = time.monotonic()
done = 0
with ThreadPoolExecutor(max_workers=32) as pool:
    futures = [pool.submit(download, job) for job in jobs]
    for count, future in enumerate(as_completed(futures), 1):
        done += future.result()
        if count % 8 == 0 or count == len(jobs):
            print(json.dumps({'chunks': count, 'total_chunks': len(jobs), 'downloaded_MB': round(done/1e6), 'seconds': round(time.monotonic()-started)}), flush=True)
for f in files:
    target = ROOT / f['rfilename']
    digest = hashlib.sha256()
    parts = ROOT / '.parts' / f['rfilename'].replace('/', '_')
    with target.with_suffix('.verified-download').open('wb') as out:
        for start in range(0, f['size'], CHUNK):
            with (parts / str(start)).open('rb') as part:
                for block in iter(lambda: part.read(1024*1024), b''):
                    digest.update(block)
                    out.write(block)
    assert digest.hexdigest() == f['lfs']['sha256'], 'Downloaded weight hash mismatch'
    target.with_suffix('.verified-download').replace(target)
    print('Verified ' + f['rfilename'], flush=True)
(ROOT / 'download-manifest.json').write_text(json.dumps({'model_id': 'Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice', 'revision': REV,
    'files': {f['rfilename']:f['lfs']['sha256'] for f in files}}, indent=2))
