MODEL_NAME = "small"  # MODEL_NAME can be changed to "small" / "medium"
SAMPLE_RATE = 16000
CHUNK = 1024
CPU_THREADS = 4  # CPU_THREADS can be changed to your current cpu core count (not threads count)
LOG_FILE = "transcriptions.log"
ERROR_LOG_FILE = "error_log.txt"

# INITIAL_PROMPT can be changed to something related to your field of work. Mine is QA, so...
INITIAL_PROMPT = (
    "QA, Python, Git, Pull Request, commit, deploy, bug report, API,"
    " framework, microservices, database, SQL, Docker."
)

# TRANSCRIBE_SETTINGS_FOR_SMALL_MODEL uses fewer parameters for better accuracy
# This parameter also works fine for the "medium" model, but transcription will be slightly slower.
TRANSCRIBE_SETTINGS_FOR_SMALL_MODEL = {
    "language": "uk",
    "condition_on_previous_text": False,
    "initial_prompt": INITIAL_PROMPT,
}

# TRANSCRIBE_SETTINGS_FOR_MEDIUM_MODEL used more parameters for faster response
# This parameter also works fine for the "small" model, but can be less accurate with these settings.
TRANSCRIBE_SETTINGS_FOR_MEDIUM_MODEL = {
    "language": "uk",
    "beam_size": 1,
    "condition_on_previous_text": False,
    "vad_filter": True,
    "vad_parameters": {
        "min_silence_duration_ms": 500,
        "speech_pad_ms": 300,
    },
    "max_new_tokens": 128,
    "initial_prompt": INITIAL_PROMPT,
}
