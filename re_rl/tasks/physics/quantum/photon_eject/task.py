"""PhotonEjectTask — фотоны выбивают электроны, если энергии хватает на работу выхода.

Кинетическая энергия выбитого электрона равна энергии фотона минус работа выхода.
Число фотонов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def photon_trace(work: int, energies: Sequence[int]) -> List[Tuple[int, int, int]]:
    count = 0
    kinetic = 0
    trace = []
    for energy in energies:
        gained = 0
        if energy >= work:
            count += 1
            gained = energy - work
            kinetic += gained
        trace.append((gained, count, kinetic))
    return trace


class PhotonEjectTask(BaseMathTask):
    TASK_TYPE = "photon_eject"
    TASK_TYPES = ["count", "kinetic"]

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
        self.work = random.randint(2, 6)
        self.energies = [random.randint(1, 10) for _ in range(self.n)]
        self.trace = photon_trace(self.work, self.energies)
        _, self.count, self.kinetic = self.trace[-1]
        self.answer = self.count if self.task_type == "count" else self.kinetic
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(str(energy) for energy in self.energies)
        key = "s0" if self.task_type == "count" else "s1"
        return texts.t(key, language, work=self.work, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, energy=energy, gained=gained, count=count, kinetic=kinetic)
            for index, (energy, (gained, count, kinetic)) in enumerate(zip(self.energies, self.trace), 1)
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
