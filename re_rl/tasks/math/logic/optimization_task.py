"""Задачи комбинаторной оптимизации: рюкзак 0/1 и сумма подмножества."""

import random
from typing import Any, ClassVar, Dict, List

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class KnapsackTask(BaseMathTask):
    TASK_TYPE = "knapsack"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "wmax": 6, "vmax": 8}, 2: {"n": 4, "wmax": 7, "vmax": 9},
        3: {"n": 4, "wmax": 8, "vmax": 10}, 4: {"n": 5, "wmax": 9, "vmax": 12},
        5: {"n": 6, "wmax": 10, "vmax": 15}, 6: {"n": 7, "wmax": 12, "vmax": 15},
        7: {"n": 8, "wmax": 12, "vmax": 20}, 8: {"n": 9, "wmax": 15, "vmax": 20},
        9: {"n": 10, "wmax": 15, "vmax": 25}, 10: {"n": 12, "wmax": 18, "vmax": 30},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n, self.wmax, self.vmax = int(p["n"]), int(p["wmax"]), int(p["vmax"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.weights = [random.randint(1, self.wmax) for _ in range(self.n)]
        self.values = [random.randint(1, self.vmax) for _ in range(self.n)]
        self.capacity = random.randint(self.wmax, sum(self.weights))
        self._answer = self._solve_dp()

    def _solve_dp(self):
        cap = self.capacity
        dp = [0] * (cap + 1)
        for w, v in zip(self.weights, self.values):
            for c in range(cap, w - 1, -1):
                dp[c] = max(dp[c], dp[c - w] + v)
        return dp[cap]

    def _descr(self, language):
        ru = language == "ru"
        items = "; ".join(f"#{i+1} (вес {self.weights[i]}, ценность {self.values[i]})"
                          for i in range(self.n))
        return ((f"Рюкзак вмещает вес не более {self.capacity}. Предметы: {items}.\n"
                 f"Каждый предмет можно взять не более одного раза. Найдите максимальную суммарную "
                 f"ценность.") if ru else
                (f"A knapsack holds weight at most {self.capacity}. Items: "
                 + "; ".join(f"#{i+1} (weight {self.weights[i]}, value {self.values[i]})"
                             for i in range(self.n)) +
                 ".\nEach item can be taken at most once. Find the maximum total value."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Динамика по вместимости: dp[c] — макс. ценность при лимите веса c." if ru else
             "DP over capacity: dp[c] is the max value with weight limit c."),
            (f"Максимальная ценность = {self._answer}." if ru else f"Maximum value = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


class SubsetSumTask(BaseMathTask):
    TASK_TYPE = "subset_sum"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "vmax": 9}, 2: {"n": 5, "vmax": 12}, 3: {"n": 5, "vmax": 15},
        4: {"n": 6, "vmax": 15}, 5: {"n": 7, "vmax": 20}, 6: {"n": 8, "vmax": 20},
        7: {"n": 9, "vmax": 25}, 8: {"n": 10, "vmax": 30}, 9: {"n": 11, "vmax": 35},
        10: {"n": 12, "vmax": 40},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n, self.vmax = int(p["n"]), int(p["vmax"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.nums = [random.randint(1, self.vmax) for _ in range(self.n)]
        if random.random() < 0.5:  # заведомо достижимая цель
            k = random.randint(1, self.n)
            self.target = sum(random.sample(self.nums, k))
        else:
            self.target = random.randint(1, sum(self.nums))
        self._answer = self._reachable()

    def _reachable(self):
        possible = {0}
        for x in self.nums:
            possible |= {p + x for p in possible}
        return self.target in possible

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Дан набор чисел: {', '.join(map(str, self.nums))}. Существует ли подмножество с "
                 f"суммой ровно {self.target}? Ответьте да/нет.") if ru else
                (f"Given the numbers: {', '.join(map(str, self.nums))}. Is there a subset summing to "
                 f"exactly {self.target}? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Динамика по достижимым суммам: добавляем каждое число ко всем уже достижимым." if ru else
             "DP over reachable sums: add each number to all currently reachable sums."),
            ((("Такое подмножество существует." if self._answer else "Такого подмножества нет.")) if ru else
             (("Such a subset exists." if self._answer else "No such subset."))),
        ]
        self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
