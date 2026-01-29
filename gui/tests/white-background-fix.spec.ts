import { test, expect } from '@playwright/test';

/**
 * Тест для валидации исправления проблемы с белым фоном после рендера
 * Проверяет, что все ключевые элементы интерфейса имеют правильный темный фон
 * 
 * @file white-background-fix.spec.ts
 * @version 1.0.0
 * @created 2026-01-29
 */

test.describe('Исправление белого фона после рендера', () => {
  test.beforeEach(async ({ page }) => {
    // Переходим на главную страницу приложения
    await page.goto('http://localhost:5173');
    // Ждем загрузки приложения
    await page.waitForSelector('.leaflet-container');
  });

  test('HTML элемент должен иметь темный фон', async ({ page }) => {
    // Проверяем, что html элемент имеет правильный фон
    const htmlBackground = await page.evaluate(() => {
      return window.getComputedStyle(document.documentElement).backgroundColor;
    });
    
    expect(htmlBackground).toBe('rgb(5, 10, 16)'); // #050a10 в RGB
  });

  test('Body элемент должен иметь темный фон', async ({ page }) => {
    // Проверяем фон body
    const bodyBackground = await page.evaluate(() => {
      return window.getComputedStyle(document.body).backgroundColor;
    });
    
    expect(bodyBackground).toBe('rgb(5, 10, 16)');
  });

  test('Контейнер Leaflet карты должен иметь темный фон', async ({ page }) => {
    // Проверяем фон контейнера карты
    const leafletBackground = await page.evaluate(() => {
      const container = document.querySelector('.leaflet-container');
      return container ? window.getComputedStyle(container).backgroundColor : 'not found';
    });
    
    expect(leafletBackground).toBe('rgb(5, 10, 16)');
  });

  test('Родительский контейнер карты должен иметь темный фон', async ({ page }) => {
    // Проверяем фон родительского контейнера карты
    const parentBackground = await page.evaluate(() => {
      const parent = document.querySelector('div[style*="inset: 20px"]');
      return parent ? window.getComputedStyle(parent).backgroundColor : 'not found';
    });
    
    expect(parentBackground).toBe('rgb(5, 10, 16)');
  });

  test('Основной контейнер приложения должен иметь темный фон', async ({ page }) => {
    // Проверяем фон основного контейнера
    const appContainerBackground = await page.evaluate(() => {
      const container = document.querySelector('div[class*="relative"][class*="w-screen"][class*="h-screen"]');
      return container ? window.getComputedStyle(container).backgroundColor : 'not found';
    });
    
    expect(appContainerBackground).toBe('rgb(5, 10, 16)');
  });

  test('CSS переменная --bg-space должна быть установлена правильно', async ({ page }) => {
    // Проверяем CSS переменную
    const bgSpaceValue = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--bg-space').trim();
    });
    
    expect(bgSpaceValue).toBe('#050a10');
  });

  test('Тайлы карты должны загружаться', async ({ page }) => {
    // Проверяем, что тайлы карты загружены
    const tileCount = await page.evaluate(() => {
      return document.querySelectorAll('.leaflet-tile').length;
    });
    
    expect(tileCount).toBeGreaterThan(0);
  });

  test('Интерфейс должен отображать основные элементы', async ({ page }) => {
    // Проверяем наличие ключевых элементов интерфейса
    await expect(page.locator('header')).toBeVisible();
    await expect(page.locator('aside')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
    
    // Проверяем заголовок
    await expect(page.getByText('Orbital Command')).toBeVisible();
    
    // Проверяем кнопку запуска симуляции
    await expect(page.getByText('Initiate Simulation')).toBeVisible();
  });

  test('Не должно быть элементов с белым фоном (кроме UI элементов)', async ({ page }) => {
    // Проверяем, что нет крупных элементов с белым фоном
    const whiteBackgroundElements = await page.evaluate(() => {
      const allElements = document.querySelectorAll('*');
      const whiteElements = [];
      
      for (const el of allElements) {
        if (whiteElements.length > 10) break; // Ограничиваем проверку
        
        const style = window.getComputedStyle(el);
        const bg = style.backgroundColor;
        const rect = el.getBoundingClientRect();
        
        // Ищем элементы с белым фоном и значительным размером
        if ((bg === 'rgb(255, 255, 255)' || bg === 'rgba(255, 255, 255, 1)') && 
            rect.width > 50 && rect.height > 50) {
          whiteElements.push({
            tag: el.tagName,
            className: el.className,
            backgroundColor: bg,
            size: { width: rect.width, height: rect.height }
          });
        }
      }
      
      return whiteElements;
    });
    
    // Допускаем только мелкие UI элементы (кнопки, переключатели)
    expect(whiteBackgroundElements.length).toBeLessThan(3);
  });
});

test.describe('Дополнительные проверки функциональности', () => {
  test('Переключение слоев карты должно работать', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // Нажимаем кнопку Satellite
    await page.locator('button[title="Satellite"]').click();
    
    // Проверяем, что переключение произошло
    await page.waitForTimeout(500); // Даем время на обновление
    
    // Проверяем наличие тайлов
    const tileCount = await page.evaluate(() => {
      return document.querySelectorAll('.leaflet-tile').length;
    });
    
    expect(tileCount).toBeGreaterThan(0);
  });

  test('Запуск симуляции должен работать', async ({ page }) => {
    await page.goto('http://localhost:5173');
    
    // Нажимаем кнопку запуска симуляции
    await page.getByText('Initiate Simulation').click();
    
    // Проверяем, что появился индикатор прогресса
    await expect(page.getByText(/COMPUTING|Processing/)).toBeVisible({ timeout: 5000 });
    
    // Ждем завершения симуляции (демо-режим)
    await page.waitForTimeout(3000);
    
    // Проверяем, что появились результаты
    await expect(page.getByText('Mission Statistics')).toBeVisible({ timeout: 10000 });
  });
});