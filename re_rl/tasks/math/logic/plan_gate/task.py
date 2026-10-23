"""PlanGateTask — план из шагов с одним предусловием.

В начале включён только бит 1. Шаг срабатывает, если нужный бит уже есть, и тогда включает свой бит.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Action = Tuple[int, int]


def plan_trace(actions: Sequence[Action]) -> Tuple[List[Tuple[int, int]], Set[int]]:
    state = {1}
    fired = 0
    trace = []
    for need, put in actions:
        if need in state:
            state.add(put)
            fired += 1
        trace.append((fired, put if put in state else 0))
        # store fired and whether put is on; the set is separate
    return trace, state


class PlanGateTask(BaseMathTask):
    TASK_TYPE = "plan_gate"
    TASK_TYPES = ["fired", "has"]

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
        self.actions = [
            (random.randint(1, 4), random.randint(1, 6))
            for _ in range(self.n)
        ]
        self.trace, self.state = plan_trace(self.actions)
        self.fired = self.trace[-1][0]
        self.bit = random.randint(1, 6)
        self.has = int(self.bit in self.state)
        self.answer = self.fired if self.task_type == "fired" else self.has
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = "; ".join(f"{need}>{put}" for need, put in self.actions)
        key = "s0" if self.task_type == "fired" else "s1"
        return texts.t(key, language, n=self.n, listing=listing, bit=self.bit)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, need=need, put=put, fired=fired)
            for index, ((need, put), (fired, _)) in enumerate(zip(self.actions, self.trace), 1)
        ]
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
