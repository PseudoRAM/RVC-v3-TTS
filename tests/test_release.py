import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class Release(unittest.TestCase):
    def test_archive_allowlist_has_no_private_models(self):
        spec = importlib.util.spec_from_file_location('packager', ROOT/'scripts/package_source.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        files = module.ROOT_FILES + module.EXAMPLE_FILES
        self.assertTrue(all((ROOT/f).is_file() for f in files))
        self.assertFalse(any('.local-private' in f or f.endswith(('.pth','.pt','.onnx','.bin')) for f in files))
        self.assertEqual(len(module.EXAMPLE_FILES), 4)

    def test_container_excludes_unreviewed_assets(self):
        rules = (ROOT/'.dockerignore').read_text().splitlines()
        self.assertIn('.local-private', rules)
        self.assertIn('vendor/rvc-v3/rvc_models/**', rules)
        self.assertFalse(any(line.startswith('!vendor/rvc-v3/rvc_models/') and line.endswith('/**') for line in rules))
