import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
# print(f"GPU count: {torch.cuda.device_count()}")
# print(f"GPU name: {torch.cuda.get_device_name(0)}")
print(torch.cuda.is_available())  # Должно вернуть True, если GPU доступен
print(torch.cuda.device_count())  # Количество доступных GPU
print(torch.cuda.get_device_name(0))  # Имя первого GPU