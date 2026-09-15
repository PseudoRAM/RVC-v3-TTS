# RVC v3 TTS

[Public source](https://github.com/PseudoRAM/RVC-v3-TTS) | [Private Replicate model: TTS RVC](https://replicate.com/pseudoram/tts-rvc)

The Replicate model is private. See its Versions tab for published releases.

**Text -> Kokoro speech -> RVC voice conversion -> downloadable WAV.**
This project takes text. It has no recorded-audio input examples or upload workflow.
The generated TTS source is saved beside the converted output for comparison.
`v3` names the optimized service; checkpoints remain RVC v1/v2.

## Try it locally

Complete the fresh setup below first.

The installed example targets are **VCTK226 (male)** and **VCTK231 (female)**. Both are English-trained RVC v2 voices from Nekochu's VCTK collection.

```powershell
$env:RVC_PYTHON=(Resolve-Path '.venv-rvc/Scripts/python.exe').Path
.venv-tts/Scripts/python.exe cli.py "Hello! This voice began as text." --voice VCTK226 --source-voice am_michael --use-index
.venv-tts/Scripts/python.exe cli.py "Welcome back. Let us take a closer look." --voice VCTK231 --source-voice af_heart --use-index --speed 0.9
.venv-tts/Scripts/python.exe scripts/prepare_examples.py
```

Each CLI result identifies a folder with `source.wav` (generated Kokoro speech),
`speech.wav` (RVC output), and `metrics.json`. Existing output folders are never overwritten.
[Listen to the text-to-RVC examples](examples/README.md).

## Controls

- `--source-voice af_heart`: English female Kokoro source, suitable for VCTK231. Use `am_michael` for VCTK226.
- `--speed 0.5..2`: native TTS pace. 1 is normal; lower is slower.
- Punctuation guides delivery; newlines split speech, with `--pause-ms 0..2000` between segments.
- Both VCTK models support `--pitch -24..24` and `--use-index`. Start at zero shift with a matching source; the examples enable retrieval at rate 0.5.

Kokoro does not offer semantic emotion or laughter tags. Delivery depends on source voice,
punctuation and pace. RVC changes the source timbre; it does not add missing acted emotion.

## Fresh setup

Use isolated TTS and RVC environments; their NumPy/Torch requirements differ.
Install FFmpeg and libsndfile, plus espeak-ng on Linux.

```sh
python3.11 -m venv .venv-tts
.venv-tts/bin/python -m pip install -r requirements.txt
.venv-tts/bin/python scripts/download_tts.py
.venv-tts/bin/python scripts/download_rvc.py
.venv-tts/bin/python scripts/download_voices.py
python3.10 -m venv .venv-rvc
.venv-rvc/bin/python -m pip install pip==24.0 setuptools==69.5.1 wheel==0.43.0
.venv-rvc/bin/python -m pip install -r requirements-rvc.txt fairseq==0.12.2
export RVC_PYTHON="$PWD/.venv-rvc/bin/python"
.venv-tts/bin/python cli.py "Hello, welcome back." --voice VCTK226 --source-voice am_michael --use-index
```

On Windows use `Scripts/python.exe` in place of `bin/python`. The tested local TTS environment
is Python 3.11.9; RVC uses the existing Python 3.9.13 interpreter without modifying its packages.
The source RVC project is read-only. Its two VCTK checkpoints were copied and verified by SHA256.
The Linux GPU Cog container is validated; a separate manual Linux setup is not yet tested. The Windows TTS snapshot is
`requirements-tts-windows.lock`, not a cross-platform lock.

## Performance and tests

One persistent CPU ONNX session uses four threads; a separate persistent GPU RVC worker
loads HuBERT/RMVPE once and caches target voices. A lock serializes requests. There is no
response-audio cache or streaming endpoint. `RVC_VOICE_CACHE_SIZE` controls the target cache
(default 1). WAV files cross the process boundary; JSON lines carry control messages.

```sh
python -m unittest discover -s tests -v
python benchmark.py --runs 4
```

[Examples and measured timings](examples/README.md) report first requests, warm medians,
duration and real-time factor (processing seconds / audio seconds). TTS timings include
source-file writing; RVC timings include output copying. Setup is separate. No cloud
queueing, network transfer or machine-cold benchmark is implied.

## Replicate / release packaging

`predict.py` takes text and returns converted speech, its generated TTS source and metrics.
`cog.yaml` keeps a separate legacy RVC environment. Use Cog 0.22 or later and download weights before building.
`.dockerignore` allows the shared models and the two named VCTK checkpoints/indexes and their notices;
other target directories remain excluded.

```sh
cog run -i text="Hello, this began as text." -i voice=VCTK231
cog push r8.im/pseudoram/tts-rvc
python scripts/package_source.py
python scripts/package_source.py --include-examples
```

The source ZIP excludes weights and audio. The with-examples ZIP adds exactly two generated
TTS source / RVC output pairs, with settings, hashes and credits. Neither includes human
input recordings. Both exclude historical private assets and environments.

The Cog 0.22 GPU image passes both English voice smoke tests and a full Cog request returning
speech, source and metrics. Local container outputs were finite, non-silent 40 kHz WAVs with no clipped samples.
Replicate T4 execution is tracked separately from these local tests.
Local 4090 timings are not T4 costs. See [research and cost assumptions](RESEARCH.md).

## Permissions

Models: **Nekochu**, [RVC-VCTK_Voice-sample](https://huggingface.co/Nekochu/RVC-VCTK_Voice-sample),
Apache 2.0 as declared in the model card. Training corpus: Yamagishi, Veaux and MacDonald,
*CSTR VCTK Corpus v0.92* (2019), University of Edinburgh, CC BY 4.0.
[Terms and attribution](docs/ASSET_PERMISSIONS.md) accompany the generated examples;
[upstream notices](examples/licenses/) are included in the release. Model provenance does
not independently verify individual speaker releases or imply endorsement.
