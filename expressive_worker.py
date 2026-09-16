"""Isolated, persistent Qwen process. Only JSON messages use stdout."""
import contextlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parent


def main():
    protocol = sys.stdout
    started = time.perf_counter()
    with contextlib.redirect_stdout(sys.stderr):
        import torch
        import numpy as np
        import soundfile as sf
        from qwen_tts import Qwen3TTSModel
        from emotion import MODEL_FOLDER
        if not torch.cuda.is_available():
            raise RuntimeError('Expressive TTS requires a CUDA GPU in its isolated environment')
        torch.set_num_threads(4)
        model = Qwen3TTSModel.from_pretrained(
            str(ROOT / 'models' / MODEL_FOLDER), device_map='cuda:0',
            dtype=torch.bfloat16 if torch.cuda.is_bf16_supported(including_emulation=False) else torch.float16,
            attn_implementation='sdpa', local_files_only=True)
    print(json.dumps({'ready': True, 'setup_seconds': time.perf_counter() - started}), file=protocol, flush=True)
    for line in sys.stdin:
        try:
            request = json.loads(line)
            with contextlib.redirect_stdout(sys.stderr):
                torch.manual_seed(request['seed'])
                torch.cuda.manual_seed_all(request['seed'])
                waves, sr = model.generate_custom_voice(
                    text=request['text'], language='English', speaker=request['speaker'],
                    instruct=request['instruct'], max_new_tokens=4096)
                if not len(waves[0]) or not np.isfinite(waves[0]).all():
                    raise RuntimeError('Expressive TTS returned invalid samples')
                sf.write(request['output'], waves[0], sr, subtype='PCM_16')
            print(json.dumps({'path': request['output'], 'sample_rate': sr}), file=protocol, flush=True)
        except Exception as error:
            print(json.dumps({'error': str(error)}), file=protocol, flush=True)


if __name__ == '__main__':
    main()
