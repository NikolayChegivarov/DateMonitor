# pip install easyocr numpy Pillow torch
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# pip install easyocr
import os
import shutil
from PIL import ImageGrab, Image
import easyocr
import numpy as np
from datetime import datetime, timedelta
import time
import torch
import tkinter as tk
from threading import Thread
import threading
import re  # Добавлен импорт для работы с регулярными выражениями

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
os.makedirs(output_folder, exist_ok=True)  # Создаем папку, если она не существует


# Функция для захвата определенной области экрана
def capture_screen_area(bbox):
    screenshot = ImageGrab.grab(bbox=bbox)
    # Поворачиваем изображение на 90 градусов (или -90, в зависимости от ориентации текста)
    screenshot = screenshot.rotate(90, expand=True)
    return np.array(screenshot)


# Функция для распознавания даты
def extract_date_from_image(image):
    results = reader.readtext(image)
    print(f"Распознанные результаты: {results}")  # Отладочная информация
    for result in results:
        text = result[1].strip()  # Убираем лишние пробелы
        print(f"Распознанный текст: {text}")  # Отладочная информация

        # Ищем дату в формате DD.MM.YY с помощью регулярного выражения
        date_pattern = re.compile(r"\b(\d{2}\.\d{2}\.\d{2})\b")
        match = date_pattern.search(text)
        if match:
            cleaned_text = match.group(1)  # Извлекаем найденную дату
            print(f"Найдена дата: {cleaned_text}")  # Отладочная информация
            try:
                # Пытаемся распознать дату в формате "DD.MM.YY"
                date = datetime.strptime(cleaned_text, "%d.%m.%y")
                return date
            except ValueError:
                print(f"Текст '{cleaned_text}' не соответствует формату даты.")  # Отладочная информация
                continue
        else:
            print(f"Дата не найдена в тексте: {text}")  # Отладочная информация
    return None


# Функция для вывода кастомного окна с красным фоном
def show_custom_warning(message):
    def show_window():
        warning_window = tk.Tk()
        warning_window.title("Предупреждение")
        warning_window.geometry("400x200")
        warning_window.configure(bg="red")
        label = tk.Label(warning_window, text=message, font=("Arial", 14), bg="red", fg="white")
        label.pack(pady=50)
        ok_button = tk.Button(warning_window, text="OK", command=warning_window.destroy, bg="white", fg="black")
        ok_button.pack()
        warning_window.mainloop()

    # Запускаем окно в отдельном потоке
    Thread(target=show_window).start()


# Функция для сохранения изображения с указанием статуса
def save_image_with_status(image, status):
    # Генерируем имя файла: дата_время_статус.png
    filename = datetime.now().strftime("%y.%m.%d_%H.%M.%S") + f"_{status}.png"
    filepath = os.path.join(output_folder, filename)
    Image.fromarray(image).save(filepath)
    print(f"Изображение сохранено: {filepath}")


# Функция для удаления старых файлов, если их больше 100
def cleanup_old_files():
    files = sorted(os.listdir(output_folder), key=lambda x: os.path.getmtime(os.path.join(output_folder, x)))
    while len(files) > 100:  # Ограничиваем количество файлов до 100
        oldest_file = files.pop(0)
        os.remove(os.path.join(output_folder, oldest_file))
        print(f"Удален старый файл: {oldest_file}")


# Основной цикл программы
def main():
    show_custom_warning("Распознавание даты запущено")
    bbox = (185, 350, 245, 450)  # Область захвата экрана

    while True:
        image = capture_screen_area(bbox)
        date = extract_date_from_image(image)

        if date:
            current_date = datetime.now()
            delta = (date - current_date).days  # Разница в днях между датой на бирке и текущей датой

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

            if status in ["Not relevant", "future"]:
                show_custom_warning(message)  # Показываем сообщение пользователю об ошибках
                save_image_with_status(image, status)  # Сохраняем изображение для ошибок
        else:
            status = "Not recognized"
            print("Дата не распознана.")
            show_custom_warning("Дата не распознана.")
            save_image_with_status(image, status)

        cleanup_old_files()
        time.sleep(15)


if __name__ == "__main__":
    main()
    # thread = threading.Thread(target=main)
    # thread.daemon = True
    # thread.start()
    # time.sleep(30)  # Время работы
    # print("Программа завершена")