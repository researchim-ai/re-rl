"""AgendaVoteTask — повестка попарных голосований.

Первая альтернатива — текущий победитель. Каждая следующая вызывает его и занимает место, если побеждает в паре.
В цикле победитель зависит от порядка повестки.
Число вызовов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Pair = Tuple[int, int, int]


def agenda_trace(agenda: Sequence[int], pairs: Sequence[Pair]) -> List[Tuple[int, int, int, int]]:
    winner = {(left, right): chosen for left, right, chosen in pairs}
    current = agenda[0]
    changes = 0
    trace = []
    for challenger in agenda[1:]:
        previous = current
        left, right = (challenger, current) if challenger < current else (current, challenger)
        if winner[(left, right)] == challenger:
            current = challenger
            changes += 1
        trace.append((challenger, previous, current, changes))
    return trace


class AgendaVoteTask(BaseMathTask):
    TASK_TYPE = "agenda_vote"
    TASK_TYPES = ["winner", "changes"]

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
        self.alts = self.n + 1
        self.pairs: List[Pair] = []
        for left in range(1, self.alts + 1):
            for right in range(left + 1, self.alts + 1):
                self.pairs.append((left, right, random.choice((left, right))))
        self.agenda = list(range(1, self.alts + 1))
        random.shuffle(self.agenda)
        self.trace = agenda_trace(self.agenda, self.pairs)
        self.winner = self.trace[-1][2]
        self.changes = self.trace[-1][3]
        self.answer = self.winner if self.task_type == "winner" else self.changes
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        pairs = ", ".join(f"{chosen}>{left if chosen == right else right}" for left, right, chosen in self.pairs)
        agenda = ", ".join(str(item) for item in self.agenda)
        key = "s0" if self.task_type == "winner" else "s1"
        return texts.t(key, language, alts=self.alts, pairs=pairs, agenda=agenda)

    def solve(self):
        steps = [
            texts.t(
                "s2", self.language, i=index, challenger=challenger, previous=previous,
                current=current, changes=changes,
            )
            for index, (challenger, previous, current, changes) in enumerate(self.trace, 1)
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
