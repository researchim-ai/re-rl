"""DopplerChainTask — цепочка точных доплеровских сдвигов.

Наблюдатель покоится, источник едет к нему. Частота умножается на c/(c-vs).
Скорости подобраны так, что деление нацело. Число шагов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

SOUND = 12
GAPS = (3, 4, 6, 12)


def doppler_trace(start: int, speeds: Sequence[int], sound: int = SOUND) -> List[Tuple[int, int]]:
    freq = start
    rises = 0
    trace = []
    for speed in speeds:
        nxt = freq * sound // (sound - speed)
        if nxt > freq:
            rises += 1
        freq = nxt
        trace.append((freq, rises))
    return trace


class DopplerChainTask(BaseMathTask):
    TASK_TYPE = "doppler_chain"
    TASK_TYPES = ["final", "rises"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2}, 2: {"n": 2}, 3: {"n": 3}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 8}, 10: {"n": 9},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.sound = SOUND
        self.start = random.randint(2, 8)
        self.speeds = [self.sound - random.choice(GAPS) for _ in range(self.n)]
        self.trace = doppler_trace(self.start, self.speeds, self.sound)
        self.final, self.rises = self.trace[-1]
        self.answer = self.final if self.task_type == "final" else self.rises
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(value) for value in self.speeds)
        key = "s0" if self.task_type == "final" else "s1"
        return texts.t(key, language, sound=self.sound, start=self.start, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, speed=speed, freq=freq, rises=rises)
            for index, (speed, (freq, rises)) in enumerate(zip(self.speeds, self.trace), 1)
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
