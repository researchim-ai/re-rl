"""Дедуктивные задачи: логическая сетка соответствий, круговая рассадка,
турнирные подсчёты (круговой и на выбывание)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.deduction2_shared.base import _DedBase, _TEAMS, _TEAMS_EN

class TournamentTask(_DedBase):
    TASK_TYPE = "tournament"
    TASK_TYPES = ["round_robin", "knockout"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"rr": 3, "ko": 2}, 2: {"rr": 3, "ko": 2}, 3: {"rr": 4, "ko": 3},
        4: {"rr": 4, "ko": 3}, 5: {"rr": 5, "ko": 3}, 6: {"rr": 5, "ko": 4},
        7: {"rr": 6, "ko": 4}, 8: {"rr": 6, "ko": 4}, 9: {"rr": 7, "ko": 4}, 10: {"rr": 8, "ko": 4},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.subtype = subtype or kwargs.get("task_type") or random.choice(self.TASK_TYPES)
        self.rr = int(p["rr"])
        self.ko = int(p["ko"])
        self.augment = augment
        self.teams_pool = ({"ru": (_TEAMS), "en": (_TEAMS_EN)}.get(language, (_TEAMS_EN)))
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        if self.subtype == "round_robin":
            self.teams = self.teams_pool[:self.rr]
            self.results = []  # (a, b, outcome) outcome in {A,B,D}
            self.points = {t: 0 for t in self.teams}
            for i in range(len(self.teams)):
                for j in range(i + 1, len(self.teams)):
                    a, b = self.teams[i], self.teams[j]
                    o = random.choice(["A", "B", "D"])
                    self.results.append((a, b, o))
                    if o == "A":
                        self.points[a] += 3
                    elif o == "B":
                        self.points[b] += 3
                    else:
                        self.points[a] += 1; self.points[b] += 1
            self.query = random.choice(self.teams)
            self.answer = self.points[self.query]
        else:
            size = 2 ** self.ko
            self.bracket_teams = self.teams_pool[:0] + [f"T{i+1}" for i in range(size)]
            # исходы задаём случайно, детерминированно определяем чемпиона
            self.rounds = []
            cur = self.bracket_teams[:]
            while len(cur) > 1:
                rnd = []
                nxt = []
                for k in range(0, len(cur), 2):
                    win = random.choice([cur[k], cur[k + 1]])
                    rnd.append((cur[k], cur[k + 1], win))
                    nxt.append(win)
                self.rounds.append(rnd)
                cur = nxt
            self.champion = cur[0]

    def _descr(self, language):
        if self.subtype == "round_robin":
            lines = []
            for a, b, o in self.results:
                if o == "A":
                    res = ((texts.t('s6', language, a=a, b=b)))
                elif o == "B":
                    res = ((texts.t('s8', language, b=b, a=a)))
                else:
                    res = ((texts.t('s9', language, a=a, b=b)))
                lines.append("- " + res)
            body = "\n".join(lines)
            return ((texts.t('s1', language, body=body, query=self.query)))
        lines = []
        for ri, rnd in enumerate(self.rounds):
            for a, b, w in rnd:
                lines.append(((texts.t('s7', language, v0=ri + 1, a=a, b=b, w=w))))
        body = "\n".join(lines)
        return ((texts.t('s0', language, body=body)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.subtype == "round_robin":
            self.solution_steps = [
                ((texts.t('s2', self.language))),
                ((texts.t('s3', self.language, query=self.query, answer=self.answer))),
            ]
            self.final_answer = str(self.answer)
        else:
            self.solution_steps = [
                ((texts.t('s4', self.language))),
                ((texts.t('s5', self.language, champion=self.champion))),
            ]
            self.final_answer = self.champion

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.subtype == "round_robin":
            return U.verify_int(prediction, int(self.answer))
        return U.verify_label(prediction, [self.champion])
