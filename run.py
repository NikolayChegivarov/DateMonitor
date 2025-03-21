# pip install easyocr numpy Pillow torch
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# pip install easyocr
import easyocr
import numpy as np
from PIL import ImageGrab
from datetime import datetime, timedelta
import time
import torch
import ctypes

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


# Функция для вывода окна с предупреждением
def show_warning(message):
    ctypes.windll.user32.MessageBoxW(0, message, "DataMonitor", 0x30)  # 0x30 - иконка предупреждения


# Основной цикл программы
def main():
    # Выводим сообщение о запуске
    show_warning("Мониторинг даты запущен!")

    # Определяем область экрана, где появляется бирка с датой (left, top, right, bottom)
    bbox = (593, 357, 756, 448)

    while True:
        # Захватываем область экрана
        image = capture_screen_area(bbox)

        # Распознаем дату
        date = extract_date_from_image(image)

        if date:
            # Проверяем актуальность даты
            current_date = datetime.now()

            if date > current_date:
                message = "Это будущее еще не наступило. Не торопись ковбой."
                print(message)
                show_warning(message)  # Вывод окна с предупреждением
            elif not is_date_actual(date):
                message = "Ошибка: Дата не актуальна!"
                print(message)
                show_warning(message)  # Вывод окна с предупреждением
            else:
                print(f"Дата актуальна: {date.strftime('%d.%m.%y')}")
        else:
            print("Дата не распознана.")

        # Проверка нажатия клавиши (например, 'q' для выхода)
        # if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        #     key = sys.stdin.read(1)
        #     if key == 'q':
        #         print("Скрипт остановлен.")
        #         break

        # Пауза перед следующим захватом экрана
        time.sleep(5)


if __name__ == "__main__":
    main()