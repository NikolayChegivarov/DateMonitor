# DateMonitor

*Проект создан по заказу производственной компании,  
предназначен для мониторинга определённой зоны экрана  
на наличие ошибки в дате.*

Для работы программ установите зависимости командой  
```bash
pip install -r requirements.txt
```
Или вручную
```bash
pip install easyocr numpy Pillow torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install easyocr
```

Для определения нужной области экрана в формате bbox имеются отдельные скрипты 
в папке Calibration.

Все изменяемые параметры выведены в файл config.py

Для того что бы воспользоваться программой запустите **run_custom.py**.
