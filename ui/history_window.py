import os
import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip

from config import LOG_FILE
from utils.logger import log_error


class HistoryWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Історія транскрибації")
        self.geometry("650x400")

        self.last_file_position = 0
        self._setup_ui()
        self._check_for_new_logs()

    def _on_ctrl_c(self, event=None):
        # Перевіряємо: якщо це подія клавіатури, то обробляємо тільки клавішу 'C' (keycode 67 у Windows)
        if event:
            # keycode 67 відповідає фізичній клавіші 'C' / 'С' на клавіатурі
            # keysym 'c' або 'C' покриває випадок англійської розкладки
            if event.keycode == 67 or event.keysym.lower() == "c":
                self.copy_selected()
                return "break"
            return  # Якщо натиснуто Ctrl + інша клавіша (наприклад Ctrl+A), не перехоплюємо її

        self.copy_selected()
        return "break"

    def _setup_ui(self):
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X)

        frame = ttk.Frame(self, padding=10)
        frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        self.text_area = tk.Text(
            frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            cursor="arrow",
        )
        scrollbar.config(command=self.text_area.yview)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Копіювання подвійним кліком
        self.text_area.bind("<Double-Button-1>", self.copy_selected)

        # 1. Англійська розкладка (Ctrl+C / Ctrl+c)
        self.text_area.bind("<Control-c>", self._on_ctrl_c)
        self.text_area.bind("<Control-C>", self._on_ctrl_c)

        # 2. Універсальна обробка натискання будь-якої клавіші для перевірки KeyCode / Cyrillic
        self.text_area.bind("<Control-KeyPress>", self._on_ctrl_c)

        self.text_area.config(state=tk.DISABLED)

        copy_btn = ttk.Button(btn_frame, text="Копіювати текст", command=self.copy_selected)
        copy_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = ttk.Button(btn_frame, text="Очистити історію", command=self.clear_logs)
        clear_btn.pack(side=tk.RIGHT, padx=5)

    def copy_selected(self, event=None):
        try:
            try:
                selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            except tk.TclError:
                selected_text = None

            if not selected_text:
                line_index = self.text_area.index("insert linestart")
                line_end = self.text_area.index("insert lineend")
                selected_text = self.text_area.get(line_index, line_end).strip()

            if selected_text:
                clean_text = (
                    selected_text[22:] if len(selected_text) > 22 and selected_text.startswith("[") else selected_text
                )
                pyperclip.copy(clean_text)
                self.title("Історія транскрибації — [Скопійовано!]")
                self.after(1500, lambda: self.title("Історія транскрибації"))
        except Exception as e:
            log_error("copy_selected", e)

    def clear_logs(self):
        try:
            if messagebox.askyesno("Підтвердження", "Очистити всі збережені логи?", parent=self):
                if os.path.exists(LOG_FILE):
                    open(LOG_FILE, "w", encoding="utf-8").close()
                self.text_area.config(state=tk.NORMAL)
                self.text_area.delete("1.0", tk.END)
                self.text_area.config(state=tk.DISABLED)
        except Exception as e:
            log_error("clear_logs", e)

    def _check_for_new_logs(self):
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    f.seek(0, os.SEEK_END)
                    file_size = f.tell()

                    if file_size < self.last_file_position:
                        self.last_file_position = 0

                    f.seek(self.last_file_position)
                    new_lines = f.readlines()
                    self.last_file_position = f.tell()

                    if new_lines:
                        self.text_area.config(state=tk.NORMAL)
                        for line in new_lines:
                            if line.strip():
                                self.text_area.insert("1.0", line.strip() + "\n\n")
                        self.text_area.config(state=tk.DISABLED)

            self.after(1000, self._check_for_new_logs)
        except Exception as e:
            log_error("check_for_new_logs", e)
