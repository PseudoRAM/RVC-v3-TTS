import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import numpy as np
import soundfile as sf
from pipeline import Pipeline, Request, ROOT
from cli import build_parser


class Defaults(unittest.TestCase):
    def test_cli_and_request_defaults_and_opt_out(self):
        for extra, expected in [([], (4, .75, True)),
                                (['--pitch', '0', '--no-use-index', '--index-rate', '.5'], (0, .5, False))]:
            args = build_parser().parse_args(['Hello', '--voice', 'DavidGoggins'] + extra)
            request = Request(**{name: getattr(args, name) for name in Request.__dataclass_fields__})
            request.validate()
            self.assertEqual((request.pitch, request.index_rate, request.use_index), expected)

    def test_index_rate_validation(self):
        for rate in (-.1, 1.1, float('nan'), float('inf')):
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                Request('Hello', voice='DavidGoggins', index_rate=rate).validate()

    def test_settings_reach_worker_and_metrics(self):
        for options in ({}, {'pitch': 0, 'use_index': False, 'index_rate': .2}):
            with self.subTest(options=options), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                converted = root / 'worker' / 'output.wav'
                converted.parent.mkdir()
                signal = (.2 * np.sin(np.arange(2400) * .1)).astype(np.float32)
                sf.write(converted, signal, 24000)
                runner = Pipeline.__new__(Pipeline)
                runner.lock = threading.Lock()
                runner.tts = SimpleNamespace(create=Mock(return_value=(signal, 24000)))
                runner.worker = SimpleNamespace(stdin=io.StringIO())
                runner._response = Mock(return_value={'path': str(converted)})
                request = Request('Hello world', voice='DavidGoggins', source_voice='am_michael', **options)
                _, metrics = runner.run(request, root / 'result')
                payload = json.loads(runner.worker.stdin.getvalue())
                self.assertEqual(payload['pitch_change'], request.pitch)
                self.assertEqual(payload['use_index'], request.use_index)
                self.assertEqual(payload['index_rate'], request.index_rate)
                self.assertEqual(metrics['request']['index_rate'], request.index_rate)

    def test_cog_entrypoint_forwards_default_and_explicit_controls(self):
        cog = SimpleNamespace(BaseRunner=object, BaseModel=object, Path=Path,
                              Input=lambda default=None, **kwargs: default)
        spec = importlib.util.spec_from_file_location('tts_predict_test', ROOT / 'predict.py')
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'cog': cog}):
            spec.loader.exec_module(module)
        module.Output = lambda **kwargs: kwargs
        predictor = module.Predictor()
        predictor.pipeline = SimpleNamespace(run=Mock(return_value=(Path('output'), {})))
        for options, expected in [({}, (4, .75, True)),
                                  ({'pitch': 0, 'index_rate': .5, 'use_index': False}, (0, .5, False))]:
            predictor.run('Hello', voice='VCTK226', **options)
            request = predictor.pipeline.run.call_args.args[0]
            self.assertEqual((request.pitch, request.index_rate, request.use_index), expected)
