"""Offline Kokoro -> persistent RVC worker, with saved A/B audio and timings."""
from dataclasses import dataclass, asdict
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'vendor/rvc-v3/src'))
from defaults import PITCH_CHANGE, INDEX_RATE, USE_INDEX

@dataclass
class Request:
    text: str
    voice: str = ''
    source_voice: str = 'af_heart'
    speed: float = 1.0
    pitch: int = PITCH_CHANGE
    pause_ms: int = 180
    use_index: bool = USE_INDEX
    index_rate: float = INDEX_RATE

    def validate(self):
        if not isinstance(self.text, str) or not self.text.strip() or len(self.text) > 3000:
            raise ValueError('Text must contain 1–3000 characters')
        if not math.isfinite(self.speed) or not 0.5 <= self.speed <= 2:
            raise ValueError('Speed must be 0.5–2.0')
        if not -24 <= self.pitch <= 24 or not 0 <= self.pause_ms <= 2000:
            raise ValueError('Pitch must be -24–24; pause must be 0–2000 ms')
        if not math.isfinite(self.index_rate) or not 0 <= self.index_rate <= 1:
            raise ValueError('Index rate must be 0–1')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', self.voice):
            raise ValueError('Invalid RVC voice name')
        if not re.fullmatch(r'[ab][fm]_[a-z]+', self.source_voice):
            raise ValueError('Choose an English Kokoro source voice')
        if self.voice in ('AisoHowatto', 'AisoSittori') and (self.pitch != 0 or self.use_index):
            raise ValueError('AISO checkpoints have no pitch guidance and use no retrieval index; set pitch=0 and use_index=False')

class Pipeline:
    def __init__(self, rvc_python=None, threads=4):
        self.lock = threading.Lock()
        self.worker = None
        started = time.perf_counter()
        import onnxruntime as ort
        from kokoro_adapter import CompatibleKokoro
        options = ort.SessionOptions()
        options.intra_op_num_threads = threads
        options.inter_op_num_threads = 1
        session = ort.InferenceSession(str(ROOT/'models/kokoro-v1.0.onnx'), sess_options=options,
                                       providers=['CPUExecutionProvider'])
        self.tts = CompatibleKokoro.from_session(session, str(ROOT/'models/voices-v1.0.bin'))
        self.tts_setup_seconds = time.perf_counter() - started
        interpreter = rvc_python or os.environ.get('RVC_PYTHON', sys.executable)
        self.worker = subprocess.Popen([interpreter, '-u', str(ROOT/'rvc_worker.py')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8',
            cwd=ROOT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE':'1'})
        try:
            ready = self._response()
            if not ready.get('ready'):
                raise RuntimeError(f'RVC startup failed: {ready}')
            self.rvc_setup_seconds = ready['setup_seconds']
        except Exception:
            self.close()
            raise
        self.setup_seconds = time.perf_counter() - started

    def _response(self):
        line = self.worker.stdout.readline()
        if not line:
            raise RuntimeError('RVC worker exited; see stderr for model/dependency errors')
        response = json.loads(line)
        if 'error' in response:
            raise RuntimeError(response['error'])
        return response

    def run(self, request, output_dir=None):
        request.validate()
        import numpy as np
        import soundfile as sf
        with self.lock:
            started = time.perf_counter()
            folder = Path(output_dir or ROOT/'demos'/uuid.uuid4().hex).resolve()
            folder.mkdir(parents=True, exist_ok=False)
            parts = [p.strip() for p in request.text.split('\n') if p.strip()]
            chunks = []
            for part in parts:
                samples, sr = self.tts.create(part, voice=request.source_voice, speed=request.speed,
                    lang='en-gb' if request.source_voice.startswith('b') else 'en-us')
                if chunks:
                    chunks.append(np.zeros(round(sr*request.pause_ms/1000), dtype=np.float32))
                chunks.append(samples)
            source = np.concatenate(chunks)
            if not len(source) or not np.isfinite(source).all():
                raise RuntimeError('TTS returned invalid audio')
            source_path = folder/'source.wav'
            sf.write(source_path, source, sr, subtype='PCM_16')
            tts_done = time.perf_counter()
            self.worker.stdin.write(json.dumps({'input_audio': str(source_path), 'rvc_model': request.voice,
                'pitch_change': request.pitch, 'use_index': request.use_index,
                'index_rate': request.index_rate})+'\n')
            self.worker.stdin.flush()
            converted = Path(self._response()['path'])
            try:
                shutil.copy2(converted, folder/'speech.wav')
            finally:
                # Only remove the exact output file created by our worker.
                converted.unlink()
                converted.parent.rmdir()
            finished = time.perf_counter()
            output, output_sr = sf.read(folder/'speech.wav')
            duration = len(output)/output_sr
            metrics = {'request': asdict(request), 'tts_seconds': tts_done-started,
                'rvc_and_copy_seconds': finished-tts_done, 'total_seconds': finished-started,
                'source_duration_seconds': len(source)/sr, 'duration_seconds': duration,
                'rtf': (finished-started)/duration, 'sample_rate': output_sr,
                'finite': bool(np.isfinite(output).all()), 'rms': float(np.sqrt(np.mean(output**2))),
                'peak': float(np.max(np.abs(output))), 'clipped_samples': int((np.abs(output)>=1).sum())}
            if not metrics['finite'] or metrics['rms'] < 1e-5:
                raise RuntimeError('RVC returned invalid or silent audio')
            (folder/'metrics.json').write_text(json.dumps(metrics, indent=2), encoding='utf-8')
            return folder, metrics

    def close(self):
        if self.worker:
            self.worker.stdin.close()
            try:
                self.worker.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.worker.terminate()
                self.worker.wait(timeout=10)
            self.worker.stdout.close()
            self.worker = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
