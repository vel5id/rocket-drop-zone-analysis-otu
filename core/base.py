"""
Базовые классы и интерфейсы для проекта rocket-drop-zone-analysis-otu.
Ссылка на спецификацию: architecture/base_classes из требований проекта.

Этот модуль содержит абстрактные классы и интерфейсы, которые определяют
контракты для основных компонентов системы.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import numpy as np
from enum import Enum


class SimulationStatus(Enum):
    """Статусы выполнения симуляции."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SimulationResult:
    """Базовый класс для результатов симуляции.
    
    Attributes:
        status: Статус выполнения
        data: Данные результатов
        metadata: Метаданные симуляции
        errors: Список ошибок (если есть)
    """
    status: SimulationStatus
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ISimulationEngine(ABC):
    """Интерфейс для движка симуляции.
    
    Определяет контракт для всех движков симуляции в системе.
    """
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Инициализация движка с конфигурацией.
        
        Args:
            config: Конфигурация движка
        """
        pass
    
    @abstractmethod
    def run(self, parameters: Dict[str, Any]) -> SimulationResult:
        """Запуск симуляции с заданными параметрами.
        
        Args:
            parameters: Параметры симуляции
            
        Returns:
            Результат симуляции
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Валидация параметров симуляции.
        
        Args:
            parameters: Параметры для валидации
            
        Returns:
            Список ошибок валидации (пустой если валидация прошла успешно)
        """
        pass
    
    @abstractmethod
    def get_progress(self) -> float:
        """Получение текущего прогресса симуляции.
        
        Returns:
            Прогресс от 0.0 до 1.0
        """
        pass
    
    @abstractmethod
    def cancel(self) -> None:
        """Отмена текущей симуляции."""
        pass


class IDataProvider(ABC):
    """Интерфейс для провайдеров данных.
    
    Определяет контракт для получения данных из различных источников.
    """
    
    @abstractmethod
    def connect(self, connection_params: Dict[str, Any]) -> bool:
        """Подключение к источнику данных.
        
        Args:
            connection_params: Параметры подключения
            
        Returns:
            True если подключение успешно, иначе False
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Отключение от источника данных."""
        pass
    
    @abstractmethod
    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Получение данных по запросу.
        
        Args:
            query: Запрос данных
            
        Returns:
            Данные в формате словаря
        """
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Получение метаданных источника данных.
        
        Returns:
            Метаданные источника
        """
        pass


class IIndexCalculator(ABC):
    """Интерфейс для калькуляторов экологических индексов.
    
    Определяет контракт для расчета различных экологических индексов.
    """
    
    @abstractmethod
    def calculate(self, input_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Расчет индекса на основе входных данных.
        
        Args:
            input_data: Входные данные в формате словаря
            
        Returns:
            Результаты расчета в формате словаря
        """
        pass
    
    @abstractmethod
    def normalize(self, values: np.ndarray) -> np.ndarray:
        """Нормализация значений индекса.
        
        Args:
            values: Исходные значения
            
        Returns:
            Нормализованные значения в диапазоне [0, 1]
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, np.ndarray]) -> List[str]:
        """Валидация входных данных.
        
        Args:
            input_data: Входные данные для валидации
            
        Returns:
            Список ошибок валидации
        """
        pass


class IVisualizationRenderer(ABC):
    """Интерфейс для рендереров визуализации.
    
    Определяет контракт для создания визуализаций результатов.
    """
    
    @abstractmethod
    def render_map(self, data: Dict[str, Any], style: Dict[str, Any]) -> Any:
        """Рендеринг карты.
        
        Args:
            data: Данные для отображения
            style: Стили отображения
            
        Returns:
            Объект карты (зависит от реализации)
        """
        pass
    
    @abstractmethod
    def render_chart(self, data: Dict[str, Any], chart_type: str) -> Any:
        """Рендеринг графика.
        
        Args:
            data: Данные для графика
            chart_type: Тип графика
            
        Returns:
            Объект графика
        """
        pass
    
    @abstractmethod
    def export(self, visualization: Any, format: str, path: str) -> bool:
        """Экспорт визуализации в файл.
        
        Args:
            visualization: Объект визуализации
            format: Формат экспорта (png, pdf, html и т.д.)
            path: Путь для сохранения
            
        Returns:
            True если экспорт успешен, иначе False
        """
        pass


class BaseModel(ABC):
    """Базовый класс для всех моделей в системе.
    
    Предоставляет общую функциональность для сериализации, валидации и т.д.
    """
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразование модели в словарь.
        
        Returns:
            Словарь с данными модели
        """
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Создание модели из словаря.
        
        Args:
            data: Данные для создания модели
            
        Returns:
            Экземпляр модели
        """
        pass
    
    def validate(self) -> List[str]:
        """Валидация модели.
        
        Returns:
            Список ошибок валидации
        """
        # Базовая реализация - возвращает пустой список
        # Наследники могут переопределить этот метод
        return []


# Базовые исключения системы
class RocketAnalysisError(Exception):
    """Базовое исключение для проекта."""
    pass


class SimulationError(RocketAnalysisError):
    """Исключение для ошибок симуляции."""
    pass


class DataProviderError(RocketAnalysisError):
    """Исключение для ошибок провайдеров данных."""
    pass


class ValidationError(RocketAnalysisError):
    """Исключение для ошибок валидации."""
    pass


class ConfigurationError(RocketAnalysisError):
    """Исключение для ошибок конфигурации."""
    pass