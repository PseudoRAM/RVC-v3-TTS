"""Cog entry point. Worker state survives warm predictions."""
from cog import BaseRunner, BaseModel, Input, Path
from pipeline import Pipeline, Request, PITCH_CHANGE, INDEX_RATE, USE_INDEX

class Output(BaseModel):
    speech: Path
    source: Path
    metrics: Path

class Predictor(BaseRunner):
    def setup(self):
        self.pipeline = Pipeline(rvc_python='/opt/rvc/bin/python')

    def run(self, text: str = Input(description='English text, 1–3000 characters. Newlines add pauses.'),
                voice: str = Input(description='English RVC target: VCTK226 (male) or VCTK231 (female).', choices=['VCTK226', 'VCTK231']),
                source_voice: str = Input(default='af_heart', description='English Kokoro source voice. Use am_michael for VCTK226 or af_heart for VCTK231.'),
                speed: float = Input(default=1.0, ge=.5, le=2.0, description='TTS speed: 1 is normal; lower values are slower.'),
                pitch: int = Input(default=PITCH_CHANGE, ge=-24, le=24, description='RVC pitch shift in semitones. Default +4; set 0 to preserve source pitch.'),
                pause_ms: int = Input(default=180, ge=0, le=2000, description='Silence in milliseconds between nonempty lines of text.'),
                use_index: bool = Input(default=USE_INDEX, description='Use the target retrieval index when available; enabled by default.'),
                index_rate: float = Input(default=INDEX_RATE, ge=0, le=1, description='Retrieval blend; default 0.75.')) -> Output:
        folder, _ = self.pipeline.run(Request(text, voice, source_voice, speed, pitch, pause_ms, use_index, index_rate))
        return Output(speech=Path(folder/'speech.wav'), source=Path(folder/'source.wav'),
                      metrics=Path(folder/'metrics.json'))
