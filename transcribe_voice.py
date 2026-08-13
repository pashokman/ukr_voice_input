import sys
import threading
import queue
import time
import numpy as np
from faster_whisper import WhisperModel
import pyaudio
import keyboard
from pynput.keyboard import Controller

# --- Configuration ---
# You can change the model from 'base' to 'small', 'medium', etc.
# 'base' is fast and good for Ukrainian. 'small' is more accurate.
MODEL_NAME = "small"
SAMPLE_RATE = 16000
CHUNK = 1024
FORMAT = pyaudio.paInt16

# Global variables
transcription_queue = queue.Queue()
is_recording = False
recording_data = []

# Initialize Faster Whisper model
print(f"Loading Faster Whisper model '{MODEL_NAME}'... Please wait.")
# Використовуємо device="cpu" та compute_type="int8" для максимальної швидкості на процесорі
model = WhisperModel(MODEL_NAME, device="cpu", compute_type="int8")
print("Model loaded.")

audio = pyaudio.PyAudio()

def record_audio():
    global is_recording, recording_data
    stream = audio.open(format=FORMAT,
                        channels=1,
                        rate=SAMPLE_RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
    
    print("Recording... (Press Ctrl+Space again to stop)")
    
    while is_recording:
        data = stream.read(CHUNK)
        recording_data.append(np.frombuffer(data, dtype=np.int16))
    
    stream.stop_stream()
    stream.close()
    
    # Convert to float32 for Whisper
    audio_np = np.array(recording_data).flatten().astype(np.float32) / 32768.0
    transcription_queue.put(audio_np)

def process_transcription():
    while True:
        audio_data = transcription_queue.get()
        if audio_data is None:
            break
        
        print("Transcribing...")
        # faster-whisper повертає генератор сегментів та інформацію
        segments, info = model.transcribe(audio_data, language="uk")
        
        # Збираємо весь текст з отриманих сегментів
        text = "".join([segment.text for segment in segments]).strip()
        
        if text:
            print(f"Result: {text}")
            type_text(text)
        else:
            print("No speech detected.")

def type_text(text):
    keyboard_controller = Controller()
    # We use a small delay to ensure the focus is correct if needed
    # and type characters one by one or as a string
    # typing one by one is more natural for some apps
    for char in text:
        keyboard_controller.type(char)
        time.sleep(0.01)

def start_recording():
    global is_recording, recording_data
    if not is_recording:
        is_recording = True
        recording_data = []
        print("Started recording...")
        threading.Thread(target=record_audio).start()

def stop_recording():
    global is_recording
    if is_recording:
        is_recording = False
        print("Stopped recording.")
        # Start processing in a separate thread to not block the hotkey listener
        threading.Thread(target=process_transcription).start()

# Set up hotkey
# Using 'ctrl+space' as a default. 
# You can change this to any combination.
keyboard.add_hotkey('ctrl+space', lambda: start_recording() if not is_recording else stop_recording())

print("Utility is running. Press Ctrl+Space to start/stop recording.")
print("Press 'Esc' to exit.")

try:
    keyboard.wait('esc')
except KeyboardInterrupt:
    pass

# Cleanup
print("Exiting...")
sys.exit()