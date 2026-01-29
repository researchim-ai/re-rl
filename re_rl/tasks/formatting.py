# re_rl/tasks/formatting.py
"""
Утилиты для форматирования математических выражений.

Поддерживаемые форматы:
- "text": обычный текстовый формат (x² + 2x - 3)
- "latex": LaTeX формат ($x^{2} + 2x - 3$)
- "unicode": Unicode символы (x² + 2x − 3)
"""

from typing import Union, Any, Literal
import sympy as sp

FormatType = Literal["text", "latex", "unicode"]


class MathFormatter:
    """Форматтер математических выражений."""
    
    # Unicode замены для text формата
    SUPERSCRIPTS = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '-': '⁻', '+': '⁺', 'n': 'ⁿ'
    }
    
    SUBSCRIPTS = {
        '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
        '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
        '-': '₋', '+': '₊'
    }
    
    @classmethod
    def format_expression(
        cls, 
        expr: Union[sp.Expr, str, Any], 
        format_type: FormatType = "text"
    ) -> str:
        """
        Форматирует математическое выражение в заданном формате.
        
        Args:
            expr: Sympy выражение или строка
            format_type: "text", "latex" или "unicode"
            
        Returns:
            Отформатированная строка
        """
        if format_type == "latex":
            return cls._to_latex(expr)
        elif format_type == "unicode":
            return cls._to_unicode(expr)
        else:  # text
            return cls._to_text(expr)
    
    @classmethod
    def _to_latex(cls, expr: Union[sp.Expr, str, Any]) -> str:
        """Конвертирует выражение в LaTeX."""
        if isinstance(expr, str):
            try:
                expr = sp.sympify(expr)
            except:
                return expr
        
        try:
            return sp.latex(expr)
        except:
            return str(expr)
    
    @classmethod
    def _to_text(cls, expr: Union[sp.Expr, str, Any]) -> str:
        """Конвертирует выражение в текст с Unicode символами."""
        if isinstance(expr, sp.Expr):
            text = str(expr)
        else:
            text = str(expr)
        
        # Заменяем ** на степени
        import re
        
        def replace_power(match):
            base = match.group(1)
            exp = match.group(2)
            sup = ''.join(cls.SUPERSCRIPTS.get(c, c) for c in exp)
            return f"{base}{sup}"
        
        # x**2 -> x²
        text = re.sub(r'(\w)\*\*(\d+)', replace_power, text)
        
        # Заменяем * на · (умножение) только между числами/переменными
        text = re.sub(r'(\w)\*(\w)', r'\1·\2', text)
        
        return text
    
    @classmethod
    def _to_unicode(cls, expr: Union[sp.Expr, str, Any]) -> str:
        """Конвертирует выражение в Unicode формат."""
        text = cls._to_text(expr)
        # Дополнительные Unicode замены
        text = text.replace('-', '−')  # минус
        text = text.replace('sqrt', '√')
        text = text.replace('pi', 'π')
        text = text.replace('inf', '∞')
        return text
    
    @classmethod
    def wrap_latex(cls, latex_str: str, inline: bool = True) -> str:
        """
        Оборачивает LaTeX строку в разделители.
        
        Args:
            latex_str: LaTeX выражение
            inline: True для $...$ (inline), False для $$...$$ (display)
        """
        if inline:
            return f"${latex_str}$"
        return f"$${latex_str}$$"
    
    @classmethod
    def format_equation(
        cls,
        lhs: Union[sp.Expr, str],
        rhs: Union[sp.Expr, str] = 0,
        format_type: FormatType = "text"
    ) -> str:
        """
        Форматирует уравнение lhs = rhs.
        
        Args:
            lhs: Левая часть уравнения
            rhs: Правая часть уравнения
            format_type: Формат вывода
        """
        if format_type == "latex":
            lhs_latex = cls._to_latex(lhs)
            rhs_latex = cls._to_latex(rhs)
            return f"{lhs_latex} = {rhs_latex}"
        else:
            lhs_text = cls._to_text(lhs)
            rhs_text = cls._to_text(rhs)
            return f"{lhs_text} = {rhs_text}"
    
    @classmethod
    def format_fraction(
        cls,
        numerator: Union[sp.Expr, str, int],
        denominator: Union[sp.Expr, str, int],
        format_type: FormatType = "text"
    ) -> str:
        """Форматирует дробь."""
        if format_type == "latex":
            num = cls._to_latex(numerator)
            den = cls._to_latex(denominator)
            return f"\\frac{{{num}}}{{{den}}}"
        else:
            return f"({numerator})/({denominator})"
    
    @classmethod  
    def format_sqrt(
        cls,
        expr: Union[sp.Expr, str, int],
        format_type: FormatType = "text"
    ) -> str:
        """Форматирует квадратный корень."""
        if format_type == "latex":
            inner = cls._to_latex(expr)
            return f"\\sqrt{{{inner}}}"
        else:
            return f"√({expr})"
    
    @classmethod
    def format_subscript(cls, base: str, sub: str, format_type: FormatType = "text") -> str:
        """Форматирует индекс (subscript)."""
        if format_type == "latex":
            return f"{base}_{{{sub}}}"
        else:
            sub_text = ''.join(cls.SUBSCRIPTS.get(c, c) for c in str(sub))
            return f"{base}{sub_text}"
    
    @classmethod
    def format_superscript(cls, base: str, sup: str, format_type: FormatType = "text") -> str:
        """Форматирует степень (superscript)."""
        if format_type == "latex":
            return f"{base}^{{{sup}}}"
        else:
            sup_text = ''.join(cls.SUPERSCRIPTS.get(c, c) for c in str(sup))
            return f"{base}{sup_text}"


    # ========== Физические форматы ==========
    
    # Греческие буквы
    GREEK_TEXT = {
        'alpha': 'α', 'beta': 'β', 'gamma': 'γ', 'delta': 'δ', 'epsilon': 'ε',
        'zeta': 'ζ', 'eta': 'η', 'theta': 'θ', 'iota': 'ι', 'kappa': 'κ',
        'lambda': 'λ', 'mu': 'μ', 'nu': 'ν', 'xi': 'ξ', 'pi': 'π',
        'rho': 'ρ', 'sigma': 'σ', 'tau': 'τ', 'phi': 'φ', 'chi': 'χ',
        'psi': 'ψ', 'omega': 'ω', 'Delta': 'Δ', 'Omega': 'Ω', 'Sigma': 'Σ',
    }
    
    GREEK_LATEX = {
        'alpha': '\\alpha', 'beta': '\\beta', 'gamma': '\\gamma', 'delta': '\\delta',
        'epsilon': '\\epsilon', 'zeta': '\\zeta', 'eta': '\\eta', 'theta': '\\theta',
        'lambda': '\\lambda', 'mu': '\\mu', 'nu': '\\nu', 'xi': '\\xi', 'pi': '\\pi',
        'rho': '\\rho', 'sigma': '\\sigma', 'tau': '\\tau', 'phi': '\\phi',
        'chi': '\\chi', 'psi': '\\psi', 'omega': '\\omega', 'Delta': '\\Delta',
        'Omega': '\\Omega', 'Sigma': '\\Sigma',
    }
    
    # Физические единицы
    UNITS_TEXT = {
        'm/s': 'м/с', 'm/s^2': 'м/с²', 'kg': 'кг', 'm': 'м', 's': 'с',
        'N': 'Н', 'J': 'Дж', 'W': 'Вт', 'Pa': 'Па', 'K': 'К', 'C': 'Кл',
        'V': 'В', 'A': 'А', 'Ohm': 'Ом', 'F': 'Ф', 'H': 'Гн', 'T': 'Тл',
        'Hz': 'Гц', 'eV': 'эВ', 'MeV': 'МэВ',
    }
    
    UNITS_LATEX = {
        'm/s': '\\text{м/с}', 'm/s^2': '\\text{м/с}^2', 'kg': '\\text{кг}',
        'm': '\\text{м}', 's': '\\text{с}', 'N': '\\text{Н}', 'J': '\\text{Дж}',
        'W': '\\text{Вт}', 'Pa': '\\text{Па}', 'K': '\\text{К}', 'C': '\\text{Кл}',
        'V': '\\text{В}', 'A': '\\text{А}', 'Ohm': '\\Omega', 'F': '\\text{Ф}',
        'H': '\\text{Гн}', 'T': '\\text{Тл}', 'Hz': '\\text{Гц}',
        'eV': '\\text{эВ}', 'MeV': '\\text{МэВ}',
    }
    
    @classmethod
    def format_physics_value(
        cls,
        value: Union[float, int, str],
        unit: str,
        format_type: FormatType = "text",
        precision: int = 4
    ) -> str:
        """
        Форматирует физическую величину с единицей измерения.
        
        Args:
            value: Числовое значение
            unit: Единица измерения
            format_type: Формат вывода
            precision: Точность для float
        """
        # Форматируем число
        if isinstance(value, float):
            if abs(value) < 0.001 or abs(value) > 10000:
                val_str = f"{value:.{precision}e}"
            else:
                val_str = f"{value:.{precision}f}".rstrip('0').rstrip('.')
        else:
            val_str = str(value)
        
        if format_type == "latex":
            unit_latex = cls.UNITS_LATEX.get(unit, f"\\text{{{unit}}}")
            return f"${val_str} \\, {unit_latex}$"
        else:
            unit_text = cls.UNITS_TEXT.get(unit, unit)
            return f"{val_str} {unit_text}"
    
    @classmethod
    def format_physics_formula(
        cls,
        formula: str,
        format_type: FormatType = "text"
    ) -> str:
        """
        Форматирует физическую формулу.
        
        Args:
            formula: Формула (например, "F = ma", "E = mc^2")
            format_type: Формат вывода
        """
        if format_type == "latex":
            # Заменяем греческие буквы
            result = formula
            for name, latex in cls.GREEK_LATEX.items():
                result = result.replace(name, latex)
            return f"${result}$"
        else:
            result = formula
            for name, symbol in cls.GREEK_TEXT.items():
                result = result.replace(name, symbol)
            return result
    
    @classmethod
    def format_integral(
        cls,
        integrand: str,
        var: str = "x",
        lower: str = None,
        upper: str = None,
        format_type: FormatType = "text"
    ) -> str:
        """Форматирует интеграл."""
        if format_type == "latex":
            if lower and upper:
                return f"$\\int_{{{lower}}}^{{{upper}}} {integrand} \\, d{var}$"
            return f"$\\int {integrand} \\, d{var}$"
        else:
            if lower and upper:
                return f"∫[{lower},{upper}] {integrand} d{var}"
            return f"∫ {integrand} d{var}"
    
    @classmethod
    def format_derivative(
        cls,
        func: str,
        var: str = "x",
        order: int = 1,
        format_type: FormatType = "text"
    ) -> str:
        """Форматирует производную."""
        if format_type == "latex":
            if order == 1:
                return f"$\\frac{{d{func}}}{{d{var}}}$"
            return f"$\\frac{{d^{order}{func}}}{{d{var}^{order}}}$"
        else:
            if order == 1:
                return f"d{func}/d{var}"
            return f"d^{order}{func}/d{var}^{order}"
    
    @classmethod
    def format_limit(
        cls,
        expr: str,
        var: str = "x",
        to: str = "∞",
        format_type: FormatType = "text"
    ) -> str:
        """Форматирует предел."""
        if format_type == "latex":
            to_latex = to.replace("∞", "\\infty")
            return f"$\\lim_{{{var} \\to {to_latex}}} {expr}$"
        else:
            return f"lim({var}→{to}) {expr}"
    
    @classmethod
    def format_sum(
        cls,
        expr: str,
        var: str = "n",
        lower: str = "1",
        upper: str = "∞",
        format_type: FormatType = "text"
    ) -> str:
        """Форматирует сумму ряда."""
        if format_type == "latex":
            upper_latex = upper.replace("∞", "\\infty")
            return f"$\\sum_{{{var}={lower}}}^{{{upper_latex}}} {expr}$"
        else:
            return f"Σ({var}={lower}..{upper}) {expr}"
    
    @classmethod
    def format_matrix(
        cls,
        matrix: list,
        format_type: FormatType = "text"
    ) -> str:
        """Форматирует матрицу."""
        if format_type == "latex":
            rows = []
            for row in matrix:
                rows.append(" & ".join(str(x) for x in row))
            return "$\\begin{pmatrix} " + " \\\\ ".join(rows) + " \\end{pmatrix}$"
        else:
            rows = []
            for row in matrix:
                rows.append("[" + ", ".join(str(x) for x in row) + "]")
            return "[" + ", ".join(rows) + "]"


# Удобные функции-сокращения
def to_latex(expr: Union[sp.Expr, str, Any], wrap: bool = True) -> str:
    """Конвертирует выражение в LaTeX."""
    latex = MathFormatter.format_expression(expr, "latex")
    return MathFormatter.wrap_latex(latex) if wrap else latex


def to_text(expr: Union[sp.Expr, str, Any]) -> str:
    """Конвертирует выражение в текстовый формат."""
    return MathFormatter.format_expression(expr, "text")


def format_math(
    expr: Union[sp.Expr, str, Any], 
    format_type: FormatType = "text",
    wrap_latex: bool = True
) -> str:
    """
    Универсальная функция форматирования.
    
    Args:
        expr: Выражение для форматирования
        format_type: "text" или "latex"
        wrap_latex: Оборачивать LaTeX в $...$
    """
    result = MathFormatter.format_expression(expr, format_type)
    if format_type == "latex" and wrap_latex:
        result = MathFormatter.wrap_latex(result)
    return result


def format_value(value, unit: str, format_type: str = "text", precision: int = 4) -> str:
    """Форматирует физическую величину."""
    return MathFormatter.format_physics_value(value, unit, format_type, precision)
