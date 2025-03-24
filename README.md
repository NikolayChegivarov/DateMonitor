DateMonitor

Проект создан по заказу производственной компании,  
предназначен для мониторинга определённой зоны экрана  
на наличие ошибки в дате. 

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

Для определения нужной области экрана в формате bbox
запустите скрипт region.py следуйте инструкциям:
Зажмите левую кнопку мыши в левом верхнем углу нужной области,  
проведите к правому нижнему углу, отпустите кнопку мыши. 
Скрипт выведет нужные для bbox координаты. 

Для того что бы воспользоваться программой запустите 
run.py или run_custom.py (они отличаются окном выводящим ошибку).
