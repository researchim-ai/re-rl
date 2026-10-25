"""DungGroundTask — обоснованное расширение аргументации.

Нападение идёт только от меньшего номера к большему, поэтому рамка ациклична.
Аргумент принят, если каждый нападающий отвергнут. Итерация обоснованной разметки сверяет однопроходный ответ.
Число аргументов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def ground_trace(attacks: Sequence[Sequence[int]]) -> List[Tuple[int, int]]:
    label = [0]
    inside = 0
    trace = []
    for who in attacks:
        accepted = 0 if any(label[attacker] == 1 for attacker in who) else 1
        label.append(accepted)
        inside += accepted
        trace.append((accepted, inside))
    return trace


def grounded_labels(attacks: Sequence[Sequence[int]]) -> List[int]:
    size = len(attacks)
    accepted = [0] * (size + 1)
    rejected = [0] * (size + 1)
    for _ in range(size + 1):
        next_accepted = [0] * (size + 1)
        next_rejected = [0] * (size + 1)
        for index, who in enumerate(attacks, 1):
            if any(accepted[attacker] for attacker in who):
                next_rejected[index] = 1
            elif all(rejected[attacker] for attacker in who):
                next_accepted[index] = 1
        if next_accepted == accepted and next_rejected == rejected:
            break
        accepted, rejected = next_accepted, next_rejected
    else:
        raise AssertionError("unsettled")
    assert all(accepted[index] + rejected[index] == 1 for index in range(1, size + 1))
    return accepted


class DungGroundTask(BaseMathTask):
    TASK_TYPE = "dung_ground"
    TASK_TYPES = ["inside", "here"]

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
        self.attacks: List[List[int]] = [[]]
        for index in range(2, self.n + 1):
            who: List[int] = []
            if random.random() < 0.8:
                who.append(random.randint(1, index - 1))
            if index > 2 and random.random() < 0.45:
                extra = random.randint(1, index - 1)
                if extra not in who:
                    who.append(extra)
            self.attacks.append(sorted(who))
        self.trace = ground_trace(self.attacks)
        accepted = grounded_labels(self.attacks)
        assert [bit for bit, _total in self.trace] == accepted[1:]
        self.inside = self.trace[-1][1]
        self.k = random.randint(1, self.n)
        self.here = self.trace[self.k - 1][0]
        self.answer = self.inside if self.task_type == "inside" else self.here
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = ", ".join(
            f"{index}:-" if not who else f"{index}:" + " ".join(str(attacker) for attacker in who)
            for index, who in enumerate(self.attacks, 1)
        )
        key = "s0" if self.task_type == "inside" else "s1"
        return texts.t(key, language, n=self.n, attacks=shown, k=self.k)

    def solve(self):
        steps = []
        for index, (who, (accepted, inside)) in enumerate(zip(self.attacks, self.trace), 1):
            attackers = "-" if not who else " ".join(str(attacker) for attacker in who)
            steps.append(texts.t(
                "s2", self.language, i=index, attackers=attackers, label=accepted, inside=inside,
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
