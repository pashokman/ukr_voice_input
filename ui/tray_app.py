import threading
import pystray
from PIL import Image
from pynput import keyboard

from utils.paths import resource_path
from utils.logger import log_error
from ui.history_window import HistoryWindow


class TrayApplication:
    def __init__(self, root, recorder, transcriber, on_exit_callback):
        self.root = root
        self.recorder = recorder
        self.transcriber = transcriber
        self.on_exit_callback = on_exit_callback

        self.history_window = None
        self.icon = None
        self.hotkey_listener = None

    def _load_tray_icon(self):
        try:
            icon_path = resource_path("assets/icon.ico")
            return Image.open(icon_path)
        except Exception as e:
            log_error("load_tray_icon", e)
            return Image.new("RGB", (64, 64), color="black")

    def open_history_window(self):
        try:
            if self.history_window is not None and self.history_window.winfo_exists():
                # Якщо вікно згорнуте на панель задач, розгортаємо його
                if self.history_window.state() == "iconic":
                    self.history_window.deiconify()

                # Піднімаємо вікно поверх інших та фокусуємося на ньому
                self.history_window.lift()
                self.history_window.focus_force()
                return

            self.history_window = HistoryWindow(self.root)
        except Exception as e:
            log_error("open_history_window", e)

    def _toggle_recording_safe(self):
        """Блокує запис, якщо модель ще завантажується."""
        if not self.transcriber.is_ready():
            return
        self.recorder.toggle_recording()

    def _start_hotkey_listener(self):
        """Ініціалізує та запускає слухач клавіш у фоні через pynput."""
        try:
            self.hotkey_listener = keyboard.GlobalHotKeys({"<ctrl>+<space>": self._toggle_recording_safe})
            self.hotkey_listener.start()
        except Exception as e:
            log_error("start_hotkey_listener", e)

    def run_in_background(self):
        # Налаштування гарячої клавіші
        self._start_hotkey_listener()

        # Контекстне меню трею
        menu = pystray.Menu(
            pystray.MenuItem("Ukrainian Voice Input (Ctrl+Space)", None, enabled=False),
            pystray.MenuItem("Історія записів", lambda icon, item: self.root.after(0, self.open_history_window)),
            pystray.MenuItem("Вихід", self._on_exit),
        )

        icon_image = self._load_tray_icon()
        self.icon = pystray.Icon("voice_transcriber", icon_image, "Голосове введення", menu)

        threading.Thread(target=self.icon.run, daemon=True).start()

    def _on_exit(self, icon, item):
        try:
            # Зупиняємо слухач клавіш, щоб потік коректно завершився
            if self.hotkey_listener:
                self.hotkey_listener.stop()

            if self.icon:
                self.icon.stop()

            self.on_exit_callback()
            self.root.after(0, self.root.destroy)
        except Exception as e:
            log_error("on_exit", e)
