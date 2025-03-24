# pip install easyocr numpy Pillow torch
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# pip install easyocr
import os
import shutil
from PIL import ImageGrab, Image
import easyocr
import numpy as np
from datetime import datetime
import time
import torch
import tkinter as tk
from threading import Thread, Event
import re

# Инициализация EasyOCR
reader = easyocr.Reader(['en'])

if torch.cuda.is_available():
    device = 'cuda'
elif torch.backends.mps.is_available():
    device = 'mps'
else:
    device = 'cpu'

print(f"Использование устройства: {device}")

# Папка для сохранения изображений
output_folder = "screenshots"
os.makedirs(output_folder, exist_ok=True)


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем главное окно, так как оно не нужно

        # Окно предупреждения
        self.warning_window = None
        self.stop_event = Event()
        self.worker_thread = None

    def show_warning(self, message):
        """Показывает окно с предупреждением (только одно)"""
        # Закрываем предыдущее окно, если оно есть
        if self.warning_window is not None:
            try:
                self.warning_window.destroy()
            except:
                pass

        # Создаем новое окно
        self.warning_window = tk.Toplevel()
        self.warning_window.title("Предупреждение")
        self.warning_window.geometry("400x200")
        self.warning_window.configure(bg="red")

        label = tk.Label(
            self.warning_window,
            text=message,
            font=("Arial", 14),
            bg="red",
            fg="white",
            wraplength=380
        )
        label.pack(expand=True, fill='both')

        # Делаем окно поверх всех
        self.warning_window.attributes('-topmost', True)

        # При закрытии окна просто уничтожаем его
        self.warning_window.protocol("WM_DELETE_WINDOW", self.warning_window.destroy)

    def run_worker(self):
        """Основной рабочий цикл"""
        bbox = (185, 350, 245, 450)

        while not self.stop_event.is_set():
            try:
                image = ImageGrab.grab(bbox=bbox)
                image = image.rotate(90, expand=True)
                image_np = np.array(image)

                date = self.extract_date_from_image(image_np)

                if date:
                    current_date = datetime.now()
                    delta = (date - current_date).days

                    # Сохраняем оригинальную логику обработки дат
                    if delta > 4:  # Если дата старше текущей даты более чем на 4 дня
                        status = "future"
                        message = f"Ошибка: Дата {date} старше {current_date} более чем на 4 дня!"
                    elif delta >= 0:  # Если дата в пределах 4 дней в будущем
                        status = "relevant"
                        message = f"Дата актуальна: {date.strftime('%d.%m.%y')}"
                    else:  # Если дата в прошлом
                        status = "Not relevant"
                        message = f"Ошибка: Дата {date} не актуальна!"

                    print(message)

                    # Сохраняем изображение только при ошибках
                    if status in ["Not relevant", "future"]:
                        self.show_warning(message)
                        self.save_image_with_status(image_np, status)
                else:
                    status = "Not recognized"
                    message = "Дата не распознана."
                    print(message)
                    # Сохраняем изображение при ошибке распознавания
                    self.save_image_with_status(image_np, status)

                self.cleanup_old_files()

            except Exception as e:
                error_msg = f"Ошибка: {str(e)}"
                print(error_msg)

            time.sleep(15)

    def extract_date_from_image(self, image):
        """Извлекает дату из изображения"""
        results = reader.readtext(image)
        print(f"Распознанные результаты: {results}")

        for result in results:
            text = result[1].strip()
            print(f"Распознанный текст: {text}")

            date_pattern = re.compile(r"\b(\d{2}\.\d{2}\.\d{2})\b")
            match = date_pattern.search(text)

            if match:
                cleaned_text = match.group(1)
                print(f"Найдена дата: {cleaned_text}")
                try:
                    return datetime.strptime(cleaned_text, "%d.%m.%y")
                except ValueError:
                    print(f"Текст '{cleaned_text}' не соответствует формату даты.")
                    continue

        return None

    def save_image_with_status(self, image, status):
        """Сохраняет изображение с указанием статуса"""
        filename = datetime.now().strftime("%y.%m.%d_%H.%M.%S") + f"_{status}.png"
        filepath = os.path.join(output_folder, filename)
        Image.fromarray(image).save(filepath)
        print(f"Изображение сохранено: {filepath}")

    def cleanup_old_files(self):
        """Удаляет старые файлы, оставляя только 100 последних"""
        files = sorted(os.listdir(output_folder), key=lambda x: os.path.getmtime(os.path.join(output_folder, x)))
        while len(files) > 100:
            oldest_file = files.pop(0)
            os.remove(os.path.join(output_folder, oldest_file))
            print(f"Удален старый файл: {oldest_file}")

    def run(self):
        """Запускает приложение"""
        self.worker_thread = Thread(target=self.run_worker, daemon=True)
        self.worker_thread.start()
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()