"""CodonScanTask — проход по кодонам в поисках стоп-сигнала.

Стоп-кодоны TAG, TAA и TGA. Остальные кодоны цепочку не обрывают.
Число кодонов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

BASES = ("A", "C", "G", "T")
STOPS = ("TAG", "TAA", "TGA")
CODING = tuple(
    first + second + third
    for first in BASES for second in BASES for third in BASES
    if first + second + third not in STOPS
)


def scan_codons(codons: Sequence[str]):
    stops = 0
    first = 0
    trace = []
    for index, codon in enumerate(codons, 1):
        hit = codon in STOPS
        if hit:
            stops += 1
            if first == 0:
                first = index
        trace.append((hit, stops))
    return stops, first, trace


class CodonScanTask(BaseMathTask):
    TASK_TYPE = "codon_scan"
    TASK_TYPES = ["stops", "first"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 4},
        5: {"n": 5}, 6: {"n": 6}, 7: {"n": 7}, 8: {"n": 8},
        9: {"n": 10}, 10: {"n": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(3, int(p["n"]))
        self.codons = [random.choice(CODING) for _ in range(self.n)]
        extras = random.randint(0, min(3, self.n))
        for index in random.sample(range(self.n), extras):
            self.codons[index] = random.choice(STOPS)
        self.stops, self.first, self.trace = scan_codons(self.codons)
        self.answer = self.stops if self.task_type == "stops" else self.first
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        listing = ", ".join(self.codons)
        key = "s0" if self.task_type == "stops" else "s1"
        return texts.t(key, language, n=self.n, listing=listing)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, codon=codon, hit=int(hit), stops=stops)
            for index, (codon, (hit, stops)) in enumerate(zip(self.codons, self.trace), 1)
        ]
        steps.append(texts.t("s3", self.language, stops=self.stops, first=self.first))
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
