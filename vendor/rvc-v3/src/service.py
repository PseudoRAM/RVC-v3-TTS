"""Persistent RVC inference state owned by a single Cog worker."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time

from model_cache import DownloadCache, ModelCache, model_files

ROOT = Path(__file__).resolve().parent.parent


class VoiceService:
    def __init__(self):
        import torch
        from rvc import Config, load_hubert
        from rmvpe import RMVPE

        started = time.perf_counter()
        self.lock = threading.Lock()
        self.models = ROOT / "rvc_models"
        self.config = Config("cuda:0" if torch.cuda.is_available() else "cpu", torch.cuda.is_available())
        self.hubert = load_hubert(self.config.device, self.config.is_half, str(self.models / "hubert_base.pt"))
        self.pitch = RMVPE(str(self.models / "rmvpe.pt"), is_half=self.config.is_half, device=self.config.device)
        self.voices = ModelCache(int(os.environ.get("RVC_VOICE_CACHE_SIZE", "1")))
        self.downloads = DownloadCache(ROOT / ".cache" / "voices")
        print(json.dumps({"event": "setup", "seconds": time.perf_counter() - started}))

    def convert(self, input_audio, rvc_model="CUSTOM", custom_url=None, refresh=False,
                pitch_change=0, index_rate=0.5, filter_radius=3, rms_mix_rate=0.25,
                protect=0.33, f0_method="rmvpe", crepe_hop_length=160,
                output_format="wav", use_index=False):
        import torch
        from rvc import get_vc, rvc_infer

        if output_format not in ("wav", "mp3") or f0_method not in ("rmvpe", "mangio-crepe"):
            raise ValueError("Unsupported output format or pitch method")
        if crepe_hop_length < 1:
            raise ValueError("CREPE hop length must be positive")
        with self.lock:
            started = time.perf_counter()
            download_hit = None
            if custom_url:
                folder, download_hit = self.downloads.get(custom_url, refresh)
            else:
                folder = (self.models / rvc_model).resolve()
                if folder.parent != self.models.resolve():
                    raise ValueError("Voice name must identify a directory inside rvc_models")
            checkpoint, index = model_files(folder)
            stat = checkpoint.stat()
            key = (str(checkpoint), stat.st_size, stat.st_mtime_ns)

            def load():
                voice = get_vc(self.config.device, self.config.is_half, self.config, str(checkpoint))
                voice[-1].model_rmvpe = self.pitch
                return voice

            voice, voice_hit = self.voices.get(key, load)
            loaded = time.perf_counter()
            cpt, version, net_g, sample_rate, pipeline = voice
            # Cog collects returned paths after predict completes. Do not delete here.
            output_dir = Path(tempfile.mkdtemp(prefix="rvc-v3-output-"))
            output = output_dir / "output.wav"
            try:
                with torch.no_grad():
                    rvc_infer(str(index) if use_index and index else "", index_rate,
                              str(input_audio), str(output), pitch_change, f0_method,
                              cpt, version, net_g, filter_radius, sample_rate,
                              rms_mix_rate, protect, crepe_hop_length, pipeline, self.hubert)
                if output_format == "mp3":
                    encoded = output.with_suffix(".mp3")
                    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y",
                                    "-i", str(output), "-codec:a", "libmp3lame", "-q:a", "2", str(encoded)], check=True)
                    output.unlink()
                    output = encoded
            except Exception:
                import shutil
                shutil.rmtree(output_dir)
                raise
            print(json.dumps({"event": "prediction", "voice_cache_hit": voice_hit,
                              "download_cache_hit": download_hit,
                              "load_seconds": loaded - started,
                              "conversion_seconds": time.perf_counter() - loaded,
                              "total_seconds": time.perf_counter() - started}))
            return output
