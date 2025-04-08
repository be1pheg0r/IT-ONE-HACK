# schemas/request.py
from pydantic import BaseModel
from fastapi import UploadFile, File

class AudioRequest(BaseModel):
    audio_file: UploadFile = File(..., description="Аудиофайл для транскрипции")

