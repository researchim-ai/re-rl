# re_rl/tasks/arithmetic_task.py

"""
ArithmeticTask — задачи на арифметические вычисления с настраиваемой сложностью.

Поддерживает:
- Базовые операции: +, -, *, /
- Степени и корни
- Дроби и проценты
- Цепочки операций произвольной длины
- Вложенные скобки
"""

import random
import math
from fractions import Fraction
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES


@dataclass
class ArithmeticConfig:
    """Конфигурация для генерации арифметических задач."""
    num_operations: int = 2  # Количество операций (1-50+)
    max_number: int = 20  # Максимальное число
    min_number: int = 1  # Минимальное число
    operations: List[str] = field(default_factory=lambda: ['+', '-', '*', '/'])
    use_parentheses: bool = True  # Использовать скобки
    use_fractions: bool = False  # Использовать дроби
    use_percentages: bool = False  # Использовать проценты
    use_powers: bool = False  # Использовать степени
    use_roots: bool = False  # Использовать корни
    max_nesting_depth: int = 3  # Максимальная глубина вложенности скобок
    ensure_integer_result: bool = True  # Гарантировать целочисленный результат
    
    
# Пресеты сложности для ArithmeticTask
DIFFICULTY_PRESETS = {
    1: ArithmeticConfig(
        num_operations=1,
        max_number=10,
        operations=['+', '-'],
        use_parentheses=False,
        ensure_integer_result=True
    ),
    2: ArithmeticConfig(
        num_operations=2,
        max_number=20,
        operations=['+', '-', '*'],
        use_parentheses=False,
        ensure_integer_result=True
    ),
    3: ArithmeticConfig(
        num_operations=2,
        max_number=30,
        operations=['+', '-', '*', '/'],
        use_parentheses=True,
        max_nesting_depth=1,
        ensure_integer_result=True
    ),
    4: ArithmeticConfig(
        num_operations=3,
        max_number=50,
        operations=['+', '-', '*', '/'],
        use_parentheses=True,
        max_nesting_depth=2,
        ensure_integer_result=True
    ),
    5: ArithmeticConfig(
        num_operations=4,
        max_number=100,
        operations=['+', '-', '*', '/'],
        use_parentheses=True,
        max_nesting_depth=2,
        use_powers=True,
        ensure_integer_result=True
    ),
    6: ArithmeticConfig(
        num_operations=5,
        max_number=100,
        operations=['+', '-', '*', '/'],
        use_parentheses=True,
        max_nesting_depth=3,
        use_powers=True,
        use_roots=True,
        ensure_integer_result=True
    ),
    7: ArithmeticConfig(
        num_operations=6,
        max_number=200,
        operations=['+', '-', '*', '/'],
        use_parentheses=True,
        max_nesting_depth=3,
        use_powers=True,
        use_roots=True,
        use_fractions=True,
        ensure_integer_result=False
    ),
    8: ArithmeticConfig(
        num_operations=8,
        max_number=500,
        operations=['+', '-', '*', '/'],
        use_parentheses=True,
        max_nesting_depth=4,
        use_powers=True,
        use_roots=True,
        use_fractions=True,
        use_percentages=True,
        ensure_integer_result=False
    ),
    9: ArithmeticConfig(
        num_operations=12,
        max_number=1000,
        operations=['+', '-', '*', '/'],
        use_parentheses=True,
        max_nesting_depth=5,
        use_powers=True,
        use_roots=True,
        use_fractions=True,
        use_percentages=True,
        ensure_integer_result=False
    ),
    10: ArithmeticConfig(
        num_operations=20,
        max_number=1000,
        operations=['+', '-', '*', '/'],
        use_parentheses=True,
        max_nesting_depth=6,
        use_powers=True,
        use_roots=True,
        use_fractions=True,
        use_percentages=True,
        ensure_integer_result=False
    ),
}


class ExpressionNode:
    """Узел дерева выражения для построения арифметических задач."""
    pass


@dataclass
class NumberNode(ExpressionNode):
    """Числовой узел."""
    value: Union[int, float, Fraction]
    is_percentage: bool = False
    
    def evaluate(self) -> float:
        val = float(self.value)
        if self.is_percentage:
            return val / 100
        return val
    
    def to_string(self, language: str = "ru") -> str:
        if self.is_percentage:
            return f"{self.value}%"
        if isinstance(self.value, Fraction):
            return f"{self.value.numerator}/{self.value.denominator}"
        if isinstance(self.value, float) and self.value == int(self.value):
            return str(int(self.value))
        return str(self.value)


@dataclass 
class BinaryOpNode(ExpressionNode):
    """Бинарная операция."""
    left: ExpressionNode
    op: str
    right: ExpressionNode
    
    def evaluate(self) -> float:
        left_val = self.left.evaluate()
        right_val = self.right.evaluate()
        
        if self.op == '+':
            return left_val + right_val
        elif self.op == '-':
            return left_val - right_val
        elif self.op == '*':
            return left_val * right_val
        elif self.op == '/':
            if right_val == 0:
                raise ValueError("Division by zero")
            return left_val / right_val
        elif self.op == '^':
            return left_val ** right_val
        else:
            raise ValueError(f"Unknown operation: {self.op}")
    
    def to_string(self, language: str = "ru") -> str:
        left_str = self.left.to_string(language)
        right_str = self.right.to_string(language)
        
        # Добавляем скобки для вложенных операций если нужно
        if isinstance(self.left, BinaryOpNode):
            if self._needs_parentheses(self.left.op, self.op, is_left=True):
                left_str = f"({left_str})"
        
        if isinstance(self.right, BinaryOpNode):
            if self._needs_parentheses(self.right.op, self.op, is_left=False):
                right_str = f"({right_str})"
        
        op_symbol = self.op
        if self.op == '*':
            op_symbol = '×' if language == 'ru' else '*'
        elif self.op == '/':
            op_symbol = '÷' if language == 'ru' else '/'
        elif self.op == '^':
            return f"{left_str}^{right_str}"
            
        return f"{left_str} {op_symbol} {right_str}"
    
    def _needs_parentheses(self, inner_op: str, outer_op: str, is_left: bool) -> bool:
        """Определяет, нужны ли скобки."""
        precedence = {'+': 1, '-': 1, '*': 2, '/': 2, '^': 3}
        inner_prec = precedence.get(inner_op, 0)
        outer_prec = precedence.get(outer_op, 0)
        
        if inner_prec < outer_prec:
            return True
        if inner_prec == outer_prec and not is_left and outer_op in ['-', '/']:
            return True
        return False


@dataclass
class UnaryOpNode(ExpressionNode):
    """Унарная операция (корень, отрицание)."""
    op: str
    operand: ExpressionNode
    
    def evaluate(self) -> float:
        val = self.operand.evaluate()
        if self.op == 'sqrt':
            if val < 0:
                raise ValueError("Square root of negative number")
            return math.sqrt(val)
        elif self.op == '-':
            return -val
        else:
            raise ValueError(f"Unknown unary operation: {self.op}")
    
    def to_string(self, language: str = "ru") -> str:
        operand_str = self.operand.to_string(language)
        if isinstance(self.operand, BinaryOpNode):
            operand_str = f"({operand_str})"
            
        if self.op == 'sqrt':
            if language == 'ru':
                return f"√({operand_str})"
            return f"sqrt({operand_str})"
        elif self.op == '-':
            return f"-{operand_str}"
        return operand_str


class ArithmeticTask(BaseMathTask):
    """
    Задача на арифметические вычисления с настраиваемой сложностью.
    
    Параметры:
        difficulty: Уровень сложности (1-10), определяет пресет параметров
        config: Явная конфигурация (переопределяет difficulty)
        language: Язык ("ru" или "en")
        detail_level: Уровень детализации решения
        
    Примеры:
        # По уровню сложности
        task = ArithmeticTask(difficulty=5, language="ru")
        
        # С явной конфигурацией
        config = ArithmeticConfig(num_operations=10, max_number=100)
        task = ArithmeticTask(config=config, language="en")
    """
    
    DIFFICULTY_PRESETS = DIFFICULTY_PRESETS
    
    def __init__(
        self,
        difficulty: int = 5,
        config: Optional[ArithmeticConfig] = None,
        language: str = "ru",
        detail_level: int = 3,
        expression: Optional[str] = None,  # Для явного задания выражения
        **config_overrides
    ):
        self.difficulty = difficulty
        self.language = language.lower()
        
        # Определяем конфигурацию
        if config is not None:
            self.config = config
        else:
            # Берём пресет и применяем переопределения
            base_config = self.DIFFICULTY_PRESETS.get(difficulty, self.DIFFICULTY_PRESETS[5])
            config_dict = {
                'num_operations': base_config.num_operations,
                'max_number': base_config.max_number,
                'min_number': base_config.min_number,
                'operations': base_config.operations.copy(),
                'use_parentheses': base_config.use_parentheses,
                'use_fractions': base_config.use_fractions,
                'use_percentages': base_config.use_percentages,
                'use_powers': base_config.use_powers,
                'use_roots': base_config.use_roots,
                'max_nesting_depth': base_config.max_nesting_depth,
                'ensure_integer_result': base_config.ensure_integer_result,
            }
            config_dict.update(config_overrides)
            self.config = ArithmeticConfig(**config_dict)
        
        # Генерируем или используем заданное выражение
        if expression is not None:
            self.expression_str = expression
            self.expression_tree = None
            self.answer = self._evaluate_expression(expression)
        else:
            self.expression_tree = self._generate_expression()
            self.expression_str = self.expression_tree.to_string(self.language)
            self.answer = self.expression_tree.evaluate()
        
        # Формируем описание задачи
        description = self._create_problem_description()
        super().__init__(description, language, detail_level)
    
    def _create_problem_description(self) -> str:
        """Создаёт текст задачи."""
        templates = PROMPT_TEMPLATES.get("arithmetic", {})
        problem_template = templates.get("problem", {}).get(
            self.language, 
            {"ru": "Вычислите: {expression}", "en": "Calculate: {expression}"}[self.language]
        )
        return problem_template.format(expression=self.expression_str)
    
    def _generate_expression(self) -> ExpressionNode:
        """Генерирует случайное арифметическое выражение."""
        max_attempts = 100
        
        for _ in range(max_attempts):
            try:
                expr = self._build_expression(
                    remaining_ops=self.config.num_operations,
                    depth=0
                )
                # Проверяем, что результат валидный
                result = expr.evaluate()
                if math.isnan(result) or math.isinf(result):
                    continue
                    
                # Проверяем целочисленность если требуется
                if self.config.ensure_integer_result:
                    if abs(result - round(result)) > 1e-9:
                        continue
                        
                return expr
            except (ValueError, ZeroDivisionError):
                continue
        
        # Fallback: простое выражение
        a = random.randint(self.config.min_number, self.config.max_number)
        b = random.randint(self.config.min_number, self.config.max_number)
        return BinaryOpNode(NumberNode(a), '+', NumberNode(b))
    
    def _build_expression(self, remaining_ops: int, depth: int) -> ExpressionNode:
        """Рекурсивно строит дерево выражения."""
        # Базовый случай: просто число
        if remaining_ops <= 0 or depth > self.config.max_nesting_depth:
            return self._generate_number_node()
        
        # Выбираем операцию
        available_ops = self.config.operations.copy()
        if self.config.use_powers and depth < 2:  # Степени только на верхних уровнях
            available_ops.append('^')
        
        op = random.choice(available_ops)
        
        # Распределяем оставшиеся операции между левой и правой частью
        if remaining_ops == 1:
            left_ops = 0
            right_ops = 0
        else:
            left_ops = random.randint(0, remaining_ops - 1)
            right_ops = remaining_ops - 1 - left_ops
        
        # Строим поддеревья
        left = self._build_expression(left_ops, depth + 1)
        right = self._build_expression(right_ops, depth + 1)
        
        # Для деления обеспечиваем ненулевой делитель
        if op == '/':
            right = self._ensure_nonzero(right)
            # Для целочисленного результата подбираем делимое
            if self.config.ensure_integer_result:
                left, right = self._make_divisible(left, right)
        
        # Для степени ограничиваем показатель
        if op == '^':
            right = NumberNode(random.randint(2, 3))
        
        node = BinaryOpNode(left, op, right)
        
        # Возможно оборачиваем в корень
        if self.config.use_roots and random.random() < 0.2 and depth == 0:
            # Делаем подкоренное выражение квадратом
            val = node.evaluate()
            if val > 0:
                sqrt_val = int(math.sqrt(val))
                if sqrt_val * sqrt_val == val:
                    return UnaryOpNode('sqrt', node)
        
        return node
    
    def _generate_number_node(self) -> ExpressionNode:
        """Генерирует числовой узел."""
        # Проценты
        if self.config.use_percentages and random.random() < 0.15:
            value = random.choice([10, 20, 25, 50, 75, 100])
            return NumberNode(value, is_percentage=True)
        
        # Дроби
        if self.config.use_fractions and random.random() < 0.2:
            numerator = random.randint(1, 10)
            denominator = random.randint(2, 10)
            return NumberNode(Fraction(numerator, denominator))
        
        # Обычное число
        value = random.randint(self.config.min_number, self.config.max_number)
        return NumberNode(value)
    
    def _ensure_nonzero(self, node: ExpressionNode) -> ExpressionNode:
        """Гарантирует, что узел не равен нулю."""
        try:
            if abs(node.evaluate()) < 1e-9:
                return NumberNode(random.randint(1, self.config.max_number))
        except:
            pass
        return node
    
    def _make_divisible(self, left: ExpressionNode, right: ExpressionNode) -> Tuple[ExpressionNode, ExpressionNode]:
        """Подбирает числа так, чтобы деление было целочисленным."""
        try:
            right_val = int(right.evaluate())
            if right_val == 0:
                right_val = random.randint(1, 10)
                right = NumberNode(right_val)
            
            # Генерируем делимое как кратное делителю
            multiplier = random.randint(1, max(1, self.config.max_number // abs(right_val)))
            left_val = right_val * multiplier
            left = NumberNode(left_val)
        except:
            pass
        return left, right
    
    def _evaluate_expression(self, expr_str: str) -> float:
        """Вычисляет строковое выражение."""
        # Заменяем Unicode символы на стандартные
        expr_str = expr_str.replace('×', '*').replace('÷', '/').replace('√', 'sqrt')
        
        # Безопасное вычисление
        allowed_names = {
            'sqrt': math.sqrt,
            'abs': abs,
            'pow': pow,
        }
        return eval(expr_str, {"__builtins__": {}}, allowed_names)
    
    def solve(self):
        """Решает задачу пошагово."""
        steps = []
        
        if self.expression_tree is not None:
            steps = self._solve_tree(self.expression_tree, 0)
        else:
            # Для явно заданного выражения - простое решение
            if self.language == "ru":
                steps.append(f"Шаг 1: Вычисляем выражение {self.expression_str}")
                steps.append(f"Шаг 2: Результат = {self._format_answer()}")
            else:
                steps.append(f"Step 1: Calculate the expression {self.expression_str}")
                steps.append(f"Step 2: Result = {self._format_answer()}")
        
        # Ограничиваем по detail_level
        self.solution_steps = steps[:self.detail_level] if self.detail_level < len(steps) else steps
        self.final_answer = self._format_answer()
    
    def _solve_tree(self, node: ExpressionNode, step_num: int) -> List[str]:
        """Рекурсивно решает дерево выражения."""
        steps = []
        
        if isinstance(node, NumberNode):
            return steps
        
        if isinstance(node, UnaryOpNode):
            inner_steps = self._solve_tree(node.operand, step_num)
            steps.extend(inner_steps)
            
            step_num += len(inner_steps)
            operand_val = node.operand.evaluate()
            result = node.evaluate()
            
            if self.language == "ru":
                if node.op == 'sqrt':
                    steps.append(f"Шаг {step_num + 1}: Вычисляем √({operand_val}) = {result:.4g}")
            else:
                if node.op == 'sqrt':
                    steps.append(f"Step {step_num + 1}: Calculate sqrt({operand_val}) = {result:.4g}")
            return steps
        
        if isinstance(node, BinaryOpNode):
            # Сначала решаем поддеревья
            left_steps = self._solve_tree(node.left, step_num)
            steps.extend(left_steps)
            
            right_steps = self._solve_tree(node.right, step_num + len(left_steps))
            steps.extend(right_steps)
            
            step_num += len(left_steps) + len(right_steps)
            
            left_val = node.left.evaluate()
            right_val = node.right.evaluate()
            result = node.evaluate()
            
            op_name = {
                '+': ('Складываем', 'Add'),
                '-': ('Вычитаем', 'Subtract'),
                '*': ('Умножаем', 'Multiply'),
                '/': ('Делим', 'Divide'),
                '^': ('Возводим в степень', 'Raise to power'),
            }
            
            ru_name, en_name = op_name.get(node.op, ('Вычисляем', 'Calculate'))
            
            if self.language == "ru":
                steps.append(f"Шаг {step_num + 1}: {ru_name} {left_val:.4g} {node.op} {right_val:.4g} = {result:.4g}")
            else:
                steps.append(f"Step {step_num + 1}: {en_name} {left_val:.4g} {node.op} {right_val:.4g} = {result:.4g}")
            
            return steps
        
        return steps
    
    def _format_answer(self) -> str:
        """Форматирует ответ."""
        if self.config.ensure_integer_result and abs(self.answer - round(self.answer)) < 1e-9:
            return str(int(round(self.answer)))
        return f"{self.answer:.6g}"
    
    def get_task_type(self) -> str:
        return "arithmetic"
    
    @classmethod
    def from_difficulty(cls, difficulty: int, language: str = "ru", detail_level: int = 3, **overrides):
        """Создаёт задачу с заданным уровнем сложности."""
        return cls(difficulty=difficulty, language=language, detail_level=detail_level, **overrides)
