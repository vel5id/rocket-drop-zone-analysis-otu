"""
Data Transfer Objects (DTO) для проекта rocket-drop-zone-analysis-otu.
Ссылка на спецификацию: architecture/data_transfer_objects из требований проекта.

Этот модуль содержит классы DTO для передачи данных между слоями приложения.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import numpy as np
from datetime import datetime


class CoordinateSystem(Enum):
    """Системы координат."""
    WGS84 = "WGS84"  # EPSG:4326
    UTM = "UTM"      # Universal Transverse Mercator
    ECEF = "ECEF"    # Earth-Centered, Earth-Fixed


@dataclass
class GeoPoint:
    """Географическая точка с координатами.
    
    Attributes:
        latitude: Широта в градусах
        longitude: Долгота в градусах
        altitude: Высота в метрах (опционально)
    """
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    
    def to_tuple(self) -> Tuple[float, float]:
        """Преобразование в кортеж (широта, долгота)."""
        return (self.latitude, self.longitude)
    
    def to_3d_tuple(self) -> Tuple[float, float, float]:
        """Преобразование в кортеж (широта, долгота, высота)."""
        if self.altitude is not None:
            return (self.latitude, self.longitude, self.altitude)
        return (self.latitude, self.longitude, 0.0)


@dataclass
class BoundingBox:
    """Ограничивающий прямоугольник (bounding box).
    
    Attributes:
        min_lat: Минимальная широта
        max_lat: Максимальная широта
        min_lon: Минимальная долгота
        max_lon: Максимальная долгота
    """
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    
    @property
    def center(self) -> GeoPoint:
        """Центр bounding box."""
        center_lat = (self.min_lat + self.max_lat) / 2
        center_lon = (self.min_lon + self.max_lon) / 2
        return GeoPoint(latitude=center_lat, longitude=center_lon)
    
    @property
    def width(self) -> float:
        """Ширина в градусах долготы."""
        return self.max_lon - self.min_lon
    
    @property
    def height(self) -> float:
        """Высота в градусах широты."""
        return self.max_lat - self.min_lat


@dataclass
class RocketParameters:
    """Параметры ракеты-носителя.
    
    Attributes:
        name: Название РН
        dry_mass: Сухая масса (кг)
        propellant_mass: Масса топлива (кг)
        diameter: Диаметр (м)
        length: Длина (м)
        reference_area: Площадь миделя (м²)
        drag_coefficient: Коэффициент лобового сопротивления
    """
    name: str
    dry_mass: float
    propellant_mass: float
    diameter: float
    length: float
    reference_area: float
    drag_coefficient: float = 1.2


@dataclass
class EngineParameters:
    """Параметры двигательной установки.
    
    Attributes:
        name: Название двигателя
        thrust: Тяга (Н)
        specific_impulse_vacuum: Удельный импульс в вакууме (с)
        specific_impulse_sea_level: Удельный импульс на уровне моря (с)
        burn_time: Время работы (с)
        count: Количество двигателей
    """
    name: str
    thrust: float
    specific_impulse_vacuum: float
    specific_impulse_sea_level: float
    burn_time: float
    count: int = 1


@dataclass
class SeparationParameters:
    """Параметры отделения ступени.
    
    Attributes:
        altitude: Высота отделения (м)
        velocity: Скорость отделения (м/с)
        flight_path_angle: Угол траектории (градусы)
        azimuth: Азимут (градусы)
        latitude: Широта точки отделения
        longitude: Долгота точки отделения
    """
    altitude: float
    velocity: float
    flight_path_angle: float
    azimuth: float
    latitude: float
    longitude: float


@dataclass
class MonteCarloParameters:
    """Параметры метода Монте-Карло.
    
    Attributes:
        iterations: Количество итераций
        seed: Seed для генератора случайных чисел
        distributions: Распределения параметров
        perturbations: Возмущения параметров
    """
    iterations: int
    seed: Optional[int] = None
    distributions: Dict[str, str] = field(default_factory=dict)
    perturbations: Dict[str, Dict[str, float]] = field(default_factory=dict)


@dataclass
class SimulationRequest:
    """Запрос на выполнение симуляции.
    
    Attributes:
        rocket_params: Параметры ракеты
        engine_params: Параметры двигателя
        separation_params: Параметры отделения
        monte_carlo_params: Параметры Монте-Карло
        bounding_box: Область анализа
        output_format: Формат выходных данных
        metadata: Дополнительные метаданные
    """
    rocket_params: RocketParameters
    engine_params: EngineParameters
    separation_params: SeparationParameters
    monte_carlo_params: MonteCarloParameters
    bounding_box: BoundingBox
    output_format: str = "geojson"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ImpactPoint:
    """Точка падения.
    
    Attributes:
        latitude: Широта
        longitude: Долгота
        altitude: Высота
        velocity: Скорость в момент падения (м/с)
        angle: Угол падения (градусы)
        iteration: Номер итерации Монте-Карло
    """
    latitude: float
    longitude: float
    altitude: float
    velocity: float
    angle: float
    iteration: int


@dataclass
class DispersionEllipse:
    """Эллипс рассеивания.
    
    Attributes:
        center: Центр эллипса
        semi_major_axis: Большая полуось (м)
        semi_minor_axis: Малая полуось (м)
        orientation: Ориентация (градусы от севера)
        sigma_level: Уровень сигма (1σ, 2σ, 3σ)
        confidence: Доверительная вероятность
    """
    center: GeoPoint
    semi_major_axis: float
    semi_minor_axis: float
    orientation: float
    sigma_level: int = 3
    confidence: float = 0.997


@dataclass
class EcologicalIndex:
    """Экологический индекс для ячейки.
    
    Attributes:
        q_vi: Вегетационный индекс [0, 1]
        q_si: Индекс прочности почв [0, 1]
        q_bi: Индекс качества почв [0, 1]
        q_relief: Модификатор рельефа [0, 1]
        q_otu: Композитный индекс Q_OTU [0, 1]
        latitude: Широта центра ячейки
        longitude: Долгота центра ячейки
        cell_id: Идентификатор ячейки
    """
    q_vi: float
    q_si: float
    q_bi: float
    q_relief: float
    q_otu: float
    latitude: float
    longitude: float
    cell_id: str


@dataclass
class GridCell:
    """Ячейка сетки.
    
    Attributes:
        id: Идентификатор ячейки
        bounding_box: Bounding box ячейки
        centroid: Центроид ячейки
        area: Площадь ячейки (м²)
        ecological_index: Экологический индекс (опционально)
        impact_probability: Вероятность попадания (опционально)
    """
    id: str
    bounding_box: BoundingBox
    centroid: GeoPoint
    area: float
    ecological_index: Optional[EcologicalIndex] = None
    impact_probability: Optional[float] = None


@dataclass
class SimulationResponse:
    """Ответ с результатами симуляции.
    
    Attributes:
        request_id: Идентификатор запроса
        status: Статус выполнения
        impact_points: Точки падения
        dispersion_ellipses: Эллипсы рассеивания
        grid_cells: Ячейки сетки с результатами
        statistics: Статистика симуляции
        execution_time: Время выполнения (сек)
        errors: Ошибки выполнения
        metadata: Дополнительные метаданные
    """
    request_id: str
    status: str
    impact_points: List[ImpactPoint]
    dispersion_ellipses: List[DispersionEllipse]
    grid_cells: List[GridCell]
    statistics: Dict[str, Any]
    execution_time: float
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VisualizationRequest:
    """Запрос на создание визуализации.
    
    Attributes:
        simulation_response: Результаты симуляции
        visualization_type: Тип визуализации
        style: Стили отображения
        output_path: Путь для сохранения
        format: Формат выходного файла
    """
    simulation_response: SimulationResponse
    visualization_type: str
    style: Dict[str, Any]
    output_path: str
    format: str = "png"


@dataclass
class ExportRequest:
    """Запрос на экспорт данных.
    
    Attributes:
        data: Данные для экспорта
        format: Формат экспорта
        output_path: Путь для сохранения
        options: Дополнительные опции
    """
    data: Any
    format: str
    output_path: str
    options: Dict[str, Any] = field(default_factory=dict)


# DTO для конфигурации
@dataclass
class AppConfig:
    """Конфигурация приложения.
    
    Attributes:
        log_level: Уровень логирования
        max_workers: Максимальное количество worker'ов
        cache_enabled: Включено ли кэширование
        cache_ttl: TTL кэша (сек)
        output_dir: Директория для выходных файлов
        temp_dir: Директория для временных файлов
    """
    log_level: str = "INFO"
    max_workers: int = 4
    cache_enabled: bool = True
    cache_ttl: int = 3600
    output_dir: str = "./output"
    temp_dir: str = "./temp"