# re_rl/tasks/physics/constants.py

"""
Физические константы для задач.

Все значения в СИ (метр, килограмм, секунда, ампер, кельвин, моль, кандела).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__, 'constants_i18n.json')


from typing import Dict, Any


# Фундаментальные константы
PHYSICS_CONSTANTS: Dict[str, Dict[str, Any]] = {
    # Механика
    "g": {
        "value": 9.81,
        "unit": texts.literal('literals.s3'),
        "unit_en": "m/s²",
        "name_ru": texts.literal('literals.s4'),
        "name_en": "Gravitational acceleration",
    },
    "G": {
        "value": 6.674e-11,
        "unit": texts.literal('literals.s5'),
        "unit_en": "N·m²/kg²",
        "name_ru": texts.literal('literals.s6'),
        "name_en": "Gravitational constant",
    },
    
    # Электромагнетизм
    "c": {
        "value": 299792458,
        "unit": texts.literal('literals.s7'),
        "unit_en": "m/s",
        "name_ru": texts.literal('literals.s8'),
        "name_en": "Speed of light in vacuum",
    },
    "e": {
        "value": 1.602176634e-19,
        "unit": texts.literal('literals.s9'),
        "unit_en": "C",
        "name_ru": texts.literal('literals.s10'),
        "name_en": "Elementary charge",
    },
    "epsilon_0": {
        "value": 8.8541878128e-12,
        "unit": texts.literal('literals.s11'),
        "unit_en": "F/m",
        "name_ru": texts.literal('literals.s12'),
        "name_en": "Electric constant (vacuum permittivity)",
    },
    "mu_0": {
        "value": 1.25663706212e-6,
        "unit": texts.literal('literals.s13'),
        "unit_en": "H/m",
        "name_ru": texts.literal('literals.s14'),
        "name_en": "Magnetic constant (vacuum permeability)",
    },
    "k_e": {
        "value": 8.9875517923e9,
        "unit": texts.literal('literals.s15'),
        "unit_en": "N·m²/C²",
        "name_ru": texts.literal('literals.s16'),
        "name_en": "Coulomb's constant",
    },
    
    # Термодинамика
    "k_B": {
        "value": 1.380649e-23,
        "unit": texts.literal('literals.s17'),
        "unit_en": "J/K",
        "name_ru": texts.literal('literals.s18'),
        "name_en": "Boltzmann constant",
    },
    "R": {
        "value": 8.314462618,
        "unit": texts.literal('literals.s19'),
        "unit_en": "J/(mol·K)",
        "name_ru": texts.literal('literals.s20'),
        "name_en": "Universal gas constant",
    },
    "N_A": {
        "value": 6.02214076e23,
        "unit": texts.literal('literals.s21'),
        "unit_en": "mol⁻¹",
        "name_ru": texts.literal('literals.s22'),
        "name_en": "Avogadro's number",
    },
    "sigma": {
        "value": 5.670374419e-8,
        "unit": texts.literal('literals.s23'),
        "unit_en": "W/(m²·K⁴)",
        "name_ru": texts.literal('literals.s24'),
        "name_en": "Stefan-Boltzmann constant",
    },
    
    # Квантовая физика
    "h": {
        "value": 6.62607015e-34,
        "unit": texts.literal('literals.s25'),
        "unit_en": "J·s",
        "name_ru": texts.literal('literals.s26'),
        "name_en": "Planck constant",
    },
    "hbar": {
        "value": 1.054571817e-34,
        "unit": texts.literal('literals.s27'),
        "unit_en": "J·s",
        "name_ru": texts.literal('literals.s28'),
        "name_en": "Reduced Planck constant",
    },
    
    # Атомная физика
    "m_e": {
        "value": 9.1093837015e-31,
        "unit": texts.literal('literals.s29'),
        "unit_en": "kg",
        "name_ru": texts.literal('literals.s30'),
        "name_en": "Electron mass",
    },
    "m_p": {
        "value": 1.67262192369e-27,
        "unit": texts.literal('literals.s31'),
        "unit_en": "kg",
        "name_ru": texts.literal('literals.s32'),
        "name_en": "Proton mass",
    },
    "m_n": {
        "value": 1.67492749804e-27,
        "unit": texts.literal('literals.s33'),
        "unit_en": "kg",
        "name_ru": texts.literal('literals.s34'),
        "name_en": "Neutron mass",
    },
    
    # Астрономические
    "AU": {
        "value": 1.495978707e11,
        "unit": texts.literal('literals.s35'),
        "unit_en": "m",
        "name_ru": texts.literal('literals.s36'),
        "name_en": "Astronomical unit",
    },
    "M_sun": {
        "value": 1.989e30,
        "unit": texts.literal('literals.s37'),
        "unit_en": "kg",
        "name_ru": texts.literal('literals.s38'),
        "name_en": "Solar mass",
    },
    "M_earth": {
        "value": 5.972e24,
        "unit": texts.literal('literals.s39'),
        "unit_en": "kg",
        "name_ru": texts.literal('literals.s40'),
        "name_en": "Earth mass",
    },
    "R_earth": {
        "value": 6.371e6,
        "unit": texts.literal('literals.s41'),
        "unit_en": "m",
        "name_ru": texts.literal('literals.s42'),
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
    unit_key = (texts.t('s0', language))
    return f"{const['value']} {const[unit_key]}"


def format_constant_info(name: str, language: str = "ru") -> str:
    """Возвращает полную информацию о константе."""
    if name not in PHYSICS_CONSTANTS:
        raise ValueError(f"Unknown constant: {name}")
    
    const = PHYSICS_CONSTANTS[name]
    name_key = (texts.t('s1', language))
    unit_key = (texts.t('s2', language))
    
    return f"{const[name_key]}: {const['value']} {const[unit_key]}"
