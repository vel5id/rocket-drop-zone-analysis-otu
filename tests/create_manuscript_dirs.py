#!/usr/bin/env python3
"""
Создание необходимых директорий для разделов рукописи.
Соответствует Task 2.7: Создание разделов рукописи в outputs/manuscript_sections/
"""

from pathlib import Path
import sys

def create_manuscript_directories():
    """Создать все необходимые директории для разделов рукописи."""
    
    # Основные директории согласно спецификации
    directories = [
        "outputs/manuscript_sections",
        "outputs/validation_framework",
        "outputs/figures",
        "outputs/supplementary_tables",
        "outputs/sensitivity_analysis",
        "logs"
    ]
    
    print("Создание директорий для разделов рукописи...")
    print("=" * 50)
    
    for dir_path in directories:
        path = Path(dir_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Создана: {dir_path}")
        except Exception as e:
            print(f"✗ Ошибка при создании {dir_path}: {e}")
    
    # Создание README файла для manuscript_sections
    readme_content = """# Manuscript Sections
## Rocket Drop Zone Analysis - OTU Pipeline

### Структура разделов рукописи:

1. **Abstract/** - Аннотация
2. **Introduction/** - Введение
3. **Materials_Methods/** - Материалы и методы
4. **Results/** - Результаты
5. **Discussion/** - Обсуждение
6. **Conclusion/** - Заключение
7. **Validation_Framework/** - Фреймворк валидации (Task 2.7)
8. **Sensitivity_Analysis/** - Анализ чувствительности
9. **Economic_Analysis/** - Экономический анализ

### Файлы, созданные Task 2.7:
- validation_section_manuscript.txt - Полный раздел валидации
- validation_section_manuscript.tex - LaTeX версия
- Validation_Framework_Section.md - Основной раздел
- Validation_Methods.tex - Методы валидации в LaTeX

### Ссылки на спецификацию:
- Task 2.7: Validation Section in Manuscript (БЛОК 2)
- IMPLEMENTATION_ROADMAP.md, строки 196-219
"""

    readme_path = Path("outputs/manuscript_sections/README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print(f"✓ Создан: {readme_path}")
    
    print("\n" + "=" * 50)
    print("Директории успешно созданы!")
    print("Теперь можно запустить validation_section_manuscript.py")
    
    return True

if __name__ == "__main__":
    create_manuscript_directories()