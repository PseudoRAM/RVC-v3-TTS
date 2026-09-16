# Deployment verification

Date: 16 September 2026 (Australia/Sydney).

## Published release

The [cloud build and push](https://github.com/PseudoRAM/RVC-v3-TTS/actions/runs/35079219375)
succeeded on 16 September 2026 at 10:40 UTC from source commit
`de273d580be61b213d352beb80f527d9716e02ff`. All 17 workflow tests passed.

The private [Replicate model](https://replicate.com/pseudoram/tts-rvc) now has version
`463eb1fdd994bc5984c3a08310d584c154982c4397f86d5ed9ba0da6158b7e64`.
The live model is configured for Nvidia T4 and exposes pitch +4, retrieval enabled,
index rate 0.75, and the expressive engine controls.

Hosted inference verification is in progress. T4 output integrity, memory use,
and timings are not yet verified.

## Local release checks

### Current defaults and expressive engine

The current release candidate was built from the working source snapshot, including
the new defaults and Qwen emotion controls. It is newer than the commit recorded in
the original checks below. The local image config digest is
`sha256:a564c57d92a16ebabcd4281339a1ac9948b8e51449e1bdac7413386b378697c2`.

- All 17 unit and packaging tests passed.
- Both approved English targets passed GPU container tests using pitch **+4**,
  retrieval **enabled**, and index rate **0.75**.
- A Cog API request that omitted those controls returned metrics confirming all
  three defaults. It produced 3.14 seconds of finite, non-silent 40 kHz audio with
  zero clipped samples in 1.84 seconds of local processing, excluding setup.
- An expressive Qwen request also passed. A separate forced-float16 run checked
  the precision path used when native bfloat16 is unavailable: 4.06 seconds of
  converted audio, finite and non-silent with zero clipped samples. Processing
  took 15.61 seconds, including 9.09 seconds of expressive model setup.
- These checks ran locally on the RTX 4090. Forced float16 checks precision
  compatibility; it does not establish T4 latency or memory use.
- The final code layer explicitly excludes emulated bfloat16 support from the
  precision check (`including_emulation=False`). A simulated T4 capability check
  selected float16. Both English targets and expressive synthesis passed again
  in that final image. Their audio remained finite, non-silent and unclipped.

Publication succeeded as recorded above; hosted T4 inference remains under verification.

### Original Kokoro release checks

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

## Hosted output compatibility follow-up

Source `def3161` published as version
`8d0ef4544cf7f03018a1ae8fc4dcdcf79b6e6575986d53ecfcef1a8fba72cb6d`.
A male text-only prediction succeeded in 7.4 seconds of processing (3m56s
including cold start). Saving to Examples succeeded, but audio remained
unavailable in its preview: output files were embedded data URLs.

The next build pins Cog 0.16.12 and uses BasePredictor.predict to restore
the server's per-request output_file_prefix upload handling, absent from
Cog 0.22's request schema. Hosted verification of this compatibility change
is pending. All 18 unit and packaging tests pass.
