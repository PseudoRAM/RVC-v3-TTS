# English text-to-RVC assets and permissions

## Target checkpoints

Creator: **Nekochu**. [RVC-VCTK_Voice-sample](https://huggingface.co/Nekochu/RVC-VCTK_Voice-sample)
declares Apache 2.0 and identifies the VCTK training corpus. Pinned revision:
`005c2f948ee9dafd7e3aa7f261b4c3a24beebeef`.

- Male p226: `VCTK226/Mp226rmvpe.pth`, matching v2 retrieval index.
- Female p231: `VCTK231/Fp231rmvpe.pth`, matching v2 retrieval index.
- Both are English-trained RVC v2, 40 kHz, with pitch guidance. These are RVC models,
  not the Beatrice architecture also present in the repository.
- Checkpoints and indexes are unchanged; the downloader pins SHA256 for all four files.
- Retain [Apache 2.0](../examples/licenses/APACHE-2.0.txt), the
  [model card](../examples/licenses/VCTK-model-card.md) and creator credit with redistribution.

Training data attribution: Junichi Yamagishi, Christophe Veaux and Kirsten MacDonald (2019),
*CSTR VCTK Corpus: English Multi-speaker Corpus for CSTR Voice Cloning Toolkit, version 0.92*,
University of Edinburgh CSTR. [Original release](https://doi.org/10.7488/ds/2645),
[CC BY 4.0](../examples/licenses/VCTK-CC-BY-4.0.txt).
These are the published model/data terms and provenance, not independently verified individual
speaker releases. Do not identify anonymous speakers or imply endorsement.

## Text-generated examples

All examples start with newly written text -> Kokoro -> VCTK RVC. Male source: `am_michael`;
female source: `af_heart`. No recorded human input clips are included or used.
The `source.wav` files are synthetic TTS intermediates; `speech.wav` files have RVC applied.
Retain synthetic labels, model credits and change descriptions when sharing.
The model licenses do not automatically relicense generated outputs. This project adds no
additional restrictions to generated example use; example text can be reused under its MIT license.

Kokoro weights/source voices: [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M),
Apache-2.0. ONNX wrapper: MIT, `vendor/KOKORO-ONNX-LICENSE`.
Application/RVC code: MIT with original notices retained. Shared HuBERT/RMVPE weights remain
separate downloads; their upstream terms still apply to model-bearing containers.

## Packaging

Source and example ZIPs omit weights/indexes. The example ZIP contains exactly two generated
source/conversion pairs. Docker allows the two VCTK targets and indexes, their license documents,
and shared weights. Other targets and `.local-private/` remain excluded. AISO is no longer the
release example collection. No cloud deployment or publication has been performed.
