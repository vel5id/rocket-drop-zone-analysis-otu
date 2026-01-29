# Настройка Playwright для тестирования UI

## Краткое руководство по установке

### 1. Установка Playwright
```bash
cd gui
npm init playwright@latest
```

При установке выберите:
- TypeScript: Да
- Добавить в package.json: Да
- Установить браузеры: Да

### 2. Альтернативная установка (ручная)
```bash
cd gui
npm install --save-dev @playwright/test
npx playwright install
```

### 3. Добавление скриптов в package.json
```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "playwright:show-report": "playwright show-report"
  }
}
```

## Конфигурация Playwright

### Базовый конфигурационный файл: `playwright.config.ts`
```typescript
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

## Запуск тестов

### 1. Предварительные требования
```bash
# Запустите dev сервер в отдельном терминале
cd gui
npm run dev
```

### 2. Базовый запуск тестов
```bash
# Все тесты
npx playwright test

# Конкретный тест
npx playwright test tests/white-background-fix.spec.ts

# С указанием браузера
npx playwright test --project=chromium
```

### 3. Расширенные команды
```bash
# Запуск с UI режимом
npx playwright test --ui

# Запуск в debug режиме
npx playwright test --debug

# Генерация отчета
npx playwright test --reporter=html
npx playwright show-report
```

### 4. CI/CD интеграция
```bash
# Установка браузеров для CI
npx playwright install --with-deps

# Запуск в headless режиме
npx playwright test --headed=false
```

## Созданные тесты

### Структура тестов
```
gui/tests/
└── white-background-fix.spec.ts    # Тесты для проверки исправления белого фона
```

### Ключевые проверки в тестах:
1. **Фон элементов** - проверка темного фона на всех уровнях
2. **CSS переменные** - валидация цветовой схемы
3. **Функциональность** - работа кнопок и переключателей
4. **Загрузка ресурсов** - тайлы карты и изображения
5. **Визуальная целостность** - отсутствие белых областей

## Интеграция с GitHub Actions

### Пример workflow: `.github/workflows/playwright.yml`
```yaml
name: Playwright Tests
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
    - name: Install dependencies
      run: |
        cd gui
        npm ci
        npx playwright install --with-deps
    - name: Run Playwright tests
      run: |
        cd gui
        npm run test:e2e
    - uses: actions/upload-artifact@v4
      if: always()
      with:
        name: playwright-report
        path: gui/playwright-report/
        retention-days: 30
```

## Отладка и устранение неполадок

### Частые проблемы и решения:

#### 1. Браузеры не устанавливаются
```bash
# Принудительная переустановка
npx playwright install --force
```

#### 2. Ошибки подключения к dev серверу
- Убедитесь, что сервер запущен: `npm run dev`
- Проверьте порт: по умолчанию `http://localhost:5173`
- В конфигурации увеличьте timeout для webServer

#### 3. Селекторы не находятся
- Используйте `page.pause()` для отладки
- Проверяйте селекторы в DevTools
- Используйте `data-testid` атрибуты для стабильных селекторов

#### 4. Проблемы с асинхронностью
```typescript
// Всегда используйте await
await page.waitForSelector('.element');
await page.click('button');
await expect(page.locator('.result')).toBeVisible();
```

## Дополнительные ресурсы

### Документация:
- [Официальная документация Playwright](https://playwright.dev/docs/intro)
- [TypeScript с Playwright](https://playwright.dev/docs/test-typescript)
- [Лучшие практики](https://playwright.dev/docs/best-practices)

### Полезные команды:
```bash
# Генерация тестов из записей
npx playwright codegen http://localhost:5173

# Создание скриншотов
npx playwright screenshot --full-page http://localhost:5173 screenshot.png

# Тестирование производительности
npx playwright show-trace trace.zip
```

## Поддержка и обновление

### Обновление Playwright:
```bash
cd gui
npm update @playwright/test
npx playwright install
```

### Добавление новых тестов:
1. Создайте файл в `gui/tests/`
2. Используйте шаблон из существующих тестов
3. Запустите тесты локально перед коммитом
4. Добавьте тест в CI пайплайн

---

*Документация обновлена: 2026-01-29*