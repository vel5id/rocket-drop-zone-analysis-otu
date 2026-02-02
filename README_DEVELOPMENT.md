### 🇬🇧 English
[EN]
# 👨‍💻 Rocket Drop Zone Analysis (OTU) System - Development & Contribution

## 📋 Document Purpose

This document provides a guide for developers wishing to contribute to the Rocket Drop Zone Analysis (OTU) project. It describes development processes, coding standards, testing, and the project roadmap.

**Related Documents:**
- For a general overview, see [README_OVERVIEW.md](README_OVERVIEW.md)
- For technical implementation, see [README_TECHNICAL.md](README_TECHNICAL.md)
- For scientific methodology, see [README_SCIENCE.md](README_SCIENCE.md)
- For economic analysis, see [README_ECONOMICS.md](README_ECONOMICS.md)

# 💻 Development & Usage

[⬅️ Back to Main README](./README.md)

---

## 🚀 Getting Started for Contributors

### Prerequisites

- **Git**: For version control
- **Python 3.10+**: For backend development
- **Node.js 18+**: For frontend development
- **Docker** (optional): For containerization
- **Code Editor**: VS Code, PyCharm, or similar

### Cloning the Repository

```bash
# Clone the repository
git clone https://github.com/your-org/rocket-drop-zone-analysis.git
cd rocket-drop-zone-analysis

# Create a branch for new functionality
git checkout -b feature/your-feature-name
```

### Development Environment Setup

#### Backend Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Additional dev dependencies
```

#### Frontend Environment
```bash
# Go to frontend directory
cd gui

# Install dependencies
npm install

# Install dev dependencies
npm install --save-dev
```

### Running in Development Mode

```bash
# Run backend server (in one terminal)
python run_server.py --reload

# Run frontend dev server (in another terminal)
cd gui
npm run dev
```

---

## 📝 Contribution Guide

### Change Process

1. **Find an issue or create a new one**
   - Check the [issue list](https://github.com/your-org/rocket-drop-zone-analysis/issues)
   - If no suitable issue exists, create a new one with a clear description

2. **Discuss changes**
   - Comment on the issue to discuss the approach
   - Ensure your proposal aligns with the project roadmap

3. **Create a branch**
   ```bash
   git checkout -b feature/short-description
   # or
   git checkout -b fix/bug-description
   ```

4. **Make changes**
   - Follow coding standards
   - Write tests for new functionality
   - Update documentation

5. **Test changes**
   ```bash
   # Run tests
   pytest tests/
   npm test  # for frontend
   ```

6. **Create a Pull Request**
   - Describe changes in the PR
   - Link related issues
   - Request review from maintainers

### Contribution Types

| Contribution Type | Description | Examples |
|-------------------|-------------|----------|
| **Bug fixes** | Fixing errors in code | Calculation fixes, edge case handling |
| **Feature development** | Adding new functionality | New algorithms, integrations, UI components |
| **Documentation** | Improving documentation | README, API docs, code comments |
| **Tests** | Adding tests | Unit tests, integration tests, test data |
| **Performance improvements** | Optimizing performance | Algorithm speedup, memory reduction |
| **Code refactoring** | Improving code structure | Refactoring, readability improvement |

### Community Etiquette

1. **Be respectful**: Critique code, not people
2. **Provide context**: Explain why you are proposing changes
3. **Be patient**: Review may take time
4. **Accept feedback**: Be open to improvement suggestions
5. **Document changes**: Help others understand your changes

---

## 🏗️ Coding Standards

### Python (Backend)

#### Formatting
- **Black**: Automatic formatting
- **isort**: Import sorting
- **Flake8**: Style checking

```bash
# Automatic formatting
black .
isort .
flake8 .
```

#### Code Style
- **Naming**: snake_case for variables and functions, PascalCase for classes
- **Documentation**: Google style docstrings
- **Typing**: Use type hints

```python
from typing import List, Optional
import numpy as np


class EconomicDamageCalculator:
    """Calculates economic damage from fallen rocket stages.
    
    Attributes:
        config: Configuration with cost coefficients
        currency: Currency for calculations (default 'USD')
    """
    
    def __init__(self, config: EconomicConfig, currency: str = 'USD'):
        self.config = config
        self.currency = currency
    
    def calculate_damage(
        self, 
        grid: np.ndarray,
        vegetation_index: np.ndarray
    ) -> Dict[str, float]:
        """Calculates damage for a grid of cells.
        
        Args:
            grid: Array with cell coordinates
            vegetation_index: Array of NDVI values for each cell
            
        Returns:
            Dictionary with damage components
            
        Raises:
            ValueError: If array dimensions do not match
        """
        if grid.shape[0] != vegetation_index.shape[0]:
            raise ValueError("Array dimensions must match")
        
        # Calculate damage
        damage = self._compute_damage_components(grid, vegetation_index)
        
        return damage
```

#### Module Structure
```
otu/                          # Main module
├── __init__.py              # Public API export
├── calculator.py            # Main logic
├── economic_damage.py       # Economic calculations
├── geotiff_exporter.py      # Data export
└── tests/                   # Module tests
    ├── __init__.py
    ├── test_calculator.py
    └── test_economic_damage.py
```

### JavaScript/TypeScript (Frontend)

#### Formatting
- **Prettier**: Automatic formatting
- **ESLint**: Code checking

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "react/prop-types": "off",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

#### Code Style
- **Naming**: camelCase for variables and functions, PascalCase for components
- **Typing**: Use TypeScript wherever possible
- **Components**: Functional components with hooks

```typescript
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';

interface DropZoneMapProps {
  /** Geodata for display */
  geoData: GeoJSON.FeatureCollection;
  /** Callback on zone selection */
  onZoneSelect: (zoneId: string) => void;
}

/**
 * Map component for displaying drop zones.
 * Supports interactive selection and zooming.
 */
const DropZoneMap: React.FC<DropZoneMapProps> = ({ 
  geoData, 
  onZoneSelect 
}) => {
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  
  const handleZoneClick = (event: L.LeafletEvent) => {
    const zoneId = event.target.feature.properties.id;
    setSelectedZone(zoneId);
    onZoneSelect(zoneId);
  };
  
  return (
    <MapContainer 
      center={[45.965, 63.305]} 
      zoom={6} 
      style={{ height: '500px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      <GeoJSON
        data={geoData}
        onEachFeature={(feature, layer) => {
          layer.on('click', handleZoneClick);
        }}
        style={() => ({
          fillColor: selectedZone === feature.id ? '#ff7800' : '#3388ff',
          weight: 2,
          opacity: 1,
          color: 'white',
          fillOpacity: 0.7
        })}
      />
    </MapContainer>
  );
};

export default DropZoneMap;
```

---

## 🔍 Code Review Process

### What is Checked During Review

#### Functionality
- [ ] Code solves the assigned task
- [ ] No regressions in existing functionality
- [ ] Edge cases handled
- [ ] Performance not degraded

#### Code Quality
- [ ] Follows coding standards
- [ ] Code is readable and understandable
- [ ] No code duplication
- [ ] Design patterns used correctly

#### Testing
- [ ] Tests written for new functionality
- [ ] Tests pass successfully
- [ ] Test coverage not decreased
- [ ] Integration tests added if necessary

#### Documentation
- [ ] API documentation updated
- [ ] Code comments updated
- [ ] Usage examples added
- [ ] CHANGELOG updated if necessary

### Review Process

1. **Author creates PR**
   - Fills PR template
   - Assigns reviewers
   - Adds labels

2. **Reviewers check code**
   - Leave comments within 48 hours
   - Use GitHub review tools
   - Check every point from the checklist above

3. **Author makes corrections**
   - Responds to comments
   - Makes necessary changes
   - Notifies reviewers of readiness

4. **Approval and merge**
   - After approval from at least 2 reviewers
   - Author rebases on main (if necessary)
   - Squash merge with descriptive commit message

### Example of Good PR Description

```markdown
## Description of Changes
Added support for exporting results in NetCDF format for compatibility with scientific tools.

## Related Issues
Closes #123, #124

## Type of Change
- [ ] Bug fix
- [x] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [x] Added unit tests for new formatter
- [x] Tested with real data
- [x] Integration tests pass

## Checklist
- [x] My code follows project standards
- [x] I have self-reviewed my code
- [x] I have added comments to complex code sections
- [x] I have updated documentation
- [x] I have added tests proving my fix/feature works

## Screenshots (if applicable)
![NetCDF Export Example](url-to-screenshot)
```

---

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── otu/
│   │   ├── test_calculator.py
│   │   └── test_economic_damage.py
│   └── api/
│       └── test_endpoints.py
├── integration/            # Integration tests
│   ├── test_pipeline.py
│   └── test_gee_integration.py
├── e2e/                    # End-to-end tests
│   └── test_workflow.py
└── fixtures/               Test data
    ├── sample_grid.npy
    └── test_geojson.json
```

### Unit Tests

#### Backend (pytest)
```python
import pytest
import numpy as np
from otu.calculator import MonteCarloCalculator


class TestMonteCarloCalculator:
    """Tests for Monte Carlo Calculator."""
    
    @pytest.fixture
    def calculator(self):
        return MonteCarloCalculator(iterations=100)
    
    def test_initialization(self, calculator):
        """Check calculator initialization."""
        assert calculator.iterations == 100
        assert calculator.wind_std_dev == 15.0
    
    def test_simulation_output_shape(self, calculator):
        """Check simulation output data shape."""
        result = calculator.run_simulation(
            altitude_km=80.0,
            velocity_mps=2500.0
        )
        
        assert isinstance(result, dict)
        assert 'points' in result
        assert result['points'].shape == (100, 2)
        assert 'statistics' in result
    
    @pytest.mark.parametrize("altitude,expected_min_points", [
        (50.0, 95),  # Low altitude - fewer points
        (100.0, 98), # High altitude - more points
    ])
    def test_altitude_effect(self, calculator, altitude, expected_min_points):
        """Parameterized test for altitude effect."""
        result = calculator.run_simulation(
            altitude_km=altitude,
            velocity_mps=2500.0
        )
        
        assert result['statistics']['valid_points'] >= expected_min_points
```

#### Frontend (Jest + React Testing Library)
```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DropZoneMap from './DropZoneMap';
import { mockGeoData } from '../fixtures/mockData';

describe('DropZoneMap', () => {
  const mockOnZoneSelect = jest.fn();
  
  beforeEach(() => {
    mockOnZoneSelect.mockClear();
  });
  
  test('renders map with tile layer', () => {
    render(
      <DropZoneMap 
        geoData={mockGeoData} 
        onZoneSelect={mockOnZoneSelect} 
      />
    );
    
    expect(screen.getByRole('application')).toBeInTheDocument();
    expect(screen.getByAltText('OpenStreetMap')).toBeInTheDocument();
  });
  
  test('calls onZoneSelect when zone is clicked', () => {
    render(
      <DropZoneMap 
        geoData={mockGeoData} 
        onZoneSelect={mockOnZoneSelect} 
      />
    );
    
    // Simulate click on zone
    const zoneElement = screen.getByTestId('zone-123');
    fireEvent.click(zoneElement);
    
    expect(mockOnZoneSelect).toHaveBeenCalledWith('123');
    expect(mockOnZoneSelect).toHaveBeenCalledTimes(1);
  });
});
```

### Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app
from otu.calculator import MonteCarloCalculator


class TestIntegration:
    """Integration tests for full workflow."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_complete_workflow(self, client, tmp_path):
        """Test complete workflow from request to export."""
        
        # 1. Run simulation
        response = client.post('/api/v1/simulation/run', json={
            'launch_site': {'lat': 45.965, 'lon': 63.305},
            'separation_params': {
                'altitude_km': 80.0,
                'velocity_mps': 2500.0
            }
        })
        
        assert response.status_code == 200
        simulation_id = response.json()['simulation_id']
        
        # 2. Get results
        response = client.get(f'/api/v1/simulation/{simulation_id}')
        assert response.status_code == 200
        
        # 3. Export results
        response = client.get(
            f'/api/v1/export/{simulation_id}',
            params={'format': 'csv'}
        )
        
        assert response.status_code == 200
        assert 'text/csv' in response.headers['content-type']
        
        # Save for verification
        output_file = tmp_path / 'export.csv'
        output_file.write_bytes(response.content)
        
        assert output_file.stat().st_size > 0
```

### End-to-end Tests

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.e2e
class TestE2E:
    """End-to-end tests via browser."""
    
    @pytest.fixture
    def driver(self):
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_user_workflow(self, driver):
        """Test complete user workflow."""
        
        # 1. Open application
        driver.get('http://localhost:5173')
        
        # 2. Select zone on map
        map_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'leaflet-container'))
        )
        
        # 3. Fill parameters
        altitude_input = driver.find_element(By.ID, 'altitude-input')
        altitude_input.clear()
        altitude_input.send_keys('80')
        
        # 4. Run simulation
        calculate_button = driver.find_element(By.ID, 'calculate-button')
        calculate_button.click()
        
        # 5. Check results
        results_section = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'results-section'))
        )
        
        assert 'Simulation Results' in results_section.text
```

### Running Tests

```bash
# All tests
pytest tests/

# Only unit tests
pytest tests/unit/

# With code coverage
pytest --cov=otu --cov=api tests/

# Frontend tests
cd gui
npm test

# E2E tests (requires running application)
pytest tests/e2e/ -v
```

---

## 🗺️ Project Roadmap

### Version 1.0 (Current)
- [x] Basic Monte Carlo simulator
- [x] Grid generator within ellipse
- [x] Ecological index verification via GEE
- [x] Economic damage assessment
- [x] Web interface with map

### Version 1.1 (Q2 2026)
- [ ] Support for multi-stage rockets
- [ ] Accounting for Earth rotation (Coriolis effect)
- [ ] Integration with weather models (GFS, ERA5)
- [ ] Export to additional formats (NetCDF, KML)
- [ ] Performance improvement (JIT compilation)

### Version 1.2 (Q4 2026)
- [ ] Machine learning for damage classification
- [ ] Fall time forecasting
- [ ] 3D trajectory visualization
- [ ] Batch processing API
- [ ] Plugin architecture for new models

### Version 2.0 (2025)
- [ ] Support for other types of space debris
- [ ] Integration with air traffic control systems
- [ ] Real-time active launch tracking
- [ ] Mobile app for field research
- [ ] Blockchain for ecological compensation audit

### Long-term Goals
- [ ] De facto standard for assessing environmental risks of space launches
- [ ] Integration with international monitoring systems
- [ ] Open database of historical incidents
- [ ] Educational platform for universities

---

## 🏆 Contributors Recognition

### Participation Levels

| Level | Requirements | Privileges |
|-------|--------------|------------|
| **Contributor** | 1+ accepted PR | Mention in CONTRIBUTORS.md |
| **Active Contributor** | 5+ accepted PRs, review help | Access to triage issues |
| **Maintainer** | Significant contribution, deep code understanding | Right to merge PRs, participate in roadmap |
| **Core team** | Leadership in direction, architectural decisions | Right to release, represent project |

### Recognition Program

1. **CONTRIBUTORS.md**: List of all contributors
2. **Release notes**: Mention of significant contributions
3. **GitHub Profile Badges**: Special badges for active contributors
4. **Swag**: Physical rewards for top contributors
5. **Conferences**: Sponsorship for participation in relevant conferences

### How to Become a Maintainer

1. **Demonstrate Expertise**: Make significant contributions to the code
2. **Help Community**: Answer questions, help newcomers
3. **Participate in Review**: Help with code review of other PRs
4. **Suggest Improvements**: Actively participate in roadmap discussions
5. **Pass Mentorship**: Work with current maintainers

---

## 🐛 Bug Reporting

### Bug Report Template

```markdown
## Bug Description
Short description of the problem.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
Clear and concise description of what you expected to happen.

## Actual Behavior
Clear and concise description of what actually happened.

## Screenshots
If applicable, add screenshots to explain the problem.

## Environment
- OS: [e.g., Windows 10]
- Browser: [e.g., Chrome 120]
- App Version: [e.g., 1.0.0]

## Additional Context
Add any other context about the problem here.
```

### Feature Request Template

```markdown
## Feature Description
Clear and concise description of what you want.

## Problem it Solves
Clear and concise description of what problem or pain points this solves.

## Proposed Solution
Describe how you want this implemented.

## Alternatives Considered
Describe any alternative solutions or features you considered.

## Additional Context
Add any other context or screenshots about the feature request here.
```

---

## 📚 Additional Resources

### Documentation
- [Architectural Decisions](docs/architecture/decisions/) - ADR (Architecture Decision Records)
- [API Documentation](docs/api/) - Full API specification
- [Scientific Publications](docs/publications/) - Links to scientific papers

### Community
- [Discord Server](https://discord.gg/your-invite) - For discussions and questions
- [Forum](https://forum.example.com) - For long discussions
- [Twitter](https://twitter.com/your-project) - For announcements

### Development Tools
- [Development container](.devcontainer/) - Configuration for VS Code Dev Containers
- [Pre-commit hooks](.pre-commit-config.yaml) - Automatic checks before commit
- [GitHub Actions](.github/workflows/) - CI/CD configuration

---

## 🔗 Related Documents

For more information, refer to other project documents:

| Document | Target Audience | Key Content |
|----------|-----------------|-------------|
| [README_OVERVIEW.md](README_OVERVIEW.md) | General public, managers | Marketing overview, benefits, usage |
| [README_TECHNICAL.md](README_TECHNICAL.md) | Developers, DevOps | Architecture, installation, API, deployment |
| [README_SCIENCE.md](README_SCIENCE.md) | Scientists, researchers | Mathematical models, physical principles |
| [README_ECONOMICS.md](README_ECONOMICS.md) | Economists, analysts | Damage assessment methodology, ROI analysis |

---

<div align="center">
    <br>
    <i>Open contribution makes science better for everyone</i>
    <br>
    © 2026 Rocket Drop Zone Analysis Team. All rights reserved.
</div>


### 🇷🇺 Русский
[RU]
# 👨‍💻 Rocket Drop Zone Analysis (OTU) System - Разработка и вклад

## 📋 Назначение документа

Этот документ содержит руководство для разработчиков, желающих внести вклад в проект Rocket Drop Zone Analysis (OTU). Он описывает процессы разработки, стандарты кодирования, тестирование и roadmap проекта.

**Связь с другими документами:**
- Для общего обзора см. [README_OVERVIEW.md](README_OVERVIEW.md)
- Для технической реализации см. [README_TECHNICAL.md](README_TECHNICAL.md)
- Для научной методологии см. [README_SCIENCE.md](README_SCIENCE.md)
- Для экономического анализа см. [README_ECONOMICS.md](README_ECONOMICS.md)
# 💻 Development & Usage / Разработка и Использование

[⬅️ Back to Main README / Назад](./README.md)

---

## 🚀 Начало работы для контрибьюторов

### Предварительные требования

- **Git**: Для контроля версий
- **Python 3.10+**: Для backend разработки
- **Node.js 18+**: Для frontend разработки
- **Docker** (опционально): Для контейнеризации
- **Редактор кода**: VS Code, PyCharm или аналогичный

### Клонирование репозитория

```bash
# Клонирование репозитория
git clone https://github.com/your-org/rocket-drop-zone-analysis.git
cd rocket-drop-zone-analysis

# Создание ветки для новой функциональности
git checkout -b feature/your-feature-name
```

### Настройка окружения разработки

#### Backend окружение
```bash
# Создание виртуального окружения
python -m venv .venv

# Активация (Linux/macOS)
source .venv/bin/activate

# Активация (Windows)
.venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Дополнительные dev зависимости
```

#### Frontend окружение
```bash
# Переход в директорию frontend
cd gui

# Установка зависимостей
npm install

# Установка dev зависимостей
npm install --save-dev
```

### Запуск в режиме разработки

```bash
# Запуск backend сервера (в одном терминале)
python run_server.py --reload

# Запуск frontend dev сервера (в другом терминале)
cd gui
npm run dev
```

---

## 📝 Руководство по внесению вклада

### Процесс внесения изменений

1. **Найдите issue или создайте новый**
   - Проверьте [список issues](https://github.com/your-org/rocket-drop-zone-analysis/issues)
   - Если подходящего issue нет, создайте новый с четким описанием

2. **Обсудите изменения**
   - Прокомментируйте issue, чтобы обсудить подход
   - Убедитесь, что ваше предложение соответствует roadmap проекта

3. **Создайте ветку**
   ```bash
   git checkout -b feature/краткое-описание
   # или
   git checkout -b fix/описание-бага
   ```

4. **Внесите изменения**
   - Следуйте стандартам кодирования
   - Пишите тесты для новой функциональности
   - Обновляйте документацию

5. **Протестируйте изменения**
   ```bash
   # Запуск тестов
   pytest tests/
   npm test  # для frontend
   ```

6. **Создайте Pull Request**
   - Опишите изменения в PR
   - Укажите связанные issues
   - Попросите review у maintainers

### Типы вкладов

| Тип вклада | Описание | Примеры |
|------------|----------|---------|
| **Bug fixes** | Исправление ошибок в коде | Исправление расчетов, обработка edge cases |
| **Feature development** | Добавление новой функциональности | Новые алгоритмы, интеграции, UI компоненты |
| **Documentation** | Улучшение документации | README, API docs, комментарии в коде |
| **Tests** | Добавление тестов | Unit tests, integration tests, test data |
| **Performance improvements** | Оптимизация производительности | Ускорение алгоритмов, уменьшение памяти |
| **Code refactoring** | Улучшение структуры кода | Рефакторинг, улучшение читаемости |

### Этикет сообщества

1. **Будьте уважительны**: Критикуйте код, а не людей
2. **Предоставляйте контекст**: Объясняйте, почему вы предлагаете изменения
3. **Будьте терпеливы**: Review может занять время
4. **Принимайте feedback**: Будьте открыты к предложениям по улучшению
5. **Документируйте изменения**: Помогите другим понять ваши изменения

---

## 🏗️ Стандарты кодирования

### Python (Backend)

#### Форматирование
- **Black**: Автоматическое форматирование
- **isort**: Сортировка импортов
- **Flake8**: Проверка стиля

```bash
# Автоматическое форматирование
black .
isort .
flake8 .
```

#### Стиль кода
- **Именование**: snake_case для переменных и функций, PascalCase для классов
- **Документация**: Google style docstrings
- **Типизация**: Использование type hints

```python
from typing import List, Optional
import numpy as np


class EconomicDamageCalculator:
    """Калькулятор экономического ущерба от падения ОЧРН.
    
    Attributes:
        config: Конфигурация с коэффициентами стоимости
        currency: Валюта для расчетов (по умолчанию 'USD')
    """
    
    def __init__(self, config: EconomicConfig, currency: str = 'USD'):
        self.config = config
        self.currency = currency
    
    def calculate_damage(
        self, 
        grid: np.ndarray,
        vegetation_index: np.ndarray
    ) -> Dict[str, float]:
        """Рассчитывает ущерб для сетки ячеек.
        
        Args:
            grid: Массив с координатами ячеек
            vegetation_index: Массив значений NDVI для каждой ячейки
            
        Returns:
            Словарь с компонентами ущерба
            
        Raises:
            ValueError: Если размеры массивов не совпадают
        """
        if grid.shape[0] != vegetation_index.shape[0]:
            raise ValueError("Размеры массивов должны совпадать")
        
        # Расчет ущерба
        damage = self._compute_damage_components(grid, vegetation_index)
        
        return damage
```

#### Структура модулей
```
otu/                          # Основной модуль
├── __init__.py              # Экспорт публичного API
├── calculator.py            # Основная логика
├── economic_damage.py       # Экономические расчеты
├── geotiff_exporter.py      # Экспорт данных
└── tests/                   # Тесты модуля
    ├── __init__.py
    ├── test_calculator.py
    └── test_economic_damage.py
```

### JavaScript/TypeScript (Frontend)

#### Форматирование
- **Prettier**: Автоматическое форматирование
- **ESLint**: Проверка кода

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "react/prop-types": "off",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

#### Стиль кода
- **Именование**: camelCase для переменных и функций, PascalCase для компонентов
- **Типизация**: Использование TypeScript везде, где возможно
- **Компоненты**: Functional components с hooks

```typescript
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';

interface DropZoneMapProps {
  /** Геоданные для отображения */
  geoData: GeoJSON.FeatureCollection;
  /** Callback при выборе зоны */
  onZoneSelect: (zoneId: string) => void;
}

/**
 * Компонент карты для отображения зон падения.
 * Поддерживает интерактивное выделение и масштабирование.
 */
const DropZoneMap: React.FC<DropZoneMapProps> = ({ 
  geoData, 
  onZoneSelect 
}) => {
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  
  const handleZoneClick = (event: L.LeafletEvent) => {
    const zoneId = event.target.feature.properties.id;
    setSelectedZone(zoneId);
    onZoneSelect(zoneId);
  };
  
  return (
    <MapContainer 
      center={[45.965, 63.305]} 
      zoom={6} 
      style={{ height: '500px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      <GeoJSON
        data={geoData}
        onEachFeature={(feature, layer) => {
          layer.on('click', handleZoneClick);
        }}
        style={() => ({
          fillColor: selectedZone === feature.id ? '#ff7800' : '#3388ff',
          weight: 2,
          opacity: 1,
          color: 'white',
          fillOpacity: 0.7
        })}
      />
    </MapContainer>
  );
};

export default DropZoneMap;
```

---

## 🔍 Процесс код-ревью

### Что проверяется при review

#### Функциональность
- [ ] Код решает поставленную задачу
- [ ] Нет регрессий существующей функциональности
- [ ] Обработаны edge cases
- [ ] Производительность не ухудшилась

#### Качество кода
- [ ] Следует стандартам кодирования
- [ ] Код читаем и понятен
- [ ] Нет дублирования кода
- [ ] Правильно используются паттерны проектирования

#### Тестирование
- [ ] Написаны тесты для новой функциональности
- [ ] Тесты проходят успешно
- [ ] Тестовое покрытие не уменьшилось
- [ ] Добавлены интеграционные тесты при необходимости

#### Документация
- [ ] Обновлена документация API
- [ ] Обновлены комментарии в коде
- [ ] Добавлены примеры использования
- [ ] Обновлен CHANGELOG при необходимости

### Процесс review

1. **Автор создает PR**
   - Заполняет шаблон PR
   - Указывает reviewers
   - Добавляет labels

2. **Reviewers проверяют код**
   - Оставляют комментарии в течение 48 часов
   - Используют GitHub review tools
   - Проверяют каждый пункт из checklist выше

3. **Автор вносит правки**
   - Отвечает на комментарии
   - Вносит необходимые изменения
   - Уведомляет reviewers о готовности

4. **Approval и merge**
   - После approval от至少 2 reviewers
   - Автор rebase на main (при необходимости)
   - Squash merge с описательной commit message

### Пример хорошего PR описания

```markdown
## Описание изменений
Добавлена поддержка экспорта результатов в формате NetCDF для совместимости с научными инструментами.

## Связанные Issues
Closes #123, #124

## Тип изменений
- [ ] Bug fix
- [x] New feature
- [ ] Breaking change
- [ ] Documentation update

## Тестирование
- [x] Добавлены unit tests для нового форматера
- [x] Протестировано с реальными данными
- [x] Интеграционные тесты проходят

## Checklist
- [x] Мой код следует стандартам проекта
- [x] Я самостоятельно проверил свой код
- [x] Я добавил комментарии к сложным участкам кода
- [x] Я обновил документацию
- [x] Я добавил тесты, которые подтверждают, что мой fix/feature работает

## Скриншоты (если применимо)
![Пример экспорта NetCDF](url-to-screenshot)
```

---

## 🧪 Тестирование

### Структура тестов

```
tests/
├── unit/                    # Unit тесты
│   ├── otu/
│   │   ├── test_calculator.py
│   │   └── test_economic_damage.py
│   └── api/
│       └── test_endpoints.py
├── integration/            # Интеграционные тесты
│   ├── test_pipeline.py
│   └── test_gee_integration.py
├── e2e/                    # End-to-end тесты
│   └── test_workflow.py
└── fixtures/               Тестовые данные
    ├── sample_grid.npy
    └── test_geojson.json
```

### Unit тесты

#### Backend (pytest)
```python
import pytest
import numpy as np
from otu.calculator import MonteCarloCalculator


class TestMonteCarloCalculator:
    """Тесты для калькулятора Монте-Карло."""
    
    @pytest.fixture
    def calculator(self):
        return MonteCarloCalculator(iterations=100)
    
    def test_initialization(self, calculator):
        """Проверка инициализации калькулятора."""
        assert calculator.iterations == 100
        assert calculator.wind_std_dev == 15.0
    
    def test_simulation_output_shape(self, calculator):
        """Проверка формы выходных данных симуляции."""
        result = calculator.run_simulation(
            altitude_km=80.0,
            velocity_mps=2500.0
        )
        
        assert isinstance(result, dict)
        assert 'points' in result
        assert result['points'].shape == (100, 2)
        assert 'statistics' in result
    
    @pytest.mark.parametrize("altitude,expected_min_points", [
        (50.0, 95),  # Низкая высота - меньше точек
        (100.0, 98), # Высокая высота - больше точек
    ])
    def test_altitude_effect(self, calculator, altitude, expected_min_points):
        """Параметризованный тест влияния высоты."""
        result = calculator.run_simulation(
            altitude_km=altitude,
            velocity_mps=2500.0
        )
        
        assert result['statistics']['valid_points'] >= expected_min_points
```

#### Frontend (Jest + React Testing Library)
```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DropZoneMap from './DropZoneMap';
import { mockGeoData } from '../fixtures/mockData';

describe('DropZoneMap', () => {
  const mockOnZoneSelect = jest.fn();
  
  beforeEach(() => {
    mockOnZoneSelect.mockClear();
  });
  
  test('renders map with tile layer', () => {
    render(
      <DropZoneMap 
        geoData={mockGeoData} 
        onZoneSelect={mockOnZoneSelect} 
      />
    );
    
    expect(screen.getByRole('application')).toBeInTheDocument();
    expect(screen.getByAltText('OpenStreetMap')).toBeInTheDocument();
  });
  
  test('calls onZoneSelect when zone is clicked', () => {
    render(
      <DropZoneMap 
        geoData={mockGeoData} 
        onZoneSelect={mockOnZoneSelect} 
      />
    );
    
    // Симуляция клика по зоне
    const zoneElement = screen.getByTestId('zone-123');
    fireEvent.click(zoneElement);
    
    expect(mockOnZoneSelect).toHaveBeenCalledWith('123');
    expect(mockOnZoneSelect).toHaveBeenCalledTimes(1);
  });
});
```

### Интеграционные тесты

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app
from otu.calculator import MonteCarloCalculator


class TestIntegration:
    """Интеграционные тесты полного workflow."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_complete_workflow(self, client, tmp_path):
        """Тест полного workflow от запроса до экспорта."""
        
        # 1. Запуск симуляции
        response = client.post('/api/v1/simulation/run', json={
            'launch_site': {'lat': 45.965, 'lon': 63.305},
            'separation_params': {
                'altitude_km': 80.0,
                'velocity_mps': 2500.0
            }
        })
        
        assert response.status_code == 200
        simulation_id = response.json()['simulation_id']
        
        # 2. Получение результатов
        response = client.get(f'/api/v1/simulation/{simulation_id}')
        assert response.status_code == 200
        
        # 3. Экспорт результатов
        response = client.get(
            f'/api/v1/export/{simulation_id}',
            params={'format': 'csv'}
        )
        
        assert response.status_code == 200
        assert 'text/csv' in response.headers['content-type']
        
        # Сохранение для проверки
        output_file = tmp_path / 'export.csv'
        output_file.write_bytes(response.content)
        
        assert output_file.stat().st_size > 0
```

### End-to-end тесты

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.e2e
class TestE2E:
    """End-to-end тесты через браузер."""
    
    @pytest.fixture
    def driver(self):
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_user_workflow(self, driver):
        """Тест полного пользовательского workflow."""
        
        # 1. Открытие приложения
        driver.get('http://localhost:5173')
        
        # 2. Выбор зоны на карте
        map_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'leaflet-container'))
        )
        
        # 3. Заполнение параметров
        altitude_input = driver.find_element(By.ID, 'altitude-input')
        altitude_input.clear()
        altitude_input.send_keys('80')
        
        # 4. Запуск симуляции
        calculate_button = driver.find_element(By.ID, 'calculate-button')
        calculate_button.click()
        
        # 5. Проверка результатов
        results_section = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'results-section'))
        )
        
        assert 'Результаты симуляции' in results_section.text
```

### Запуск тестов

```bash
# Все тесты
pytest tests/

# Только unit тесты
pytest tests/unit/

# С покрытием кода
pytest --cov=otu --cov=api tests/

# Frontend тесты
cd gui
npm test

# E2E тесты (требуется запущенное приложение)
pytest tests/e2e/ -v
```

---

## 🗺️ Roadmap проекта

### Версия 1.0 (Текущая)
- [x] Базовый Монте-Карло симулятор
- [x] Генератор сетки внутри эллипса
- [x] Расчет экологических индексов через GEE
- [x] Экономическая оценка ущерба
- [x] Веб-интерфейс с картой

### Версия 1.1 (Q2 2026)
- [ ] Поддержка многоступенчатых ракет
- [ ] Учет вращения Земли (эффект Кориолиса)
- [ ] Интеграция с погодными моделями (GFS, ERA5)
- [ ] Экспорт в дополнительные форматы (NetCDF, KML)
- [ ] Улучшение производительности (JIT компиляция)

### Версия 1.2 (Q4 2026)
- [ ] Машинное обучение для классификации повреждений
- [ ] Прогнозирование времени падения
- [ ] 3D визуализация траекторий
- [ ] API для batch processing
- [ ] Плагинная архитектура для новых моделей

### Версия 2.0 (2025)
- [ ] Поддержка других типов космического мусора
- [ ] Интеграция с системами управления воздушным движением
- [ ] Реальное время отслеживание активных запусков
- [ ] Мобильное приложение для полевых исследований
- [ ] Блокчейн для аудита экологических компенсаций

### Долгосрочные цели
- [ ] Стандарт де-факто для оценки экологических рисков космических запусков
- [ ] Интеграция с международными системами мониторинга
- [ ] Открытая база данных исторических инцидентов
- [ ] Образовательная платформа для университетов

---

## 🏆 Признание контрибьюторов

### Уровни участия

| Уровень | Требования | Привилегии |
|---------|------------|------------|
| **Участник** | 1+ принятых PR | Упоминание в CONTRIBUTORS.md |
| **Активный контрибьютор** | 5+ принятых PR, помощь в review | Доступ к triage issues |
| **Maintainer** | Значительный вклад, глубокое понимание кода | Право на merge PR, участие в roadmap |
| **Core team** | Лидерство в направлении, архитектурные решения | Право на release, представление проекта |

### Программа признания

1. **CONTRIBUTORS.md**: Список всех контрибьюторов
2. **Release notes**: Упоминание значительных вкладов
3. **Баджи в профиле GitHub**: Специальные badges для активных контрибьюторов
4. **Swag**: Физические награды для top контрибьюторов
5. **Конференции**: Спонсирование участия в relevant conferences

### Как стать maintainer

1. **Продемонстрируйте экспертизу**: Внесите значительный вклад в код
2. **Помогайте сообществу**: Отвечайте на вопросы, помогайте новичкам
3. **Участвуйте в review**: Помогайте с код-ревью других PR
4. **Предложите улучшения**: Активно участвуйте в обсуждениях roadmap
5. **Пройдите mentorship**: Поработайте с текущими maintainers

---

## 🐛 Отчет об ошибках

### Шаблон для bug reports

```markdown
## Описание бага
Краткое описание проблемы.

## Шаги для воспроизведения
1. Перейдите на '...'
2. Нажмите на '....'
3. Прокрутите до '....'
4. Увидите ошибку

## Ожидаемое поведение
Четкое и краткое описание того, что вы ожидали произойти.

## Фактическое поведение
Четкое и краткое описание того, что произошло на самом деле.

## Скриншоты
Если применимо, добавьте скриншоты для объяснения проблемы.

## Окружение
- ОС: [например, Windows 10]
- Браузер: [например, Chrome 120]
- Версия приложения: [например, 1.0.0]

## Дополнительный контекст
Добавьте любой другой контекст о проблеме здесь.
```

### Шаблон для feature requests

```markdown
## Описание фичи
Четкое и краткое описание того, что вы хотите.

## Проблема, которую это решает
Четкое и краткое описание какой проблемы или боли points это решает.

## Предлагаемое решение
Опишите, как вы хотите, чтобы это было реализовано.

## Альтернативы, которые вы рассматривали
Опишите любые альтернативные решения или фичи, которые вы рассматривали.

## Дополнительный контекст
Добавьте любой другой контекст или скриншоты о запросе фичи здесь.
```

---

## 📚 Дополнительные ресурсы

### Документация
- [Архитектурные решения](docs/architecture/decisions/) - ADR (Architecture Decision Records)
- [API документация](docs/api/) - Полная спецификация API
- [Научные публикации](docs/publications/) - Ссылки на научные работы

### Сообщество
- [Discord сервер](https://discord.gg/your-invite) - Для обсуждения и вопросов
- [Форум](https://forum.example.com) - Для длительных обсуждений
- [Twitter](https://twitter.com/your-project) - Для анонсов

### Инструменты разработки
- [Development container](.devcontainer/) - Конфигурация для VS Code Dev Containers
- [Pre-commit hooks](.pre-commit-config.yaml) - Автоматические проверки перед commit
- [GitHub Actions](.github/workflows/) - CI/CD конфигурация

---

## 🔗 Связанные документы

Для получения дополнительной информации обратитесь к другим документам проекта:

| Документ | Целевая аудитория | Ключевое содержание |
|----------|-------------------|---------------------|
| [README_OVERVIEW.md](README_OVERVIEW.md) | Широкая публика, руководители | Маркетинговый обзор, преимущества, применение |
| [README_TECHNICAL.md](README_TECHNICAL.md) | Разработчики, DevOps | Архитектура, установка, API, развертывание |
| [README_SCIENCE.md](README_SCIENCE.md) | Ученые, исследователи | Математические модели, физические принципы |
| [README_ECONOMICS.md](README_ECONOMICS.md) | Экономисты, аналитики | Методология оценки ущерба, ROI анализ |

---

<div align="center">
    <br>
    <i>Открытый вклад делает науку лучше для всех</i>
    <br>
    © 2026 Rocket Drop Zone Analysis Team. Все права защищены.
</div>


### 🇰🇿 Қазақша
[KZ]

# 👨‍💻 Rocket Drop Zone Analysis (OTU) System - Әзірлеу және Үлес қосу

## 📋 Құжаттың мақсаты

Бұл құжат Rocket Drop Zone Analysis (OTU) жобасына үлес қосқысы келетін әзірлеушілерге арналған нұсқаулықты қамтиды. Онда әзірлеу процестері, кодтау стандарттары, тестілеу және жобаның жол картасы (roadmap) сипатталған.

**Басқа құжаттармен байланыс:**
- Жалпы шолу үшін: [README_OVERVIEW.md](README_OVERVIEW.md)
- Техникалық іске асыру үшін: [README_TECHNICAL.md](README_TECHNICAL.md)
- Ғылыми әдістеме үшін: [README_SCIENCE.md](README_SCIENCE.md)
- Экономикалық талдау үшін: [README_ECONOMICS.md](README_ECONOMICS.md)

# 💻 Әзірлеу және Пайдалану

[⬅️ Негізгі README-ге қайту](./README.md)

---

## 🚀 Контрибьюторлар үшін жұмысты бастау

### Талаптар

- **Git**: Нұсқаларды бақылау үшін
- **Python 3.10+**: Backend әзірлеу үшін
- **Node.js 18+**: Frontend әзірлеу үшін
- **Docker** (қосымша): Контейнеризация үшін
- **Код редакторы**: VS Code, PyCharm немесе ұқсас

### Репозиторийді клондау

```bash
# Репозиторийді клондау
git clone https://github.com/your-org/rocket-drop-zone-analysis.git
cd rocket-drop-zone-analysis

# Жаңа функционалдылық үшін тармақ (branch) құру
git checkout -b feature/your-feature-name
```

### Әзірлеу ортасын баптау

#### Backend ортасы
```bash
# Виртуалды ортаны құру
python -m venv .venv

# Іске қосу (Linux/macOS)
source .venv/bin/activate

# Іске қосу (Windows)
.venv\Scripts\activate

# Тәуелділіктерді орнату
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Қосымша dev тәуелділіктер
```

#### Frontend ортасы
```bash
# Frontend каталогына өту
cd gui

# Тәуелділіктерді орнату
npm install

# Dev тәуелділіктерді орнату
npm install --save-dev
```

### Әзірлеу режимінде іске қосу

```bash
# Backend серверді іске қосу (бір терминалда)
python run_server.py --reload

# Frontend dev серверді іске қосу (басқа терминалда)
cd gui
npm run dev
```

---

## 📝 Үлес қосу нұсқаулығы

### Өзгерістер енгізу процесі

1. **Issue табыңыз немесе жаңасын құрыңыз**
   - [Issues тізімін](https://github.com/your-org/rocket-drop-zone-analysis/issues) тексеріңіз
   - Егер сәйкес issue болмаса, нақты сипаттамасы бар жаңасын құрыңыз

2. **Өзгерістерді талқылаңыз**
   - Тәсілді талқылау үшін issue-ге түсініктеме жазыңыз
   - Ұсынысыңыз жобаның roadmap-ына сәйкес келетініне көз жеткізіңіз

3. **Тармақ (branch) құрыңыз**
   ```bash
   git checkout -b feature/қысқаша-сипаттама
   # немесе
   git checkout -b fix/баг-сипаттамасы
   ```

4. **Өзгерістер енгізіңіз**
   - Кодтау стандарттарын сақтаңыз
   - Жаңа функционалдылық үшін тесттер жазыңыз
   - Құжаттаманы жаңартыңыз

5. **Өзгерістерді тексеріңіз**
   ```bash
   # Тесттерді іске қосу
   pytest tests/
   npm test  # frontend үшін
   ```

6. **Pull Request құрыңыз**
   - PR-да өзгерістерді сипаттаңыз
   - Байланысты issue-лерді көрсетіңіз
   - Maintainers-тен review сұраңыз

### Үлес түрлері

| Үлес түрі | Сипаттамасы | Мысалдар |
|-----------|-------------|----------|
| **Bug fixes** | Кодтағы қателерді түзету | Есептеулерді түзету, edge cases өңдеу |
| **Feature development** | Жаңа функционалдылық қосу | Жаңа алгоритмдер, интеграциялар, UI компоненттері |
| **Documentation** | Құжаттаманы жақсарту | README, API docs, кодтағы түсініктемелер |
| **Tests** | Тесттер қосу | Unit tests, integration tests, test data |
| **Performance improvements** | Өнімділікті оңтайландыру | Алгоритмдерді жылдамдату, жадты азайту |
| **Code refactoring** | Код құрылымын жақсарту | Рефакторинг, оқылуын жақсарту |

### Қоғамдастық этикеті

1. **Құрметті болыңыз**: Адамдарды емес, кодты сынаңыз
2. **Контекст беріңіз**: Неге өзгерістер ұсынып жатқаныңызды түсіндіріңіз
3. **Сабырлы болыңыз**: Review уақыт алуы мүмкін
4. **Кері байланысты қабылдаңыз**: Жақсарту ұсыныстарына ашық болыңыз
5. **Өзгерістерді құжаттаңыз**: Басқаларға өзгерістеріңізді түсінуге көмектесіңіз

---

## 🏗️ Кодтау стандарттары

### Python (Backend)

#### Форматтау
- **Black**: Автоматты форматтау
- **isort**: Импорттарды сұрыптау
- **Flake8**: Стильді тексеру

```bash
# Автоматты форматтау
black .
isort .
flake8 .
```

#### Код стилі
- **Атау**: Айнымалылар мен функциялар үшін snake_case, кластар үшін PascalCase
- **Құжаттама**: Google style docstrings
- **Типтеу**: type hints қолдану

```python
from typing import List, Optional
import numpy as np


class EconomicDamageCalculator:
    """Ғашырық қалдықтарының құлауынан экономикалық шығынды есептегіш.
    
    Attributes:
        config: Құн коэффициенттері бар конфигурация
        currency: Есептеулер үшін валюта (әдепкі бойынша 'USD')
    """
    
    def __init__(self, config: EconomicConfig, currency: str = 'USD'):
        self.config = config
        self.currency = currency
    
    def calculate_damage(
        self, 
        grid: np.ndarray,
        vegetation_index: np.ndarray
    ) -> Dict[str, float]:
        """Ұяшықтар торы үшін шығынды есептейді.
        
        Args:
            grid: Ұяшықтар координаттары бар массив
            vegetation_index: Әр ұяшық үшін NDVI мәндері бар массив
            
        Returns:
            Шығын компоненттері бар сөздік
            
        Raises:
            ValueError: Егер массив өлшемдері сәйкес келмесе
        """
        if grid.shape[0] != vegetation_index.shape[0]:
            raise ValueError("Массив өлшемдері сәйкес келуі керек")
        
        # Шығынды есептеу
        damage = self._compute_damage_components(grid, vegetation_index)
        
        return damage
```

#### Модуль құрылымы
```
otu/                          # Негізгі модуль
├── __init__.py              # Жария API экспорты
├── calculator.py            # Негізгі логика
├── economic_damage.py       # Экономикалық есептеулер
├── geotiff_exporter.py      # Деректер экспорты
└── tests/                   # Модуль тесттері
    ├── __init__.py
    ├── test_calculator.py
    └── test_economic_damage.py
```

### JavaScript/TypeScript (Frontend)

#### Форматтау
- **Prettier**: Автоматты форматтау
- **ESLint**: Кодты тексеру

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "react/prop-types": "off",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

#### Код стилі
- **Атау**: Айнымалылар мен функциялар үшін camelCase, компоненттер үшін PascalCase
- **Типтеу**: Мүмкіндігінше TypeScript қолдану
- **Компоненттер**: Hooks бар Functional components

```typescript
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';

interface DropZoneMapProps {
  /** Көрсетуге арналған геодеректер */
  geoData: GeoJSON.FeatureCollection;
  /** Аймақты таңдау кезіндегі callback */
  onZoneSelect: (zoneId: string) => void;
}

/**
 * Құлау аймақтарын көрсетуге арналған карта компоненті.
 * Интерактивті таңдауды және масштабтауды қолдайды.
 */
const DropZoneMap: React.FC<DropZoneMapProps> = ({ 
  geoData, 
  onZoneSelect 
}) => {
  const [selectedZone, setSelectedZone] = useState<string | null>(null);
  
  const handleZoneClick = (event: L.LeafletEvent) => {
    const zoneId = event.target.feature.properties.id;
    setSelectedZone(zoneId);
    onZoneSelect(zoneId);
  };
  
  return (
    <MapContainer 
      center={[45.965, 63.305]} 
      zoom={6} 
      style={{ height: '500px', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      <GeoJSON
        data={geoData}
        onEachFeature={(feature, layer) => {
          layer.on('click', handleZoneClick);
        }}
        style={() => ({
          fillColor: selectedZone === feature.id ? '#ff7800' : '#3388ff',
          weight: 2,
          opacity: 1,
          color: 'white',
          fillOpacity: 0.7
        })}
      />
    </MapContainer>
  );
};

export default DropZoneMap;
```

---

## 🔍 Код-ревью процесі

### Review кезінде не тексеріледі

#### Функционалдылық
- [ ] Код қойылған тапсырманы шешеді
- [ ] Қолданыстағы функционалдылықта регрессия жоқ
- [ ] Edge cases өңделген
- [ ] Өнімділік нашарламаған

#### Код сапасы
- [ ] Кодтау стандартына сәйкес
- [ ] Код оқылатын және түсінікті
- [ ] Код қайталанбайды
- [ ] Жобалау паттерндері дұрыс қолданылған

#### Тестілеу
- [ ] Жаңа функционалдылық үшін тесттер жазылған
- [ ] Тесттер сәтті өтеді
- [ ] Тестпен қамту азаймаған
- [ ] Қажет болса, интеграциялық тесттер қосылған

#### Құжаттама
- [ ] API құжаттамасы жаңартылған
- [ ] Кодтағы түсініктемелер жаңартылған
- [ ] Қолдану мысалдары қосылған
- [ ] Қажет болса CHANGELOG жаңартылған

### Review процесі

1. **Автор PR құрады**
   - PR шаблонын толтырады
   - Reviewers көрсетеді
   - Labels қосады

2. **Reviewers кодты тексереді**
   - 48 сағат ішінде пікір қалдырады
   - GitHub review құралдарын қолданады
   - Жоғарыдағы checklist-тің әр тармағын тексереді

3. **Автор түзетулер енгізеді**
   - Пікірлерге жауап береді
   - Қажетті өзгерістерді енгізеді
   - Reviewers-ке дайын екенін хабарлайды

4. **Approval және merge**
   - Кемінде 2 reviewer мақұлдағаннан кейін
   - Автор main-ге rebase жасайды (қажет болса)
   - Сипаттамалы commit message-бен Squash merge

### Жақсы PR сипаттамасының мысалы

```markdown
## Өзгерістер сипаттамасы
Ғылыми құралдармен үйлесімділік үшін нәтижелерді NetCDF форматында экспорттау қолдауы қосылды.

## Байланысты Issues
Closes #123, #124

## Өзгеріс түрі
- [ ] Bug fix
- [x] New feature
- [ ] Breaking change
- [ ] Documentation update

## Тестілеу
- [x] Жаңа форматер үшін unit tests қосылды
- [x] Нақты деректермен тексерілді
- [x] Интеграциялық тесттер өтеді

## Checklist
- [x] Менің кодым жоба стандарттарына сәйкес
- [x] Мен өз кодыма өзім шолу жасадым
- [x] Мен кодтың күрделі жерлеріне түсініктеме қостым
- [x] Мен құжаттаманы жаңарттым
- [x] Мен fix/feature жұмыс істейтінін растайтын тесттер қостым

## Скриншоттар (егер қажет болса)
![NetCDF Export Example](url-to-screenshot)
```

---

## 🧪 Тестілеу

### Тесттер құрылымы

```
tests/
├── unit/                    # Unit тесттер
│   ├── otu/
│   │   ├── test_calculator.py
│   │   └── test_economic_damage.py
│   └── api/
│       └── test_endpoints.py
├── integration/            # Интеграциялық тесттер
│   ├── test_pipeline.py
│   └── test_gee_integration.py
├── e2e/                    # End-to-end тесттер
│   └── test_workflow.py
└── fixtures/               Тесттік деректер
    ├── sample_grid.npy
    └── test_geojson.json
```

### Unit тесттер

#### Backend (pytest)
```python
import pytest
import numpy as np
from otu.calculator import MonteCarloCalculator


class TestMonteCarloCalculator:
    """Монте-Карло калькуляторына арналған тесттер."""
    
    @pytest.fixture
    def calculator(self):
        return MonteCarloCalculator(iterations=100)
    
    def test_initialization(self, calculator):
        """Калькулятор инициализациясын тексеру."""
        assert calculator.iterations == 100
        assert calculator.wind_std_dev == 15.0
    
    def test_simulation_output_shape(self, calculator):
        """Симуляция шығыс деректерінің формасын тексеру."""
        result = calculator.run_simulation(
            altitude_km=80.0,
            velocity_mps=2500.0
        )
        
        assert isinstance(result, dict)
        assert 'points' in result
        assert result['points'].shape == (100, 2)
        assert 'statistics' in result
    
    @pytest.mark.parametrize("altitude,expected_min_points", [
        (50.0, 95),  # Төмен биіктік - аз нүктелер
        (100.0, 98), # Жоғары биіктік - көп нүктелер
    ])
    def test_altitude_effect(self, calculator, altitude, expected_min_points):
        """Биіктік әсерін параметрленген тесттеу."""
        result = calculator.run_simulation(
            altitude_km=altitude,
            velocity_mps=2500.0
        )
        
        assert result['statistics']['valid_points'] >= expected_min_points
```

#### Frontend (Jest + React Testing Library)
```typescript
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DropZoneMap from './DropZoneMap';
import { mockGeoData } from '../fixtures/mockData';

describe('DropZoneMap', () => {
  const mockOnZoneSelect = jest.fn();
  
  beforeEach(() => {
    mockOnZoneSelect.mockClear();
  });
  
  test('renders map with tile layer', () => {
    render(
      <DropZoneMap 
        geoData={mockGeoData} 
        onZoneSelect={mockOnZoneSelect} 
      />
    );
    
    expect(screen.getByRole('application')).toBeInTheDocument();
    expect(screen.getByAltText('OpenStreetMap')).toBeInTheDocument();
  });
  
  test('calls onZoneSelect when zone is clicked', () => {
    render(
      <DropZoneMap 
        geoData={mockGeoData} 
        onZoneSelect={mockOnZoneSelect} 
      />
    );
    
    // Аймақты басуды симуляциялау
    const zoneElement = screen.getByTestId('zone-123');
    fireEvent.click(zoneElement);
    
    expect(mockOnZoneSelect).toHaveBeenCalledWith('123');
    expect(mockOnZoneSelect).toHaveBeenCalledTimes(1);
  });
});
```

### Интеграциялық тесттер

```python
import pytest
from fastapi.testclient import TestClient
from api.main import app
from otu.calculator import MonteCarloCalculator


class TestIntegration:
    """Толық workflow интеграциялық тесттері."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_complete_workflow(self, client, tmp_path):
        """Сұраныстан экспортқа дейінгі толық workflow тесті."""
        
        # 1. Симуляцияны іске қосу
        response = client.post('/api/v1/simulation/run', json={
            'launch_site': {'lat': 45.965, 'lon': 63.305},
            'separation_params': {
                'altitude_km': 80.0,
                'velocity_mps': 2500.0
            }
        })
        
        assert response.status_code == 200
        simulation_id = response.json()['simulation_id']
        
        # 2. Нәтижелерді алу
        response = client.get(f'/api/v1/simulation/{simulation_id}')
        assert response.status_code == 200
        
        # 3. Нәтижелерді экспорттау
        response = client.get(
            f'/api/v1/export/{simulation_id}',
            params={'format': 'csv'}
        )
        
        assert response.status_code == 200
        assert 'text/csv' in response.headers['content-type']
        
        # Тексеру үшін сақтау
        output_file = tmp_path / 'export.csv'
        output_file.write_bytes(response.content)
        
        assert output_file.stat().st_size > 0
```

### End-to-end тесттер

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.e2e
class TestE2E:
    """Браузер арқылы End-to-end тесттер."""
    
    @pytest.fixture
    def driver(self):
        driver = webdriver.Chrome()
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def test_user_workflow(self, driver):
        """Толық пайдаланушы workflow тесті."""
        
        # 1. Қосымшаны ашу
        driver.get('http://localhost:5173')
        
        # 2. Картада аймақты таңдау
        map_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'leaflet-container'))
        )
        
        # 3. Параметрлерді толтыру
        altitude_input = driver.find_element(By.ID, 'altitude-input')
        altitude_input.clear()
        altitude_input.send_keys('80')
        
        # 4. Симуляцияны іске қосу
        calculate_button = driver.find_element(By.ID, 'calculate-button')
        calculate_button.click()
        
        # 5. Нәтижелерді тексеру
        results_section = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, 'results-section'))
        )
        
        assert 'Симуляция нәтижелері' in results_section.text
```

### Тесттерді іске қосу

```bash
# Барлық тесттер
pytest tests/

# Тек unit тесттер
pytest tests/unit/

# Кодты қамтумен (coverage)
pytest --cov=otu --cov=api tests/

# Frontend тесттер
cd gui
npm test

# E2E тесттер (қосымша іске қосылған болуы керек)
pytest tests/e2e/ -v
```

---

## 🗺️ Жобаның жол картасы (Roadmap)

### Версия 1.0 (Ағымдағы)
- [x] Базалық Монте-Карло симуляторы
- [x] Эллипс ішінде тор генераторы
- [x] GEE арқылы экологиялық индекстерді тексеру
- [x] Экономикалық шығынды бағалау
- [x] Картасы бар веб-интерфейс

### Версия 1.1 (Q2 2026)
- [ ] Көп сатылы зымырандарды қолдау
- [ ] Жердің айналуын есепке алу (Кориолис эффектісі)
- [ ] Ауа райы модельдерімен интеграция (GFS, ERA5)
- [ ] Қосымша форматтарға экспорттау (NetCDF, KML)
- [ ] Өнімділікті жақсарту (JIT компиляция)

### Версия 1.2 (Q4 2026)
- [ ] Зақымдануларды жіктеу үшін машиналық оқыту
- [ ] Құлау уақытын болжау
- [ ] Траекторияларды 3D визуализациялау
- [ ] Batch processing үшін API
- [ ] Жаңа модельдер үшін плагиндік архитектура

### Версия 2.0 (2025)
- [ ] Ғарыш қоқыстарының басқа түрлерін қолдау
- [ ] Әуе қозғалысын басқару жүйелерімен интеграция
- [ ] Белсенді ұшыруларды нақты уақытта бақылау
- [ ] Далалық зерттеулерге арналған мобильді қосымша
- [ ] Экологиялық өтемақыларды аудиттеу үшін блокчейн

### Узақ мерзімді мақсаттар
- [ ] Ғарыштық ұшырулардың экологиялық қауіптерін бағалаудың де-факто стандарты
- [ ] Халықаралық мониторинг жүйелерімен интеграция
- [ ] Тарихи инциденттердің ашық деректер базасы
- [ ] Университеттерге арналған білім беру платформасы

---

## 🏆 Контрибьюторларды тану

### Қатысу деңгейлері

| Деңгей | Талаптар| Артықшылықтар |
|--------|---------|---------------|
| **Қатысушы** | 1+ қабылданған PR | CONTRIBUTORS.md ішінде атап өту |
| **Белсенді контрибьютор** | 5+ қабылданған PR, review көмек | Triage issues-ке қолжетімділік |
| **Maintainer** | Маңызды үлес, кодты терең түсіну | PR merge құқығы, roadmap-қа қатысу |
| **Core team** | Бағытта көшбасшылық, архитектуралық шешімдер | Release құқығы, жобаны таныстыру |

### Тану бағдарламасы

1. **CONTRIBUTORS.md**: Барлық контрибьюторлар тізімі
2. **Release notes**: Маңызды үлестерді атап өту
3. **GitHub профильдегі бадждар**: Белсенді контрибьюторлар үшін арнайы badges
4. **Swag**: Top контрибьюторлар үшін физикалық сыйлықтар
5. **Конференциялар**: Тиісті конференцияларға қатысуға демеушілік

### Қалай maintainer болуға болады

1. **Сараптаманы көрсетіңіз**: Кодқа маңызды үлес қосыңыз
2. **Қоғамдастыққа көмектесіңіз**: Сұрақтарға жауап беріңіз, жаңадан келгендерге көмектесіңіз
3. **Review-ге қатысыңыз**: Басқа PR-ларға код-ревью жасауға көмектесіңіз
4. **Жақсартуларды ұсыныңыз**: Roadmap талқылауларына белсенді қатысыңыз
5. **Тәлімгерліктен өтіңіз**: Ағымдағы maintainers-пен жұмыс істеңіз

---

## 🐛 Қате туралы хабарлау

### Bug reports шаблоны

```markdown
## Баг сипаттамасы
Мәселенің қысқаша сипаттамасы.

## Қайталау қадамдары
1. '...'-ға өтіңіз
2. '....'-ны басыңыз
3. '....'-ға дейін жылжытыңыз
4. Қатені көресіз

## Күтілетін әрекет
Не болуы керек екендігінің нақты және қысқаша сипаттамасы.

## Нақты әрекет
Іс жүзінде не болғанының нақты және қысқаша сипаттамасы.

## Скриншоттар
Егер қажет болса, мәселені түсіндіру үшін скриншоттар қосыңыз.

## Орта
- ОЖ: [мысалы, Windows 10]
- Браузер: [мысалы, Chrome 120]
- Қосымша нұсқасы: [мысалы, 1.0.0]

## Қосымша контекст
Мәселе туралы кез келген басқа контекстті осында қосыңыз.
```

### Feature requests шаблоны

```markdown
## Фича сипаттамасы
Сіз не қалайтыныңыздың нақты және қысқаша сипаттамасы.

## Бұл қандай мәселені шешеді
Бұл қандай мәселені немесе қиындықты шешетінінің нақты және қысқаша сипаттамасы.

## Ұсынылатын шешім
Мұны қалай жүзеге асырғыңыз келетінін сипаттаңыз.

## Қаралған баламалар
Қарастырған кез келген балама шешімдерді немесе фичаларды сипаттаңыз.

## Қосымша контекст
Фича сұратуы туралы кез келген басқа контекстті немесе скриншоттарды осында қосыңыз.
```

---

## 📚 Қосымша ресурстар

### Құжаттама
- [Архитектуралық шешімдер](docs/architecture/decisions/) - ADR (Architecture Decision Records)
- [API құжаттамасы](docs/api/) - Толық API спецификациясы
- [Ғылыми жарияланымдар](docs/publications/) - Ғылыми еңбектерге сілтемелер

### Қоғамдастық
- [Discord сервер](https://discord.gg/your-invite) - Талқылау және сұрақтар үшін
- [Форум](https://forum.example.com) - Ұзақ талқылаулар үшін
- [Twitter](https://twitter.com/your-project) - Хабарландырулар үшін

### Әзірлеу құралдары
- [Development container](.devcontainer/) - VS Code Dev Containers конфигурациясы
- [Pre-commit hooks](.pre-commit-config.yaml) - Commit алдындағы автоматты тексерулер
- [GitHub Actions](.github/workflows/) - CI/CD конфигурациясы

---

## 🔗 Байланысты құжаттар

Қосымша ақпарат алу үшін жобаның басқа құжаттарына жүгініңіз:

| Құжат | Мақсатты аудитория | Негізгі мазмұны |
|-------|--------------------|-----------------|
| [README_OVERVIEW.md](README_OVERVIEW.md) | Көпшілік, басшылар | Маркетингтік шолу, артықшылықтар, қолдану |
| [README_TECHNICAL.md](README_TECHNICAL.md) | Әзірлеушілер, DevOps | Архитектура, орнату, API, орналастыру |
| [README_SCIENCE.md](README_SCIENCE.md) | Ғалымдар, зерттеушілер | Математикалық модельдер, физикалық принциптер |
| [README_ECONOMICS.md](README_ECONOMICS.md) | Экономистер, талдаушылар | Шығынды бағалау әдістемесі, ROI талдау |

---

<div align="center">
    <br>
    <i>Ашық үлес ғылымды барлығы үшін жақсартады</i>
    <br>
    © 2026 Rocket Drop Zone Analysis Team. Барлық құқықтар қорғалған.
</div>
