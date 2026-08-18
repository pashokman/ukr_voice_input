import time
import traceback

from config import ERROR_LOG_FILE, LOG_FILE


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
