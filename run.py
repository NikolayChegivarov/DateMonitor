# pip install easyocr numpy Pillow torch
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# pip install easyocr
import easyocr
import numpy as np
from PIL import ImageGrab
from datetime import datetime, timedelta
import time
import torch

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


# Основной цикл программы
def main():
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
                print("Это будущее еще не наступило. Не торопись ковбой.")
            elif not is_date_actual(date):
                print("Ошибка: Дата не актуальна!")
            else:
                print(f"Дата актуальна: {date.strftime('%d.%m.%y')}")
        else:
            print("Дата не распознана.")

        # Пауза перед следующим захватом экрана
        time.sleep(5)


if __name__ == "__main__":
    main()
