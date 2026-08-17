# 🎙️ Ukrainian Voice Input

<p align="center">
  <img src="https://img.shields.io/badge/OS-Windows-blue?style=flat&logo=windows" alt="OS Windows">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=flat&logo=python" alt="Python Version">
  <a href="https://github.com/pashokman/ukr_voice_input/stargazers"><img src="https://img.shields.io/github/stars/pashokman/ukr_voice_input?style=social" alt="GitHub Stars"></a>
</p>

[English](#-english) | [Українська](#-українська)

---

## 🇺🇦 Українська

**Ukrainian Voice Input** — це легка та повністю локальна утиліта для ОС Windows, яка дозволяє вводити текст голосом українською мовою у будь-якому активному вікні (Word, Telegram, браузер, Блокнот тощо). Без надсилання аудіо на сторонні сервери — повна приватність завдяки ШІ-моделям Whisper. Усі обчислення відбуваються виключно на CPU.

> 💡 **Чому CPU?** На GPU можна запускати точніші моделі і вони працюватимуть швидше. Проте цей підхід обрано свідомо через повномасштабну війну, яку розпочала росія, — для забезпечення мінімального споживання електроенергії та можливості використання на ПК без дискретної відеокарти.

---

### 📦 Релізи та Версії Моделей (Releases)

Завантажити готову збірку програми можна на сторінці **[GitHub Releases](https://github.com/pashokman/ukr_voice_input/releases/)**.

| Модель | Рекомендовано для | Споживання ОЗП (RAM) | Параметр у `config.py` |
| :--- | :--- | :--- | :--- |
| **Small** *(за замовчуванням)* | Слабопотужні CPU | < 500 MB | `MODEL_NAME = "small"` |
| **Medium** | Сучасні CPU | < 1.6 GB | `MODEL_NAME = "medium"` |

*Примітка: Усі інші параметри конфігурації однакові для обох моделей, за винятком `TRANSCRIBE_SETTINGS`.*

---

### ✨ Особливості
- **100% Локально:** Ваші голосові дані не залишають ваш комп'ютер. При першому запуску програма завантажує необхідну модель з Hugging Face (`C:\Users\<User>\.cache\huggingface\hub\...`).
- **Глобальні гарячі клавіші:** Працює поверх будь-якої програми, де є активне поле для введення тексту.
- **Швидкість та точність:** Оптимізовано під розпізнавання української мови на CPU.

---

### 💻 Системні вимоги

| Компонент | Мінімально | Рекомендовано |
| :--- | :--- | :--- |
| **Процесор (CPU)** | 4 ядра / 4 потоки | 6–8 ядер *(наприклад, AMD Ryzen 5600 / Intel i5-12400)* |
| **Оперативна пам'ять (RAM)** | 8 ГБ | 16 ГБ |
| **Накопичувач** | HDD | SSD |
| **Мікрофон** | Будь-який | З функцією шумозаглушення |
| **Інтернет** | Потрібен тільки при першому запуску *(для завантаження моделі)* |

---

### 🚀 Інструкція зі встановлення (Для розробників)

1. **Клонуйте репозиторій:**
   `git clone https://github.com/pashokman/ukr_voice_input.git`
   `cd ukr_voice_input`

2. **Встановіть залежності:**
   `pip install -r requirements.txt`

3. **Запустіть утиліту:**
   `python transcribe_voice.py`

---

### ⌨️ Використання

1. Клацніть мишкою у будь-яке поле для введення тексту (наприклад, чат з ШІ чи документ Word).
2. Натисніть **`Ctrl` + `Space`** для початку запису.
3. Продиктуйте текст українською мовою.
4. Натисніть **`Ctrl` + `Space`** знову, щоб завершити запис.
5. Зачекайте 1–3 секунди — розпізнаний текст автоматично з'явиться у полі введення.

---

### ⚙️ Налаштування (`config.py`)

Ви можете налаштувати параметри роботи програми у файлі `config.py`:
- `MODEL_NAME` — вибір моделі (`"small"` або `"medium"`).
- `TRANSCRIBE_SETTINGS` — детальні параметри транскрибації мовлення.
- Налаштування гарячих клавіш для запуску/зупинки запису.

---

### 🤝 Внесок у проєкт (Contributing)
Будь-які пропозиції, багрепорти та Pull Request'и вітаються! Якщо у вас є ідеї щодо покращення швидкодії або оптимізації — створюйте Issue.

⭐ **Сподобався проєкт? Поставте зірочку (Star) на GitHub, щоб підтримка українського Open Source зростала!**

---

## 🇬🇧 English

**Ukrainian Voice Input** is a lightweight and fully local Windows utility that allows you to input text using your voice in Ukrainian into any active window (Word, any messenger, browser, Notepad, etc.). Complete privacy with no audio sent to third-party servers, powered by Whisper AI models running entirely on the CPU.

> 💡 **Why CPU?** While running larger models on GPUs is faster and offers higher precision, CPU execution was intentionally chosen due to the ongoing full-scale war started by russia — aiming for lower power consumption and ensuring accessibility on systems without dedicated GPUs.

---

### 📦 Releases & Model Versions

You can download ready-to-use binaries on the **[GitHub Releases](https://github.com/pashokman/ukr_voice_input/releases/)** page.

| Model | Recommended For | RAM Consumption | Setting in `config.py` |
| :--- | :--- | :--- | :--- |
| **Small** *(default)* | Entry-level / Weak CPUs | < 500 MB | `MODEL_NAME = "small"` |
| **Medium** | Modern CPUs | < 1.6 GB | `MODEL_NAME = "medium"` |

*Note: All other configuration parameters remain identical for both models, except for `TRANSCRIBE_SETTINGS`.*

---

### ✨ Features
- **100% Local:** Your voice data never leaves your device. On first launch, the required model is downloaded locally from Hugging Face (`C:\Users\<User>\.cache\huggingface\hub\...`).
- **Global Hotkeys:** Works system-wide on top of any active input field.
- **Speed & Accuracy:** Optimized specifically for Ukrainian speech recognition on CPU.

---

### 💻 System Requirements

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **Processor (CPU)** | 4 cores / 4 threads | 6–8 cores *(e.g., AMD Ryzen 5600 / Intel i5-12400)* |
| **RAM** | 8 GB | 16 GB |
| **Storage** | HDD | SSD |
| **Microphone** | Any | Noise-canceling microphone |
| **Internet** | Required only on first launch *(to download the model)* |

---

### 🚀 Getting Started (For Developers)

1. **Clone the repository:**
   `git clone https://github.com/pashokman/ukr_voice_input.git`
   `cd ukr_voice_input`

2. **Install dependencies:**
   `pip install -r requirements.txt`

3. **Run the application:**
   `python transcribe_voice.py`

---

### ⌨️ Usage

1. Focus on any text input area (e.g., AI chat, Word document, search bar).
2. Press **`Ctrl` + `Space`** to start recording.
3. Dictate your text in Ukrainian.
4. Press **`Ctrl` + `Space`** again to stop recording.
5. Wait a few seconds, and the transcribed text will automatically paste into your field.

---

### ⚙️ Configuration (`config.py`)

You can tweak options inside the `config.py` file:
- `MODEL_NAME`: Switch between `"small"` and `"medium"`.
- `TRANSCRIBE_SETTINGS`: Fine-tune transcription parameters.
- Change hotkey bindings if needed.

---

### 🤝 Contributing
Contributions, issue reports, and feature requests are welcome! Feel free to open an Issue or submit a Pull Request.

⭐ **Enjoying the project? Give it a Star on GitHub to support Ukrainian Open Source!**