"""IntervalSchedulingTask — рассуждения о временных интервалах.

Подтипы:
- max_activities: максимальное число попарно непересекающихся интервалов
  (классический жадный алгоритм);
- min_rooms: минимальное число «переговорных» = максимум одновременно идущих
  интервалов;
- overlap: пересекаются ли два указанных интервала (да/нет).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class IntervalSchedulingTask(BaseMathTask):
    TASK_TYPE = "interval_scheduling"
    TASK_TYPES = ["max_activities", "min_rooms", "overlap"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "span": 10}, 2: {"n": 4, "span": 12}, 3: {"n": 5, "span": 14},
        4: {"n": 6, "span": 16}, 5: {"n": 7, "span": 18}, 6: {"n": 8, "span": 20},
        7: {"n": 9, "span": 24}, 8: {"n": 10, "span": 28}, 9: {"n": 12, "span": 32},
        10: {"n": 14, "span": 40},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype: Optional[str] = None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(preset["n"])
        self.span = int(preset["span"])
        self.subtype = subtype or kwargs.get("task_type") or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        self.intervals: List[Tuple[int, int]] = []
        for _ in range(self.n):
            s = random.randint(0, self.span - 2)
            e = random.randint(s + 1, min(self.span, s + max(2, self.span // 3)))
            self.intervals.append((s, e))
        if self.subtype == "max_activities":
            self._answer = self._max_nonoverlap()
        elif self.subtype == "min_rooms":
            self._answer = self._max_concurrent()
        else:
            self.i, self.j = random.sample(range(self.n), 2)
            a, b = self.intervals[self.i], self.intervals[self.j]
            self._answer = a[0] < b[1] and b[0] < a[1]  # полуинтервалы [s,e)

    def _max_nonoverlap(self) -> int:
        cnt, last_end = 0, -1
        for s, e in sorted(self.intervals, key=lambda iv: iv[1]):
            if s >= last_end:
                cnt += 1
                last_end = e
        return cnt

    def _max_concurrent(self) -> int:
        events = []
        for s, e in self.intervals:
            events.append((s, 1))
            events.append((e, -1))
        events.sort(key=lambda x: (x[0], x[1]))  # -1 раньше +1 при равенстве (конец освобождает)
        cur = best = 0
        for _, delta in events:
            cur += delta
            best = max(best, cur)
        return best

    def _make_description(self, language: str) -> str:
        lst = ", ".join(f"[{s}, {e})" for s, e in self.intervals)
        head = ((texts.t('s0', language, lst=lst)))
        if self.subtype == "max_activities":
            q = ((texts.t('s1', language)))
        elif self.subtype == "min_rooms":
            q = ((texts.t('s2', language)))
        else:
            a, b = self.intervals[self.i], self.intervals[self.j]
            q = ((texts.t('s3', language, v0=a[0], v1=a[1], v2=b[0], v3=b[1])))
        return head + q

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.subtype == "max_activities":
            self.solution_steps = [
                ((texts.t('s4', self.language))),
                ((texts.t('s5', self.language, _answer=self._answer))),
            ]
            self.final_answer = str(self._answer)
        elif self.subtype == "min_rooms":
            self.solution_steps = [
                ((texts.t('s8', self.language))),
                ((texts.t('s9', self.language, _answer=self._answer))),
            ]
            self.final_answer = str(self._answer)
        else:
            self.solution_steps = [
                ((texts.t('s10', self.language))),
                ((texts.t('s11', self.language) if self._answer else texts.t('s12', self.language))),
            ]
            self.final_answer = (texts.t('s6', self.language) if self._answer else texts.t('s7', self.language))

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.subtype == "overlap":
            return U.verify_bool(prediction, bool(self._answer))
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
