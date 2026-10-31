"""MinesweeperDeductionTask — логический вывод в стиле «Сапёра».

Дано частично открытое поле: в открытых клетках указано число мин среди
соседей, остальные клетки скрыты («?»). Требуется определить, является ли
конкретная скрытая клетка миной или безопасна — при условии, что это следует
однозначно из открытых чисел (проверяется перебором совместимых расстановок).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
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
                 augment: bool = True, n=None, num_mines=None, extra_hidden=None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.n = int(preset['n']) if n is None else n
        self.num_mines = int(preset['mines']) if num_mines is None else num_mines
        self.extra_hidden = int(preset['hidden']) if extra_hidden is None else extra_hidden
        if type(self.n) is not int or not 2 <= self.n <= 8:
            raise ValueError('invalid_size')
        if type(self.num_mines) is not int or not 0 <= self.num_mines < self.n*self.n:
            raise ValueError('invalid_num_mines')
        if type(self.extra_hidden) is not int or not 0 <= self.extra_hidden < self.n*self.n-self.num_mines:
            raise ValueError('invalid_extra_hidden')
        if not 1 <= self.num_mines+self.extra_hidden <= 14:
            raise ValueError('invalid_hidden_count')
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

            from re_rl.tasks.math.logic.deduction_search import mine_status
            clues = {cell:number[cell] for cell in revealed}
            forced = []
            for cell in random.sample(hidden,len(hidden)):
                possible = mine_status(n,clues,cell)
                if len(possible) == 1:
                    forced.append((cell,bool(possible[0])))
                    break
            if not forced:
                continue
            self.mines = mines
            self.number = number
            self.revealed = set(revealed)
            self.hidden = set(hidden)
            self.target, self.target_is_mine = random.choice(forced)
            return
        raise ValueError('generation_failed')

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
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        verdict = ((texts.t('s1', self.language) if self.target_is_mine else texts.t('s2', self.language)))
        self.solution_steps = [
            ((texts.t('s3', self.language))),
            ((texts.t('s4', self.language, verdict=verdict))),
        ]
        self.final_answer = verdict

    def verify(self, prediction: str) -> float:
        fingerprint = (self.n,tuple(sorted((r,c,self.number[r,c]) for r,c in self.revealed)),tuple(self.target))
        certificate = getattr(self,'_mine_certificate',None)
        if certificate is None or certificate[0] != fingerprint:
            try:self.solve()
            except ValueError:return 0.0
        status = self._mine_certificate[1]
        text = U.clean(prediction).strip().rstrip('.!').strip().casefold()
        mine_syn = {texts.t(key,lang).casefold() for key in ('s1','s5','s6','s7') for lang in ('ru','en')}
        safe_syn = {texts.t(key,lang).casefold() for key in ('s2','s8','s9','s10','not_mine','not_mine_short') for lang in ('ru','en')}
        found_mine = text in mine_syn
        found_safe = text in safe_syn
        if found_mine == found_safe:
            return 0.0
        return 1.0 if found_mine == bool(status) else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
