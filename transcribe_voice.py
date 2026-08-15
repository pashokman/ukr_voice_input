import os
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

from faster_whisper import WhisperModel
import keyboard
import numpy as np

import PIL.Image
import PIL.ImageDraw
from pynput.keyboard import Controller, Key
import pyperclip
import pyaudio
import pystray

# --- Configuration ---
MODEL_NAME = "medium"
SAMPLE_RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CPU_THREADS = 8
LOG_FILE = "transcriptions.log"

transcription_queue = queue.Queue()
is_recording = False
root = None  # Глобальний екземпляр Tkinter
history_window = None  # Посилання на вікно історії

# Завантаження моделі з обробкою на CPU
print(f"Loading Faster Whisper model '{MODEL_NAME}'...")
model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8", cpu_threads=CPU_THREADS)
print("Model loaded.")

audio = pyaudio.PyAudio()
keyboard_controller = Controller()


def log_transcription(text):
    """Зберігає розпізнаний текст у файл із позначкою часу."""
    timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
    entry = f"{timestamp} {text}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)


def create_tray_icon(color=(0, 122, 255)):
    image = PIL.Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    dc = PIL.ImageDraw.Draw(image)
    dc.ellipse((8, 8, 56, 56), fill=color)
    return image


def record_audio():
    global is_recording
    stream = audio.open(
        format=FORMAT,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

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
    while True:
        audio_data = transcription_queue.get()
        if audio_data is None:
            break

        try:
            segments, info = model.transcribe(
                audio_data,
                language="uk",
                beam_size=1,
                condition_on_previous_text=False,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=300,
                ),
                max_new_tokens=128,
                initial_prompt=(
                    "QA, Python, Git, Pull Request, commit, deploy, bug report, API,"
                    " framework, microservices, database, SQL, Docker."
                ),
            )
            text = "".join([segment.text for segment in segments]).strip()
            if text:
                log_transcription(text)
                type_text(text)
                del audio_data
        except Exception as e:
            print(f"Error during transcription: {e}")
        finally:
            transcription_queue.task_done()


def type_text(text):
    while keyboard.is_pressed("ctrl") or keyboard.is_pressed("space"):
        time.sleep(0.02)

    time.sleep(0.05)

    try:
        old_clip = pyperclip.paste()
    except Exception:
        old_clip = ""

    try:
        pyperclip.copy(text)
        with keyboard_controller.pressed(Key.ctrl):
            keyboard_controller.press("v")
            keyboard_controller.release("v")
        time.sleep(0.1)
    finally:
        try:
            pyperclip.copy(old_clip)
        except Exception:
            pass


def toggle_recording():
    global is_recording
    if not is_recording:
        is_recording = True
        threading.Thread(target=record_audio, daemon=True).start()
    else:
        is_recording = False


# --- GUI для логів ---
def open_history_window():
    global history_window

    # Якщо вікно вже відкрите — просто виводимо його на передній план
    if history_window is not None and tk.Toplevel.winfo_exists(history_window):
        history_window.lift()
        history_window.focus_force()
        return

    history_window = tk.Toplevel(root)
    history_window.title("Історія транскрибації")
    history_window.geometry("650x400")

    def copy_selected(event=None):
        try:
            selection = listbox.curselection()
            if not selection:
                return
            selected_text = listbox.get(selection[0])
            clean_text = selected_text[22:] if len(selected_text) > 22 else selected_text
            pyperclip.copy(clean_text)

            history_window.title("Історія транскрибації — [Скопійовано!]")
            history_window.after(1500, lambda: history_window.title("Історія транскрибації"))
        except (tk.TclError, Exception):
            pass

    def clear_logs():
        if messagebox.askyesno("Підтвердження", "Очистити всі збережені логи?", parent=history_window):
            if os.path.exists(LOG_FILE):
                open(LOG_FILE, "w", encoding="utf-8").close()
            listbox.delete(0, tk.END)

    frame = ttk.Frame(history_window, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
    listbox = tk.Listbox(
        frame,
        yscrollcommand=scrollbar.set,
        selectmode=tk.SINGLE,
        font=("Consolas", 10),
    )
    scrollbar.config(command=listbox.yview)

    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    listbox.bind("<Double-Button-1>", copy_selected)

    last_file_position = [0]

    def check_for_new_logs():
        if not tk.Toplevel.winfo_exists(history_window):
            return

        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    f.seek(0, os.SEEK_END)
                    file_size = f.tell()

                    if file_size < last_file_position[0]:
                        last_file_position[0] = 0

                    f.seek(last_file_position[0])
                    new_lines = f.readlines()
                    last_file_position[0] = f.tell()

                    for line in new_lines:
                        if line.strip():
                            listbox.insert(0, line.strip())
            except Exception:
                pass

        history_window.after(1000, check_for_new_logs)

    check_for_new_logs()

    btn_frame = ttk.Frame(history_window, padding=10)
    btn_frame.pack(fill=tk.X)

    copy_btn = ttk.Button(btn_frame, text="Копіювати текст", command=copy_selected)
    copy_btn.pack(side=tk.LEFT, padx=5)

    clear_btn = ttk.Button(btn_frame, text="Очистити історію", command=clear_logs)
    clear_btn.pack(side=tk.RIGHT, padx=5)


def show_history_from_tray(icon, item):
    # Безпечно передаємо виклик відкриття вікна в головний потік Tkinter
    if root:
        root.after(0, open_history_window)


def on_exit(icon, item):
    icon.stop()
    transcription_queue.put(None)
    audio.terminate()
    if root:
        root.after(0, root.destroy)


# --- Запуск програмних потоків ---
transcribe_thread = threading.Thread(target=process_transcription_worker, daemon=True)
transcribe_thread.start()

keyboard.add_hotkey("ctrl+space", toggle_recording, suppress=True)

# Створення меню в треї
icon_image = create_tray_icon()
menu = pystray.Menu(
    pystray.MenuItem("Voice Transcriber (Ctrl+Space)", None, enabled=False),
    pystray.MenuItem("Історія записів", show_history_from_tray),
    pystray.MenuItem("Вихід", on_exit),
)

icon = pystray.Icon("voice_transcriber", icon_image, "Голосове введення", menu)

# Запускаємо pystray у фоновому потоці
tray_thread = threading.Thread(target=icon.run, daemon=True)
tray_thread.start()

if __name__ == "__main__":
    # Головний потік віддаємо для Tkinter (приховане root-вікно)
    root = tk.Tk()
    root.withdraw()  # Ховаємо головне порожнє вікно
    root.mainloop()
