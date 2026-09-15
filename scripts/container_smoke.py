"""Run both text-to-RVC paths inside the built GPU container before pushing."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import Pipeline, Request, ROOT

voices = ROOT/'vendor/rvc-v3/rvc_models'
assert sorted(p.name for p in voices.iterdir() if p.is_dir()) == ['VCTK226', 'VCTK231']
assert not (ROOT/'.local-private').exists()
assert not (ROOT/'.env').exists()
assert (ROOT/'examples/licenses/APACHE-2.0.txt').is_file()
with Pipeline('/opt/rvc/bin/python') as pipeline:
    print(json.dumps({'setup_seconds':pipeline.setup_seconds}), flush=True)
    for voice, source in [('VCTK226','am_michael'), ('VCTK231','af_heart')]:
        folder, metrics = pipeline.run(Request(
            'Hello! This is a test of our text to speech voice conversion.', voice, source,
            speed=1.05, use_index=True))
        assert metrics['finite'] and metrics['rms'] > 1e-5
        assert metrics['sample_rate'] == 40000
        print(json.dumps({'output':str(folder), **metrics}), flush=True)
