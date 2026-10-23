"""ToolPickTask — выбор самого дешёвого инструмента под тип запроса.

При равной цене берётся меньший номер. Число запросов растёт с уровнем.
На запрос смотрится короткий список инструментов, это дёшево при генерации.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Tool = Tuple[int, Tuple[int, ...]]


def tool_assign(queries: Sequence[int], tools: Sequence[Tool]) -> Tuple[List[int], int]:
    chosen = []
    total = 0
    for kind in queries:
        best = 0
        best_cost = None
        for index, (cost, kinds) in enumerate(tools, 1):
            if kind in kinds and (best_cost is None or cost < best_cost):
                best = index
                best_cost = cost
        chosen.append(best)
        total += best_cost
    return chosen, total


class ToolPickTask(BaseMathTask):
    TASK_TYPE = "tool_pick"
    TASK_TYPES = ["cost", "tool"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.tools = []
        for kind in range(1, 5):
            self.tools.append((random.randint(1, 9), (kind,)))
        for index in range(4):
            extra = random.randint(1, 4)
            cost, kinds = self.tools[index]
            if extra not in kinds:
                self.tools[index] = (cost, kinds + (extra,))
        self.queries = [random.randint(1, 4) for _ in range(self.n)]
        self.chosen, self.cost = tool_assign(self.queries, self.tools)
        self.k = random.randint(1, self.n)
        self.tool = self.chosen[self.k - 1]
        self.answer = self.cost if self.task_type == "cost" else self.tool
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _tool_text(self, index: int, tool: Tool) -> str:
        cost, kinds = tool
        covered = " ".join(str(kind) for kind in kinds)
        return f"{index}: {cost} / {covered}"

    def _descr(self, language):
        tools = "; ".join(self._tool_text(index, tool) for index, tool in enumerate(self.tools, 1))
        queries = ", ".join(str(kind) for kind in self.queries)
        key = "s0" if self.task_type == "cost" else "s1"
        return texts.t(key, language, n=self.n, tools=tools, queries=queries, k=self.k)

    def solve(self):
        running = 0
        steps = []
        for index, (kind, tool) in enumerate(zip(self.queries, self.chosen), 1):
            cost = self.tools[tool - 1][0]
            running += cost
            steps.append(texts.t(
                "s2", self.language, i=index, kind=kind, tool=tool, cost=running,
            ))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
