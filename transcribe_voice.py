import sys
import threading
import queue
import time
import numpy as np
from faster_whisper import WhisperModel
import pyaudio
import keyboard
from pynput.keyboard import Controller, Key
import pystray
from PIL import Image, ImageDraw
import pyperclip

# --- Configuration ---
MODEL_NAME = "medium"  # can be changed to "small", saves about 1.2Gb of RAM
SAMPLE_RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CPU_THREADS = 8  # should be less or equal to max cores count (not threads count)

transcription_queue = queue.Queue()
is_recording = False

# Load model with CPU optimizations
print(f"Loading Faster Whisper model '{MODEL_NAME}'...")
model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8", cpu_threads=CPU_THREADS)
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
    global is_recording
    stream = audio.open(format=FORMAT, channels=1, rate=SAMPLE_RATE, input=True, frames_per_buffer=CHUNK)

    local_frames = []
    while is_recording:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            local_frames.append(data)
        except Exception:
            pass

    stream.stop_stream()
    stream.close()

    if local_frames:
        audio_bytes = b"".join(local_frames)
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        transcription_queue.put(audio_np)


def process_transcription_worker():
    """Фоновий потік, який постійно чекає на нові аудіозаписи з черги."""
    while True:
        audio_data = transcription_queue.get()
        if audio_data is None:
            break

        try:
            segments, info = model.transcribe(
                audio_data,
                language="uk",
                beam_size=1,  # Прискорює обробку на CPU в 2-3 рази
                condition_on_previous_text=False,
                vad_filter=True,  # Відтинає тишу до того, як вона потрапить у нейромережу
                vad_parameters=dict(
                    min_silence_duration_ms=500,  # Швидше відсікає паузу в кінці вашої фрази
                    speech_pad_ms=300,  # Мінімальний відступ навколо слів, зменшення може призводити до обрізання тексту перед або після запису
                ),
                max_new_tokens=128,  # Не дає моделі генерувати довгі тексти при галюцинаціях
                initial_prompt="QA, Python, Git, Pull Request, commit, deploy, bug report, API, framework, microservices, database, SQL, Docker.",
            )
            text = "".join([segment.text for segment in segments]).strip()
            if text:
                type_text(text)
                del audio_data
        except Exception as e:
            print(f"Error during transcription: {e}")
        finally:
            transcription_queue.task_done()


def type_text(text):
    # Чекаємо відпускання Ctrl та Space, щоб вони не заважали комбінації Ctrl+V
    while keyboard.is_pressed("ctrl") or keyboard.is_pressed("space"):
        time.sleep(0.02)

    time.sleep(0.05)

    # Зберігаємо попередній вміст буфера обміну (опціонально)
    try:
        old_clip = pyperclip.paste()
    except Exception:
        old_clip = ""

    try:
        # Копіюємо розпізнаний текст у буфер
        pyperclip.copy(text)

        # Емулюємо натискання Ctrl+V для вставки
        with keyboard_controller.pressed(Key.ctrl):
            keyboard_controller.press("v")
            keyboard_controller.release("v")

        # Невелика пауза, щоб програма встигла обробити вставку
        time.sleep(0.1)
    finally:
        # Відновлюємо попередній вміст буфера обміну
        pyperclip.copy(old_clip)


def toggle_recording():
    global is_recording
    if not is_recording:
        is_recording = True
        threading.Thread(target=record_audio, daemon=True).start()
    else:
        is_recording = False


# Запускаємо фоновий потік для обробки
transcribe_thread = threading.Thread(target=process_transcription_worker, daemon=True)
transcribe_thread.start()

# Реєстрація гарячої клавіші з пригніченням стандартного сигналу (suppress=True)
keyboard.add_hotkey("ctrl+space", toggle_recording, suppress=True)


def on_exit(icon, item):
    icon.stop()
    transcription_queue.put(None)
    audio.terminate()
    sys.exit(0)


# Створення меню в треї
icon_image = create_tray_icon()
menu = pystray.Menu(
    pystray.MenuItem("Voice Transcriber (Ctrl+Space)", None, enabled=False),
    pystray.MenuItem("Вихід", on_exit),
)

icon = pystray.Icon("voice_transcriber", icon_image, "Голосове введення", menu)

if __name__ == "__main__":
    icon.run()
