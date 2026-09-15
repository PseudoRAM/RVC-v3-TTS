"""Real model regression: a faster pace must produce shorter source speech."""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import onnxruntime as ort
from kokoro_adapter import CompatibleKokoro
from pipeline import ROOT

options = ort.SessionOptions()
options.intra_op_num_threads = 4
model = CompatibleKokoro.from_session(ort.InferenceSession(str(ROOT/'models/kokoro-v1.0.onnx'),
    sess_options=options, providers=['CPUExecutionProvider']), str(ROOT/'models/voices-v1.0.bin'))
durations = {}
for speed in (.8, 1.2):
    audio, sr = model.create('It is a beautiful day to walk through the quiet forest.',
                             voice='af_heart', speed=speed)
    durations[str(speed)] = len(audio)/sr
assert durations['1.2'] < durations['0.8']*.85, durations
(ROOT/'demos/pace-check.json').write_text(json.dumps(durations, indent=2))
print(durations)
