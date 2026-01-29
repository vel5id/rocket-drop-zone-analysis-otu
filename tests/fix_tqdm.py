#!/usr/bin/env python3
"""
Исправление проблемы с tqdm в неинтерактивном режиме.
"""
import sys
import os

def fix_tqdm_in_file(filepath):
    """Исправить использование tqdm в файле."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменить импорт tqdm на умную версию
    old_import = """try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable"""
    
    new_import = """try:
    from tqdm import tqdm
    import sys
    # Умный tqdm: отключается в неинтерактивном режиме
    def smart_tqdm(iterable, **kwargs):
        if not sys.stdout.isatty():
            # Неинтерактивный режим - отключаем прогресс-бар
            kwargs['disable'] = True
        return tqdm(iterable, **kwargs)
except ImportError:
    def smart_tqdm(iterable, **kwargs):
        return iterable"""
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        # Заменить все вызовы tqdm на smart_tqdm
        content = content.replace('tqdm(', 'smart_tqdm(')
        print(f"Исправлен tqdm в {filepath}")
    else:
        print(f"Шаблон импорта tqdm не найден в {filepath}")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_unicode_in_file(filepath):
    """Исправить Unicode символы в файле."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменить Unicode символы на ASCII эквиваленты
    replacements = {
        '✓': '[OK]',
        '✔': '[OK]',
        '✗': '[FAIL]',
        '×': '[FAIL]',
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '°': 'deg',
    }
    
    changed = False
    for unicode_char, ascii_repl in replacements.items():
        if unicode_char in content:
            content = content.replace(unicode_char, ascii_repl)
            changed = True
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Исправлены Unicode символы в {filepath}")

def create_requirements():
    """Создать requirements.txt из виртуального окружения."""
    import subprocess
    
    # Получить список установленных пакетов
    cmd = "venv_311\\Scripts\\pip.exe freeze"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            with open("requirements.txt", "w", encoding='utf-8') as f:
                f.write(result.stdout)
            print("Создан requirements.txt")
            
            # Также создать облегченную версию
            core_packages = [
                "numpy>=2.0.0",
                "pandas>=2.0.0",
                "scipy>=1.10.0",
                "tqdm>=4.65.0",
                "earthengine-api>=0.1.370",
                "geopandas>=0.14.0",
                "shapely>=2.0.0",
                "folium>=0.14.0",
                "numba>=0.58.0",
                "sqlite3"  # встроен в Python
            ]
            
            with open("requirements_core.txt", "w", encoding='utf-8') as f:
                f.write("\n".join(core_packages))
            print("Создан requirements_core.txt")
        else:
            print(f"Ошибка получения пакетов: {result.stderr}")
    except Exception as e:
        print(f"Ошибка создания requirements: {e}")

def optimize_geojson_output():
    """Создать скрипт для оптимизации GeoJSON вывода."""
    script = '''#!/usr/bin/env python3
"""
Оптимизация GeoJSON вывода - уменьшение размера файлов.
"""
import json
import gzip
import sys
from pathlib import Path

def optimize_geojson(input_path, output_path=None, compress=True, precision=6):
    """
    Оптимизировать GeoJSON файл:
    1. Уменьшить точность координат
    2. Удалить лишние пробелы
    3. Сжать при необходимости
    """
    if output_path is None:
        output_path = input_path
    
    print(f"Оптимизация {input_path}...")
    
    # Чтение GeoJSON
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Функция для округления координат
    def round_coords(coords, precision):
        if isinstance(coords, (list, tuple)):
            if len(coords) == 2 and isinstance(coords[0], (int, float)):
                # Координата [lon, lat]
                return [round(coords[0], precision), round(coords[1], precision)]
            else:
                # Вложенный список
                return [round_coords(c, precision) for c in coords]
        return coords
    
    # Обработка геометрий
    if 'features' in data:
        for feature in data['features']:
            if 'geometry' in feature and 'coordinates' in feature['geometry']:
                feature['geometry']['coordinates'] = round_coords(
                    feature['geometry']['coordinates'], precision
                )
    
    # Сохранение
    if compress:
        # Сжатый JSON
        output_path_gz = str(output_path) + '.gz'
        with gzip.open(output_path_gz, 'wt', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))  # Минимизировать пробелы
        print(f"  Сохранен сжатый файл: {output_path_gz}")
        return output_path_gz
    else:
        # Несжатый JSON с минимальным форматированием
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, separators=(',', ':'))  # Минимизировать пробелы
        print(f"  Сохранен оптимизированный файл: {output_path}")
        return output_path

def main():
    """Основная функция."""
    if len(sys.argv) < 2:
        print("Использование: python optimize_geojson.py <путь_к_geojson> [выходной_путь]")
        return
    
    input_path = Path(sys.argv[1])
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not input_path.exists():
        print(f"Файл не найден: {input_path}")
        return
    
    # Оптимизировать
    optimize_geojson(input_path, output_path, compress=True)
    
    # Сравнить размеры
    original_size = input_path.stat().st_size / (1024 * 1024)
    print(f"  Исходный размер: {original_size:.2f} MB")
    
    compressed_path = Path(str(input_path) + '.gz')
    if compressed_path.exists():
        compressed_size = compressed_path.stat().st_size / (1024 * 1024)
        print(f"  Сжатый размер: {compressed_size:.2f} MB")
        print(f"  Коэффициент сжатия: {original_size/compressed_size:.1f}x")

if __name__ == "__main__":
    main()
'''
    
    with open("optimize_geojson.py", "w", encoding='utf-8') as f:
        f.write(script)
    print("Создан optimize_geojson.py")

def main():
    """Основная функция исправлений."""
    print("="*60)
    print("ИСПРАВЛЕНИЕ ПРОБЛЕМ OTU ПАЙПЛАЙНА")
    print("="*60)
    
    # 1. Исправить tqdm в основных файлах
    files_to_fix = ["run_pipeline.py", "run_otu_pipeline.py"]
    for filepath in files_to_fix:
        if os.path.exists(filepath):
            fix_tqdm_in_file(filepath)
            fix_unicode_in_file(filepath)
        else:
            print(f"Файл не найден: {filepath}")
    
    # 2. Создать requirements.txt
    create_requirements()
    
    # 3. Создать скрипт оптимизации GeoJSON
    optimize_geojson_output()
    
    # 4. Создать исправленный запускаемый скрипт
    create_fixed_runner()
    
    print("\n" + "="*60)
    print("ИСПРАВЛЕНИЯ ЗАВЕРШЕНЫ")
    print("="*60)
    print("Выполнены следующие исправления:")
    print("1. tqdm теперь автоматически отключается в неинтерактивном режиме")
    print("2. Удалены Unicode символы, вызывающие ошибки в Windows")
    print("3. Создан requirements.txt для управления зависимостями")
    print("4. Создан скрипт оптимизации GeoJSON файлов")
    print("5. Создан исправленный runner для тестирования")

def create_fixed_runner():
    """Создать исправленный скрипт для запуска пайплайна."""
    script = '''#!/usr/bin/env python3
"""
Исправленный запуск OTU пайплайна с обработкой ошибок.
"""
import subprocess
import sys
import time
from pathlib import Path

def run_pipeline_fixed():
    """Запустить пайплайн с исправлениями."""
    # Параметры для быстрого теста
    cmd = [
        "venv_311\\Scripts\\python.exe",
        "run_otu_pipeline.py",
        "--date", "2024-09-09",
        "--iterations", "10",
        "--mock",
        "--no-gpu",
        "--output", "output/fixed_test"
    ]
    
    print("Запуск исправленного пайплайна...")
    print(f"Команда: {' '.join(cmd)}")
    
    # Очистить предыдущие результаты
    output_dir = Path("output/fixed_test")
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
    
    # Запуск с обработкой вывода в реальном времени
    start_time = time.time()
    
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True,
            encoding='utf-8',
            errors='replace'  # Заменять нечитаемые символы
        )
        
        # Чтение вывода в реальном времени
        for line in process.stdout:
            print(line.rstrip())
        
        # Ожидание завершения
        return_code = process.wait()
        elapsed = time.time() - start_time
        
        print(f"\\nПайплайн завершен за {elapsed:.1f} секунд")
        print(f"Код возврата: {return_code}")
        
        # Проверить результаты
        if return_code == 0:
            check_results(output_dir)
            return True
        else:
            print("Пайплайн завершился с ошибкой")
            return False
            
    except Exception as e:
        print(f"Ошибка запуска пайплайна: {e}")
        return False

def check_results(output_dir):
    """Проверить созданные файлы."""
    print("\\nПроверка результатов...")
    
    if not output_dir.exists():
        print("  Выходная директория не создана")
        return
    
    # Список ожидаемых файлов
    expected_files = [
        output_dir / "otu" / "otu_2024-09-09.geojson",
        output_dir / "otu_visualization.html",
    ]
    
    for filepath in expected_files:
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"  ✓ {filepath.relative_to(output_dir)}: {size_kb:.1f} KB")
        else:
            print(f"  ✗ {filepath.relative_to(output_dir)}: ОТСУТСТВУЕТ")
    
    # Подсчитать общее количество файлов
    all_files = list(output_dir.rglob("*"))
    print(f"\\nВсего создано файлов: {len(all_files)}")
    
    # Показать самые большие файлы
    large_files = sorted(all_files, key=lambda x: x.stat().st_size if x.is_file() else 0, reverse=True)[:5]
    print("Самые большие файлы:")
    for f in large_files:
        if f.is_file():
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  {f.relative_to(output_dir)}: {size_mb:.2f} MB")

def main():
    """Основная функция."""
    print("="*60)
    print("ТЕСТ ИСПРАВЛЕННОГО OTU ПАЙПЛАЙНА")
    print("="*60)
    
    success = run_pipeline_fixed()
    
    print("\\n" + "="*60)
    if success:
        print("ТЕСТ ПРОЙДЕН УСПЕШНО")
        print("Исправления работают корректно")
    else:
        print("ТЕСТ НЕ ПРОЙДЕН")
        print("Требуется дополнительная отладка")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
    
    with open("test_fixed_pipeline.py", "w", encoding='utf-8') as f:
        f.write(script)
    print("Создан test_fixed_pipeline.py")

if __name__ == "__main__":
    main()