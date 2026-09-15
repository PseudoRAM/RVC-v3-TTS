"""Cog entry point. Worker state survives warm predictions."""
from cog import BasePredictor, Input, Path
from pydantic import BaseModel
from pipeline import Pipeline, Request

class Output(BaseModel):
    speech: Path
    source: Path
    metrics: Path

class Predictor(BasePredictor):
    def setup(self):
        self.pipeline = Pipeline(rvc_python='/opt/rvc/bin/python')

    def predict(self, text: str = Input(description='English text; newlines add pauses'),
                voice: str = Input(description='Required: installed, authorized RVC voice folder'),
                source_voice: str = Input(default='af_heart'),
                speed: float = Input(default=1.0, ge=.5, le=2.0),
                pitch: int = Input(default=0, ge=-24, le=24),
                pause_ms: int = Input(default=180, ge=0, le=2000),
                use_index: bool = Input(default=False)) -> Output:
        folder, _ = self.pipeline.run(Request(text, voice, source_voice, speed, pitch, pause_ms, use_index))
        return Output(speech=Path(folder/'speech.wav'), source=Path(folder/'source.wav'),
                      metrics=Path(folder/'metrics.json'))
