from fastapi import APIRouter, UploadFile, File
from app.services.audio_service import AudioService
from app.services.transcription import TranscriptionService
import shutil
import os


router = APIRouter()
audio_service = AudioService()
transcription_service = TranscriptionService()

@router.post("/record-audio")
async def record_audio():
    """
    Запись аудио с микрофона.
    """
    audio_path = audio_service.record_audio()
    if audio_path:
        return {"message": "Аудио записано", "audio_path": audio_path}
    else:
        return {"message": "Ошибка записи аудио"}

@router.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...)):

    """
    Транскрипция аудио.
    """
    # Сохранение загруженного файла
    audio_path = f"temp/{file.filename}"
    with open(audio_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Транскрипция
    transcription = transcription_service.transcribe(audio_path)
    if not transcription:
        return {"message": "Ошибка транскрипции"}

    # Удаление временного файла
    os.remove(audio_path)

    return {"message": "Аудио транскрибировано", "transcription": transcription}





