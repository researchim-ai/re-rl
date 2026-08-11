"""FamilyTreeTask — многошаговое рассуждение о родственных отношениях.

Строится небольшое генеалогическое древо из трёх поколений (с указанием пола и
браков). Требуется определить, кем приходится один человек другому. Отношение
вычисляется структурно по графу родителей/супругов.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_MALE = ["Иван", "Пётр", "Сергей", "Олег", "Роман", "Павел", "Юрий", "Максим", "Артём"]
_FEMALE = ["Мария", "Ольга", "Елена", "Наталья", "Ирина", "Светлана", "Татьяна", "Дарья", "Алина"]

# role_key -> (ru если муж., ru если жен. — уже задан ключом), синонимы для проверки.
_ROLE_WORDS = {
    "father": ("отец", ["отец", "папа", "father"]),
    "mother": ("мать", ["мать", "мама", "mother"]),
    "son": ("сын", ["сын", "son"]),
    "daughter": ("дочь", ["дочь", "дочка", "daughter"]),
    "brother": ("брат", ["брат", "brother"]),
    "sister": ("сестра", ["сестра", "sister"]),
    "grandfather": ("дедушка", ["дедушка", "дед", "grandfather"]),
    "grandmother": ("бабушка", ["бабушка", "grandmother"]),
    "grandson": ("внук", ["внук", "grandson"]),
    "granddaughter": ("внучка", ["внучка", "granddaughter"]),
    "uncle": ("дядя", ["дядя", "uncle"]),
    "aunt": ("тётя", ["тётя", "тетя", "aunt"]),
    "nephew": ("племянник", ["племянник", "nephew"]),
    "niece": ("племянница", ["племянница", "niece"]),
    "cousin_m": ("двоюродный брат", ["двоюродный", "кузен", "cousin"]),
    "cousin_f": ("двоюродная сестра", ["двоюродная", "кузина", "cousin"]),
    "husband": ("муж", ["муж", "супруг", "husband"]),
    "wife": ("жена", ["жена", "супруга", "wife"]),
}


class FamilyTreeTask(BaseMathTask):
    TASK_TYPE = "family_tree"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        self.augment = augment
        self.difficulty = difficulty
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
        self._males_pool = _MALE[:]
        self._females_pool = _FEMALE[:]
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
                if role is not None:
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
        ru = language == "ru"
        males = [self.name[i] for i in self.gender if self.gender[i] == "m"]
        females = [self.name[i] for i in self.gender if self.gender[i] == "f"]
        lines = []
        lines.append((f"Мужчины: {', '.join(males)}. Женщины: {', '.join(females)}." if ru else
                      f"Men: {', '.join(males)}. Women: {', '.join(females)}."))
        for a, b in self.couples:
            lines.append((f"{self.name[a]} и {self.name[b]} — супруги." if ru else
                          f"{self.name[a]} and {self.name[b]} are married."))
        for a, b, kids in self.child_groups:
            kids_names = ", ".join(self.name[k] for k in kids)
            lines.append((f"У {self.name[a]} и {self.name[b]} есть дети: {kids_names}." if ru else
                          f"{self.name[a]} and {self.name[b]} have children: {kids_names}."))
        q = (f"\nКем приходится {self.name[self.a]} для {self.name[self.b]}?" if ru else
             f"\nHow is {self.name[self.a]} related to {self.name[self.b]}?")
        random.shuffle(lines)
        return "\n".join(lines) + q

    def solve(self):
        ru = self.language == "ru"
        word = _ROLE_WORDS[self.role][0]
        self.solution_steps = [
            ("Прослеживаем связи родитель–ребёнок и браки от одного человека к другому." if ru else
             "Trace parent–child links and marriages from one person to the other."),
            (f"{self.name[self.a]} приходится {word} для {self.name[self.b]}." if ru else
             f"{self.name[self.a]} is the {word} of {self.name[self.b]}."),
        ]
        self.final_answer = word

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_label(prediction, _ROLE_WORDS[self.role][1])

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
