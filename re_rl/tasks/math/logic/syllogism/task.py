"""SyllogismTask — проверка валидности категорического силлогизма.

Две посылки и заключение над тремя терминами (S, M, P). Валидность
определяется семантически: перебором всех вариантов занятости 8 областей
диаграммы Венна (булева интерпретация: All/No — универсальные, Some — с
экзистенциальным требованием).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_TERMS_RU = [texts.literal('literals.s8'), texts.literal('literals.s9'), texts.literal('literals.s10'), texts.literal('literals.s11'), texts.literal('literals.s12'), texts.literal('literals.s13'),
             texts.literal('literals.s14'), texts.literal('literals.s15'), texts.literal('literals.s16'), texts.literal('literals.s17'), texts.literal('literals.s18'), texts.literal('literals.s19')]
_TERMS_EN = ["cats", "mammals", "predators", "birds", "fish", "plants",
             "philosophers", "mortals", "Greeks", "poets", "scientists", "musicians"]

# Квантификаторы: (ключ, шаблон ru, шаблон en)
_QUANT = {
    "all": (texts.literal('literals.s20'), "All {x} are {y}."),
    "no": (texts.literal('literals.s21'), "No {x} are {y}."),
    "some": (texts.literal('literals.s22'), "Some {x} are {y}."),
    "some_not": (texts.literal('literals.s23'), texts.literal('literals.s24')),
}


class SyllogismTask(BaseMathTask):
    TASK_TYPE = "syllogism"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {"figure":1 if i <= 3 else 2 if i <= 6 else 3 if i <= 8 else 4} for i in range(1, 11)}

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, figure=None, mood=None, **kwargs):
        self.figure = self._interpolate_difficulty(difficulty)['figure'] if figure is None else figure
        if type(self.figure) is not int or self.figure not in (1,2,3,4):raise ValueError('invalid_figure')
        if mood is not None and (not isinstance(mood,(tuple,list)) or len(mood) != 3 or any(q not in _QUANT for q in mood)):
            raise ValueError('invalid_mood')
        self.mood = tuple(mood) if mood is not None else None
        self.augment = augment
        self.difficulty = difficulty
        terms = (({"ru": (_TERMS_RU), "en": (_TERMS_EN)}.get(language, (_TERMS_EN))))
        self.S, self.M, self.P = random.sample(terms, 3)
        self.language = language
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        # Индексы терминов в кортеже занятости региона: (S, M, P).
        idx = {"S": 0, "M": 1, "P": 2}
        # Посылки классической структуры: (M,P), (S,M); заключение (S,P).
        major,minor = {1:(('M','P'),('S','M')),2:(('P','M'),('S','M')),
                       3:(('M','P'),('M','S')),4:(('P','M'),('M','S'))}[self.figure]
        mood = self.mood if self.mood is not None else tuple(random.choice(list(_QUANT)) for _ in range(3))
        self.premise1 = (mood[0],*major)
        self.premise2 = (mood[1],*minor)
        self.conclusion = (mood[2],'S','P')
        self._idx = idx
        self._valid = self._check_validity()

    def _stmt_holds(self, stmt, occupied) -> bool:
        """occupied — множество занятых регионов (кортежей 0/1 по (S,M,P))."""
        q, xk, yk = stmt
        xi, yi = self._idx[xk], self._idx[yk]
        if q == "all":  # нет региона X∧¬Y
            return not any(r[xi] == 1 and r[yi] == 0 for r in occupied)
        if q == "no":  # нет региона X∧Y
            return not any(r[xi] == 1 and r[yi] == 1 for r in occupied)
        if q == "some":  # есть регион X∧Y
            return any(r[xi] == 1 and r[yi] == 1 for r in occupied)
        return any(r[xi] == 1 and r[yi] == 0 for r in occupied)  # some_not

    def _check_validity(self) -> bool:
        regions = list(product([0, 1], repeat=3))  # 8 регионов
        for mask in product([0, 1], repeat=8):
            occupied = [regions[i] for i in range(8) if mask[i]]
            if self._stmt_holds(self.premise1, occupied) and self._stmt_holds(self.premise2, occupied):
                if not self._stmt_holds(self.conclusion, occupied):
                    return False  # контрмодель найдена
        return True

    def _fmt(self, stmt) -> str:
        q, xk, yk = stmt
        names = {"S": self.S, "M": self.M, "P": self.P}
        tmpl = _QUANT[q][{"ru": 0, "en": 1}.get(self.language, 1)]
        return tmpl.format(x=names[xk], y=names[yk])

    def _make_description(self, language: str) -> str:
        head = ((texts.t('s2', language)))
        body = (f"1) {self._fmt(self.premise1)}\n"
                f"2) {self._fmt(self.premise2)}\n"
                f"{(texts.t('s7', language))}: {self._fmt(self.conclusion)}\n")
        tail = ((texts.t('s3', language)))
        return head + body + tail

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s4', self.language))),
            ((texts.t('s5', self.language) if self._valid else
               texts.t('s6', self.language))),
        ]
        self.final_answer = texts.t('s0', self.language) if self._valid else texts.t('s1', self.language)

    def verify(self, prediction: str) -> float:
        self.solve()
        text = U.clean(prediction).strip().rstrip('.!').strip().casefold()
        valid_syn = {texts.t(key,lang).casefold() for key in ('s0','s25','s26','s27','s28') for lang in ('ru','en')}
        invalid_syn = {texts.t(key,lang).casefold() for key in ('s1','s29','s30','s31','s32','not_valid') for lang in ('ru','en')}
        found_valid = text in valid_syn
        found_invalid = text in invalid_syn
        if found_valid == found_invalid:  # оба или ни одного — неоднозначно
            return 0.0
        predicted_valid = found_valid
        return 1.0 if predicted_valid == self._valid else 0.0

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
