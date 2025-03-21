# pip install easyocr numpy Pillow torch
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# pip install easyocr
import easyocr
import numpy as np
from PIL import ImageGrab
from datetime import datetime, timedelta
import time
import torch
import tkinter as tk  # Для создания кастомных окон
from tkinter import messagebox  # Для стандартных окон (не используется здесь)

# Инициализация EasyOCR
reader = easyocr.Reader(['en'])

if torch.cuda.is_available():
    device = 'cuda'
elif torch.backends.mps.is_available():
    device = 'mps'
else:
    device = 'cpu'

print(f"Использование устройства: {device}")


# Функция для захвата определенной области экрана
def capture_screen_area(bbox):
    screenshot = ImageGrab.grab(bbox=bbox)
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
    # Создаем окно
    warning_window = tk.Tk()
    warning_window.title("Предупреждение")
    warning_window.geometry("400x200")  # Размер окна
    warning_window.configure(bg="red")  # Красный фон

    # Добавляем текст сообщения
    label = tk.Label(warning_window, text=message, font=("Arial", 14), bg="red", fg="white")
    label.pack(pady=50)

    # Добавляем кнопку "ОК"
    ok_button = tk.Button(warning_window, text="OK", command=warning_window.destroy, bg="white", fg="black")
    ok_button.pack()

    # Запускаем главный цикл окна
    warning_window.mainloop()


# Основной цикл программы
def main():
    # Сначала показываем сообщение о запуске
    show_custom_warning("Распознавание даты запущено")

    # Определяем область экрана, где появляется бирка с датой (left, top, right, bottom)
    bbox = (1200, 1000, 1500, 1100)

    while True:
        # Захватываем область экрана
        image = capture_screen_area(bbox)

        # Распознаем дату
        date = extract_date_from_image(image)

        if date:
            # Проверяем актуальность даты
            current_date = datetime.now()

            if date > current_date:
                message = "Этот день еще не наступил."
                print(message)
                show_custom_warning(message)  # Вывод кастомного окна с предупреждением
            elif not is_date_actual(date):
                message = "Ошибка: Дата не актуальна!"
                print(message)
                show_custom_warning(message)  # Вывод кастомного окна с предупреждением
            else:
                print(f"Дата актуальна: {date.strftime('%d.%m.%y')}")
        else:
            print("Дата не распознана.")

        # Пауза перед следующим захватом экрана
        time.sleep(5)


if __name__ == "__main__":
    main()
