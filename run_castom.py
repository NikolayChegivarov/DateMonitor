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
        self.root.title("Мониторинг дат")
        self.root.geometry("400x200")

        # Главное окно нельзя закрыть, только свернуть
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)

        self.message_var = tk.StringVar()
        self.message_var.set("Инициализация...")

        self.label = tk.Label(
            self.root,
            textvariable=self.message_var,
            font=("Arial", 14),
            bg="red",
            fg="white",
            wraplength=380
        )
        self.label.pack(expand=True, fill='both')

        self.stop_event = Event()
        self.worker_thread = None

        # Окно предупреждения
        self.warning_window = None

    def minimize_to_tray(self):
        """Сворачивает окно в трей вместо закрытия"""
        self.root.iconify()

    def show_warning(self, message, is_error=True):
        """Показывает окно с предупреждением (только одно)"""
        # Закрываем предыдущее окно, если оно есть
        if self.warning_window is not None:
            try:
                self.warning_window.destroy()
            except:
                pass

        # Создаем новое окно
        self.warning_window = tk.Toplevel(self.root)
        self.warning_window.title("Предупреждение")
        self.warning_window.geometry("400x200")
        bg_color = "red" if is_error else "green"
        self.warning_window.configure(bg=bg_color)

        label = tk.Label(
            self.warning_window,
            text=message,
            font=("Arial", 14),
            bg=bg_color,
            fg="white",
            wraplength=380
        )
        label.pack(expand=True, fill='both')

        # Делаем окно поверх всех и модальным
        self.warning_window.attributes('-topmost', True)
        self.warning_window.grab_set()

        # При закрытии окна просто уничтожаем его
        self.warning_window.protocol("WM_DELETE_WINDOW", self.warning_window.destroy)

    def update_status(self, message, is_error=False):
        """Обновляет статус в главном окне"""
        self.message_var.set(message)
        self.label.config(bg="red" if is_error else "green")
        self.root.update()

        # Для ошибок показываем отдельное окно
        if is_error:
            self.show_warning(message, is_error)

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

                    if delta > 4:
                        status = "future"
                        message = f"Ошибка: Дата {date.date()} старше текущей на {delta} дней!"
                        is_error = True
                    elif delta >= 0:
                        status = "relevant"
                        message = f"Дата актуальна: {date.strftime('%d.%m.%y')}"
                        is_error = False
                    else:
                        status = "Not relevant"
                        message = f"Ошибка: Дата {date.date()} просрочена на {-delta} дней!"
                        is_error = True

                    print(message)
                    self.save_image_with_status(image_np, status)
                else:
                    status = "Not recognized"
                    message = "Дата не распознана."
                    is_error = True
                    print(message)
                    self.save_image_with_status(image_np, status)

                self.root.after(0, self.update_status, message, is_error)
                self.cleanup_old_files()

            except Exception as e:
                error_msg = f"Ошибка: {str(e)}"
                print(error_msg)
                self.root.after(0, self.update_status, error_msg, True)

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
        self.update_status("Распознавание дат запущено", False)
        self.worker_thread = Thread(target=self.run_worker, daemon=True)
        self.worker_thread.start()
        self.root.mainloop()


if __name__ == "__main__":
    app = App()
    app.run()
    # thread = threading.Thread(target=main)
    # thread.daemon = True
    # thread.start()
    # time.sleep(30)  # Время работы
    # print("Программа завершена")