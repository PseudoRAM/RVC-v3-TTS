# Vendored RVC source

Upstream: https://github.com/PseudoRAM/RVC-v3

Synchronized locally from commit `da3aba6343f20e48322285448763cf6e513501a9`
on 16 September 2026. Every Python source file in `src/` matches upstream,
allowing Windows newline normalization. This commit may not be pushed yet.

The service uses shared defaults from `src/defaults.py`: pitch +4,
retrieval enabled when available, and index rate 0.75. TTS Request, CLI,
and Cog inputs import these defaults and forward explicit overrides.
Model files are separate local assets and are not part of this source sync.
