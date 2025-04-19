import os
import numpy as np
import pyaudio
import time
from pydub import AudioSegment

SILENCE_THRESHOLD = -40
SILENCE_DURATION = 3000

class AudioService:

    def __init__(self, chunk_size:int = 1024, sample_format=pyaudio.paInt16, channels:int = 1, rate:int = 44100):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        self.audio_data = []
        self.chunk_size = chunk_size
        self.sample_format = sample_format
        self.channels = channels
        self.rate = rate


    def detect_silence(self, audio_chunk: np.ndarray) -> bool:
        """
        Определяет, является ли аудиочасть тишиной.
        """

        rms = np.sqrt(np.mean(np.square(audio_chunk)))
        return rms < SILENCE_THRESHOLD

    def record_audio(self):

        stream = self.audio.open(format=self.sample_format,
                            channels=self.channels,
                            rate=self.rate,
                            input=True,
                            frames_per_buffer=self.chunk_size)

        frames = []
        silence_start = None

        self.is_recording = True
        print("Запись аудио...")

        while self.is_recording:
            audio_data = np.frombuffer(stream.read(self.chunk_size), dtype=np.int16)
            frames.append(audio_data)

            if self.detect_silence(audio_data):
                if silence_start is None:
                    silence_start = time.time()
                elif (time.time() - silence_start) * 1000 >= SILENCE_DURATION:
                    print("Обнаружена тишина, завершение записи...")
                    break
            else:
                silence_start = None

        stream.stop_stream()
        stream.close()
        self.audio.terminate()

        self.audio_data = np.concatenate(frames)
        print("Запись завершена.")

        audio_segment = AudioSegment(
            self.audio_data.tobytes(),
            frame_rate=self.rate,
            sample_width=self.audio.get_sample_size(self.sample_format),
            channels=self.channels
        )


        audio_path = f"../audio/{int(time.time())}.wav"
        audio_segment.export(audio_path, format="wav")

        return audio_path



AudioService().record_audio()