# Deployment verification

Date: 16 September 2026 (Australia/Sydney).

## Local release checks

Source commit: `a41501c`. Cog CLI: `0.22.0`. Linux GPU container with Python 3.10,
an isolated RVC environment, PyTorch `2.0.1+cu118`, and CUDA available on an NVIDIA RTX 4090.

- All 10 unit and release-packaging tests passed.
- The container contained only VCTK226 and VCTK231 target folders, retained license notices,
  and excluded `.local-private` and `.env`.
- Both targets produced finite, non-silent, mono 40 kHz PCM16 WAVs with zero clipped samples.
- A full Cog API request succeeded and returned all three artifacts: converted speech,
  generated source speech, and JSON metrics. Returned data was decoded after the request
  and both WAV files were readable.

The two-voice test used the text “Hello! This is a test of our text to speech voice conversion.”,
speed 1.05, pitch 0, and retrieval enabled. A single persistent pipeline handled both requests.

| Target | Kokoro source | Output duration | Processing time |
| --- | --- | ---: | ---: |
| VCTK226 | am_michael | 3.72 s | 2.33 s |
| VCTK231 | af_heart | 3.50 s | 1.45 s |

Pipeline setup took 4.30 seconds. These are single local container smoke tests, not a warm
benchmark or T4 cost estimate. The separate Cog API request returned 4.52 seconds of converted
audio in 2.10 seconds of prediction time, excluding setup.

## Reproduce the checks

Acquire assets with the repository download scripts, then:

```sh
python -m unittest discover -s tests -v
cog build
docker run --rm --gpus all --entrypoint python r8.im/pseudoram/tts-rvc scripts/container_smoke.py
cog run r8.im/pseudoram/tts-rvc -i text="Hello! This began as text." -i voice=VCTK231 -i use_index=true -o result.json
```

The Cog CLI JSON response embeds returned files as data URLs; Replicate serves downloadable
file URLs. Audio checks establish basic signal integrity, not a perceptual-quality score.
