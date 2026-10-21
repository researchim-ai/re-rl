"""Дедуктивные задачи: логическая сетка соответствий, круговая рассадка,
турнирные подсчёты (круговой и на выбывание)."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from itertools import permutations
from typing import Any, ClassVar, Dict, List, Optional, Tuple
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U
from re_rl.tasks.math.logic.deduction2_shared.base import _DedBase, _NAMES, _NAMES_EN

class LogicGridTask(_DedBase):
    TASK_TYPE = "logic_grid"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 3}, 4: {"n": 4}, 5: {"n": 4},
        6: {"n": 4}, 7: {"n": 4}, 8: {"n": 5}, 9: {"n": 5}, 10: {"n": 5},
    }
    _DRINKS = {"ru": [texts.literal('literals.s10'), texts.literal('literals.s11'), texts.literal('literals.s12'), texts.literal('literals.s13'), texts.literal('literals.s14')],
               "en": ["tea", "coffee", "juice", "milk", "cocoa"]}
    _SPORTS = {"ru": [texts.literal('literals.s15'), texts.literal('literals.s16'), texts.literal('literals.s17'), texts.literal('literals.s18'), texts.literal('literals.s19')],
               "en": ["tennis", "chess", "football", "swimming", "running"]}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.lang = language
        self.augment = augment
        self.people = (({"ru": (_NAMES), "en": (_NAMES_EN)}.get(language, (_NAMES_EN))))[:self.n]
        self.drinks = self._DRINKS[(texts.t('s8', language))][:self.n]
        self.sports = self._SPORTS[(texts.t('s9', language))][:self.n]
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.drink_of = dict(zip(self.people, random.sample(self.drinks, self.n)))
        self.sport_of = dict(zip(self.people, random.sample(self.sports, self.n)))

        pool = []  # (тип, текст-функция, предикат(assignment)->bool)
        for pr in self.people:
            pool.append(("d+", pr, self.drink_of[pr]))
            pool.append(("s+", pr, self.sport_of[pr]))
            pool.append(("link", self.drink_of[pr], self.sport_of[pr]))  # у кого напиток -> тот спорт
        for pr in self.people:  # отрицания
            other = random.choice([d for d in self.drinks if d != self.drink_of[pr]])
            pool.append(("d-", pr, other))
        random.shuffle(pool)

        clues = []
        for cl in pool:
            clues.append(cl)
            if self._count_solutions(clues) == 1:
                break
        if self._count_solutions(clues) != 1:
            clues = [("d+", pr, self.drink_of[pr]) for pr in self.people] + \
                    [("s+", pr, self.sport_of[pr]) for pr in self.people]
        pruned = clues[:]
        for cl in clues:
            trial = [x for x in pruned if x is not cl]
            if self._count_solutions(trial) == 1:
                pruned = trial
        random.shuffle(pruned)
        self.clues = pruned
        self.query_person = random.choice(self.people)
        self.query_attr = random.choice(["drink", "sport"])
        self.answer = self.drink_of[self.query_person] if self.query_attr == "drink" \
            else self.sport_of[self.query_person]

    def _clue_holds(self, cl, dmap, smap):
        kind, a, b = cl
        if kind == "d+":
            return dmap[a] == b
        if kind == "d-":
            return dmap[a] != b
        if kind == "s+":
            return smap[a] == b
        # link: человек с напитком a занимается спортом b
        person = next(pr for pr in self.people if dmap[pr] == a)
        return smap[person] == b

    def _count_solutions(self, clues):
        cnt = 0
        people = self.people
        for dperm in permutations(self.drinks):
            dmap = dict(zip(people, dperm))
            if not all(self._clue_holds(c, dmap, None) for c in clues if c[0] in ("d+", "d-")):
                continue
            for sperm in permutations(self.sports):
                smap = dict(zip(people, sperm))
                if all(self._clue_holds(c, dmap, smap) for c in clues):
                    cnt += 1
                    if cnt > 1:
                        return cnt
        return cnt

    def _clue_text(self, cl):
        kind, a, b = cl
        if kind == "d+":
            return ((texts.t('s2', self.language, a=a, b=b)))
        if kind == "d-":
            return ((texts.t('s3', self.language, a=a, b=b)))
        if kind == "s+":
            return ((texts.t('s4', self.language, a=a, b=b)))
        return ((texts.t('s0', self.language, a=a, b=b)))

    def _descr(self, language):
        head = ((texts.t('s1', language, n=self.n, v1=', '.join(self.people), v2=', '.join(self.drinks), v3=', '.join(self.sports))))
        body = "\n".join(f"- {self._clue_text(c)}" for c in self.clues)
        if self.query_attr == "drink":
            q = ((texts.t('s5', language, query_person=self.query_person)))
        else:
            q = ((texts.t('s6', language, query_person=self.query_person)))
        return head + body + q

    def solve(self):
        self.solution_steps = [
            ((texts.t('s7', self.language))),
            ((texts.common('answer_line', self.language, answer=self.answer))),
        ]
        self.final_answer = self.answer

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_label(prediction, [self.answer])
