import io
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import numpy as np
import soundfile as sf
from pipeline import Pipeline, Request
from emotion import delivery_instruction
from cli import build_parser


class EmotionTests(unittest.TestCase):
    def test_auto_routing_and_no_silent_ignored_emotion(self):
        self.assertEqual(Request('Hello', voice='Test').resolved_engine, 'kokoro')
        for options in ({'emotion': 'yelling'}, {'instruct': 'Sound nervous.'}, {'engine': 'qwen'}):
            request = Request('Hello', voice='Test', **options)
            request.validate()
            self.assertEqual(request.resolved_engine, 'qwen')
        for options in ({'engine': 'kokoro', 'emotion': 'angry'}, {'emotion': 'invented'},
                        {'emotion': 'yelling', 'speed': 1.2}, {'intensity': float('nan')},
                        {'intensity': 1.1}, {'seed': -1}, {'instruct': 'a' * 1001}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                Request('Hello', voice='Test', **options).validate()

    def test_cli_routes_yelling_and_builds_stronger_instruction(self):
        args = build_parser().parse_args(['Hello', '--voice', 'DavidGoggins', '--emotion', 'yelling',
                                          '--intensity', '1', '--instruct', 'Rough and urgent.'])
        request = Request(**{name: getattr(args, name) for name in Request.__dataclass_fields__})
        request.validate()
        self.assertEqual(request.resolved_engine, 'qwen')
        self.assertNotEqual(delivery_instruction('yelling', .3), delivery_instruction('yelling', 1))
        self.assertIn('Rough and urgent.', delivery_instruction(request.emotion, request.intensity, request.instruct))

    def test_expression_is_generated_before_rvc_and_saved_in_metrics(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            converted = root / 'worker' / 'output.wav'
            converted.parent.mkdir()
            signal = (.2 * np.sin(np.arange(2400) * .1)).astype(np.float32)
            sf.write(converted, signal, 24000)
            runner = Pipeline.__new__(Pipeline)
            runner.lock = threading.Lock()
            runner.tts = SimpleNamespace(create=Mock(side_effect=AssertionError('Kokoro must not handle emotion')))
            runner.expressive = None
            runner.worker = SimpleNamespace(stdin=io.StringIO())
            runner._response = Mock(return_value={'path': str(converted)})
            source = Mock(setup_seconds=.5)
            def create(text, speaker, instruct, seed, output):
                sf.write(output, signal, 24000)
            source.create.side_effect = create
            request = Request('Push forward!', voice='DavidGoggins', emotion='yelling', intensity=1)
            with patch('expressive.ExpressiveSource', return_value=source) as factory:
                folder, metrics = runner.run(request, root / 'result')
            factory.assert_called_once()
            self.assertEqual(source.create.call_args.args[1], 'Ryan')
            self.assertIn('Yell at the top', source.create.call_args.args[2])
            self.assertEqual(metrics['tts_engine'], 'qwen')
            self.assertEqual(metrics['expressive_setup_seconds'], .5)
            self.assertEqual(json.loads(runner.worker.stdin.getvalue())['input_audio'], str(folder / 'source.wav'))
            self.assertTrue((folder / 'source.wav').is_file())
            self.assertFalse((folder / '_expressive_chunk.wav').exists())


if __name__ == '__main__':
    unittest.main()
