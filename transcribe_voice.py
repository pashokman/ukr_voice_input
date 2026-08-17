import sys
import os
import time
import queue
import threading
import traceback
import tkinter as tk
from tkinter import messagebox, ttk

import keyboard
import numpy as np
import pyaudio
import pyperclip
import pystray
from PIL import Image
from faster_whisper import WhisperModel

from config import (
    CPU_THREADS,
    CHUNK,
    LOG_FILE,
    ERROR_LOG_FILE,
    MODEL_NAME,
    SAMPLE_RATE,
    TRANSCRIBE_SETTINGS_FOR_MEDIUM_MODEL,
    TRANSCRIBE_SETTINGS_FOR_SMALL_MODEL,
)

transcription_queue = queue.Queue()
is_recording = False
root = None  # Global Tkinter instance
history_window = None  # Reference to the history window
model = None  # Model will be initialized in the background
audio = None


def log_error(context, exception):
    """Centralized error logging to error_log.txt with a stack trace."""
    timestamp = time.strftime("[%H:%M:%S %d-%m-%Y]")
    error_msg = f"{timestamp} [{context}] {type(exception).__name__}: {exception}\n"
    error_msg += traceback.format_exc() + "\n" + "-" * 50 + "\n"

    try:
        with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(error_msg)
    except Exception as e:
        print(f"Failed to log error to file: {e}")


def log_transcription(text):
    """Saves the transcribed text to a file with a timestamp."""
    try:
        timestamp = time.strftime("[%H:%M:%S %d-%m-%Y]")
        entry = f"{timestamp} {text}\n"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        log_error("log_transcription", e)


def resource_path(relative_path):
    """Returns the absolute path to the file (for normal execution and for PyInstaller)"""
    try:
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
    except Exception as e:
        log_error("resource_path", e)
        return relative_path


def load_tray_icon():
    try:
        icon_path = resource_path("icon.ico")
        return Image.open(icon_path)
    except Exception as e:
        log_error("load_tray_icon", e)
        # Return a black fallback image if the ico file is missing
        return Image.new("RGB", (64, 64), color="black")


def record_audio():
    global is_recording
    try:
        if not audio:
            return

        stream = audio.open(
            format=pyaudio.paInt16,
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
            except Exception as e:
                log_error("record_audio_stream_read", e)

        stream.stop_stream()
        stream.close()

        if local_frames:
            audio_bytes = b"".join(local_frames)
            audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            transcription_queue.put(audio_np)
    except Exception as e:
        log_error("record_audio_main", e)


def process_transcription_worker():
    while True:
        try:
            audio_data = transcription_queue.get()
            if audio_data is None:
                break

            if model is None:
                continue

            if MODEL_NAME == "small":
                segments, info = model.transcribe(audio_data, **TRANSCRIBE_SETTINGS_FOR_SMALL_MODEL)
            else:
                segments, info = model.transcribe(audio_data, **TRANSCRIBE_SETTINGS_FOR_MEDIUM_MODEL)

            text = "".join([segment.text for segment in segments]).strip()
            if text:
                log_transcription(text)
                type_text(text)
                del audio_data
        except Exception as e:
            log_error("process_transcription_worker", e)
        finally:
            transcription_queue.task_done()


def type_text(text):
    try:
        while keyboard.is_pressed("ctrl") or keyboard.is_pressed("space"):
            time.sleep(0.02)

        time.sleep(0.05)

        try:
            old_clip = pyperclip.paste()
        except Exception as e:
            log_error("type_text_paste", e)
            old_clip = ""

        try:
            pyperclip.copy(text)
            time.sleep(0.05)
            keyboard.send("ctrl+v")
            time.sleep(0.1)
        finally:
            try:
                pyperclip.copy(old_clip)
            except Exception as e:
                log_error("type_text_restore_clip", e)
    except Exception as e:
        log_error("type_text_main", e)


def toggle_recording():
    try:
        global is_recording
        if model is None:
            return  # Block recording if the model is still loading

        if not is_recording:
            is_recording = True
            threading.Thread(target=record_audio, daemon=True).start()
        else:
            is_recording = False
    except Exception as e:
        log_error("toggle_recording", e)


# --- GUI for logs ---
def open_history_window():
    global history_window

    try:
        if history_window is not None and tk.Toplevel.winfo_exists(history_window):
            history_window.lift()
            history_window.focus_force()
            return

        history_window = tk.Toplevel(root)
        history_window.title("Історія транскрибації")
        history_window.geometry("650x400")

        btn_frame = ttk.Frame(history_window, padding=10)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        frame = ttk.Frame(history_window, padding=10)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        text_area = tk.Text(
            frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            cursor="arrow",
        )
        scrollbar.config(command=text_area.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        def copy_selected(event=None):
            try:
                try:
                    selected_text = text_area.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
                except tk.TclError:
                    selected_text = None

                if not selected_text:
                    try:
                        line_index = text_area.index("insert linestart")
                        line_end = text_area.index("insert lineend")
                        selected_text = text_area.get(line_index, line_end).strip()
                    except Exception as e:
                        log_error("copy_selected_get_line", e)
                        return

                if selected_text:
                    clean_text = (
                        selected_text[22:]
                        if len(selected_text) > 22 and selected_text.startswith("[")
                        else selected_text
                    )
                    pyperclip.copy(clean_text)

                    history_window.title("Історія транскрибації — [Скопійовано!]")
                    history_window.after(1500, lambda: history_window.title("Історія транскрибації"))
            except Exception as e:
                log_error("copy_selected", e)

        def clear_logs():
            try:
                if messagebox.askyesno("Підтвердження", "Очистити всі збережені логи?", parent=history_window):
                    if os.path.exists(LOG_FILE):
                        open(LOG_FILE, "w", encoding="utf-8").close()
                    text_area.config(state=tk.NORMAL)
                    text_area.delete("1.0", tk.END)
                    text_area.config(state=tk.DISABLED)
            except Exception as e:
                log_error("clear_logs", e)

        text_area.bind("<Double-Button-1>", copy_selected)
        text_area.config(state=tk.DISABLED)

        last_file_position = [0]

        def check_for_new_logs():
            try:
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

                            if new_lines:
                                text_area.config(state=tk.NORMAL)
                                for line in new_lines:
                                    if line.strip():
                                        text_area.insert("1.0", line.strip() + "\n\n")
                                text_area.config(state=tk.DISABLED)
                    except Exception as e:
                        log_error("check_for_new_logs_file_read", e)

                history_window.after(1000, check_for_new_logs)
            except Exception as e:
                log_error("check_for_new_logs_main", e)

        check_for_new_logs()

        copy_btn = ttk.Button(btn_frame, text="Копіювати текст", command=copy_selected)
        copy_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_frame, text="Очистити історію", command=clear_logs)
        clear_btn.pack(side=tk.RIGHT, padx=5)
    except Exception as e:
        log_error("open_history_window", e)


def show_history_from_tray(icon, item):
    try:
        if root:
            root.after(0, open_history_window)
    except Exception as e:
        log_error("show_history_from_tray", e)


def on_exit(icon, item):
    try:
        icon.stop()
        transcription_queue.put(None)
        if audio:
            audio.terminate()
        if root:
            root.after(0, root.destroy)
    except Exception as e:
        log_error("on_exit", e)


# --- Model verification and loading with GUI window ---
def is_model_cached(model_name):
    """Checks if the model is cached in the local Hugging Face folder."""
    try:
        cache_dir = os.path.expanduser(os.path.join(os.environ.get("HF_HOME", "~/.cache/huggingface"), "hub"))
        folder_name = f"models--Systran--faster-whisper-{model_name}"
        model_path = os.path.join(cache_dir, folder_name)
        return os.path.exists(model_path)
    except Exception as e:
        log_error("is_model_cached", e)
        return False


def load_model_async(splash, status_label):
    global model
    try:
        # Loading the model
        model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8", cpu_threads=CPU_THREADS)

        # Updating UI upon completion
        if root:
            root.after(0, lambda: status_label.config(text="Модель успішно завантажено!"))
            root.after(800, splash.destroy)  # Close window after 0.8 seconds
    except Exception as e:
        log_error("load_model_async", e)
        if root:
            root.after(0, lambda: status_label.config(text=f"Помилка завантаження: {e}"))


def show_loading_screen():
    try:
        splash = tk.Toplevel(root)
        splash.title("Завантаження")
        splash.geometry("380x130")
        splash.resizable(False, False)

        # Center window on screen
        splash.update_idletasks()
        x = (splash.winfo_screenwidth() // 2) - (380 // 2)
        y = (splash.winfo_screenheight() // 2) - (130 // 2)
        splash.geometry(f"380x130+{x}+{y}")
        splash.attributes("-topmost", True)

        # Determine status message
        if is_model_cached(MODEL_NAME):
            message = f"Модель '{MODEL_NAME}' знайдена.\nІніціалізація..."
        else:
            message = f"Перший запуск: завантаження моделі '{MODEL_NAME}'...\nЦе може зайняти кілька хвилин."

        lbl = ttk.Label(splash, text=message, font=("Arial", 10), justify="center")
        lbl.pack(pady=15, padx=10)

        progress = ttk.Progressbar(splash, mode="indeterminate", length=300)
        progress.pack(pady=5)
        progress.start(10)

        # Run model loading in a separate thread
        threading.Thread(target=load_model_async, args=(splash, lbl), daemon=True).start()
    except Exception as e:
        log_error("show_loading_screen", e)


if __name__ == "__main__":
    try:
        audio = pyaudio.PyAudio()
    except Exception as e:
        log_error("PyAudio_init", e)

    try:
        # Create Tkinter root
        root = tk.Tk()
        root.withdraw()  # Hide the main empty window

        # Display the loading status window
        show_loading_screen()

        # Start background transcription worker thread
        transcribe_thread = threading.Thread(target=process_transcription_worker, daemon=True)
        transcribe_thread.start()

        keyboard.add_hotkey("ctrl+space", toggle_recording, suppress=True)

        # Create system tray menu
        icon_image = load_tray_icon()
        menu = pystray.Menu(
            pystray.MenuItem("Ukrainian Voice Input (Ctrl+Space)", None, enabled=False),
            pystray.MenuItem("Історія записів", show_history_from_tray),
            pystray.MenuItem("Вихід", on_exit),
        )

        icon = pystray.Icon("voice_transcriber", icon_image, "Голосове введення", menu)
        tray_thread = threading.Thread(target=icon.run, daemon=True)
        tray_thread.start()

        root.mainloop()
    except Exception as e:
        log_error("main_execution", e)
