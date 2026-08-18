import threading
import tkinter as tk
from tkinter import ttk

from config import MODEL_NAME
from utils.logger import log_error


def show_loading_screen(root, transcriber):
    try:
        splash = tk.Toplevel(root)
        splash.title("Завантаження")
        splash.geometry("380x130")
        splash.resizable(False, False)

        splash.update_idletasks()
        x = (splash.winfo_screenwidth() // 2) - (380 // 2)
        y = (splash.winfo_screenheight() // 2) - (130 // 2)
        splash.geometry(f"380x130+{x}+{y}")
        splash.attributes("-topmost", True)

        if transcriber.is_model_cached(MODEL_NAME):
            message = f"Модель '{MODEL_NAME}' знайдена.\nІніціалізація..."
        else:
            message = f"Перший запуск: завантаження моделі '{MODEL_NAME}'...\nЦе може зайняти кілька хвилин."

        lbl = ttk.Label(splash, text=message, font=("Arial", 10), justify="center")
        lbl.pack(pady=15, padx=10)

        progress = ttk.Progressbar(splash, mode="indeterminate", length=300)
        progress.pack(pady=5)
        progress.start(10)

        def load_async():
            try:
                transcriber.load_model()
                root.after(0, lambda: lbl.config(text="Модель успішно завантажено!"))
                root.after(800, splash.destroy)
            except Exception as e:
                log_error("load_model_async", e)
                root.after(0, lambda: lbl.config(text=f"Помилка завантаження: {e}"))

        threading.Thread(target=load_async, daemon=True).start()

    except Exception as e:
        log_error("show_loading_screen", e)
