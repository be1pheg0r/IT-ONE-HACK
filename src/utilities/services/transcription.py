from faster_whisper import WhisperModel
import torch
from tqdm import tqdm

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


model = WhisperModel("small", compute_type='int8', device=DEVICE)

class TranscriptionService:
    def __init__(self, model: WhisperModel = model):
        self.model = model

    def transcribe(self, audio_file: str) -> str:
        segments, _ = self.model.transcribe(audio_file, beam_size=5)
        result = []

        # Оборачиваем цикл в tqdm для отображения прогресса
        for segment in tqdm(segments, desc="Транскрипция в процессе...", unit="сегмент"):
            result.append(segment.text)

        return " ".join(result)