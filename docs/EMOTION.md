# Expressive text to RVC

The source engine is Kokoro for neutral speech or Qwen3-TTS 1.7B CustomVoice for
acted delivery. Auto mode selects Qwen for a non-neutral emotion or a nonempty
delivery instruction. Source speech and converted speech are both returned.

```sh
python cli.py "That is wonderful news!" --voice VCTK226 --emotion happy
python cli.py "We can work through this together." --voice VCTK231 --emotion calm
```

Use speed 1 for Qwen and describe pace in the instruction. The source speakers
are Ryan and Aiden. Intensity changes prompt wording, not audio gain; emotion
strength is approximate and RVC may change it. The conversion defaults are pitch
+4, retrieval enabled, and index rate 0.75.

The expressive model is pinned to revision
`0c0e3051f131929182e2c023b9537f8b1c68adfe`; the cloud release workflow verifies both
safetensors files against the locally tested hashes before building.
Qwen model weights are Apache 2.0. See the
[official model](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice).

The worker chooses float16 on T4 and bfloat16 only on devices with native support.
Local GPU tests pass; hosted T4 inference must be verified after publication.
