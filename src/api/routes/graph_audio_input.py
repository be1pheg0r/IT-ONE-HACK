import decouple
import os

from fastapi import APIRouter, File, HTTPException, UploadFile

router = APIRouter(prefix="/user_input", tags=["user_input"])

UPLOAD_DIR = decouple.config(
    "UPLOAD_AUDIO_DIR", cast=str)

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/voice")
async def upload_voice_message(file: UploadFile = File(...)):

    allowed_extensions = {".wav", ".mp3", ".m4a"}
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Недопустимый формат файла. Поддерживаются: .wav, .mp3, .m4a"
        )

    try:
        file_name = f"{file.filename.split('.')[0]}_{os.urandom(8).hex()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        return

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при загрузке файла: {str(e)}"
        )
