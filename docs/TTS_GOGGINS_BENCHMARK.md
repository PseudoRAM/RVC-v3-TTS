# David Goggins text-to-speech generation test

The local pipeline generates Kokoro speech from text and converts it with the
separately provisioned David Goggins RVC v2 checkpoint. The source and converted
audio are retained together for listening review. These are AI-generated demos,
not authentic David Goggins recordings.

The benchmark uses the shared defaults: pitch +4, retrieval enabled at 0.75,
RMVPE, protect 0.33 and RMS mix 0.25. Kokoro speed is 1.0 with 180 ms newline pauses.
It covers short, medium and long passages using am_michael, and the same medium
passage using am_adam. Each case runs three times in one persistent pipeline.

```powershell
$env:RVC_PYTHON = 'path/to/rvc/python.exe'
& .venv-tts/Scripts/python.exe scripts/benchmark_goggins.py --runs 3
```

Provision `vendor/rvc-v3/rvc_models/DavidGoggins` with the checkpoint and matching
index first. Model source: https://huggingface.co/Kaknes/DavidGoggins at revision
`c7010705f53adccea12bdf97d506f1d19b923da0`. Weights and generated demo audio are
excluded from source commits and container releases. The hosted Cog voice list
remains VCTK226/VCTK231; this benchmark uses the local pipeline/CLI.

Metrics are saved under the newly created `demos/goggins-*/results.json`.
Setup is separate; first-request time is not machine-cold latency. Warm medians
exclude the first request of each case. TTS timing includes source WAV writing;
RVC timing includes worker communication and output copying. These measurements
do not include cloud queueing or network transfer and do not establish speaker
similarity; listen to the generated source/output pairs.

## Measured results — 16 September 2026

Windows, RTX 4090, Torch 2.0.1+cu118 in Python 3.9.13; Kokoro ONNX Runtime 1.30.0 on CPU (4 threads) in Python 3.11.9.

Pipeline setup: **5.079 s**; TTS setup 1.201 s; RVC worker setup including its imports 3.828 s. Setup plus the first request: 9.043 s.

| Clip / source | Audio (s) | First (s) | Warm total (s) | Warm TTS (s) | Warm RVC + copy (s) |
| --- | ---: | ---: | ---: | ---: | ---: |
| Short / Michael | 6.600 | 3.965 | 2.013 | 1.290 | 0.724 |
| Medium / Michael | 17.200 | 4.310 | 3.823 | 3.216 | 0.607 |
| Long / Michael | 37.200 | 7.641 | 7.654 | 6.833 | 0.820 |
| Medium / Adam | 14.620 | 3.331 | 3.272 | 2.677 | 0.594 |

All 12 conversions produced finite, non-silent 40 kHz WAVs with zero clipped samples. The saved listening pair is the first generation for each case. Warm numbers are medians of only two repeats, not production latency distributions. RVC pitch +4 does not automatically adapt to each Kokoro source range. Similarity is unscored pending listening review.

[Full metrics and input texts](benchmarks/goggins-20260916.json). [Private listening page](https://rvc-goggins-audio-demo.orangeyellow.chatgpt.site/tts-goggins.html).
