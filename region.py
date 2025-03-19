# pip install pynput Pillow
from pynput.mouse import Controller, Listener
from PIL import ImageGrab
# import time

# Инициализация контроллера мыши
mouse = Controller()


# Функция для ожидания нажатия левой кнопки мыши
def wait_for_mouse_click():
    print("Ожидание нажатия левой кнопки мыши...")

    def on_click(x, y, button, pressed):
        if pressed and button == button.left:
            return False  # Останавливаем слушатель
    with Listener(on_click=on_click) as listener:
        listener.join()
    print("Левая кнопка мыши нажата!")


# Функция для ожидания отпускания левой кнопки мыши
def wait_for_mouse_release():
    print("Ожидание отпускания левой кнопки мыши...")

    def on_click(x, y, button, pressed):
        if not pressed and button == button.left:
            return False  # Останавливаем слушатель
    with Listener(on_click=on_click) as listener:
        listener.join()
    print("Левая кнопка мыши отпущена!")


# Ждем, пока пользователь нажмет левую кнопку мыши
wait_for_mouse_click()

# Фиксируем начальные координаты (левый верхний угол)
start_x, start_y = mouse.position
print(f"Левая верхняя точка: ({start_x}, {start_y})")

# Ждем, пока пользователь отпустит левую кнопку мыши
wait_for_mouse_release()

# Фиксируем конечные координаты (правый нижний угол)
end_x, end_y = mouse.position
print(f"Правая нижняя точка: ({end_x}, {end_y})")

# Формируем bbox
bbox = (
    min(start_x, end_x),  # left
    min(start_y, end_y),  # top
    max(start_x, end_x),  # right
    max(start_y, end_y)   # bottom
)

print(f"Выбранная область: {bbox}")

# Захватываем выбранную область
try:
    print("Захват изображения...")
    screenshot = ImageGrab.grab(bbox=bbox)
    print("Изображение успешно захвачено!")
    screenshot.save("screenshot.png")  # Сохраняем изображение в файл
    print("Изображение сохранено как 'screenshot.png'.")
except Exception as e:
    print(f"Произошла ошибка: {e}")
