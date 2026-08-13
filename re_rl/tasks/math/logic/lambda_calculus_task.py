"""β-редукция в бестиповом λ-исчислении (нормальный порядок редукции).

Подтипы:
- ``beta_steps``     — сколько шагов β-редукции ведут к нормальной форме;
- ``is_normal_form`` — находится ли терм уже в нормальной форме (да/нет).

Термы генерируются случайно; берутся только нормализующиеся за ограниченное число
шагов (защита от расходимости). Масштаб задаётся размером терма.
"""

import random
from typing import Any, ClassVar, Dict, Optional, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.math.logic import _logic_utils as U

# Терм: ('var', name) | ('abs', var, body) | ('app', f, arg)
Term = Tuple
_CAP = 120


class LambdaCalculusTask(BaseMathTask):
    TASK_TYPE = "lambda_calculus"
    TASK_TYPES = ["beta_steps", "is_normal_form"]

    VARS = ["x", "y", "z", "w", "v"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"depth": 2}, 2: {"depth": 2}, 3: {"depth": 3}, 4: {"depth": 3},
        5: {"depth": 4}, 6: {"depth": 4}, 7: {"depth": 5}, 8: {"depth": 5},
        9: {"depth": 6}, 10: {"depth": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format="text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.depth = int(p["depth"])
        self._fresh = 0
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    # --- генерация ---
    def _gen(self, depth: int, scope):
        r = random.random()
        if depth <= 0 or (r < 0.3 and scope):
            return ("var", random.choice(scope) if scope else random.choice(self.VARS))
        if r < 0.6:
            v = random.choice(self.VARS)
            return ("abs", v, self._gen(depth - 1, scope + [v]))
        return ("app", self._gen(depth - 1, scope), self._gen(depth - 1, scope))

    def _redex_term(self, depth, scope):
        v = random.choice(self.VARS)
        body = self._gen(depth - 1, scope + [v])
        arg = self._gen(depth - 1, scope)
        return ("app", ("abs", v, body), arg)

    def _build(self):
        if self.task_type == "beta_steps":
            for _ in range(400):
                t = self._redex_term(self.depth, [])
                nf, steps, ok = self._normalize(t)
                if ok and steps >= 1:
                    self.term, self.nf, self.steps = t, nf, steps
                    return
            # запасной вариант: (λx.x) y  → y за 1 шаг
            self.term = ("app", ("abs", "x", ("var", "x")), ("var", "y"))
            self.nf, self.steps = ("var", "y"), 1
        else:  # is_normal_form
            if random.random() < 0.5:
                self.term = self._redex_term(self.depth, [])
            else:
                self.term = self._normal_term(self.depth, [])
            self.is_nf = not self._has_redex(self.term)

    def _normal_term(self, depth, scope):
        """Терм без редексов: аргумент применения — не абстракция."""
        r = random.random()
        if depth <= 0 or (r < 0.4 and scope):
            return ("var", random.choice(scope) if scope else random.choice(self.VARS))
        if r < 0.7:
            v = random.choice(self.VARS)
            return ("abs", v, self._normal_term(depth - 1, scope + [v]))
        # применение вида (var t1 t2...) — голова не абстракция
        head = ("var", random.choice(scope) if scope else random.choice(self.VARS))
        return ("app", head, self._normal_term(depth - 1, scope))

    # --- редукция ---
    def _free_vars(self, t: Term) -> Set[str]:
        if t[0] == "var":
            return {t[1]}
        if t[0] == "abs":
            return self._free_vars(t[2]) - {t[1]}
        return self._free_vars(t[1]) | self._free_vars(t[2])

    def _fresh_name(self, avoid: Set[str]) -> str:
        while True:
            self._fresh += 1
            name = f"t{self._fresh}"
            if name not in avoid:
                return name

    def _subst(self, t: Term, x: str, s: Term) -> Term:
        if t[0] == "var":
            return s if t[1] == x else t
        if t[0] == "app":
            return ("app", self._subst(t[1], x, s), self._subst(t[2], x, s))
        # abs
        y, body = t[1], t[2]
        if y == x:
            return t
        if y in self._free_vars(s):
            y2 = self._fresh_name(self._free_vars(s) | self._free_vars(body) | {x})
            body = self._subst(body, y, ("var", y2))
            return ("abs", y2, self._subst(body, x, s))
        return ("abs", y, self._subst(body, x, s))

    def _has_redex(self, t: Term) -> bool:
        if t[0] == "var":
            return False
        if t[0] == "abs":
            return self._has_redex(t[2])
        # app
        if t[1][0] == "abs":
            return True
        return self._has_redex(t[1]) or self._has_redex(t[2])

    def _step(self, t: Term):
        """Один шаг редукции в нормальном порядке (крайний левый внешний редекс)."""
        if t[0] == "var":
            return t, False
        if t[0] == "abs":
            b, ok = self._step(t[2])
            return (("abs", t[1], b), ok)
        # app
        if t[1][0] == "abs":  # сам является редексом
            return self._subst(t[1][2], t[1][1], t[2]), True
        f, ok = self._step(t[1])
        if ok:
            return ("app", f, t[2]), True
        a, ok = self._step(t[2])
        return ("app", t[1], a), ok

    def _normalize(self, t: Term):
        steps = 0
        while steps < _CAP:
            t2, ok = self._step(t)
            if not ok:
                return t, steps, True
            t, steps = t2, steps + 1
        return t, steps, False

    # --- рендер ---
    def _render(self, t: Term) -> str:
        if t[0] == "var":
            return t[1]
        if t[0] == "abs":
            return f"(λ{t[1]}. {self._render(t[2])})"
        return f"({self._render(t[1])} {self._render(t[2])})"

    def _descr(self, language):
        ru = language == "ru"
        term = self._render(self.term)
        if self.task_type == "beta_steps":
            return ((f"Дан λ-терм: {term}\nРедуцируйте его в нормальном порядке (крайний левый "
                     f"внешний редекс) до нормальной формы. Сколько шагов β-редукции для этого "
                     f"потребуется?") if ru else
                    (f"Given the λ-term: {term}\nReduce it in normal order (leftmost-outermost "
                     f"redex) to normal form. How many β-reduction steps are needed?"))
        return ((f"Дан λ-терм: {term}\nНаходится ли он в нормальной форме (нет ни одного "
                 f"β-редекса)? (да/нет)") if ru else
                (f"Given the λ-term: {term}\nIs it in normal form (no β-redex)? (yes/no)"))

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "beta_steps":
            self.solution_steps = [
                ("На каждом шаге находим крайний левый внешний редекс (λx.M) N и заменяем его "
                 "на M[x:=N] (с переименованием во избежание захвата переменных)." if ru else
                 "At each step find the leftmost-outermost redex (λx.M) N and replace it by "
                 "M[x:=N] (renaming to avoid variable capture)."),
                (f"Нормальная форма: {self._render(self.nf)}." if ru else
                 f"Normal form: {self._render(self.nf)}."),
                (f"Число шагов: {self.steps}." if ru else f"Number of steps: {self.steps}.")]
            self.final_answer = str(self.steps)
        else:
            self.solution_steps = [
                ("Ищем β-редекс — подтерм вида (λx.M) N." if ru else
                 "Look for a β-redex — a subterm of the form (λx.M) N."),
                (("Редекс отсутствует." if self.is_nf else "Редекс присутствует.") if ru else
                 ("No redex present." if self.is_nf else "A redex is present."))]
            self.final_answer = ("да" if self.is_nf else "нет") if ru else \
                ("yes" if self.is_nf else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "beta_steps":
            return U.verify_int(prediction, int(self.steps))
        return U.verify_bool(prediction, self.is_nf)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
