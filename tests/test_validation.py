import unittest
from pipeline import Request

class Validation(unittest.TestCase):
    def test_aiso_controls(self):
        Request('Hello', voice='AisoHowatto').validate()
        for options in ({'pitch':3}, {'use_index':True}):
            with self.assertRaises(ValueError):
                Request('Hello', voice='AisoSittori', **options).validate()
    def test_no_implicit_target_voice(self):
        with self.assertRaises(ValueError): Request('Hello').validate()
    def test_empty_and_long_text(self):
        for text in ('', '  ', 'a'*3001):
            with self.assertRaises(ValueError): Request(text).validate()

    def test_nonfinite_and_out_of_range(self):
        for value in (float('nan'), float('inf'), .49, 2.01):
            with self.assertRaises(ValueError): Request('hello', speed=value).validate()

    def test_traversal(self):
        for voice in ('../MyVoice', '/tmp', 'a/b', 'a\\b'):
            with self.assertRaises(ValueError): Request('hello', voice=voice).validate()

    def test_valid_controls(self):
        Request('Hello!\nHow are you?', 'MyFemaleVoice', 'af_heart', 1.1, 3, 500).validate()

if __name__ == '__main__': unittest.main()
