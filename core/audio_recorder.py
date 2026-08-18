import threading
import numpy as np
import pyaudio

from config import SAMPLE_RATE, CHUNK
from utils.logger import log_error


class AudioRecorder:
    def __init__(self, output_queue):
        self.output_queue = output_queue
        self.is_recording = False
        self.audio = None

        try:
            self.audio = pyaudio.PyAudio()
        except Exception as e:
            log_error("PyAudio_init", e)

    def toggle_recording(self):
        """Перемикає стан запису (вмикає/вимикає)."""
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        if not self.audio or self.is_recording:
            return
        self.is_recording = True
        threading.Thread(target=self._record_loop, daemon=True).start()

    def stop_recording(self):
        self.is_recording = False

    def _record_loop(self):
        stream = None
        try:
            stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            local_frames = []
            while self.is_recording:
                try:
                    data = stream.read(CHUNK, exception_on_overflow=False)
                    local_frames.append(data)
                except Exception as e:
                    log_error("record_audio_stream_read", e)

            if local_frames:
                audio_bytes = b"".join(local_frames)
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                self.output_queue.put(audio_np)

        except Exception as e:
            log_error("record_audio_main", e)
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    log_error("record_audio_stream_close", e)

    def terminate(self):
        """Завершує роботу PyAudio при виході з програми."""
        if self.audio:
            self.audio.terminate()
