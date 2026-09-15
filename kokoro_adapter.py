"""Kokoro 0.4.9 adapter for the release graph's float speed input."""
import numpy as np
from kokoro_onnx import Kokoro

class CompatibleKokoro(Kokoro):
    def _create_audio(self, phonemes, voice, speed):
        tokens = self.tokenizer.tokenize(phonemes)
        if not tokens or len(tokens) > 510:
            raise ValueError('Phoneme segment must contain 1–510 tokens')
        names = {value.name: value.type for value in self.sess.get_inputs()}
        token_name = 'input_ids' if 'input_ids' in names else 'tokens'
        if names['speed'] != 'tensor(float)':
            raise ValueError('This pipeline requires a model with continuous float speed control')
        inputs = {token_name: np.asarray([[0, *tokens, 0]], dtype=np.int64),
                  'style': np.asarray(voice[len(tokens)], dtype=np.float32),
                  'speed': np.asarray([speed], dtype=np.float32)}
        return self.sess.run(None, inputs)[0], 24000
