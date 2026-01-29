# re_rl/tasks/physics/constants.py

"""
Физические константы для задач.

Все значения в СИ (метр, килограмм, секунда, ампер, кельвин, моль, кандела).
"""

from typing import Dict, Any


# Фундаментальные константы
PHYSICS_CONSTANTS: Dict[str, Dict[str, Any]] = {
    # Механика
    "g": {
        "value": 9.81,
        "unit": "м/с²",
        "unit_en": "m/s²",
        "name_ru": "Ускорение свободного падения",
        "name_en": "Gravitational acceleration",
    },
    "G": {
        "value": 6.674e-11,
        "unit": "Н·м²/кг²",
        "unit_en": "N·m²/kg²",
        "name_ru": "Гравитационная постоянная",
        "name_en": "Gravitational constant",
    },
    
    # Электромагнетизм
    "c": {
        "value": 299792458,
        "unit": "м/с",
        "unit_en": "m/s",
        "name_ru": "Скорость света в вакууме",
        "name_en": "Speed of light in vacuum",
    },
    "e": {
        "value": 1.602176634e-19,
        "unit": "Кл",
        "unit_en": "C",
        "name_ru": "Элементарный заряд",
        "name_en": "Elementary charge",
    },
    "epsilon_0": {
        "value": 8.8541878128e-12,
        "unit": "Ф/м",
        "unit_en": "F/m",
        "name_ru": "Электрическая постоянная",
        "name_en": "Electric constant (vacuum permittivity)",
    },
    "mu_0": {
        "value": 1.25663706212e-6,
        "unit": "Гн/м",
        "unit_en": "H/m",
        "name_ru": "Магнитная постоянная",
        "name_en": "Magnetic constant (vacuum permeability)",
    },
    "k_e": {
        "value": 8.9875517923e9,
        "unit": "Н·м²/Кл²",
        "unit_en": "N·m²/C²",
        "name_ru": "Постоянная Кулона",
        "name_en": "Coulomb's constant",
    },
    
    # Термодинамика
    "k_B": {
        "value": 1.380649e-23,
        "unit": "Дж/К",
        "unit_en": "J/K",
        "name_ru": "Постоянная Больцмана",
        "name_en": "Boltzmann constant",
    },
    "R": {
        "value": 8.314462618,
        "unit": "Дж/(моль·К)",
        "unit_en": "J/(mol·K)",
        "name_ru": "Универсальная газовая постоянная",
        "name_en": "Universal gas constant",
    },
    "N_A": {
        "value": 6.02214076e23,
        "unit": "моль⁻¹",
        "unit_en": "mol⁻¹",
        "name_ru": "Число Авогадро",
        "name_en": "Avogadro's number",
    },
    "sigma": {
        "value": 5.670374419e-8,
        "unit": "Вт/(м²·К⁴)",
        "unit_en": "W/(m²·K⁴)",
        "name_ru": "Постоянная Стефана-Больцмана",
        "name_en": "Stefan-Boltzmann constant",
    },
    
    # Квантовая физика
    "h": {
        "value": 6.62607015e-34,
        "unit": "Дж·с",
        "unit_en": "J·s",
        "name_ru": "Постоянная Планка",
        "name_en": "Planck constant",
    },
    "hbar": {
        "value": 1.054571817e-34,
        "unit": "Дж·с",
        "unit_en": "J·s",
        "name_ru": "Приведённая постоянная Планка",
        "name_en": "Reduced Planck constant",
    },
    
    # Атомная физика
    "m_e": {
        "value": 9.1093837015e-31,
        "unit": "кг",
        "unit_en": "kg",
        "name_ru": "Масса электрона",
        "name_en": "Electron mass",
    },
    "m_p": {
        "value": 1.67262192369e-27,
        "unit": "кг",
        "unit_en": "kg",
        "name_ru": "Масса протона",
        "name_en": "Proton mass",
    },
    "m_n": {
        "value": 1.67492749804e-27,
        "unit": "кг",
        "unit_en": "kg",
        "name_ru": "Масса нейтрона",
        "name_en": "Neutron mass",
    },
    
    # Астрономические
    "AU": {
        "value": 1.495978707e11,
        "unit": "м",
        "unit_en": "m",
        "name_ru": "Астрономическая единица",
        "name_en": "Astronomical unit",
    },
    "M_sun": {
        "value": 1.989e30,
        "unit": "кг",
        "unit_en": "kg",
        "name_ru": "Масса Солнца",
        "name_en": "Solar mass",
    },
    "M_earth": {
        "value": 5.972e24,
        "unit": "кг",
        "unit_en": "kg",
        "name_ru": "Масса Земли",
        "name_en": "Earth mass",
    },
    "R_earth": {
        "value": 6.371e6,
        "unit": "м",
        "unit_en": "m",
        "name_ru": "Радиус Земли",
        "name_en": "Earth radius",
    },
}


def get_constant(name: str) -> float:
    """Возвращает значение физической константы."""
    if name not in PHYSICS_CONSTANTS:
        raise ValueError(f"Unknown constant: {name}")
    return PHYSICS_CONSTANTS[name]["value"]


def get_constant_with_unit(name: str, language: str = "ru") -> str:
    """Возвращает константу с единицей измерения в виде строки."""
    if name not in PHYSICS_CONSTANTS:
        raise ValueError(f"Unknown constant: {name}")
    
    const = PHYSICS_CONSTANTS[name]
    unit_key = "unit" if language == "ru" else "unit_en"
    return f"{const['value']} {const[unit_key]}"


def format_constant_info(name: str, language: str = "ru") -> str:
    """Возвращает полную информацию о константе."""
    if name not in PHYSICS_CONSTANTS:
        raise ValueError(f"Unknown constant: {name}")
    
    const = PHYSICS_CONSTANTS[name]
    name_key = "name_ru" if language == "ru" else "name_en"
    unit_key = "unit" if language == "ru" else "unit_en"
    
    return f"{const[name_key]}: {const['value']} {const[unit_key]}"
