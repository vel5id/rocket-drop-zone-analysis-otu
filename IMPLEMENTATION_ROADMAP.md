# 🗺️ ПЛАН РЕАЛИЗАЦИИ ОСТАВШИХСЯ ЗАДАЧ
## Rocket Drop Zone Analysis - OTU Pipeline

**Дата создания:** 2026-01-28  
**Текущий прогресс:** 14/35 задач (40%)  
**Оставшихся задач:** 21  

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ

### ✅ Завершено (14 задач):
- **БЛОК 1:** 7/7 (100%) - Методология и данные
- **БЛОК 2:** 3/8 (38%) - Валидация (скрипты созданы)
- **БЛОК 3:** 4/9 (44%) - Визуализация (инструменты готовы)
- **БЛОК 4:** 0/6 (0%) - Язык и литература
- **БЛОК 5:** 0/5 (0%) - Экономический анализ

### ⚠️ Критические находки:
1. **Скрипты созданы, но не выполнены** - Tasks 2.1-2.3, 3.7-3.8
2. **Экономический модуль частично реализован** - в `run_otu_pipeline.py`
3. **Визуализация работает** - 9 HTML карт созданы
4. **Документация отсутствует** - БЛОК 4 не начат

---

## 🎯 ПРИОРИТИЗАЦИЯ ЗАДАЧ

### Уровень 1: КРИТИЧНО (должно быть выполнено)
1. Task 2.4: Интеграция результатов анализа чувствительности
2. Task 2.5-2.7: Фреймворк валидации
3. Task FD.1-FD.3: Финальные deliverables

### Уровень 2: ВАЖНО (значительно улучшит качество)
1. Task 3.3-3.6: Улучшение фигур
2. Task 3.9: Упаковка supplementary materials
3. Task 4.1-4.4: Языковая правка

### Уровень 3: ЖЕЛАТЕЛЬНО (nice to have)
1. Task 2.8: Анализ неопределенности
2. Task 5.1-5.5: Детальный экономический анализ
3. Task 4.5: Профессиональная правка

---

## 📋 ДЕТАЛЬНЫЙ ПЛАН РЕАЛИЗАЦИИ

---

## 🔴 БЛОК 2: ВАЛИДАЦИЯ И АНАЛИЗ (5 задач осталось)

### Task 2.4: Sensitivity Results Integration ⚡ ПРИОРИТЕТ 1

**Статус:** Не начата  
**Зависимости:** Tasks 2.1-2.3 (скрипты готовы, нужно выполнить)  
**Срок:** Day 2 (сегодня + 1 день)

**Шаги реализации:**

1. **Выполнить скрипты анализа чувствительности**
   ```bash
   # OAT Analysis
   venv_311\Scripts\python.exe scripts/sensitivity_analysis_oat.py
   
   # Monte Carlo Analysis
   venv_311\Scripts\python.exe scripts/sensitivity_analysis_monte_carlo_complete.py
   
   # Sobol Indices
   venv_311\Scripts\python.exe scripts/sensitivity_analysis_sobol_complete.py
   ```

2. **Создать скрипт интеграции результатов**
   - Файл: `scripts/create_sensitivity_integration.py`
   - Функции:
     - Загрузка всех результатов (OAT, MC, Sobol)
     - Создание Supplementary Figure S1 (комбинированные графики)
     - Создание Supplementary Table S4 (численные результаты)
     - Генерация текста для раздела "Sensitivity Analysis"

3. **Deliverables:**
   - `outputs/sensitivity_analysis/Figure_S1_Combined_Sensitivity.png` (300 DPI)
   - `outputs/supplementary_tables/Table_S4_Sensitivity_Results.xlsx/csv/tex`
   - `outputs/manuscript_sections/Sensitivity_Analysis_Section.md`
   - `outputs/manuscript_sections/Discussion_Sensitivity_Interpretation.md`

**Код для реализации:**
```python
# scripts/create_sensitivity_integration.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

class SensitivityIntegrator:
    def __init__(self, results_dir="outputs/sensitivity_analysis"):
        self.results_dir = Path(results_dir)
        
    def load_all_results(self):
        """Load OAT, MC, Sobol results"""
        oat = pd.read_excel(self.results_dir / "sensitivity_analysis_results.xlsx")
        mc = pd.read_excel(self.results_dir / "monte_carlo_results.xlsx")
        sobol = pd.read_excel(self.results_dir / "sobol_indices.xlsx")
        return oat, mc, sobol
    
    def create_figure_s1(self, oat, mc, sobol):
        """Create combined sensitivity figure"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=300)
        # Plot OAT results
        # Plot MC distributions
        # Plot Sobol indices
        # Add labels, legends
        plt.savefig(self.results_dir / "Figure_S1_Combined_Sensitivity.png")
    
    def create_table_s4(self, oat, mc, sobol):
        """Create numerical results table"""
        # Combine all metrics
        # Export to Excel/CSV/LaTeX
        pass
    
    def generate_manuscript_text(self):
        """Generate text for manuscript"""
        # Sensitivity Analysis section
        # Discussion interpretation
        pass
```

---

### Task 2.5: Validation Framework Design ⚡ ПРИОРИТЕТ 1

**Статус:** Не начата  
**Срок:** Day 3

**Шаги реализации:**

1. **Создать скрипт дизайна валидации**
   - Файл: `scripts/create_validation_framework_design.py`
   - Уже существует: `scripts/validation_framework_design_complete.py`
   - **Действие:** Выполнить существующий скрипт

2. **Определить протоколы сбора данных**
   - Field sampling protocol (GPS coordinates, soil samples, vegetation surveys)
   - Remote sensing validation (ground truth points)
   - Temporal validation (multi-date comparison)

3. **Определить метрики валидации**
   - Correlation coefficient (Pearson's r)
   - Cohen's Kappa (classification agreement)
   - ANOVA (statistical significance)
   - RMSE (root mean square error)

4. **Определить критерии успеха**
   - r > 0.7 (strong correlation)
   - Kappa > 0.6 (substantial agreement)
   - p < 0.05 (statistical significance)

5. **Deliverables:**
   - `outputs/validation/Validation_Framework_Design.pdf`
   - `outputs/validation/Data_Collection_Protocol.md`
   - `outputs/validation/Success_Criteria.xlsx`

---

### Task 2.6: Validation Framework Implementation ⚡ ПРИОРИТЕТ 1

**Статус:** Не начата  
**Срок:** Day 4

**Шаги реализации:**

1. **Выполнить существующий скрипт**
   ```bash
   venv_311\Scripts\python.exe scripts/validation_framework_implementation.py
   ```

2. **Создать класс ValidationFramework**
   - Уже реализован в скрипте
   - Добавить методы:
     - `simulate_field_data()` - генерация симулированных полевых данных
     - `calculate_metrics()` - расчет всех метрик
     - `generate_report()` - создание отчета

3. **Создать Supplementary Figure S2**
   - Validation workflow diagram
   - Scatter plots (predicted vs observed)
   - Confusion matrix
   - Residual plots

4. **Deliverables:**
   - `outputs/validation/Figure_S2_Validation_Workflow.png`
   - `outputs/validation/Validation_Results.xlsx`
   - `outputs/validation/Validation_Report.pdf`

---

### Task 2.7: Validation Section in Manuscript ⚡ ПРИОРИТЕТ 1

**Статус:** Не начата  
**Срок:** Day 5

**Шаги реализации:**

1. **Выполнить существующий скрипт**
   ```bash
   venv_311\Scripts\python.exe scripts/validation_section_manuscript.py
   ```

2. **Написать раздел "Validation Framework"**
   - Структура:
     - 4.1 Data Collection Protocols
     - 4.2 Validation Metrics
     - 4.3 Success Criteria
     - 4.4 Implementation Timeline

3. **Deliverables:**
   - `outputs/manuscript_sections/Validation_Framework_Section.md`
   - `outputs/manuscript_sections/Validation_Methods.tex`

---

### Task 2.8: Uncertainty Analysis 🟡 ПРИОРИТЕТ 2

**Статус:** Не начата  
**Срок:** Day 6

**Шаги реализации:**

1. **Выполнить существующий скрипт**
   ```bash
   venv_311\Scripts\python.exe scripts/uncertainty_analysis.py
   ```

2. **Добавить раздел об источниках неопределенности**
   - DEM uncertainty: ±10-15m (SRTM specification)
   - NDVI variability: ±0.1-0.15 (seasonal, atmospheric)
   - Ballistic accuracy: ±500m (Monte Carlo std)
   - Soil data uncertainty: ±20% (SoilGrids accuracy)

3. **Предложить методы propagation of uncertainty**
   - Monte Carlo propagation
   - First-order Taylor series
   - Sensitivity-based bounds

4. **Deliverables:**
   - `outputs/uncertainty/Uncertainty_Analysis_Report.md`
   - `outputs/uncertainty/Uncertainty_Propagation.xlsx`
   - `outputs/manuscript_sections/Uncertainty_Discussion.md`

---

## 🟡 БЛОК 3: ВИЗУАЛИЗАЦИЯ И ДОКУМЕНТАЦИЯ (5 задач осталось)

### Task 3.3: Enhance Specific Figures (Group 1) 🟡 ПРИОРИТЕТ 2

**Статус:** Не начата  
**Срок:** Day 7-8

**Шаги реализации:**

1. **Создать скрипт улучшения фигур**
   - Файл: `scripts/enhance_figures_group1.py`
   - Использовать `FigureEnhancer` из `figure_enhancement_complete.py`

2. **Улучшить конкретные фигуры:**
   - **Figure 6: Topographic map**
     - ADD: North arrow (top-right)
     - ADD: Scale bar (bottom-left, metric)
     - ENHANCE: Contour labels (font ≥10pt)
   
   - **Figure 7: OTU grid**
     - IMPROVE: Cell labels (font ≥10pt)
     - ADD: Colorbar with clear ticks
     - ENHANCE: Legend positioning
   
   - **Figure 8: NDVI map**
     - ADD: Colorblind-friendly scheme (viridis)
     - ADD: Hatching patterns for accessibility
     - ENHANCE: Contrast (histogram equalization)
   
   - **Figure 9: Soil quality**
     - ADD: Scale bar
     - ENHANCE: Contrast (CLAHE)
     - IMPROVE: Legend clarity

3. **Код для реализации:**
```python
# scripts/enhance_figures_group1.py
from scripts.figure_enhancement_complete import FigureEnhancer
import matplotlib.pyplot as plt

enhancer = FigureEnhancer()

# Figure 6: Topographic map
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
# Load topographic data
# Plot contours
enhancer.add_north_arrow(ax, position='top-right')
enhancer.add_scale_bar(ax, length_km=10, position='bottom-left')
# Enhance labels
plt.savefig('outputs/figures/Figure_6_Topographic_Enhanced.png', dpi=300)

# Repeat for Figures 7-9
```

4. **Deliverables:**
   - `outputs/figures/Figure_6_Topographic_Enhanced.png` (300 DPI)
   - `outputs/figures/Figure_7_OTU_Grid_Enhanced.png` (300 DPI)
   - `outputs/figures/Figure_8_NDVI_Enhanced.png` (300 DPI)
   - `outputs/figures/Figure_9_Soil_Quality_Enhanced.png` (300 DPI)

---

### Task 3.4: Enhance Specific Figures (Group 2) 🟡 ПРИОРИТЕТ 2

**Статус:** Не начата  
**Срок:** Day 9-10

**Аналогично Task 3.3, но для Figures 10-16**

---

### Task 3.5: Simplify Flowcharts 🟡 ПРИОРИТЕТ 2

**Статус:** Не начата  
**Срок:** Day 11

**Шаги реализации:**

1. **Redesign Figure 4 (IAS architecture)**
   - Reduce text in boxes (max 5 words per box)
   - Use minimum 12pt fonts
   - Simplify arrows (remove redundant connections)
   - Move detailed text to caption

2. **Redesign Figure 5 (IAS detailed)**
   - Consider merging with Figure 4
   - Or: Create hierarchical view (overview + detail)
   - Simplify component labels

3. **Tools:**
   - Use draw.io or Inkscape for vector graphics
   - Export as SVG + PNG (300 DPI)

4. **Deliverables:**
   - `outputs/figures/Figure_4_IAS_Architecture_Simplified.svg`
   - `outputs/figures/Figure_5_IAS_Detailed_Simplified.svg`
   - Updated captions in `outputs/manuscript_sections/Figure_Captions.md`

---

### Task 3.6: Final Map - Figure 18 🟡 ПРИОРИТЕТ 2

**Статус:** Не начата  
**Срок:** Day 12

**Шаги реализации:**

1. **Apply ALL improvements to Figure 18**
   - Colorblind-friendly palette (viridis or RdYlGn)
   - Hatching patterns for OTU classes
   - North arrow (top-right)
   - Scale bar (bottom-left, 10 km)
   - Clear legend (font ≥10pt)
   - Export at 300 DPI

2. **Код:**
```python
# scripts/create_figure_18_final.py
from scripts.figure_enhancement_complete import FigureEnhancer
import matplotlib.pyplot as plt
import geopandas as gpd

enhancer = FigureEnhancer()

# Load OTU data
otu_data = gpd.read_file('output/otu/otu_2024-09-09.geojson')

# Create figure
fig, ax = plt.subplots(figsize=(12, 10), dpi=300)

# Plot OTU with colorblind-friendly scheme
cmap = enhancer.create_colorblind_friendly_cmap('viridis')
otu_data.plot(column='q_otu', cmap=cmap, ax=ax, legend=True)

# Add enhancements
enhancer.add_north_arrow(ax, position='top-right')
enhancer.add_scale_bar(ax, length_km=10, position='bottom-left')

# Add hatching for accessibility
# (code for hatching patterns)

plt.savefig('outputs/figures/Figure_18_Recommended_OTUs_Final.png', dpi=300, bbox_inches='tight')
```

3. **Deliverables:**
   - `outputs/figures/Figure_18_Recommended_OTUs_Final.png` (300 DPI)
   - `outputs/figures/Figure_18_Recommended_OTUs_Final.svg` (vector)

---

### Task 3.9: Supplementary Materials Package 🟡 ПРИОРИТЕТ 2

**Статус:** Не начата  
**Срок:** Day 13

**Шаги реализации:**

1. **Выполнить существующий скрипт**
   ```bash
   venv_311\Scripts\python.exe scripts/supplementary_materials_package.py
   ```

2. **Собрать все Tables S1-S7**
   - Table S1: Sentinel-2 scenes ✅ (готова)
   - Table S2: Soil quality coefficients ✅ (готова)
   - Table S3: Protodyakonov strength ✅ (готова)
   - Table S4: Sensitivity results ⚠️ (нужно создать)
   - Table S5: OTU distribution ✅ (скрипт готов)
   - Table S6: Weighting coefficients ✅ (скрипт готов)
   - Table S7: Economic cost breakdown ⚠️ (нужно создать)

3. **Собрать все Figures S1-S2**
   - Figure S1: Combined sensitivity plots ⚠️ (нужно создать)
   - Figure S2: Validation workflow ⚠️ (нужно создать)

4. **Создать README для supplementary materials**
   ```markdown
   # Supplementary Materials
   ## Rocket Drop Zone Analysis - OTU Pipeline
   
   ### Tables
   - Table S1: Sentinel-2 Scene Metadata
   - Table S2: Soil Quality Coefficients (Bonitet)
   - Table S3: Protodyakonov Strength Coefficients
   - Table S4: Sensitivity Analysis Results
   - Table S5: OTU Distribution by Stability Class
   - Table S6: Weighting Coefficients Rationale
   - Table S7: Economic Cost Breakdown
   
   ### Figures
   - Figure S1: Combined Sensitivity Analysis
   - Figure S2: Validation Framework Workflow
   
   ### Data Files
   - otu_2024-09-09.geojson: OTU grid data
   - impact_points_primary.geojson: Primary impact points
   - impact_points_fragments.geojson: Fragment impact points
   ```

5. **Упаковать в ZIP архив**
   ```python
   import zipfile
   from pathlib import Path
   
   def create_supplementary_package():
       with zipfile.ZipFile('outputs/Supplementary_Materials.zip', 'w') as zipf:
           # Add all tables
           for table in Path('outputs/supplementary_tables').glob('*.xlsx'):
               zipf.write(table, f'tables/{table.name}')
           
           # Add all figures
           for fig in Path('outputs/figures').glob('Figure_S*.png'):
               zipf.write(fig, f'figures/{fig.name}')
           
           # Add README
           zipf.write('outputs/supplementary_materials/README.md', 'README.md')
   ```

6. **Deliverables:**
   - `outputs/Supplementary_Materials.zip`
   - `outputs/supplementary_materials/README.md`
   - `outputs/supplementary_materials/File_Manifest.xlsx`

---

## 🟡 БЛОК 4: ЯЗЫК И ЛИТЕРАТУРА (6 задач)

### Task 4.1: Automated Language Check 🟡 ПРИОРИТЕТ 2

**Статус:** Не начата  
**Срок:** Day 14

**Шаги реализации:**

1. **Установить LanguageTool**
   ```bash
   pip install language-tool-python
   ```

2. **Создать скрипт проверки**
   ```python
   # scripts/automated_language_check.py
   import language_tool_python
   import pandas as pd
   from pathlib import Path
   
   tool = language_tool_python.LanguageTool('en-US')
   
   def check_manuscript(text_file):
       with open(text_file, 'r', encoding='utf-8') as f:
           text = f.read()
       
       matches = tool.check(text)
       
       errors = []
       for match in matches:
           errors.append({
               'Line': match.context,
               'Error Type': match.ruleId,
               'Message': match.message,
               'Suggestion': match.replacements[:3] if match.replacements else []
           })
       
       df = pd.DataFrame(errors)
       df.to_excel('outputs/language_check/Grammar_Errors_Report.xlsx', index=False)
       
       return df
   ```

3. **Запустить на всех разделах рукописи**
   - Abstract
   - Introduction
   - Materials & Methods
   - Results
   - Discussion
   - Conclusion

4. **Deliverables:**
   - `outputs/language_check/Grammar_Errors_Report.xlsx`
   - `outputs/language_check/Article_Usage_Issues.xlsx`
   - `outputs/language_check/Language_Check_Summary.md`

---

### Tasks 4.2-4.3: Manual Language Editing 🟡 ПРИОРИТЕТ 3

**Статус:** Не начаты  
**Срок:** Day 15-17

**Шаги:**
1. Исправить артикли (a/an/the)
2. Исправить subject-verb agreement
3. Упростить сложные предложения (>30 words)
4. Активный залог вместо пассивного
5. Исправить literal translations from Russian
6. Обеспечить consistency терминологии

**Deliverables:**
- Исправленные разделы рукописи
- Change log с отслеживанием правок

---

### Task 4.4: Bibliography Formatting 🟡 ПРИОРИТЕТ 2

**Статус:** Не начата  
**Срок:** Day 18

**Шаги реализации:**

1. **Создать скрипт форматирования библиографии**
   ```python
   # scripts/format_bibliography.py
   import requests
   import bibtexparser
   from pathlib import Path
   
   def fetch_doi_metadata(doi):
       """Fetch metadata from Crossref API"""
       url = f"https://api.crossref.org/works/{doi}"
       response = requests.get(url)
       if response.status_code == 200:
           return response.json()['message']
       return None
   
   def format_reference_mdpi(metadata):
       """Format reference according to MDPI Aerospace style"""
       # Extract: authors, title, journal, year, volume, pages, DOI
       # Format: Author1, A.; Author2, B. Title. Journal Year, Volume, Pages.
       pass
   
   def process_bibliography(bib_file):
       with open(bib_file) as f:
           bib_database = bibtexparser.load(f)
       
       formatted_refs = []
       for entry in bib_database.entries:
           if 'doi' in entry:
               metadata = fetch_doi_metadata(entry['doi'])
               formatted = format_reference_mdpi(metadata)
               formatted_refs.append(formatted)
       
       # Save formatted references
       with open('outputs/bibliography/formatted_references.bib', 'w') as f:
           f.write('\n\n'.join(formatted_refs))
   ```

2. **Deliverables:**
   - `outputs/bibliography/formatted_references.bib`
   - `outputs/bibliography/Missing_Metadata_Report.xlsx`
   - `outputs/bibliography/DOI_Validation_Report.txt`

---

### Task 4.5: Professional Editing Service 🟢 ПРИОРИТЕТ 3

**Статус:** Не начата  
**Срок:** Day 19-22

**Шаги:**
1. Отправить в MDPI language service
2. Ждать возврата (2-3 дня)
3. Интегрировать правки
4. Финальная проверка consistency

---

## 🟢 БЛОК 5: ЭКОНОМИЧЕСКИЙ АНАЛИЗ (5 задач)

### ⚠️ ВАЖНО: Базовый экономический расчет УЖЕ РЕАЛИЗОВАН

**Текущая реализация в `run_otu_pipeline.py`:**
```python
from otu.economic_damage import compute_impact_zone_cost

econ = compute_impact_zone_cost(results, cell_size_km=1.0)
print(f"Total Area: {econ['total_area_ha']:.0f} ha")
print(f"Vegetation Cost: ${econ['vegetation_cost_total']:,.0f}")
print(f"Soil Cost: ${econ['soil_cost_total']:,.0f}")
print(f"Fire Risk Cost: ${econ['fire_cost_total']:,.0f}")
print(f"TOTAL: ${econ['grand_total']:,.0f}")
```

**Что нужно добавить:**

### Task 5.1: Economic Calculator Implementation 🟢 ПРИОРИТЕТ 3

**Статус:** Частично реализовано  
**Срок:** Day 20

**Шаги:**

1. **Проверить существующий модуль**
   ```bash
   # Проверить otu/economic_damage.py
   ```

2. **Расширить класс `EconomicDamageCalculator`**
   - ADD: Unit costs в KZT (тенге)
   - ADD: Компонент contamination (загрязнение)
   - ADD: Компонент mechanical damage (механические повреждения)

3. **Код для расширения:**
```python
# otu/economic_damage.py (расширение)
class EconomicDamageCalculator:
    def __init__(self):
        # Unit costs in KZT per hectare
        self.costs_kzt = {
            'vegetation_loss': 50000,  # KZT/ha
            'soil_degradation': 30000,  # KZT/ha
            'fire_risk': 20000,  # KZT/ha
            'contamination': 40000,  # KZT/ha (toxic fuel)
            'mechanical_damage': 25000,  # KZT/ha (impact craters)
        }
        self.usd_to_kzt = 450  # Exchange rate
    
    def calculate_total_damage(self, otu_results, cell_size_km=1.0):
        """Calculate all damage components"""
        area_ha = len(otu_results) * (cell_size_km ** 2) * 100
        
        # Existing components
        veg_cost = self._calculate_vegetation_cost(otu_results, area_ha)
        soil_cost = self._calculate_soil_cost(otu_results, area_ha)
        fire_cost = self._calculate_fire_cost(otu_results, area_ha)
        
        # New components
        contam_cost = self._calculate_contamination_cost(otu_results, area_ha)
        mech_cost = self._calculate_mechanical_cost(otu_results, area_ha)
        
        total_kzt = veg_cost + soil_cost + fire_cost + contam_cost + mech_cost
        total_usd = total_kzt / self.usd_to_kzt
        
        return {
            'total_area_ha': area_ha,
            'vegetation_cost_kzt': veg_cost,
            'soil_cost_kzt': soil_cost,
            'fire_cost_kzt': fire_cost,
            'contamination_cost_kzt': contam_cost,
            'mechanical_cost_kzt': mech_cost,
            'grand_total_kzt': total_kzt,
            'grand_total_usd': total_usd,
        }
```

4. **Deliverables:**
   - Расширенный `otu/economic_damage.py`
   - Unit tests для всех компонентов
   - Документация методологии расчета

---

### Task 5.2: Worked Example for OTU 🟢 ПРИОРИТЕТ 3

**Статус:** Не начата  
**Срок:** Day 21

**Шаги:**

1. **Выбрать representative OTU**
   - Критерии: средний OTU (~0.3), типичная площадь (1 км²)
   - Пример: OTU_245 (lat=47.25, lon=66.50)

2. **Создать hypothetical impact scenario**
   - Сценарий: Падение ступени Протон-М
   - Масса: 30,600 кг
   - Скорость удара: 180 м/с
   - Площадь воздействия: 100 га

3. **Рассчитать все компоненты затрат**
   ```python
   # scripts/create_economic_worked_example.py
   from otu.economic_damage import EconomicDamageCalculator
   
   calc = EconomicDamageCalculator()
   
   # OTU_245 data
   otu_data = {
       'q_ndvi': 0.45,
       'q_si': 0.35,
       'q_bi': 0.28,
       'q_relief': 0.82,
       'q_otu': 0.31,
       'q_fire': 0.52,
   }
   
   # Calculate damage
   damage = calc.calculate_total_damage([otu_data], cell_size_km=1.0)
   
   # Create detailed breakdown
   breakdown = {
       'Component': ['Vegetation Loss', 'Soil Degradation', 'Fire Risk', 
                     'Contamination', 'Mechanical Damage', 'TOTAL'],
       'Cost (KZT)': [damage['vegetation_cost_kzt'], ...],
       'Cost (USD)': [damage['vegetation_cost_kzt']/450, ...],
       'Percentage': [...],
   }
   
   df = pd.DataFrame(breakdown)
   df.to_excel('outputs/economic/OTU_245_Worked_Example.xlsx')
   ```

4. **Deliverables:**
   - `outputs/economic/OTU_245_Worked_Example.xlsx`
   - `outputs/economic/OTU_245_Scenario_Description.md`
   - `outputs/manuscript_sections/Economic_Worked_Example.md`

---

### Task 5.3: Comparative Cost Analysis 🟢 ПРИОРИТЕТ 3

**Статус:** Не начата  
**Срок:** Day 22

**Шаги:**

1. **Сравнить затраты Low vs High stability OT