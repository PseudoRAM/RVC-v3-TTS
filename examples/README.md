# English text-to-RVC examples

All audio begins as text. Male Kokoro `am_michael` feeds VCTK226; female `af_heart` feeds VCTK231. No recorded input audio is used.

> Hello, and welcome! This speech began as text. Let us take a moment to listen, then try a different voice.

Pace 1.0, pitch 0, RMVPE, retrieval enabled at rate 0.5. Models by Nekochu, trained on English VCTK.

| Target | Generated TTS source | RVC output |
|---|---|---|
| VCTK226 | [Source](audio/vctk226-source.wav) | [Converted speech](audio/vctk226-speech.wav) |
| VCTK231 | [Source](audio/vctk231-source.wav) | [Converted speech](audio/vctk231-speech.wav) |

## Measured locally

Windows, Intel i9-14900K / RTX 4090. Kokoro FP32 on four CPU threads; RVC on GPU. Four real requests per target; warm median uses the last three. No response cache.

Setup **5.050 s**; setup plus first request **7.994 s**. Weights already downloaded, OS caches uncontrolled. These are not cloud cold-start figures.

| Target | First request | Warm median | Duration | Warm RTF |
|---|---:|---:|---:|---:|
| VCTK226 | 2.943 s | 1.770 s | 7.30 s | 0.243 |
| VCTK231 | 1.932 s | 1.555 s | 6.48 s | 0.240 |

All eight outputs are finite, non-silent and free of full-scale clipping. These are execution checks, not a perceptual-quality verdict.

[Full settings, timings and asset hashes](manifest.json) | [Permissions and attribution](../docs/ASSET_PERMISSIONS.md)

## Reproduce

From the TTS environment with RVC_PYTHON set to the compatible RVC interpreter:

```text
python scripts/download_tts.py
python scripts/download_rvc.py
python scripts/download_voices.py
python scripts/prepare_examples.py
```

## Credits

Models: Nekochu, RVC-VCTK_Voice-sample, Apache 2.0; [model card](licenses/VCTK-model-card.md) and [license](licenses/APACHE-2.0.txt). Training data: Yamagishi, Veaux and MacDonald (2019), CSTR VCTK Corpus v0.92, University of Edinburgh; [CC BY 4.0](licenses/VCTK-CC-BY-4.0.txt). TTS: hexgrad Kokoro-82M, Apache 2.0. Outputs are synthetic speech modified by RVC, with no speaker endorsement implied.

The with-examples ZIP includes these four generated WAVs and notices. The source ZIP omits audio. Weights/indexes are separate checksum-verified downloads.