import os
from PIL import ImageGrab, Image
import easyocr
import numpy as np
from datetime import datetime
import time
import torch
import tkinter as tk
from threading import Thread, Event
import re
from config import BBOX_COORDS, WARNING_COORDS, DELAY, DELTA_DAYS, SCREENSHOTS, FIRST_WINDOWS
import signal

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

bbox = BBOX_COORDS
bbox2 = WARNING_COORDS
bbox3 = FIRST_WINDOWS
delay = DELAY
delta_days = DELTA_DAYS
quantity_screenshot = SCREENSHOTS


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Скрываем главное окно

        self.warning_window = None
        self.stop_event = Event()
        self.worker_thread = None
        signal.signal(signal.SIGINT, self.signal_handler)
        self.show_startup_notification()

    def show_startup_notification(self):
        """Показывает одноразовое окно уведомления о запуске программы"""
        self.startup_window = tk.Toplevel()
        self.startup_window.title("Программа запущена")

        # Устанавливаем размер и позицию окна из bbox3
        x, y, width, height = bbox3
        self.startup_window.geometry(f"{width}x{height}+{x}+{y}")

        self.startup_window.configure(bg="green")

        label = tk.Label(
            self.startup_window,
            text="Программа мониторинга успешно запущена!",
            font=("Arial", 12),
            bg="green",
            fg="white",
            wraplength=width - 20
        )
        label.pack(expand=True, fill='both')

        # Кнопка закрытия
        close_button = tk.Button(
            self.startup_window,
            text="OK",
            command=self.startup_window.destroy,
            bg="white",
            fg="black"
        )
        close_button.pack(pady=5)

        # Делаем окно поверх всех
        self.startup_window.attributes('-topmost', True)
        self.startup_window.protocol("WM_DELETE_WINDOW", self.startup_window.destroy)

    def show_warning(self, message):
        """Показывает окно с предупреждением в заданной позиции"""
        if self.warning_window is not None:
            try:
                self.warning_window.destroy()
            except:
                pass

        self.warning_window = tk.Toplevel()
        self.warning_window.title("Предупреждение")

        # Устанавливаем размер и позицию окна из bbox2
        x, y, width, height = bbox2
        self.warning_window.geometry(f"{width}x{height}+{x}+{y}")

        self.warning_window.configure(bg="red")

        label = tk.Label(
            self.warning_window,
            text=message,
            font=("Arial", 14),
            bg="red",
            fg="white",
            wraplength=width - 20
        )
        label.pack(expand=True, fill='both')

        # Делаем окно поверх всех
        self.warning_window.attributes('-topmost', True)
        self.warning_window.protocol("WM_DELETE_WINDOW", self.warning_window.destroy)

    def run_worker(self):
        """Основной рабочий цикл"""
        while not self.stop_event.is_set():
            try:
                image = ImageGrab.grab(bbox=bbox)
                image = image.rotate(90, expand=True)
                image_np = np.array(image)

                date = self.extract_date_from_image(image_np)

                if date:
                    current_date = datetime.now()
                    delta = (date - current_date).days

                    # Оригинальная логика обработки дат
                    if delta > delta_days:
                        status = "future"
                        message = f"Ошибка: Дата {date} старше {current_date} более чем на {delta_days} дня!"
                    elif delta >= 0:
                        status = "relevant"
                        message = f"Дата актуальна: {date.strftime('%d.%m.%y')}"
                    else:
                        status = "Not relevant"
                        message = f"Ошибка: Дата {date} не актуальна!"

                    print(message)

                    if status in ["Not relevant", "future"]:
                        self.show_warning(message)
                        self.save_image_with_status(image_np, status)
                else:
                    status = "Not recognized"
                    message = "Дата не распознана."
                    print(message)
                    self.save_image_with_status(image_np, status)

                self.cleanup_old_files()

            except Exception as e:
                print(f"Ошибка: {str(e)}")

            time.sleep(delay)

    @staticmethod
    def extract_date_from_image(image):
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
                    continue

        return None

    @staticmethod
    def save_image_with_status(image, status):
        """Сохраняет изображение с указанием даты, времени, статуса."""
        filename = datetime.now().strftime("%y.%m.%d_%H.%M.%S") + f"_{status}.png"
        filepath = os.path.join(output_folder, filename)
        Image.fromarray(image).save(filepath)
        print(f"Изображение сохранено: {filepath}")

    @staticmethod
    def cleanup_old_files():
        """Удаляет старые файлы (оставляет N последних)"""
        files = sorted(os.listdir(output_folder), key=lambda x: os.path.getmtime(os.path.join(output_folder, x)))
        while len(files) > quantity_screenshot:
            oldest_file = files.pop(0)
            os.remove(os.path.join(output_folder, oldest_file))

    def run(self):
        """Запускает приложение"""
        self.worker_thread = Thread(target=self.run_worker, daemon=True)
        self.worker_thread.start()
        self.root.mainloop()

    def signal_handler(self, signum, frame):
        """Для корректного завершения программы."""
        print("\nЗавершение программы...")
        self.stop_event.set()
        if self.warning_window:
            self.warning_window.destroy()
        self.root.quit()
        self.root.destroy()

if __name__ == "__main__":
    app = App()
    app.run()
