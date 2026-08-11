"""Пошаговые алгоритмические задачи: вычисление ОПЗ (RPN), проверка баланса
скобок, трассировка сортировки (число инверсий / состояние после проходов)."""

import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _AlgoBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


class RPNEvalTask(_AlgoBase):
    TASK_TYPE = "rpn_eval"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "hi": 6}, 2: {"n": 3, "hi": 9}, 3: {"n": 4, "hi": 9}, 4: {"n": 4, "hi": 12},
        5: {"n": 5, "hi": 12}, 6: {"n": 5, "hi": 15}, 7: {"n": 6, "hi": 15}, 8: {"n": 6, "hi": 20},
        9: {"n": 7, "hi": 20}, 10: {"n": 8, "hi": 25},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n, self.hi = int(p["n"]), int(p["hi"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        # Строим случайное дерево, затем получаем постфиксную запись и значение.
        items = [([str(v)], v) for v in (random.randint(1, self.hi) for _ in range(self.n))]
        while len(items) > 1:
            i, j = random.sample(range(len(items)), 2)
            (ta, va), (tb, vb) = items[i], items[j]
            op = random.choice(["+", "-", "*"])
            val = va + vb if op == "+" else va - vb if op == "-" else va * vb
            tokens = ta + tb + [op]
            items = [it for idx, it in enumerate(items) if idx not in (i, j)]
            items.append((tokens, val))
        self.tokens, self._answer = items[0]

    def _descr(self, language):
        ru = language == "ru"
        expr = " ".join(self.tokens)
        return ((f"Вычислите выражение в обратной польской записи (постфикс): {expr}") if ru else
                (f"Evaluate the reverse Polish (postfix) expression: {expr}"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Идём слева направо со стеком: число кладём в стек, оператор берёт два верхних значения." if ru else
             "Scan left to right with a stack: push numbers, operators pop the top two values."),
            (f"Результат = {self._answer}." if ru else f"Result = {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))


class BalancedBracketsTask(_AlgoBase):
    TASK_TYPE = "balanced_brackets"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"pairs": 3, "kinds": 1}, 2: {"pairs": 4, "kinds": 1}, 3: {"pairs": 4, "kinds": 2},
        4: {"pairs": 5, "kinds": 2}, 5: {"pairs": 6, "kinds": 2}, 6: {"pairs": 6, "kinds": 3},
        7: {"pairs": 8, "kinds": 3}, 8: {"pairs": 9, "kinds": 3}, 9: {"pairs": 10, "kinds": 3},
        10: {"pairs": 12, "kinds": 3},
    }
    _PAIRS = [("(", ")"), ("[", "]"), ("{", "}")]

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.pairs = int(p["pairs"])
        self.kinds = int(p["kinds"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _random_balanced(self):
        opens = self._PAIRS[:self.kinds]
        s = []
        stack = []
        for _ in range(self.pairs * 2):
            if stack and (len(s) // 1) and random.random() < 0.5:
                s.append(stack.pop())
            else:
                o, c = random.choice(opens)
                s.append(o); stack.append(c)
        while stack:
            s.append(stack.pop())
        return "".join(s)

    def _build(self):
        self.balanced = random.random() < 0.5
        s = self._random_balanced()
        if not self.balanced:
            # портим: удаляем/меняем один символ
            s = list(s)
            i = random.randrange(len(s))
            allc = [c for pair in self._PAIRS[:self.kinds] for c in pair]
            s[i] = random.choice(allc)
            s = "".join(s)
            self.balanced = self._is_balanced(s)  # могло случайно остаться корректным
        self.s = s
        self._answer = self._is_balanced(s)

    def _is_balanced(self, s):
        close_to_open = {c: o for o, c in self._PAIRS}
        opens = {o for o, _ in self._PAIRS}
        stack = []
        for ch in s:
            if ch in opens:
                stack.append(ch)
            elif ch in close_to_open:
                if not stack or stack.pop() != close_to_open[ch]:
                    return False
        return not stack

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Правильно ли расставлены скобки в строке «{self.s}»? "
                 f"Ответьте да/нет.") if ru else
                (f"Is the bracket string '{self.s}' correctly balanced? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Идём по строке со стеком: открывающую кладём, закрывающая должна совпасть с вершиной." if ru else
             "Scan with a stack: push opening brackets; a closing one must match the top."),
            ((("Скобки сбалансированы." if self._answer else "Скобки не сбалансированы.")) if ru else
             (("Balanced." if self._answer else "Not balanced."))),
        ]
        self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))


class SortingTraceTask(_AlgoBase):
    TASK_TYPE = "sorting_trace"
    TASK_TYPES = ["inversions", "bubble_pass"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 5}, 3: {"n": 5}, 4: {"n": 6}, 5: {"n": 7},
        6: {"n": 8}, 7: {"n": 9}, 8: {"n": 10}, 9: {"n": 11}, 10: {"n": 12},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self.arr = random.sample(range(1, self.n * 3), self.n)
        if self.subtype == "inversions":
            self._answer = sum(1 for i in range(self.n) for j in range(i + 1, self.n)
                               if self.arr[i] > self.arr[j])
        else:
            self.k = random.randint(1, max(1, self.n - 2))
            self.result = self._bubble_passes(self.k)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _bubble_passes(self, k):
        a = self.arr[:]
        for _ in range(k):
            for i in range(len(a) - 1):
                if a[i] > a[i + 1]:
                    a[i], a[i + 1] = a[i + 1], a[i]
        return a

    def _descr(self, language):
        ru = language == "ru"
        arr = ", ".join(map(str, self.arr))
        if self.subtype == "inversions":
            return ((f"Дан массив: [{arr}]. Сколько в нём инверсий (пар i<j с a[i]>a[j])?") if ru else
                    (f"Given the array [{arr}]. How many inversions (pairs i<j with a[i]>a[j]) does it have?"))
        return ((f"Дан массив: [{arr}]. Выполните {self.k} проход(а) сортировки пузырьком (за проход "
                 f"соседние элементы, где левый больше правого, меняются местами, слева направо). "
                 f"Выпишите массив после этих проходов.") if ru else
                (f"Given the array [{arr}]. Perform {self.k} bubble-sort pass(es) (each pass swaps adjacent "
                 f"out-of-order neighbors, left to right). Output the array after these passes."))

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "inversions":
            self.solution_steps = [
                ("Считаем пары, стоящие в неправильном порядке." if ru else
                 "Count the pairs that are out of order."),
                (f"Число инверсий = {self._answer}." if ru else f"Number of inversions = {self._answer}."),
            ]
            self.final_answer = str(self._answer)
        else:
            self.solution_steps = [
                ("Проходим массив слева направо, меняя соседей местами при необходимости; повторяем нужное число раз." if ru else
                 "Sweep left to right swapping neighbors as needed; repeat the required number of times."),
                (f"Массив после {self.k} проход(ов): {', '.join(map(str, self.result))}." if ru else
                 f"Array after {self.k} pass(es): {', '.join(map(str, self.result))}."),
            ]
            self.final_answer = " ".join(map(str, self.result))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "inversions":
            return U.verify_int(prediction, int(self._answer))
        return U.verify_int_sequence(prediction, self.result)
