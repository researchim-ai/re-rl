"""Лестница слов: кратчайшая цепочка замен одной буквы между двумя словами,
все промежуточные слова — из заданного словаря (поиск в ширину)."""

import random
import string
from collections import deque
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class WordLadderTask(BaseMathTask):
    TASK_TYPE = "word_ladder"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"L": 3, "alpha": 3, "size": 6}, 2: {"L": 3, "alpha": 3, "size": 8},
        3: {"L": 3, "alpha": 4, "size": 10}, 4: {"L": 4, "alpha": 4, "size": 12},
        5: {"L": 4, "alpha": 4, "size": 14}, 6: {"L": 4, "alpha": 5, "size": 16},
        7: {"L": 4, "alpha": 5, "size": 18}, 8: {"L": 5, "alpha": 5, "size": 20},
        9: {"L": 5, "alpha": 6, "size": 24}, 10: {"L": 5, "alpha": 6, "size": 28},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.L, self.alpha, self.size = int(p["L"]), int(p["alpha"]), int(p["size"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _neighbors(self, w, letters):
        for i in range(len(w)):
            for ch in letters:
                if ch != w[i]:
                    yield w[:i] + ch + w[i + 1:]

    def _build(self):
        letters = string.ascii_lowercase[:self.alpha]
        for _ in range(50):
            comp = {"".join(random.choice(letters) for _ in range(self.L))}
            while len(comp) < self.size:
                base = random.choice(list(comp))
                cand = random.choice(list(self._neighbors(base, letters)))
                comp.add(cand)
            self.words = sorted(comp)
            wset = set(self.words)
            self.start = random.choice(self.words)
            dist = self._bfs(self.start, wset, letters)
            reachable = [(w, d) for w, d in dist.items() if d >= 2 and w != self.start]
            if reachable:
                self.target, self.answer = max(reachable, key=lambda x: x[1])
                return
        # запасной вариант: гарантированная цепочка длины 2
        w0 = "a" * self.L
        w1 = "b" + "a" * (self.L - 1)
        w2 = "bb" + "a" * (self.L - 2) if self.L >= 2 else "b" * self.L
        self.words = sorted({w0, w1, w2})
        self.start, self.target, self.answer = w0, w2, 2

    def _bfs(self, start, wset, letters):
        dist = {start: 0}
        q = deque([start])
        while q:
            w = q.popleft()
            for nb in self._neighbors(w, letters):
                if nb in wset and nb not in dist:
                    dist[nb] = dist[w] + 1
                    q.append(nb)
        return dist

    def _descr(self, language):
        ru = language == "ru"
        words = ", ".join(self.words)
        return ((f"Разрешённые слова: {words}. За один шаг можно заменить ровно одну букву, при этом "
                 f"получившееся слово тоже должно быть из списка. За наименьшее число шагов превратите "
                 f"«{self.start}» в «{self.target}». Сколько шагов нужно?") if ru else
                (f"Allowed words: {words}. In one step you may change exactly one letter, and the resulting "
                 f"word must also be in the list. Transform '{self.start}' into '{self.target}' in the "
                 f"fewest steps. How many steps are needed?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Поиск в ширину по графу слов, где рёбра — замена одной буквы." if ru else
             "Breadth-first search over the word graph where edges are one-letter changes."),
            (f"Кратчайшая цепочка = {self.answer} шаг(ов)." if ru else
             f"Shortest ladder = {self.answer} step(s)."),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
