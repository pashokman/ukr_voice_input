# 🎙️ Ukrainian voice input

[English](#english) | [Українська](#українська)

Releases:
 - **small** model for weak CPUs -  
   RAM consumption should be less than 500MB  
   config difference:  
   ```MODEL_NAME = "small"```  

 - **medium** model for modern CPUs -  
   RAM consumption should be less than 1.6GB  
   config difference:  
   ```MODEL_NAME = "medium"```  

All other config params are the same for both models except TRANSCRIBE_SETTINGS. You can adjuct them in `config.py` file.

---

## Українська

**Ukrainian voice input** — це легка та повністю локальна утиліта для ОС Windows, яка дозволяє вводити текст голосом українською мовою у будь-якому активному вікні (Word, Telegram, браузер, блокнот тощо). Без надсилання аудіо на сторонні сервери — повна приватність завдяки ШІ-моделям Whisper. Всі обчислення відбуваються на CPU.
Так, я знаю, що на GPU можна запускати більш точні моделі і вони працюватимуть швидше. Я обрав даний спосіб через війну, яку розпочала росія, бо потрібно подумати про варіант з меншим споживанням електро енергії і можливим використанням PC без GPU.

### ✨ Особливості
- **100% Локально:** Ваші голосові дані не залишають ваш комп'ютер. При першому запуску, програма завантажує LLM для транскрибації у `C:\Users\<User>\.cache\huggingface\hub\...`
- **Глобальні гарячі клавіші:** Працює поверх будь-якої програми, яка має поле для введення.
- **Швидкість та точність:** Оптимізовано під розпізнавання української мови.

### 🚀 Як запустити (Для розробників)
1. Клонуйте репозиторій:
   ```bash
   git clone https://github.com/pashokman/ukr_voice_input.git
   cd ukr_voice_input
   ```
2. Встановіть необхідні залежності:
   ```bash
   pip install -r requirements.txt
   ```
3. Запустіть скрипт:
   ```bash
   python transcribe_voice.py
   ```

### ⌨️ Використання
1. Клацніть мишкою у будь-яке поле для введення тексту.
2. Натисніть **Ctrl+Space** (за замовчуванням налаштовану у вашому скрипті).
3. Продиктуйте текст українською мовою.
4. Натисніть **Ctrl+Space** знову, щоб завершити запис, зачекайти 1 чи кілька секунд і розпізнаний текст автоматично вставиться у поле (час очікування появи тексту залежить від довжини надиктованого тексту, потужності процесору та моделі яку ви використовуєте - за замовчуванням small model).

⭐ **Сподобався проєкт? Поставте зірочку (Star) на GitHub, щоб підтримати український Open Source!**

---

## English
**Ukrainian voice input** is a lightweight and fully local utility for Windows OS that allows you to type text using your voice in Ukrainian in any active window (Word, Telegram, browser, Notepad, etc.). Without sending audio to third-party servers — full privacy thanks to Whisper AI models. All computations run on the CPU.
Yes, I know that more accurate models can be run on a GPU and will work faster. I chose this approach because of the war started by russia, as it is necessary to consider options with lower power consumption and the potential use of PCs without a GPU.

### ✨ Features
- **100% Local**: Your voice data never leaves your computer. During the first start the program loads LLM model for the transcribation in `C:\Users\<User>\.cache\huggingface\hub\...`
- **Global Hotkeys**: Works on top of any application that has an input field.
- **Speed & Accuracy**: Optimized for Ukrainian speech recognition.

### 🚀 How to Run (For Developers)
1. Clone the repository:
   ```bash
   git clone https://github.com/pashokman/ukr_voice_input.git
   cd ukr_voice_input
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python transcribe_voice.py
   ```

### ⌨️ Usage
1. Click inside any text input field. 
2. Press **Ctrl+Space** (configured by default in your script).
3. Dictate text in Ukrainian.
4. Press **Ctrl+Space** again to finish recording, wait 1 or a few seconds, and the transcribed text will automatically be inserted into the field (waiting time depends on the length of the dictated text, processor power, and the model you are using — small model by default).

⭐ **Like the project? Give it a Star on GitHub to support Ukrainian Open Source!**

---