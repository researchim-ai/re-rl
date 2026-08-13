"""SeriesParallelNetworkTask — свёртка последовательно-параллельной сети.

Один движок случайного дерева соединений порождает четыре изоморфных домена:
- ``resistor``  — резисторы (последовательно = сумма);
- ``capacitor`` — конденсаторы (параллельно = сумма);
- ``spring``    — пружины (параллельно = сумма жёсткостей);
- ``thermal``   — тепловые сопротивления (последовательно = сумма).

Сложность масштабируется числом элементов N. Проверка числовая (относительный
допуск 2%); эталон вычисляется точной рекурсией.
"""

import random
from typing import Any, ClassVar, Dict, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.physics._phys_utils import NumericPhysicsVerifyMixin, fmt

# Узел дерева: ('leaf', value) | ('series', left, right) | ('parallel', left, right)
Node = Tuple


class SeriesParallelNetworkTask(NumericPhysicsVerifyMixin, BaseMathTask):
    """Эквивалент последовательно-параллельной сети из N элементов."""

    TASK_TYPE = "series_parallel_network"
    TASK_TYPES = ["resistor", "capacitor", "spring", "thermal"]

    # Для resistor/thermal последовательное соединение складывает величины;
    # для capacitor/spring складываются параллельные.
    _SERIES_IS_SUM = {"resistor": True, "thermal": True,
                      "capacitor": False, "spring": False}

    _UNIT = {"resistor": ("Ом", "Ω"), "capacitor": ("мкФ", "µF"),
             "spring": ("Н/м", "N/m"), "thermal": ("К/Вт", "K/W")}

    _RULE_STEP = {"resistor": "resistor_rule", "capacitor": "capacitor_rule",
                  "spring": "spring_rule", "thermal": "thermal_rule"}

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "max_val": 20}, 2: {"n": 3, "max_val": 30},
        3: {"n": 3, "max_val": 50}, 4: {"n": 4, "max_val": 60},
        5: {"n": 5, "max_val": 80}, 6: {"n": 6, "max_val": 100},
        7: {"n": 7, "max_val": 120}, 8: {"n": 8, "max_val": 150},
        9: {"n": 9, "max_val": 200}, 10: {"n": 10, "max_val": 300},
    }

    def __init__(self, task_type: str = None, language: str = "ru", detail_level: int = 3,
                 difficulty: int = 5, output_format: OutputFormat = "text",
                 reasoning_mode: bool = False, **kwargs):
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.difficulty = difficulty
        preset = self._interpolate_difficulty(difficulty)
        self._preset = preset
        self.n = max(2, int(round(preset["n"])))
        self.max_val = int(preset["max_val"])
        # Для n >= 3 гарантируем смешанную топологию (есть и последовательное, и
        # параллельное соединение) — иначе задача вырождается в «плоский» случай,
        # уже покрытый CircuitsTask/CapacitorsTask.
        self.tree = self._build_tree(self.n)
        if self.n >= 3:
            for _ in range(30):
                if len(self._ops_used(self.tree)) >= 2:
                    break
                self.tree = self._build_tree(self.n)

        description = self._create_problem_description(language)
        super().__init__(description, language, detail_level, output_format)
        self.reasoning_mode = reasoning_mode

    def _build_tree(self, n: int) -> Node:
        if n <= 1:
            return ("leaf", random.randint(1, self.max_val))
        left_n = random.randint(1, n - 1)
        op = random.choice(("series", "parallel"))
        return (op, self._build_tree(left_n), self._build_tree(n - left_n))

    def _ops_used(self, node: Node) -> set:
        if node[0] == "leaf":
            return set()
        return {node[0]} | self._ops_used(node[1]) | self._ops_used(node[2])

    def _unit(self) -> str:
        u = self._UNIT[self.task_type]
        return u[0] if self.language == "ru" else u[1]

    def _render(self, node: Node) -> str:
        if node[0] == "leaf":
            return f"{node[1]} {self._unit()}"
        if self.language == "ru":
            word = "последовательно" if node[0] == "series" else "параллельно"
        else:
            word = "series" if node[0] == "series" else "parallel"
        return f"{word}({self._render(node[1])}, {self._render(node[2])})"

    def _combine(self, op: str, a: float, b: float) -> float:
        series_is_sum = self._SERIES_IS_SUM[self.task_type]
        add = op == "series" if series_is_sum else op == "parallel"
        if add:
            return a + b
        return a * b / (a + b)

    def _evaluate(self, node: Node) -> float:
        if node[0] == "leaf":
            return float(node[1])
        return self._combine(node[0], self._evaluate(node[1]), self._evaluate(node[2]))

    def _create_problem_description(self, language: str) -> str:
        p = PROMPT_TEMPLATES["series_parallel_network"]["problem"][self.task_type][language]
        return p.format(net=self._render(self.tree))

    def solve(self):
        self.solution_steps = []
        steps = PROMPT_TEMPLATES["series_parallel_network"]["steps"]
        self.solution_steps.append(steps[self._RULE_STEP[self.task_type]][self.language])
        self.solution_steps.append(steps["reduce"][self.language])
        value = self._evaluate(self.tree)
        u = self._unit()
        self.solution_steps.append(f"Эквивалент = {fmt(value)} {u}")
        self.final_answer = f"{fmt(value)} {u}"
        self._answer_numbers = [value]

    @classmethod
    def generate_random_task(cls, task_type: str = None, language: str = "ru",
                             detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, **kwargs):
        task = cls(task_type=task_type, language=language, detail_level=detail_level,
                   difficulty=difficulty, reasoning_mode=reasoning_mode)
        task.solve()
        return task
