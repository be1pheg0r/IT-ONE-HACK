from pydantic import BaseModel

class AudioResponse(BaseModel):
    """
    Путь к аудиофайлу в формате WAV
    """

    audio_path: str