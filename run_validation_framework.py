import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем скрипт
from scripts.validation_framework_implementation import main

if __name__ == "__main__":
    main()