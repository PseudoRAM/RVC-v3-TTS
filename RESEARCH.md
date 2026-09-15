# Engine choice — 15 September 2026

Primary sources checked for this project:

| Engine | License / capability | Decision |
|---|---|---|
| [Kokoro 82M](https://huggingface.co/hexgrad/Kokoro-82M) | Model card lists Apache-2.0 weights; fixed source voices and speed | Default: small local model with predictable male/female sources for RVC |
| [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) | MIT inference wrapper, local ONNX inference | CPU execution separates modern TTS dependencies from legacy GPU RVC |
| [Chatterbox Turbo](https://github.com/resemble-ai/chatterbox) | MIT; 350M English model, paralinguistic tags and voice cloning | Useful future expressive alternative, but a larger second stack and extra cloning stage; not installed or benchmarked |
| [Pocket TTS](https://huggingface.co/kyutai/pocket-tts) | Model card lists CC-BY-4.0, gated access terms and separate source-voice licenses; CPU inference and reference cloning | Promising separate comparison, but upstream latency claims do not establish RVC pipeline latency; not installed or benchmarked |

Kokoro was chosen for cost-oriented, fixed-source TTS before an existing RVC clone. No external TTS
service is called per request. It has limited semantic emotion control. If laughter, sighs or acted
emotion are essential, measure Chatterbox Turbo next rather than pretending that Kokoro understands tags.
No cross-engine quality ranking or performance benchmark was conducted here.

The [Kokoro source](https://github.com/hexgrad/kokoro) documents voice and speed inputs.
The [ONNX example](https://github.com/thewh1teagle/kokoro-onnx/blob/main/examples/save.py)
identifies the model-files-v1.1 release used here. The model is FP32 (~325.5 MB); voices are ~28.2 MB.
`models/manifest.json` records the downloaded bytes' SHA256. The download script pins the expected
digests after this acquisition; verify against upstream releases independently for supply-chain assurance.

The pinned 0.4.9 wrapper has a graph compatibility bug: for `input_ids` exports it builds integer
speed tensors, while this graph requires float. `kokoro_adapter.py` explicitly sends float32 speed,
preserving fractional pace, and rejects incompatible graphs. Vendored dependencies are not modified.

## Cost interpretation

[Replicate pricing](https://replicate.com/pricing), checked on the date above, lists T4 at
**$0.000225 per second ($0.81/hour)**. A hypothetical measured T4 processing time of 1, 2 or 5 seconds
would correspond to $0.000225, $0.00045 or $0.001125 of active compute per request respectively.
These are scenarios, not measured costs for this project. Private instances also incur setup and idle
time; one continuously running T4 is approximately $19.44/day before other charges.

For a private worker, estimate `(setup + processing + idle seconds) × hardware rate / request count`.
The local CPU+4090 timings must not be multiplied by the T4 rate and presented as a T4 quote.
TTS now contributes to end-to-end time; the parent project's 0.27-second RVC-only figure is not this
pipeline's latency. Cloud boot, transfer, concurrency, long-text memory, and cost have not been measured.
