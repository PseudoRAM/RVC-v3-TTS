# Hosted text-to-speech examples

Generated on NVIDIA T4 through Replicate, 16 September 2026 UTC.
All input speech is synthesized from the text recorded in each metrics file.
`source.wav` is TTS output; `speech.wav` is the RVC conversion.
See [model permissions and attribution](../../docs/ASSET_PERMISSIONS.md).
VCTK226/VCTK231: Nekochu models (Apache 2.0), trained on CSTR VCTK v0.92
(CC BY 4.0; Junichi Yamagishi, Christophe Veaux and Kirsten MacDonald, 2019).
Kokoro and Qwen weights: Apache 2.0. These examples imply no speaker endorsement.

All six WAVs passed finite/non-silent checks with zero clipped samples.
Converted output is mono 40 kHz. Settings: pitch +4, retrieval enabled, rate 0.75.

| Example | Engine | Audio | Processing |
| --- | --- | ---: | ---: |
| Male VCTK226 | Kokoro am_michael | 6.48 s | 6.89 s |
| Female VCTK231 | Kokoro af_heart | 5.40 s | 5.66 s |
| Excited VCTK226 | Qwen Ryan | 4.22 s | 28.52 s |

Qwen processing includes 10.90 seconds of lazy model setup. Container cold
boot is excluded and can take several minutes. These are smoke tests, not
quality scores or performance guarantees. Prediction links are in manifest.json.
