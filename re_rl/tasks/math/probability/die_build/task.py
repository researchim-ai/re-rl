"""DieBuildTask — число способов набрать сумму несколькими кубиками.

Грани 1, 2 и 3. После каждого кубика способы складываются по всем граням.
Число кубиков растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

FACES = (1, 2, 3)


def conv_ways(dice: int, target: int) -> List[Tuple[int, int, int]]:
    ways = {0: 1}
    trace = []
    for _ in range(dice):
        nxt: Dict[int, int] = {}
        for total, count in ways.items():
            for face in FACES:
                nxt[total + face] = nxt.get(total + face, 0) + count
        ways = nxt
        best = min(ways, key=lambda total: (-ways[total], total))
        trace.append((ways.get(target, 0), best, ways[best]))
    return trace


class DieBuildTask(BaseMathTask):
    TASK_TYPE = "die_build"
    TASK_TYPES = ["ways", "mode"]

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
        self.target = random.randint(self.n, self.n * 3)
        self.trace = conv_ways(self.n, self.target)
        self.ways = self.trace[-1][0]
        self.mode = self.trace[-1][1]
        self.answer = self.ways if self.task_type == "ways" else self.mode
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        key = "s0" if self.task_type == "ways" else "s1"
        return texts.t(key, language, n=self.n, target=self.target)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, ways=ways, mode=mode, best=best)
            for index, (ways, mode, best) in enumerate(self.trace, 1)
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
