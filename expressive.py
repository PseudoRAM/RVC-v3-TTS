"""Client for the optional expressive TTS worker; keeps legacy Torch isolated."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


class ExpressiveSource:
    def __init__(self, interpreter=None):
        from emotion import MODEL_FOLDER
        executable = interpreter or os.environ.get('EXPRESSIVE_PYTHON')
        if not executable:
            executable = ROOT / '.venv-expressive' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        if not Path(executable).is_file() and not interpreter and not os.environ.get('EXPRESSIVE_PYTHON') and os.name != 'nt':
            executable = Path('/opt/expressive/bin/python')
        if not Path(executable).is_file() or not (ROOT / 'models' / MODEL_FOLDER / 'config.json').is_file():
            raise RuntimeError('Expressive TTS is not installed. Follow docs/EMOTION.md to install its environment and models.')
        self.worker = subprocess.Popen([str(executable), '-u', str(ROOT / 'expressive_worker.py')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding='utf-8', cwd=ROOT,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'HF_HUB_OFFLINE': '1'})
        try:
            ready = self.response()
            if not ready.get('ready'):
                raise RuntimeError('Expressive worker did not become ready')
            self.setup_seconds = ready['setup_seconds']
        except Exception:
            self.close()
            raise

    def response(self):
        line = self.worker.stdout.readline()
        if not line:
            raise RuntimeError('Expressive worker exited; see stderr for the cause')
        response = json.loads(line)
        if 'error' in response:
            raise RuntimeError(response['error'])
        return response

    def create(self, text, speaker, instruct, seed, output):
        self.worker.stdin.write(json.dumps(dict(text=text, speaker=speaker, instruct=instruct,
                                                seed=seed, output=str(output))) + '\n')
        self.worker.stdin.flush()
        return self.response()

    def close(self):
        try:
            self.worker.stdin.close()
        except BrokenPipeError:
            pass
        try:
            self.worker.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.worker.terminate()
            self.worker.wait(timeout=10)
        self.worker.stdout.close()
