"""DoneBootTask — цель шага с обрывом бутстрапа.

Если признак конца равен 1, цель равна награде. Иначе к награде прибавляется следующее значение.
Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Row = Tuple[int, int, int]


def boot_trace(rows: Sequence[Row]) -> List[Tuple[int, int, int]]:
    total = 0
    terminals = 0
    trace = []
    for reward, nxt, done in rows:
        target = reward if done else reward + nxt
        total += target
        terminals += done
        trace.append((target, total, terminals))
    return trace


class DoneBootTask(BaseMathTask):
    TASK_TYPE = "done_boot"
    TASK_TYPES = ["total", "terminals"]

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
        self.rows = [
            (random.randint(-2, 4), random.randint(0, 5), random.randint(0, 1))
            for _ in range(self.n)
        ]
        self.trace = boot_trace(self.rows)
        self.total = self.trace[-1][1]
        self.terminals = self.trace[-1][2]
        self.answer = self.total if self.task_type == "total" else self.terminals
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{reward} {nxt} {done}" for reward, nxt, done in self.rows)
        key = "s0" if self.task_type == "total" else "s1"
        return texts.t(key, language, n=self.n, rows=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, reward=reward, nxt=nxt, done=done, target=target, total=total)
            for index, ((reward, nxt, done), (target, total, _terminals)) in enumerate(zip(self.rows, self.trace), 1)
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
