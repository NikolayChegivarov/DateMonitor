import os
import shutil
from PIL import ImageGrab, Image
import easyocr
import numpy as np
from datetime import datetime, timedelta
import time
import torch
import tkinter as tk

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
    for result in results:
        text = result[1]
        try:
            # Пытаемся распознать дату в формате "DD.MM.YY"
            date = datetime.strptime(text, "%d.%m.%y")
            return date
        except ValueError:
            continue
    return None


# Функция для проверки актуальности даты
def is_date_actual(date, delta_days=4):
    current_date = datetime.now()
    return current_date - date <= timedelta(days=delta_days)


# Функция для вывода кастомного окна с красным фоном
def show_custom_warning(message):
    warning_window = tk.Tk()
    warning_window.title("Предупреждение")
    warning_window.geometry("400x200")
    warning_window.configure(bg="red")
    label = tk.Label(warning_window, text=message, font=("Arial", 14), bg="red", fg="white")
    label.pack(pady=50)
    ok_button = tk.Button(warning_window, text="OK", command=warning_window.destroy, bg="white", fg="black")
    ok_button.pack()
    warning_window.mainloop()


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
            if date > current_date:
                status = "future"
                message = "Этот день еще не наступил."
            elif not is_date_actual(date):
                status = "Not relevant"
                message = "Ошибка: Дата не актуальна!"
            else:
                status = "relevant"
                message = f"Дата актуальна: {date.strftime('%d.%m.%y')}"

            print(message)
            show_custom_warning(message)
            save_image_with_status(image, status)  # Сохраняем изображение с статусом
        else:
            print("Дата не распознана.")

        cleanup_old_files()  # Удаляем старые файлы, если их больше 100
        time.sleep(5)


if __name__ == "__main__":
    main()
