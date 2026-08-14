import sys
import threading
import queue
import time
import numpy as np
from faster_whisper import WhisperModel
import pyaudio
import keyboard
from pynput.keyboard import Controller
import pystray
from PIL import Image, ImageDraw

# --- Configuration ---
MODEL_NAME = "medium"
SAMPLE_RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16

transcription_queue = queue.Queue()
is_recording = False
recording_data = []

# Global status for tray icon
status_text = "Готовий до роботи (Ctrl+Space)"

# Load model
print(f"Loading Faster Whisper model '{MODEL_NAME}'...")
model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8", cpu_threads=4)
print("Model loaded.")

audio = pyaudio.PyAudio()
keyboard_controller = Controller()


def create_tray_icon(color=(0, 122, 255)):
    """Створює просту круглу іконку для трею."""
    image = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    dc = ImageDraw.Draw(image)
    dc.ellipse((8, 8, 56, 56), fill=color)
    return image


def record_audio():
    global is_recording, recording_data
    stream = audio.open(format=FORMAT, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK)

    while is_recording:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            recording_data.append(np.frombuffer(data, dtype=np.int16))
        except Exception:
            pass

    stream.stop_stream()
    stream.close()

    if recording_data:
        audio_np = np.array(recording_data).flatten().astype(np.float32) / 32768.0
        transcription_queue.put(audio_np)


def process_transcription_worker():
    """Фоновий потік, який постійно чекає на нові аудіозаписи з черги."""
    while True:
        audio_data = transcription_queue.get()
        if audio_data is None:  # Сигнал завершення
            break

        try:
            # Додаємо initial_prompt з прикладами термінів, які ви часто використовуєте
            segments, info = model.transcribe(
                audio_data,
                language="uk",
                initial_prompt="IT терміни, QA, Python, PR, commit, deploy, code review, bug report, API, framework",
            )
            text = "".join([segment.text for segment in segments]).strip()
            if text:
                type_text(text)
        except Exception as e:
            print(f"Error during transcription: {e}")
        finally:
            transcription_queue.task_done()


def type_text(text):
    # Невелика затримка перед введенням
    time.sleep(0.05)
    for char in text:
        keyboard_controller.type(char)
        time.sleep(0.005)


def toggle_recording():
    global is_recording, recording_data
    if not is_recording:
        is_recording = True
        recording_data = []
        threading.Thread(target=record_audio, daemon=True).start()
    else:
        is_recording = False


# Запускаємо один фоновий потік для обробки черги
transcribe_thread = threading.Thread(target=process_transcription_worker, daemon=True)
transcribe_thread.start()

# Реєстрація гарячої клавіші
keyboard.add_hotkey("ctrl+space", toggle_recording)


def on_exit(icon, item):
    icon.stop()
    transcription_queue.put(None)
    audio.terminate()
    sys.exit(0)


# Створення меню в треї
icon_image = create_tray_icon()
menu = pystray.Menu(
    pystray.MenuItem("Voice Transcriber (Ctrl+Space)", None, enabled=False), pystray.MenuItem("Вихід", on_exit)
)

icon = pystray.Icon("voice_transcriber", icon_image, "Голосове введення", menu)

if __name__ == "__main__":
    # pystray блокує головний потік і тримає програму активною
    icon.run()
