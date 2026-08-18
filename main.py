import queue
import threading
import tkinter as tk

from core.audio_recorder import AudioRecorder
from core.transcriber import Transcriber
from core.text_injector import type_text
from ui.loading_window import show_loading_screen
from ui.tray_app import TrayApplication
from utils.logger import log_error


def main():
    try:
        root = tk.Tk()
        root.withdraw()

        transcription_queue = queue.Queue()

        # 1. Ініціалізуємо сервіси
        recorder = AudioRecorder(output_queue=transcription_queue)
        transcriber = Transcriber()

        # 2. Запускаємо воркер транскрибації
        transcription_thread = threading.Thread(
            target=transcriber.start_worker,
            args=(transcription_queue, type_text),  # type_text передається як callback
            daemon=True,
        )
        transcription_thread.start()

        # 3. Показуємо екран завантаження моделі
        show_loading_screen(root, transcriber)

        # 4. Функція очищення при виході
        def cleanup():
            transcription_queue.put(None)  # Зупиняємо воркер
            recorder.terminate()  # Завершуємо PyAudio

        # 5. Запускаємо системний трей
        tray = TrayApplication(root, recorder, transcriber, on_exit_callback=cleanup)
        tray.run_in_background()

        root.mainloop()

    except Exception as e:
        log_error("main_execution", e)


if __name__ == "__main__":
    main()
