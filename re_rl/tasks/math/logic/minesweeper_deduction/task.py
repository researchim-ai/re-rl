"""MinesweeperDeductionTask — логический вывод в стиле «Сапёра».

Дано частично открытое поле: в открытых клетках указано число мин среди
соседей, остальные клетки скрыты («?»). Требуется определить, является ли
конкретная скрытая клетка миной или безопасна — при условии, что это следует
однозначно из открытых чисел (проверяется перебором совместимых расстановок).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class MinesweeperDeductionTask(BaseMathTask):
    TASK_TYPE = "minesweeper_deduction"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3, "mines": 2, "hidden": 1}, 2: {"n": 3, "mines": 2, "hidden": 2},
        3: {"n": 3, "mines": 3, "hidden": 2}, 4: {"n": 4, "mines": 3, "hidden": 2},
        5: {"n": 4, "mines": 4, "hidden": 3}, 6: {"n": 4, "mines": 4, "hidden": 3},
        7: {"n": 4, "mines": 5, "hidden": 3}, 8: {"n": 5, "mines": 5, "hidden": 4},
        9: {"n": 5, "mines": 6, "hidden": 4}, 10: {"n": 5, "mines": 7, "hidden": 4},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(preset["n"])
        self.num_mines = int(preset["mines"])
        self.extra_hidden = int(preset["hidden"])
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _neighbors(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.n and 0 <= nc < self.n:
                    yield nr, nc

    def _build(self):
        n = self.n
        cells = [(r, c) for r in range(n) for c in range(n)]
        for _ in range(400):
            mines = set(random.sample(cells, self.num_mines))
            number = {}
            for (r, c) in cells:
                if (r, c) not in mines:
                    number[(r, c)] = sum(1 for nb in self._neighbors(r, c) if nb in mines)
            non_mines = [c for c in cells if c not in mines]
            if len(non_mines) <= self.extra_hidden:
                continue
            hidden_safe = set(random.sample(non_mines, self.extra_hidden))
            hidden = list(mines | hidden_safe)  # скрытые: все мины + часть безопасных
            if len(hidden) > 14:
                continue
            revealed = [c for c in cells if c not in set(hidden)]

            # Перебираем совместимые расстановки мин по скрытым клеткам.
            consistent = []
            hidden_idx = {cell: i for i, cell in enumerate(hidden)}
            for bits in product([0, 1], repeat=len(hidden)):
                S = {hidden[i] for i in range(len(hidden)) if bits[i]}
                ok = True
                for (r, c) in revealed:  # revealed всегда безопасны
                    cnt = sum(1 for nb in self._neighbors(r, c) if nb in S)
                    if cnt != number[(r, c)]:
                        ok = False
                        break
                if ok:
                    consistent.append(S)
            if not consistent:
                continue
            # Ищем скрытую клетку с однозначным статусом.
            forced = []
            for cell in hidden:
                vals = {cell in S for S in consistent}
                if len(vals) == 1:
                    forced.append((cell, cell in mines))
            if not forced:
                continue
            self.mines = mines
            self.number = number
            self.revealed = set(revealed)
            self.hidden = set(hidden)
            self.target, self.target_is_mine = random.choice(forced)
            return
        # Фолбэк (крайне редко): открыть всё, кроме одной мины.
        self.mines = set(random.sample(cells, 1))
        self.number = {c: sum(1 for nb in self._neighbors(*c) if nb in self.mines)
                       for c in cells if c not in self.mines}
        self.revealed = set(c for c in cells if c not in self.mines)
        self.hidden = set(self.mines)
        self.target = next(iter(self.mines))
        self.target_is_mine = True

    def _grid_str(self) -> str:
        rows = []
        for r in range(self.n):
            row = []
            for c in range(self.n):
                if (r, c) in self.revealed:
                    row.append(str(self.number[(r, c)]))
                elif (r, c) == self.target:
                    row.append("?*")
                else:
                    row.append("?")
            rows.append(" ".join(f"{x:>2}" for x in row))
        return "\n".join(rows)

    def _make_description(self, language: str) -> str:
        tr, tc = self.target
        return ((texts.t('s0', language, n=self.n, n_2=self.n, v2=tr + 1, v3=tc + 1, v4=self._grid_str())))

    def solve(self):
        verdict = ((texts.t('s1', self.language) if self.target_is_mine else texts.t('s2', self.language)))
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language, verdict=verdict))),
        ]
        self.final_answer = verdict

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        mine_syn = [texts.t('s5', self.language), texts.t('s6', self.language), texts.t('s7', self.language), "mine"]
        safe_syn = [texts.t('s8', self.language), texts.t('s9', self.language), texts.t('s10', self.language), "safe"]
        found_mine = U.verify_label(prediction, mine_syn) == 1.0
        found_safe = U.verify_label(prediction, safe_syn) == 1.0
        if found_mine == found_safe:
            return 0.0
        return 1.0 if found_mine == bool(self.target_is_mine) else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
