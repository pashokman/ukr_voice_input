import time
import keyboard
import pyperclip
from utils.logger import log_error


def type_text(text):
    """Безпечно вставляє текст через буфер обміну."""
    try:
        # Чекаємо відпускання Ctrl та Space
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
