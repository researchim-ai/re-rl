"""Симуляция автоматов и клеточных систем.

- DFASimulationTask: принимает ли ДКА заданную строку;
- TuringMachineTask: число единиц на ленте после N шагов машины Тьюринга;
- GameOfLifeTask: состояние поля «Жизни» после k шагов;
- ElementaryCATask: строка одномерного клеточного автомата после k шагов.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _SimBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


class DFASimulationTask(_SimBase):
    TASK_TYPE = "dfa_simulation"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 2, "L": 3}, 2: {"m": 2, "L": 4}, 3: {"m": 3, "L": 5}, 4: {"m": 3, "L": 6},
        5: {"m": 3, "L": 7}, 6: {"m": 4, "L": 8}, 7: {"m": 4, "L": 9}, 8: {"m": 4, "L": 10},
        9: {"m": 5, "L": 12}, 10: {"m": 5, "L": 14},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.m, self.L = int(p["m"]), int(p["L"])
        self.alphabet = ["a", "b"]
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.delta = {s: {sym: random.randrange(self.m) for sym in self.alphabet}
                      for s in range(self.m)}
        self.accepting = set(s for s in range(self.m) if random.random() < 0.5)
        if not self.accepting:
            self.accepting = {random.randrange(self.m)}
        self.word = "".join(random.choice(self.alphabet) for _ in range(self.L))
        self._answer = self._run()

    def _run(self):
        s = 0
        for ch in self.word:
            s = self.delta[s][ch]
        return s in self.accepting

    def _descr(self, language):
        ru = language == "ru"
        trans = "; ".join(f"δ({s},{sym})={self.delta[s][sym]}"
                          for s in range(self.m) for sym in self.alphabet)
        acc = ", ".join(map(str, sorted(self.accepting)))
        return ((f"ДКА с состояниями 0..{self.m-1}, начальное 0, принимающие: {{{acc}}}. Алфавит {{a,b}}. "
                 f"Переходы: {trans}.\nПринимает ли автомат строку «{self.word}»? Ответьте да/нет.") if ru else
                (f"DFA with states 0..{self.m-1}, start 0, accepting {{{acc}}}. Alphabet {{a,b}}. "
                 f"Transitions: {trans}.\nDoes the automaton accept the string '{self.word}'? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Прогоняем строку по автомату, отслеживая текущее состояние." if ru else
             "Run the string through the automaton, tracking the current state."),
            ((("Автомат принимает строку." if self._answer else "Автомат отвергает строку.")) if ru else
             (("The automaton accepts." if self._answer else "The automaton rejects."))),
        ]
        self.final_answer = ("да" if self._answer else "нет") if ru else ("yes" if self._answer else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self._answer))


class TuringMachineTask(_SimBase):
    TASK_TYPE = "turing_machine"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"states": 2, "L": 3, "steps": 4}, 2: {"states": 2, "L": 3, "steps": 6},
        3: {"states": 2, "L": 4, "steps": 8}, 4: {"states": 3, "L": 4, "steps": 10},
        5: {"states": 3, "L": 5, "steps": 12}, 6: {"states": 3, "L": 5, "steps": 15},
        7: {"states": 4, "L": 6, "steps": 18}, 8: {"states": 4, "L": 6, "steps": 22},
        9: {"states": 4, "L": 7, "steps": 26}, 10: {"states": 5, "L": 8, "steps": 30},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.nstates, self.L, self.steps = int(p["states"]), int(p["L"]), int(p["steps"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        # transition[(state, read)] = (write, move, next_state); move: +1 (R) / -1 (L)
        self.trans = {}
        for s in range(self.nstates):
            for r in (0, 1):
                self.trans[(s, r)] = (random.randint(0, 1),
                                      random.choice([1, -1]),
                                      random.randrange(self.nstates))
        self.tape0 = [random.randint(0, 1) for _ in range(self.L)]
        self._answer = self._run()

    def _run(self):
        tape = {i: self.tape0[i] for i in range(self.L)}
        pos, state = 0, 0
        for _ in range(self.steps):
            r = tape.get(pos, 0)
            write, move, nxt = self.trans[(state, r)]
            tape[pos] = write
            pos += move
            state = nxt
        return sum(1 for v in tape.values() if v == 1)

    def _descr(self, language):
        ru = language == "ru"
        rules = "; ".join(
            f"({s},{r})→(пиши {w}, {'R' if mv == 1 else 'L'}, состояние {ns})"
            for (s, r), (w, mv, ns) in self.trans.items())
        rules_en = "; ".join(
            f"({s},{r})→(write {w}, {'R' if mv == 1 else 'L'}, state {ns})"
            for (s, r), (w, mv, ns) in self.trans.items())
        tape = "".join(map(str, self.tape0))
        return ((f"Машина Тьюринга (состояния 0..{self.nstates-1}, старт 0, головка на клетке 0, вне "
                 f"ленты — нули). Лента: {tape}. Правила: {rules}.\n"
                 f"Сколько единиц будет на ленте после {self.steps} шагов?") if ru else
                (f"Turing machine (states 0..{self.nstates-1}, start 0, head at cell 0, outside cells are "
                 f"zeros). Tape: {tape}. Rules: {rules_en}.\n"
                 f"How many ones are on the tape after {self.steps} steps?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Пошагово применяем правила: читаем символ, пишем, двигаем головку, меняем состояние." if ru else
             "Apply the rules step by step: read, write, move the head, change state."),
            (f"Единиц на ленте: {self._answer}." if ru else f"Ones on the tape: {self._answer}."),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))


class GameOfLifeTask(_SimBase):
    TASK_TYPE = "game_of_life"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 3, "c": 3, "k": 1}, 2: {"r": 3, "c": 3, "k": 1}, 3: {"r": 3, "c": 4, "k": 1},
        4: {"r": 4, "c": 4, "k": 1}, 5: {"r": 4, "c": 4, "k": 2}, 6: {"r": 4, "c": 5, "k": 2},
        7: {"r": 5, "c": 5, "k": 2}, 8: {"r": 5, "c": 5, "k": 2}, 9: {"r": 5, "c": 6, "k": 3},
        10: {"r": 6, "c": 6, "k": 3},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.r, self.c, self.k = int(p["r"]), int(p["c"]), int(p["k"])
        self.augment = augment
        self.grid0 = [[random.randint(0, 1) for _ in range(self.c)] for _ in range(self.r)]
        self.grid = [row[:] for row in self.grid0]
        for _ in range(self.k):
            self.grid = self._step(self.grid)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _step(self, g):
        r, c = self.r, self.c
        new = [[0] * c for _ in range(r)]
        for i in range(r):
            for j in range(c):
                n = 0
                for di in (-1, 0, 1):
                    for dj in (-1, 0, 1):
                        if di == 0 and dj == 0:
                            continue
                        ni, nj = i + di, j + dj
                        if 0 <= ni < r and 0 <= nj < c:
                            n += g[ni][nj]
                new[i][j] = 1 if (g[i][j] and n in (2, 3)) or (not g[i][j] and n == 3) else 0
        return new

    @staticmethod
    def _grid_str(g):
        return "\n".join(" ".join(map(str, row)) for row in g)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"«Игра Жизнь» Конвея на поле {self.r}×{self.c} (клетки вне поля считаются мёртвыми). "
                 f"Начальное поле (1 — живая, 0 — мёртвая):\n{self._grid_str(self.grid0)}\n"
                 f"Каким будет поле через {self.k} шаг(а)? Выпишите все {self.r*self.c} клеток по строкам.") if ru else
                (f"Conway's Game of Life on a {self.r}×{self.c} board (cells outside are dead). "
                 f"Initial board (1 alive, 0 dead):\n{self._grid_str(self.grid0)}\n"
                 f"What is the board after {self.k} step(s)? List all {self.r*self.c} cells row by row."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Применяем правила Жизни: живая выживает при 2–3 соседях, мёртвая оживает при 3." if ru else
             "Apply Life rules: a live cell survives with 2–3 neighbors, a dead cell is born with 3."),
            ((f"Итоговое поле:\n{self._grid_str(self.grid)}") if ru else
             (f"Final board:\n{self._grid_str(self.grid)}")),
        ]
        self.final_answer = " ".join(str(self.grid[i][j]) for i in range(self.r) for j in range(self.c))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        flat = [self.grid[i][j] for i in range(self.r) for j in range(self.c)]
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < len(flat):
            return 0.0
        return 1.0 if ints[-len(flat):] == flat else 0.0


class ElementaryCATask(_SimBase):
    TASK_TYPE = "elementary_ca"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"L": 5, "k": 1}, 2: {"L": 6, "k": 1}, 3: {"L": 7, "k": 2}, 4: {"L": 7, "k": 2},
        5: {"L": 9, "k": 2}, 6: {"L": 9, "k": 3}, 7: {"L": 11, "k": 3}, 8: {"L": 11, "k": 4},
        9: {"L": 13, "k": 4}, 10: {"L": 15, "k": 5},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.L, self.k = int(p["L"]), int(p["k"])
        self.rule = random.choice([30, 90, 110, 54, 150, 60])
        self.augment = augment
        self.row0 = [random.randint(0, 1) for _ in range(self.L)]
        self.row = self.row0[:]
        for _ in range(self.k):
            self.row = self._step(self.row)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _step(self, row):
        L = self.L
        new = [0] * L
        for i in range(L):
            left = row[i - 1] if i - 1 >= 0 else 0
            mid = row[i]
            right = row[i + 1] if i + 1 < L else 0
            idx = (left << 2) | (mid << 1) | right
            new[i] = (self.rule >> idx) & 1
        return new

    def _descr(self, language):
        ru = language == "ru"
        r0 = "".join(map(str, self.row0))
        return ((f"Одномерный элементарный клеточный автомат, правило {self.rule} (границы — нули). "
                 f"Начальная строка: {r0}. Какой будет строка через {self.k} шаг(а)? "
                 f"Выпишите {self.L} бит по порядку.") if ru else
                (f"One-dimensional elementary cellular automaton, rule {self.rule} (zero boundaries). "
                 f"Initial row: {r0}. What is the row after {self.k} step(s)? "
                 f"List the {self.L} bits in order."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            (f"Для каждой клетки берём тройку (лево, центр, право) и по правилу {self.rule} находим новый бит." if ru else
             f"For each cell take the triple (left, center, right) and apply rule {self.rule}."),
            (f"Итоговая строка: {''.join(map(str, self.row))}." if ru else
             f"Final row: {''.join(map(str, self.row))}."),
        ]
        self.final_answer = " ".join(map(str, self.row))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < self.L:
            return 0.0
        return 1.0 if ints[-self.L:] == self.row else 0.0
