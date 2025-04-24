import shutil
import os
import re
from pathlib import Path
from typing import Set

# Конфигурация
COMMON_DIR = Path("common")  # Папка общих файлов
# Собираемые функции
FUNCTIONS = [
    "auth-func", 
    "base-gateway", 
    "device-manager",
    "track-manager"
    ]  
BUILD_DIR = "build"          # Временная папка (там будут собранные функции)
ZIP_OUTPUT = "zips"          # Папка для архивов

def fix_imports(file_path: Path) -> None:
    """Заменяет `from common.file` на `from file`."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = re.sub(
        r"from\s+common\.([a-zA-Z0-9_]+)\s+import",
        r"from \1 import",
        content
    )
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

def find_used_common_files(func_dir: Path) -> Set[str]:
    """Находит все общие файлы, которые импортируются в функции."""
    used_files = set()
    
    for py_file in func_dir.glob("*.py"):
        with open(py_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Ищем все импорты вида `from common.{file}`
        matches = re.finditer(
            r"from\s+common\.([a-zA-Z0-9_]+)\s+import",
            content
        )
        for match in matches:
            used_files.add(f"{match.group(1)}.py")
    
    return used_files

# Очистка старых файлов
shutil.rmtree(BUILD_DIR, ignore_errors=True)
shutil.rmtree(ZIP_OUTPUT, ignore_errors=True)
os.makedirs(BUILD_DIR, exist_ok=True)
os.makedirs(ZIP_OUTPUT, exist_ok=True)

for func in FUNCTIONS:
    func_src = Path(func)
    func_build = Path(BUILD_DIR) / func
    
    # 1. Копируем исходники функции (без __pycache__)
    shutil.copytree(func_src, func_build, ignore=shutil.ignore_patterns("__pycache__"))
    
    # 2. Исправляем импорты
    for py_file in func_build.glob("*.py"):
        fix_imports(py_file)
    
    # 3. Копируем ТОЛЬКО используемые общие файлы
    used_files = find_used_common_files(func_build)
    for common_file in COMMON_DIR.glob("*.py"):
        if common_file.name in used_files:
            shutil.copy(common_file, func_build / common_file.name)
    
    # 4. Создаём ZIP
    shutil.make_archive(f"{ZIP_OUTPUT}/{func}", "zip", func_build)

print(f"✅ Сборка завершена! Архивы в '{ZIP_OUTPUT}/'")