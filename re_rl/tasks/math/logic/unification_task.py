"""Унификация термов первого порядка.

Подтипы:
- ``unifiable``   — унифицируемы ли два терма (да/нет), с проверкой вхождения;
- ``result_term`` — если да, привести результат унификации (по построению — основной,
  т.е. без переменных) терм.

Термы: переменные (X, Y, Z, ...), константы (a, b, c, ...), функции f/g/h.
Масштаб задаётся глубиной и размером термов.
"""

import random
import string
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.math.logic import _logic_utils as U

# Терм: ('var', name) | ('const', name) | ('func', name, [args])
Term = Tuple


class UnificationTask(BaseMathTask):
    TASK_TYPE = "unification"
    TASK_TYPES = ["unifiable", "result_term"]

    FUNCS = [("f", 2), ("g", 1), ("h", 2), ("k", 1)]
    CONSTS = ["a", "b", "c", "d", "e"]
    VARS = ["X", "Y", "Z", "U", "V", "W"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"depth": 1}, 2: {"depth": 1}, 3: {"depth": 2}, 4: {"depth": 2},
        5: {"depth": 2}, 6: {"depth": 3}, 7: {"depth": 3}, 8: {"depth": 3},
        9: {"depth": 4}, 10: {"depth": 4},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format="text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.depth = int(p["depth"])
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    # --- построение термов ---
    def _ground_term(self, depth: int) -> Term:
        if depth <= 0 or random.random() < 0.4:
            return ("const", random.choice(self.CONSTS))
        name, arity = random.choice(self.FUNCS)
        return ("func", name, [self._ground_term(depth - 1) for _ in range(arity)])

    def _subterm_positions(self, term: Term, path=()) -> List[Tuple]:
        res = [path]
        if term[0] == "func":
            for i, a in enumerate(term[2]):
                res += self._subterm_positions(a, path + (i,))
        return res

    def _replace(self, term: Term, path: Tuple, repl: Term) -> Term:
        if not path:
            return repl
        i = path[0]
        args = list(term[2])
        args[i] = self._replace(args[i], path[1:], repl)
        return ("func", term[1], args)

    @staticmethod
    def _antichain(paths: List[Tuple], k: int) -> List[Tuple]:
        """Выбирает до k путей, ни один из которых не является префиксом другого."""
        random.shuffle(paths)
        chosen: List[Tuple] = []
        for pth in paths:
            if any(pth[:len(c)] == c or c[:len(pth)] == pth for c in chosen):
                continue
            chosen.append(pth)
            if len(chosen) >= k:
                break
        return chosen

    def _build(self):
        make_unifiable = (self.task_type == "result_term") or (random.random() < 0.5)
        G = self._ground_term(self.depth + 1)
        # Позиции-непустые (не корень), образующие антицепь.
        positions = [p for p in self._subterm_positions(G) if p]
        pool = self._antichain(positions, max(2, len(positions)))
        random.shuffle(pool)
        half = max(1, len(pool) // 2)
        a_pos, b_pos = pool[:half], pool[half:half + max(1, len(pool) - half)]

        var_id = 0

        def fresh():
            nonlocal var_id
            # Уникальные имена: X, Y, ... для первых, затем V7, V8, ... — чтобы имена
            # никогда не повторялись (иначе одна переменная связалась бы с двумя термами).
            v = self.VARS[var_id] if var_id < len(self.VARS) else f"V{var_id}"
            var_id += 1
            return ("var", v)

        A, B = G, G
        for pth in a_pos:
            A = self._replace(A, pth, fresh())
        for pth in b_pos:
            B = self._replace(B, pth, fresh())

        if not make_unifiable:
            # Ломаем унифицируемость: в согласованной (основной в обоих термах) позиции
            # ставим разные подтермы. Позиция не должна лежать под заменёнными на
            # переменные позициями (иначе там уже не основной подтерм).
            var_paths = a_pos + b_pos

            def under_var(pth: Tuple) -> bool:
                return any(pth[:len(vp)] == vp for vp in var_paths)

            broke = False
            for pth in positions:
                if pth in var_paths or under_var(pth):
                    continue
                A = self._replace(A, pth, ("const", "a"))
                B = self._replace(B, pth, ("func", "g", [("const", "b")]))
                broke = True
                break
            if not broke:  # запасной вариант — гарантированный конфликт на корне
                A = ("const", "a")
                B = ("func", "f", [("const", "a"), ("const", "b")])

        self.termA, self.termB = A, B
        subst = self._unify(A, B)
        self.unifiable = subst is not None
        if self.unifiable:
            self.result = self._resolve(A, subst)
        else:
            self.result = None
        # Для result_term результат обязан существовать — подстрахуемся тривиальной парой.
        if self.task_type == "result_term" and not self.unifiable:
            self.termA = ("func", "f", [("var", "X"), ("const", "b")])
            self.termB = ("func", "f", [("const", "a"), ("const", "b")])
            self.unifiable = True
            self.result = ("func", "f", [("const", "a"), ("const", "b")])

    # --- унификация ---
    def _unify(self, s: Term, t: Term, subst: Optional[Dict] = None) -> Optional[Dict]:
        if subst is None:
            subst = {}
        s = self._walk(s, subst)
        t = self._walk(t, subst)
        if s[0] == "var":
            if s == t:
                return subst
            if self._occurs(s[1], t, subst):
                return None
            subst[s[1]] = t
            return subst
        if t[0] == "var":
            return self._unify(t, s, subst)
        if s[0] == "const" and t[0] == "const":
            return subst if s[1] == t[1] else None
        if s[0] == "func" and t[0] == "func":
            if s[1] != t[1] or len(s[2]) != len(t[2]):
                return None
            for a, b in zip(s[2], t[2]):
                subst = self._unify(a, b, subst)
                if subst is None:
                    return None
            return subst
        return None

    def _walk(self, term: Term, subst: Dict) -> Term:
        while term[0] == "var" and term[1] in subst:
            term = subst[term[1]]
        return term

    def _occurs(self, var: str, term: Term, subst: Dict) -> bool:
        term = self._walk(term, subst)
        if term[0] == "var":
            return term[1] == var
        if term[0] == "func":
            return any(self._occurs(var, a, subst) for a in term[2])
        return False

    def _resolve(self, term: Term, subst: Dict) -> Term:
        term = self._walk(term, subst)
        if term[0] == "func":
            return ("func", term[1], [self._resolve(a, subst) for a in term[2]])
        return term

    # --- рендер ---
    def _render(self, term: Term) -> str:
        if term[0] in ("var", "const"):
            return term[1]
        return f"{term[1]}(" + ", ".join(self._render(a) for a in term[2]) + ")"

    def _descr(self, language):
        ru = language == "ru"
        a, b = self._render(self.termA), self._render(self.termB)
        if self.task_type == "unifiable":
            return ((f"Даны два терма первого порядка (заглавные буквы — переменные, строчные — "
                     f"константы, f/g/h/k — функции):\n  t1 = {a}\n  t2 = {b}\n"
                     f"Унифицируемы ли они? (да/нет)") if ru else
                    (f"Two first-order terms (uppercase = variables, lowercase = constants, "
                     f"f/g/h/k = functions):\n  t1 = {a}\n  t2 = {b}\n"
                     f"Are they unifiable? (yes/no)"))
        return ((f"Даны два унифицируемых терма (заглавные — переменные, строчные — константы):\n"
                 f"  t1 = {a}\n  t2 = {b}\n"
                 f"Приведите терм, получающийся после применения наиболее общего унификатора.")
                if ru else
                (f"Two unifiable terms (uppercase = variables, lowercase = constants):\n"
                 f"  t1 = {a}\n  t2 = {b}\n"
                 f"Give the term obtained after applying the most general unifier."))

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "unifiable":
            self.solution_steps = [
                ("Рекурсивно сопоставляем структуры термов, связывая переменства и проверяя "
                 "вхождение (occurs-check)." if ru else
                 "Recursively match term structures, binding variables with an occurs-check.")]
            self.solution_steps.append(
                ("Термы унифицируемы." if ru else "The terms are unifiable.") if self.unifiable
                else ("Термы не унифицируемы." if ru else "The terms are not unifiable."))
            self.final_answer = ("да" if self.unifiable else "нет") if ru else \
                ("yes" if self.unifiable else "no")
        else:
            res = self._render(self.result)
            self.solution_steps = [
                ("Применяем алгоритм унификации и подставляем найденные значения переменных."
                 if ru else
                 "Apply the unification algorithm and substitute the variable bindings."),
                (f"Результат: {res}." if ru else f"Result: {res}.")]
            self.final_answer = res

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "unifiable":
            return U.verify_bool(prediction, self.unifiable)
        # Сравниваем как строку без пробелов (терм основной, без свободных переменных).
        want = self._render(self.result).replace(" ", "")
        got = U.clean(prediction).replace(" ", "").lower()
        return 1.0 if want.lower() in got else 0.0

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
