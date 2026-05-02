import torch

assert torch.cuda.is_available(), "CUDA AKTİF DEĞİL!"
print("GPU:", torch.cuda.get_device_name(0))