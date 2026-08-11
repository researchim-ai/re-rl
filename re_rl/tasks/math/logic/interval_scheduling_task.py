"""IntervalSchedulingTask — рассуждения о временных интервалах.

Подтипы:
- max_activities: максимальное число попарно непересекающихся интервалов
  (классический жадный алгоритм);
- min_rooms: минимальное число «переговорных» = максимум одновременно идущих
  интервалов;
- overlap: пересекаются ли два указанных интервала (да/нет).
"""

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
        self.subtype = subtype or random.choice(self.TASK_TYPES)
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
        ru = language == "ru"
        lst = ", ".join(f"[{s}, {e})" for s, e in self.intervals)
        head = (f"Даны временные интервалы (в часах): {lst}." if ru else
                f"Given time intervals (in hours): {lst}.")
        if self.subtype == "max_activities":
            q = (" Какое максимальное число попарно непересекающихся интервалов можно выбрать?" if ru else
                 " What is the maximum number of pairwise non-overlapping intervals you can pick?")
        elif self.subtype == "min_rooms":
            q = (" Какое минимальное число переговорных нужно, чтобы провести все встречи?" if ru else
                 " What is the minimum number of rooms needed to host all meetings?")
        else:
            a, b = self.intervals[self.i], self.intervals[self.j]
            q = (f" Пересекаются ли интервалы [{a[0]}, {a[1]}) и [{b[0]}, {b[1]})? Ответьте да/нет." if ru else
                 f" Do intervals [{a[0]}, {a[1]}) and [{b[0]}, {b[1]}) overlap? Answer yes/no.")
        return head + q

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "max_activities":
            self.solution_steps = [
                ("Сортируем интервалы по времени окончания и жадно берём совместимые." if ru else
                 "Sort intervals by end time and greedily pick compatible ones."),
                (f"Максимум непересекающихся = {self._answer}." if ru else
                 f"Maximum non-overlapping = {self._answer}."),
            ]
            self.final_answer = str(self._answer)
        elif self.subtype == "min_rooms":
            self.solution_steps = [
                ("Считаем максимум одновременно активных интервалов (развёртка событий)." if ru else
                 "Count the maximum number of simultaneously active intervals (sweep line)."),
                (f"Минимум переговорных = {self._answer}." if ru else
                 f"Minimum rooms = {self._answer}."),
            ]
            self.final_answer = str(self._answer)
        else:
            self.solution_steps = [
                ("Два полуинтервала пересекаются, если s1 < e2 и s2 < e1." if ru else
                 "Two half-open intervals overlap iff s1 < e2 and s2 < e1."),
                (("Пересекаются." if self._answer else "Не пересекаются.") if ru else
                 ("They overlap." if self._answer else "They do not overlap.")),
            ]
            self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

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
