import shutil
import os
from pathlib import Path

# Пути
COMMON_UTILS = Path("common/utils.py")
FUNCTIONS = ["function1", "function2", "function3"]

for func in FUNCTIONS:
    # Копируем utils.py в функцию
    shutil.copy(COMMON_UTILS, f"{func}/utils.py")
    
    # Создаём ZIP (если нужно)
    shutil.make_archive(f"zips/{func}", "zip", func)