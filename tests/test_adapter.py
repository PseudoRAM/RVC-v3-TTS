import unittest
from types import SimpleNamespace
import numpy as np
from kokoro_adapter import CompatibleKokoro

class Adapter(unittest.TestCase):
    def test_fractional_speed_reaches_graph(self):
        captured = {}
        model = CompatibleKokoro.__new__(CompatibleKokoro)
        model.tokenizer = SimpleNamespace(tokenize=lambda _: [1, 2])
        def run(_, inputs):
            captured.update(inputs)
            return [np.ones(100, dtype=np.float32)]
        model.sess = SimpleNamespace(get_inputs=lambda: [
            SimpleNamespace(name='input_ids', type='tensor(int64)'),
            SimpleNamespace(name='speed', type='tensor(float)')], run=run)
        audio, sr = model._create_audio('test', np.zeros((10,256)), .85)
        self.assertAlmostEqual(float(captured['speed'][0]), .85, places=5)
        self.assertEqual(captured['speed'].dtype, np.float32)
        self.assertEqual(captured['input_ids'].tolist(), [[0,1,2,0]])
        self.assertEqual(sr, 24000)

    def test_overlong_segment_rejected(self):
        model = CompatibleKokoro.__new__(CompatibleKokoro)
        model.tokenizer = SimpleNamespace(tokenize=lambda _: [1]*511)
        with self.assertRaises(ValueError):
            model._create_audio('test', None, 1)
