from PIL import ImageGrab

# Координаты области для скриншота (left, top, right, bottom)
bbox = (600, 1000, 1500, 1100)

try:
    # Создаем скриншот указанной области
    screenshot = ImageGrab.grab(bbox=bbox)

    # Сохраняем в файл
    filename = '../screenshot.png'
    screenshot.save(filename)
    print(f'Скриншот сохранен в файл: {filename}')

finally:
    # Освобождаем ресурсы
    screenshot.close()
