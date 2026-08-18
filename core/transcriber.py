import os
import queue
from faster_whisper import WhisperModel

from config import (
    MODEL_NAME,
    CPU_THREADS,
    TRANSCRIBE_SETTINGS_FOR_MEDIUM_MODEL,
    TRANSCRIBE_SETTINGS_FOR_SMALL_MODEL,
)
from utils.logger import log_error, log_transcription


class Transcriber:
    def __init__(self):
        self.model = None

    @staticmethod
    def is_model_cached(model_name=MODEL_NAME):
        """Перевіряє, чи завантажена модель у кеш."""
        try:
            cache_dir = os.path.expanduser(os.path.join(os.environ.get("HF_HOME", "~/.cache/huggingface"), "hub"))
            folder_name = f"models--Systran--faster-whisper-{model_name}"
            model_path = os.path.join(cache_dir, folder_name)
            return os.path.exists(model_path)
        except Exception as e:
            log_error("is_model_cached", e)
            return False

    def load_model(self):
        """Синхронне завантаження моделі (викликатиметься з фонового потоку)."""
        self.model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8", cpu_threads=CPU_THREADS)

    def is_ready(self):
        return self.model is not None

    def start_worker(self, input_queue, on_text_transcribed_callback):
        """Безкінечний цикл воркера для обробки черги аудіо."""
        while True:
            try:
                audio_data = input_queue.get()
                if audio_data is None:  # Сигнал зупинки (stop poison pill)
                    break

                if not self.is_ready():
                    continue

                if MODEL_NAME == "small":
                    segments, info = self.model.transcribe(audio_data, **TRANSCRIBE_SETTINGS_FOR_SMALL_MODEL)
                else:
                    segments, info = self.model.transcribe(audio_data, **TRANSCRIBE_SETTINGS_FOR_MEDIUM_MODEL)

                text = "".join([segment.text for segment in segments]).strip()
                if text:
                    log_transcription(text)
                    # Передаємо розпізнаний текст через callback
                    on_text_transcribed_callback(text)

            except Exception as e:
                log_error("process_transcription_worker", e)
            finally:
                input_queue.task_done()
