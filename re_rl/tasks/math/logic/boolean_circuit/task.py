"""BooleanCircuitTask — вычисление логической схемы из вентилей.

Подтипы:
- evaluate: значение выхода при заданных входах (0/1);
- count: число наборов входов, дающих на выходе 1.
Вентили: AND, OR, XOR (бинарные), NOT (унарный). Выход — последний вентиль.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_OPS = ["AND", "OR", "XOR", "NOT"]


class BooleanCircuitTask(BaseMathTask):
    TASK_TYPE = "boolean_circuit"
    TASK_TYPES = ["evaluate", "count"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"k": 2, "g": 2}, 2: {"k": 2, "g": 3}, 3: {"k": 3, "g": 3},
        4: {"k": 3, "g": 4}, 5: {"k": 3, "g": 5}, 6: {"k": 4, "g": 5},
        7: {"k": 4, "g": 6}, 8: {"k": 4, "g": 7}, 9: {"k": 5, "g": 8},
        10: {"k": 5, "g": 10},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype: Optional[str] = None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.k = int(preset["k"])
        self.g = int(preset["g"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        # Узлы 0..k-1 — входы; далее вентили. Ссылки — на уже определённые узлы.
        self.gates: List[Tuple[str, int, Optional[int]]] = []
        total = self.k
        for _ in range(self.g):
            op = random.choice(_OPS)
            a = random.randrange(total)
            b = random.randrange(total) if op != "NOT" else None
            self.gates.append((op, a, b))
            total += 1
        self.total = total
        if self.subtype == "evaluate":
            self.inputs = [random.randint(0, 1) for _ in range(self.k)]
            self._answer = self._eval(self.inputs)
        else:
            self._answer = sum(self._eval(list(bits)) for bits in product([0, 1], repeat=self.k))

    def _eval(self, inputs: List[int]) -> int:
        vals = list(inputs)
        for op, a, b in self.gates:
            if op == "NOT":
                vals.append(1 - vals[a])
            elif op == "AND":
                vals.append(vals[a] & vals[b])
            elif op == "OR":
                vals.append(vals[a] | vals[b])
            else:  # XOR
                vals.append(vals[a] ^ vals[b])
        return vals[-1]

    def _node_name(self, idx: int) -> str:
        return f"x{idx + 1}" if idx < self.k else f"g{idx - self.k + 1}"

    def _make_description(self, language: str) -> str:
        lines = []
        for i, (op, a, b) in enumerate(self.gates):
            name = f"g{i + 1}"
            if op == "NOT":
                lines.append(f"{name} = NOT {self._node_name(a)}")
            else:
                lines.append(f"{name} = {self._node_name(a)} {op} {self._node_name(b)}")
        out = f"g{self.g}"
        circuit = "\n".join(lines)
        head = ((texts.t('s0', language, v0=', '.join(('x' + str(i + 1) for i in range(self.k))), out=out, circuit=circuit)))
        if self.subtype == "evaluate":
            assign = ", ".join(f"x{i + 1}={self.inputs[i]}" for i in range(self.k))
            q = ((texts.t('s1', language, assign=assign, out=out)))
        else:
            q = ((texts.t('s2', language, v0=2 ** self.k, out=out)))
        return head + q

    def solve(self):
        if self.subtype == "evaluate":
            self.solution_steps = [
                ((texts.t('s3', self.language))),
                ((texts.t('s4', self.language, _answer=self._answer))),
            ]
        else:
            self.solution_steps = [
                ((texts.t('s5', self.language))),
                ((texts.t('s6', self.language, _answer=self._answer))),
            ]
        self.final_answer = str(self._answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
