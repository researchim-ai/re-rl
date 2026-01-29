# re_rl/tasks/physics/units.py

"""
Модуль для работы с единицами измерения.

Поддерживает конвертацию и форматирование физических величин.
"""

from typing import Dict, Tuple, Optional
import math


# Таблицы конвертации в базовые единицы СИ
UNIT_CONVERSIONS: Dict[str, Dict[str, float]] = {
    # Длина -> метры
    "length": {
        "m": 1.0,
        "km": 1000.0,
        "cm": 0.01,
        "mm": 0.001,
        "um": 1e-6,
        "nm": 1e-9,
        "mi": 1609.344,
        "ft": 0.3048,
        "in": 0.0254,
        "yd": 0.9144,
    },
    # Масса -> килограммы
    "mass": {
        "kg": 1.0,
        "g": 0.001,
        "mg": 1e-6,
        "t": 1000.0,
        "lb": 0.453592,
        "oz": 0.0283495,
    },
    # Время -> секунды
    "time": {
        "s": 1.0,
        "ms": 0.001,
        "us": 1e-6,
        "ns": 1e-9,
        "min": 60.0,
        "h": 3600.0,
        "d": 86400.0,
    },
    # Скорость -> м/с
    "velocity": {
        "m/s": 1.0,
        "km/h": 1/3.6,
        "km/s": 1000.0,
        "mi/h": 0.44704,
        "ft/s": 0.3048,
    },
    # Ускорение -> м/с²
    "acceleration": {
        "m/s^2": 1.0,
        "m/s²": 1.0,
        "g": 9.81,  # единицы g
    },
    # Сила -> ньютоны
    "force": {
        "N": 1.0,
        "kN": 1000.0,
        "mN": 0.001,
        "dyn": 1e-5,
        "lbf": 4.44822,
    },
    # Энергия -> джоули
    "energy": {
        "J": 1.0,
        "kJ": 1000.0,
        "MJ": 1e6,
        "eV": 1.602176634e-19,
        "keV": 1.602176634e-16,
        "MeV": 1.602176634e-13,
        "cal": 4.184,
        "kcal": 4184.0,
        "kWh": 3.6e6,
    },
    # Мощность -> ватты
    "power": {
        "W": 1.0,
        "kW": 1000.0,
        "MW": 1e6,
        "hp": 745.7,
    },
    # Давление -> паскали
    "pressure": {
        "Pa": 1.0,
        "kPa": 1000.0,
        "MPa": 1e6,
        "bar": 1e5,
        "atm": 101325.0,
        "mmHg": 133.322,
        "psi": 6894.76,
    },
    # Температура (особый случай - не множитель)
    "temperature": {
        "K": ("K", 0),
        "C": ("K", 273.15),
        "F": ("K", None),  # Специальная обработка
    },
    # Электрический заряд -> кулоны
    "charge": {
        "C": 1.0,
        "mC": 0.001,
        "uC": 1e-6,
        "nC": 1e-9,
        "pC": 1e-12,
        "e": 1.602176634e-19,
    },
    # Напряжение -> вольты
    "voltage": {
        "V": 1.0,
        "mV": 0.001,
        "kV": 1000.0,
        "MV": 1e6,
    },
    # Сопротивление -> омы
    "resistance": {
        "Ω": 1.0,
        "ohm": 1.0,
        "mΩ": 0.001,
        "kΩ": 1000.0,
        "MΩ": 1e6,
    },
    # Ёмкость -> фарады
    "capacitance": {
        "F": 1.0,
        "mF": 0.001,
        "uF": 1e-6,
        "nF": 1e-9,
        "pF": 1e-12,
    },
    # Угол -> радианы
    "angle": {
        "rad": 1.0,
        "deg": math.pi / 180,
        "°": math.pi / 180,
    },
    # Частота -> герцы
    "frequency": {
        "Hz": 1.0,
        "kHz": 1000.0,
        "MHz": 1e6,
        "GHz": 1e9,
    },
}


# Названия единиц на русском и английском
UNIT_NAMES: Dict[str, Dict[str, Tuple[str, str]]] = {
    "length": {
        "m": ("м", "m"),
        "km": ("км", "km"),
        "cm": ("см", "cm"),
        "mm": ("мм", "mm"),
    },
    "mass": {
        "kg": ("кг", "kg"),
        "g": ("г", "g"),
        "t": ("т", "t"),
    },
    "time": {
        "s": ("с", "s"),
        "min": ("мин", "min"),
        "h": ("ч", "h"),
    },
    "velocity": {
        "m/s": ("м/с", "m/s"),
        "km/h": ("км/ч", "km/h"),
    },
    "force": {
        "N": ("Н", "N"),
        "kN": ("кН", "kN"),
    },
    "energy": {
        "J": ("Дж", "J"),
        "kJ": ("кДж", "kJ"),
    },
    "power": {
        "W": ("Вт", "W"),
        "kW": ("кВт", "kW"),
    },
    "pressure": {
        "Pa": ("Па", "Pa"),
        "kPa": ("кПа", "kPa"),
        "atm": ("атм", "atm"),
    },
    "temperature": {
        "K": ("К", "K"),
        "C": ("°C", "°C"),
    },
    "voltage": {
        "V": ("В", "V"),
    },
    "resistance": {
        "Ω": ("Ом", "Ω"),
    },
}


def find_unit_type(unit: str) -> Optional[str]:
    """Находит тип величины по единице измерения."""
    for unit_type, conversions in UNIT_CONVERSIONS.items():
        if unit in conversions:
            return unit_type
    return None


def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """
    Конвертирует значение из одной единицы в другую.
    
    Args:
        value: Исходное значение
        from_unit: Исходная единица измерения
        to_unit: Целевая единица измерения
    
    Returns:
        Сконвертированное значение
    
    Raises:
        ValueError: Если единицы несовместимы или неизвестны
    """
    from_type = find_unit_type(from_unit)
    to_type = find_unit_type(to_unit)
    
    if from_type is None:
        raise ValueError(f"Unknown unit: {from_unit}")
    if to_type is None:
        raise ValueError(f"Unknown unit: {to_unit}")
    if from_type != to_type:
        raise ValueError(f"Incompatible units: {from_unit} ({from_type}) and {to_unit} ({to_type})")
    
    # Специальная обработка температуры
    if from_type == "temperature":
        return _convert_temperature(value, from_unit, to_unit)
    
    # Стандартная конвертация через базовую единицу
    conversions = UNIT_CONVERSIONS[from_type]
    base_value = value * conversions[from_unit]
    return base_value / conversions[to_unit]


def _convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """Конвертация температуры."""
    # Сначала в Кельвины
    if from_unit == "K":
        kelvin = value
    elif from_unit == "C":
        kelvin = value + 273.15
    elif from_unit == "F":
        kelvin = (value - 32) * 5/9 + 273.15
    else:
        raise ValueError(f"Unknown temperature unit: {from_unit}")
    
    # Из Кельвинов в целевую единицу
    if to_unit == "K":
        return kelvin
    elif to_unit == "C":
        return kelvin - 273.15
    elif to_unit == "F":
        return (kelvin - 273.15) * 9/5 + 32
    else:
        raise ValueError(f"Unknown temperature unit: {to_unit}")


def format_with_units(
    value: float, 
    unit: str, 
    language: str = "ru",
    precision: int = 4
) -> str:
    """
    Форматирует значение с единицей измерения.
    
    Args:
        value: Числовое значение
        unit: Единица измерения
        language: Язык ('ru' или 'en')
        precision: Количество значащих цифр
    
    Returns:
        Отформатированная строка
    """
    # Форматируем число
    if abs(value) >= 1000 or (abs(value) < 0.01 and value != 0):
        formatted_value = f"{value:.{precision}g}"
    else:
        formatted_value = f"{value:.{precision}f}".rstrip('0').rstrip('.')
    
    # Получаем название единицы
    unit_type = find_unit_type(unit)
    if unit_type and unit_type in UNIT_NAMES and unit in UNIT_NAMES[unit_type]:
        unit_name = UNIT_NAMES[unit_type][unit][0 if language == "ru" else 1]
    else:
        unit_name = unit
    
    return f"{formatted_value} {unit_name}"


def auto_scale_unit(value: float, base_unit: str) -> Tuple[float, str]:
    """
    Автоматически масштабирует значение к удобной единице.
    
    Например: 0.001 m -> 1 mm, 1500 m -> 1.5 km
    
    Returns:
        (scaled_value, new_unit)
    """
    unit_type = find_unit_type(base_unit)
    if unit_type is None:
        return value, base_unit
    
    conversions = UNIT_CONVERSIONS[unit_type]
    
    # Сортируем по множителю
    sorted_units = sorted(
        [(u, f) for u, f in conversions.items() if isinstance(f, (int, float))],
        key=lambda x: x[1],
        reverse=True
    )
    
    # Находим наиболее подходящую единицу
    base_value = value * conversions.get(base_unit, 1.0)
    
    for unit, factor in sorted_units:
        scaled = base_value / factor
        if 0.1 <= abs(scaled) < 1000 or scaled == 0:
            return scaled, unit
    
    return value, base_unit
