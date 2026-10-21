"""ARC-подобная индукция правила: по нескольким парам «вход→выход» нужно
догадаться о преобразовании сетки и применить его к тестовому входу.

Проверяется точное совпадение с результатом применения истинного правила.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _reflect_h(g):
    return [row[::-1] for row in g]


def _reflect_v(g):
    return g[::-1]


def _rotate180(g):
    return [row[::-1] for row in g[::-1]]


def _transpose(g):
    return [list(col) for col in zip(*g)]


def _color_swap(g, a, b):
    return [[b if v == a else a if v == b else v for v in row] for row in g]


def _recolor(g, x, y):
    return [[y if v == x else v for v in row] for row in g]


def _tile2(g):
    top = [row + row for row in g]
    return top + [row[:] for row in top]


def _border(g, c):
    w = len(g[0]) + 2
    out = [[c] * w]
    for row in g:
        out.append([c] + list(row) + [c])
    out.append([c] * w)
    return out


def _roll_rows(g, k):
    k %= len(g)
    return g[-k:] + g[:-k] if k else [row[:] for row in g]


def _gravity_down(g):
    r, c = len(g), len(g[0])
    out = [[0] * c for _ in range(r)]
    for j in range(c):
        vals = [g[i][j] for i in range(r) if g[i][j] != 0]
        for k, v in enumerate(vals):
            out[r - len(vals) + k][j] = v
    return out


class ARCGridInductionTask(BaseMathTask):
    TASK_TYPE = texts.literal('literals.s3')
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 2, "c": 2, "colors": 2}, 2: {"r": 3, "c": 3, "colors": 2},
        3: {"r": 3, "c": 3, "colors": 3}, 4: {"r": 3, "c": 4, "colors": 3},
        5: {"r": 4, "c": 4, "colors": 3}, 6: {"r": 4, "c": 4, "colors": 4},
        7: {"r": 4, "c": 5, "colors": 4}, 8: {"r": 5, "c": 5, "colors": 4},
        9: {"r": 5, "c": 5, "colors": 4}, 10: {"r": 5, "c": 6, "colors": 4},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.r, self.c, self.colors = int(p["r"]), int(p["c"]), int(p["colors"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _pick_rule(self):
        cmax = self.colors - 1
        rules = [
            ("reflect_h", _reflect_h),
            ("reflect_v", _reflect_v),
            ("rotate180", _rotate180),
            ("transpose", _transpose),
            ("tile2", _tile2),
            ("gravity_down", _gravity_down),
            ("roll_rows", lambda g, k=random.randint(1, max(1, self.r - 1)): _roll_rows(g, k)),
        ]
        if cmax >= 1:
            a, b = random.sample(range(1, self.colors), 2) if self.colors > 2 else (1, cmax)
            rules.append(("color_swap", lambda g, a=a, b=b: _color_swap(g, a, b)))
            x = random.randint(1, cmax)
            y = random.randint(1, cmax)
            rules.append(("recolor", lambda g, x=x, y=y: _recolor(g, x, y)))
            rules.append(("border", lambda g, c=random.randint(1, cmax): _border(g, c)))
        return random.choice(rules)

    def _rand_grid(self):
        return [[random.randint(0, self.colors - 1) for _ in range(self.c)] for _ in range(self.r)]

    def _build(self):
        for _ in range(60):
            name, fn = self._pick_rule()
            self.rule_name = name
            self.fn = fn
            self.train = []
            ok = True
            for _ in range(3):
                gin = self._rand_grid()
                gout = fn(gin)
                self.train.append((gin, gout))
            self.test_in = self._rand_grid()
            self.test_out = fn(self.test_in)
            # правило должно быть нетривиальным хотя бы на одном примере
            if any(gin != gout for gin, gout in self.train) or self.test_in != self.test_out:
                if ok:
                    return
        # запасной вариант — гарантированно нетривиальный
        self.rule_name, self.fn = "rotate180", _rotate180
        self.train = [(self._rand_grid(), None) for _ in range(3)]
        self.train = [(g, _rotate180(g)) for g, _ in self.train]
        self.test_in = self._rand_grid()
        self.test_out = _rotate180(self.test_in)

    @staticmethod
    def _grid_str(g):
        return "\n".join(" ".join(map(str, row)) for row in g)

    def _descr(self, language):
        parts = []
        for i, (gin, gout) in enumerate(self.train, 1):
            parts.append(texts.t('s0', language, i=i, v1=self._grid_str(gin), v2=self._grid_str(gout)))
        body = "\n\n".join(parts)
        ro, co = len(self.test_out), len(self.test_out[0])
        if {"ru": True, "en": False}.get(language, False):
            return (texts.t('s5', language, body=body, v1=self._grid_str(self.test_in), ro=ro, co=co))
        return (texts.t('s4', language, body=body, v1=self._grid_str(self.test_in), ro=ro, co=co))

    def solve(self):
        flat = " ".join(str(v) for row in self.test_out for v in row)
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, flat=flat))),
        ]
        self.final_answer = flat

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        flat = [v for row in self.test_out for v in row]
        ints = [x for x in U.parse_ints(prediction) if 0 <= x <= 9]
        if len(ints) < len(flat):
            return 0.0
        return 1.0 if ints[-len(flat):] == flat else 0.0

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
