"""
Абстракции для экологических индексов проекта rocket-drop-zone-analysis-otu.
Ссылка на спецификацию: ecological_indices/abstract_classes из требований проекта.

Этот модуль содержит абстрактные классы для расчета экологических индексов.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum


class IndexType(Enum):
    """Типы экологических индексов."""
    VEGETATION = "vegetation"
    SOIL_STRENGTH = "soil_strength"
    SOIL_QUALITY = "soil_quality"
    RELIEF = "relief"
    COMPOSITE = "composite"
    FIRE_RISK = "fire_risk"
    ASPECT = "aspect"


@dataclass
class IndexMetadata:
    """Метаданные индекса.
    
    Attributes:
        name: Название индекса
        description: Описание индекса
        version: Версия расчета
        author: Автор реализации
        citation: Цитирование (если требуется)
        units: Единицы измерения
        valid_range: Допустимый диапазон значений
    """
    name: str
    description: str
    version: str
    author: str
    citation: Optional[str] = None
    units: str = "unitless"
    valid_range: Tuple[float, float] = (0.0, 1.0)


class BaseEcologicalIndex(ABC):
    """Базовый абстрактный класс для экологических индексов.
    
    Определяет общий интерфейс для всех экологических индексов в системе.
    """
    
    def __init__(self, metadata: IndexMetadata):
        """
        Args:
            metadata: Метаданные индекса
        """
        self.metadata = metadata
    
    @abstractmethod
    def calculate(self, input_data: Dict[str, np.ndarray]) -> np.ndarray:
        """Основной метод расчета индекса.
        
        Args:
            input_data: Входные данные в формате словаря
            
        Returns:
            Массив с рассчитанными значениями индекса
        """
        pass
    
    @abstractmethod
    def normalize(self, values: np.ndarray) -> np.ndarray:
        """Нормализация значений индекса к диапазону [0, 1].
        
        Args:
            values: Исходные значения индекса
            
        Returns:
            Нормализованные значения
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, np.ndarray]) -> List[str]:
        """Валидация входных данных.
        
        Args:
            input_data: Входные данные для валидации
            
        Returns:
            Список ошибок валидации (пустой если все OK)
        """
        pass
    
    def get_metadata(self) -> IndexMetadata:
        """Получение метаданных индекса.
        
        Returns:
            Метаданные индекса
        """
        return self.metadata
    
    def apply_mask(self, index_values: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """Применение маски к значениям индекса.
        
        Args:
            index_values: Значения индекса
            mask: Маска (True - валидные пиксели, False - игнорировать)
            
        Returns:
            Значения индекса с примененной маской
        """
        result = index_values.copy()
        result[~mask] = np.nan
        return result


class VegetationIndex(BaseEcologicalIndex):
    """Абстрактный класс для вегетационных индексов."""
    
    def __init__(self, metadata: IndexMetadata):
        super().__init__(metadata)
    
    @abstractmethod
    def calculate_ndvi(self, red: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """Расчет NDVI (Normalized Difference Vegetation Index).
        
        Args:
            red: Красный канал
            nir: Ближний инфракрасный канал
            
        Returns:
            Значения NDVI
        """
        pass
    
    @abstractmethod
    def calculate_evi(self, blue: np.ndarray, red: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """Расчет EVI (Enhanced Vegetation Index).
        
        Args:
            blue: Синий канал
            red: Красный канал
            nir: Ближний инфракрасный канал
            
        Returns:
            Значения EVI
        """
        pass


class SoilIndex(BaseEcologicalIndex):
    """Абстрактный класс для почвенных индексов."""
    
    def __init__(self, metadata: IndexMetadata):
        super().__init__(metadata)
    
    @abstractmethod
    def calculate_bulk_density_index(self, bulk_density: np.ndarray) -> np.ndarray:
        """Расчет индекса на основе объемной плотности почвы.
        
        Args:
            bulk_density: Объемная плотность почвы (г/см³)
            
        Returns:
            Значения индекса
        """
        pass
    
    @abstractmethod
    def calculate_clay_content_index(self, clay_content: np.ndarray) -> np.ndarray:
        """Расчет индекса на основе содержания глины.
        
        Args:
            clay_content: Содержание глины (%)
            
        Returns:
            Значения индекса
        """
        pass
    
    @abstractmethod
    def calculate_organic_carbon_index(self, organic_carbon: np.ndarray) -> np.ndarray:
        """Расчет индекса на основе органического углерода.
        
        Args:
            organic_carbon: Содержание органического углерода (%)
            
        Returns:
            Значения индекса
        """
        pass


class ReliefIndex(BaseEcologicalIndex):
    """Абстрактный класс для индексов рельефа."""
    
    def __init__(self, metadata: IndexMetadata):
        super().__init__(metadata)
    
    @abstractmethod
    def calculate_slope_index(self, slope: np.ndarray) -> np.ndarray:
        """Расчет индекса на основе уклона.
        
        Args:
            slope: Уклон (градусы)
            
        Returns:
            Значения индекса
        """
        pass
    
    @abstractmethod
    def calculate_aspect_index(self, aspect: np.ndarray) -> np.ndarray:
        """Расчет индекса на основе экспозиции склона.
        
        Args:
            aspect: Экспозиция (градусы от севера)
            
        Returns:
            Значения индекса
        """
        pass
    
    @abstractmethod
    def calculate_water_body_mask(self, water_data: np.ndarray) -> np.ndarray:
        """Создание маски водных объектов.
        
        Args:
            water_data: Данные о водных объектах
            
        Returns:
            Маска (True - водный объект, False - суша)
        """
        pass


class CompositeIndex(BaseEcologicalIndex):
    """Абстрактный класс для композитных индексов."""
    
    def __init__(self, metadata: IndexMetadata, weights: Dict[str, float]):
        """
        Args:
            metadata: Метаданные индекса
            weights: Веса компонентов индекса
        """
        super().__init__(metadata)
        self.weights = weights
    
    @abstractmethod
    def combine_indices(self, indices: Dict[str, np.ndarray]) -> np.ndarray:
        """Комбинирование нескольких индексов в один композитный.
        
        Args:
            indices: Словарь с индексами для комбинирования
            
        Returns:
            Композитный индекс
        """
        pass
    
    def validate_weights(self) -> List[str]:
        """Валидация весов компонентов.
        
        Returns:
            Список ошибок валидации
        """
        errors = []
        
        # Проверка, что сумма весов равна 1.0
        total_weight = sum(self.weights.values())
        if not np.isclose(total_weight, 1.0, atol=1e-6):
            errors.append(f"Сумма весов ({total_weight}) не равна 1.0")
        
        # Проверка, что все веса неотрицательные
        for name, weight in self.weights.items():
            if weight < 0:
                errors.append(f"Вес '{name}' отрицательный: {weight}")
        
        return errors


# Фабрика для создания индексов
class IndexFactory:
    """Фабрика для создания экологических индексов."""
    
    _registry = {}
    
    @classmethod
    def register(cls, index_type: IndexType, index_class):
        """Регистрация класса индекса.
        
        Args:
            index_type: Тип индекса
            index_class: Класс индекса
        """
        cls._registry[index_type] = index_class
    
    @classmethod
    def create(cls, index_type: IndexType, **kwargs):
        """Создание экземпляра индекса.
        
        Args:
            index_type: Тип индекса
            **kwargs: Аргументы для конструктора
            
        Returns:
            Экземпляр индекса
            
        Raises:
            ValueError: Если тип индекса не зарегистрирован
        """
        if index_type not in cls._registry:
            raise ValueError(f"Тип индекса '{index_type}' не зарегистрирован")
        
        index_class = cls._registry[index_type]
        return index_class(**kwargs)
    
    @classmethod
    def get_available_indices(cls) -> List[IndexType]:
        """Получение списка доступных типов индексов.
        
        Returns:
            Список зарегистрированных типов индексов
        """
        return list(cls._registry.keys())