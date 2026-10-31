"""FamilyTreeTask — многошаговое рассуждение о родственных отношениях.

Строится небольшое генеалогическое древо из трёх поколений (с указанием пола и
браков). Требуется определить, кем приходится один человек другому. Отношение
вычисляется структурно по графу родителей/супругов.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from .solver import relationship,fingerprint
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_MALE = [texts.literal('literals.s6'), texts.literal('literals.s7'), texts.literal('literals.s8'), texts.literal('literals.s9'), texts.literal('literals.s10'), texts.literal('literals.s11'), texts.literal('literals.s12'), texts.literal('literals.s13'), texts.literal('literals.s14')]
_FEMALE = [texts.literal('literals.s15'), texts.literal('literals.s16'), texts.literal('literals.s17'), texts.literal('literals.s18'), texts.literal('literals.s19'), texts.literal('literals.s20'), texts.literal('literals.s21'), texts.literal('literals.s22'), texts.literal('literals.s23')]
_MALE_EN = ["Ivan", "Pyotr", "Sergey", "Oleg", "Roman", "Pavel", "Yury", "Maxim", "Artyom"]
_FEMALE_EN = ["Maria", "Olga", "Elena", "Anna", "Irina", "Natalia", "Svetlana", "Tatiana", "Daria"]

# role_key -> (ru если муж., ru если жен. — уже задан ключом), синонимы для проверки.
_ROLE_WORDS = {
    "father": (texts.literal('literals.s24'), [texts.literal('literals.s42'), texts.literal('literals.s43'), "father"]),
    "mother": (texts.literal('literals.s25'), [texts.literal('literals.s44'), texts.literal('literals.s45'), "mother"]),
    "son": (texts.literal('literals.s26'), [texts.literal('literals.s46'), "son"]),
    "daughter": (texts.literal('literals.s27'), [texts.literal('literals.s47'), texts.literal('literals.s48'), "daughter"]),
    "brother": (texts.literal('literals.s28'), [texts.literal('literals.s49'), "brother"]),
    "sister": (texts.literal('literals.s29'), [texts.literal('literals.s50'), "sister"]),
    "grandfather": (texts.literal('literals.s30'), [texts.literal('literals.s51'), texts.literal('literals.s52'), "grandfather"]),
    "grandmother": (texts.literal('literals.s31'), [texts.literal('literals.s53'), "grandmother"]),
    "grandson": (texts.literal('literals.s32'), [texts.literal('literals.s54'), "grandson"]),
    "granddaughter": (texts.literal('literals.s33'), [texts.literal('literals.s55'), "granddaughter"]),
    "uncle": (texts.literal('literals.s34'), [texts.literal('literals.s56'), "uncle"]),
    "aunt": (texts.literal('literals.s35'), [texts.literal('literals.s57'), texts.literal('literals.s58'), "aunt"]),
    "nephew": (texts.literal('literals.s36'), [texts.literal('literals.s59'), "nephew"]),
    "niece": (texts.literal('literals.s37'), [texts.literal('literals.s60'), "niece"]),
    "cousin_m": (texts.literal('literals.s38'), [texts.literal('literals.s61'), texts.literal('literals.s62'), "cousin"]),
    "cousin_f": (texts.literal('literals.s39'), [texts.literal('literals.s63'), texts.literal('literals.s64'), "cousin"]),
    "husband": (texts.literal('literals.s40'), [texts.literal('literals.s65'), texts.literal('literals.s66'), "husband"]),
    "wife": (texts.literal('literals.s41'), [texts.literal('literals.s67'), texts.literal('literals.s68'), "wife"]),
}


class FamilyTreeTask(BaseMathTask):
    TASK_TYPE = "family_tree"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, relation_hops=None, **kwargs):
        difficulty = 5 if difficulty is None else difficulty
        if type(difficulty) is not int or not 1 <= difficulty <= 10:
            raise ValueError("invalid_difficulty")
        self.relation_hops = (1 if difficulty <= 2 else 2 if difficulty <= 6 else 3 if difficulty <= 8 else 4) if relation_hops is None else relation_hops
        if type(self.relation_hops) is not int or not 1 <= self.relation_hops <= 4:
            raise ValueError('invalid_relation_hops')
        self.augment = augment
        self.difficulty = difficulty
        self.language = language
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _new_name(self, gender: str) -> str:
        pool = self._males_pool if gender == "m" else self._females_pool
        name = random.choice(pool)
        pool.remove(name)
        return name

    def _build(self):
        names = {"ru": (_MALE, _FEMALE), "en": (_MALE_EN, _FEMALE_EN)}
        male, female = names.get(self.language, names["en"])
        self._males_pool = male[:]
        self._females_pool = female[:]
        self.gender: Dict[str, str] = {}
        self.parents: Dict[str, set] = {}
        self.spouse: Dict[str, str] = {}
        self.name: Dict[str, str] = {}

        def person(pid, g):
            self.gender[pid] = g
            self.name[pid] = self._new_name(g)
            self.parents.setdefault(pid, set())

        def marry(a, b):
            self.spouse[a] = b
            self.spouse[b] = a

        # Поколение 1.
        person("gp1", "m"); person("gp2", "f"); marry("gp1", "gp2")
        # Поколение 2: двое детей пары gp + их супруги.
        person("c1", random.choice("mf")); person("c2", random.choice("mf"))
        self.parents["c1"] = {"gp1", "gp2"}
        self.parents["c2"] = {"gp1", "gp2"}
        person("s1", "f" if self.gender["c1"] == "m" else "m"); marry("c1", "s1")
        person("s2", "f" if self.gender["c2"] == "m" else "m"); marry("c2", "s2")
        # Поколение 3.
        person("k1", random.choice("mf")); person("k2", random.choice("mf"))
        person("k3", random.choice("mf"))
        self.parents["k1"] = {"c1", "s1"}
        self.parents["k2"] = {"c1", "s1"}
        self.parents["k3"] = {"c2", "s2"}

        self.couples = [("gp1", "gp2"), ("c1", "s1"), ("c2", "s2")]
        self.child_groups = [("gp1", "gp2", ["c1", "c2"]),
                             ("c1", "s1", ["k1", "k2"]),
                             ("c2", "s2", ["k3"])]

        # Выбираем пару с определимым отношением.
        ids = list(self.gender)
        labeled: List[Tuple[str, str, str]] = []
        for a in ids:
            for b in ids:
                if a == b:
                    continue
                role = self._relate(a, b)
                hops = 1 if role in ('father','mother','son','daughter','husband','wife') else 2 if role in ('brother','sister','grandfather','grandmother','grandson','granddaughter') else 3 if role in ('uncle','aunt','nephew','niece') else 4
                if role is not None and hops == self.relation_hops:
                    labeled.append((a, b, role))
        self.a, self.b, self.role = random.choice(labeled)

    def _is_parent(self, x, y):
        return x in self.parents.get(y, set())

    def _is_grandparent(self, x, y):
        return any(x in self.parents.get(p, set()) for p in self.parents.get(y, set()))

    def _relate(self, A, B) -> Optional[str]:
        gA = self.gender[A]
        if self._is_parent(A, B):
            return "father" if gA == "m" else "mother"
        if self._is_parent(B, A):
            return "son" if gA == "m" else "daughter"
        if self.spouse.get(A) == B:
            return "husband" if gA == "m" else "wife"
        if self._is_grandparent(A, B):
            return "grandfather" if gA == "m" else "grandmother"
        if self._is_grandparent(B, A):
            return "grandson" if gA == "m" else "granddaughter"
        pa, pb = self.parents.get(A, set()), self.parents.get(B, set())
        if pa and pb and (pa & pb):
            return "brother" if gA == "m" else "sister"
        for p in self.parents.get(B, set()):  # A — брат/сестра родителя B
            if p != A and pa and self.parents.get(p) and (pa & self.parents[p]):
                return "uncle" if gA == "m" else "aunt"
        for p in self.parents.get(A, set()):  # B — дядя/тётя A
            if p != B and pb and self.parents.get(p) and (pb & self.parents[p]):
                return "nephew" if gA == "m" else "niece"
        for x in self.parents.get(A, set()):
            for y in self.parents.get(B, set()):
                if x != y and self.parents.get(x) and self.parents.get(y) and \
                        (self.parents[x] & self.parents[y]):
                    return "cousin_m" if gA == "m" else "cousin_f"
        return None

    def _make_description(self, language: str) -> str:
        males = [self.name[i] for i in self.gender if self.gender[i] == "m"]
        females = [self.name[i] for i in self.gender if self.gender[i] == "f"]
        lines = []
        lines.append(((texts.t('s1', language, v0=', '.join(males), v1=', '.join(females)))))
        for a, b in self.couples:
            lines.append(((texts.t('s4', language, v0=self.name[a], v1=self.name[b]))))
        for a, b, kids in self.child_groups:
            kids_names = ", ".join(self.name[k] for k in kids)
            lines.append(((texts.t('s5', language, v0=self.name[a], v1=self.name[b], kids_names=kids_names))))
        q = ((texts.t('s0', language, v0=self.name[self.a], v1=self.name[self.b])))
        random.shuffle(lines)
        return texts.t("relation_rules",language)+"\n".join(lines) + q

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        ru_word = _ROLE_WORDS[self.role][0]
        en_word = _ROLE_WORDS[self.role][1][-1]
        word = {"ru": ru_word, "en": en_word}.get(self.language, en_word)
        self.solution_steps = [
            ((texts.t('s2', self.language))),
            ((texts.t('s3', self.language, v0=self.name[self.a], word=word, v2=self.name[self.b]))),
        ]
        self.final_answer = word

    def verify(self, prediction: str) -> float:
        certificate = getattr(self,'_kin_certificate',None)
        if certificate is None or certificate[0] != fingerprint(self):
            try:self.solve()
            except ValueError:return 0.0
        role = self._kin_certificate[1]
        text = U.clean(prediction).strip().rstrip('.!').strip().casefold()
        return float(text in {word.casefold() for word in [_ROLE_WORDS[role][0]]+_ROLE_WORDS[role][1]})

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
