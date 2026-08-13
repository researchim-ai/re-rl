"""Метод резолюции для пропозициональной логики (CNF).

Подтипы:
- ``unsat``               — выводима ли пустая клауза (множество невыполнимо?) да/нет;
- ``one_step_resolvents`` — сколько различных нетавтологичных резольвент можно получить
  за один шаг резолюции из данного набора клауз.

Масштаб задаётся числом переменных и клауз.
"""

import itertools
import random
import string
from typing import Any, ClassVar, Dict, FrozenSet, List, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.math.logic import _logic_utils as U

Literal = Tuple[str, bool]   # (переменная, полярность): True = X, False = ¬X
Clause = FrozenSet[Literal]


class ResolutionTask(BaseMathTask):
    TASK_TYPE = "resolution"
    TASK_TYPES = ["unsat", "one_step_resolvents"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"vars": 3, "clauses": 3}, 2: {"vars": 3, "clauses": 4},
        3: {"vars": 3, "clauses": 5}, 4: {"vars": 4, "clauses": 5},
        5: {"vars": 4, "clauses": 6}, 6: {"vars": 4, "clauses": 7},
        7: {"vars": 5, "clauses": 7}, 8: {"vars": 5, "clauses": 8},
        9: {"vars": 6, "clauses": 9}, 10: {"vars": 6, "clauses": 10},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format="text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.n_vars, self.n_clauses = int(p["vars"]), int(p["clauses"])
        self.vars = list(string.ascii_uppercase[:self.n_vars])
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _rand_clause(self) -> Clause:
        k = random.randint(1, min(3, self.n_vars))
        chosen = random.sample(self.vars, k)
        return frozenset((v, random.random() < 0.5) for v in chosen)

    @staticmethod
    def _is_tautology(cl: Clause) -> bool:
        return any((v, not pol) in cl for v, pol in cl)

    def _sat(self, clauses: List[Clause]) -> bool:
        for bits in itertools.product([False, True], repeat=self.n_vars):
            assign = dict(zip(self.vars, bits))
            if all(any(assign[v] == pol for v, pol in cl) for cl in clauses):
                return True
        return False

    def _build(self):
        if self.task_type == "unsat":
            target_unsat = random.random() < 0.5
            if target_unsat:
                clauses: List[Clause] = []
                for _ in range(self.n_clauses * 6):
                    cl = self._rand_clause()
                    if self._is_tautology(cl) or cl in clauses:
                        continue
                    clauses.append(cl)
                    if not self._sat(clauses):
                        break
                self.clauses = clauses
            else:
                for _ in range(200):
                    cl_set: List[Clause] = []
                    while len(cl_set) < self.n_clauses:
                        cl = self._rand_clause()
                        if not self._is_tautology(cl) and cl not in cl_set:
                            cl_set.append(cl)
                    if self._sat(cl_set):
                        self.clauses = cl_set
                        break
                else:
                    self.clauses = [frozenset([(self.vars[0], True)])]
            self.answer_bool = not self._sat(self.clauses)  # True = невыполнимо
        else:  # one_step_resolvents
            cl_set = []
            while len(cl_set) < self.n_clauses:
                cl = self._rand_clause()
                if not self._is_tautology(cl) and cl not in cl_set:
                    cl_set.append(cl)
            self.clauses = cl_set
            self.answer_int = len(self._one_step_resolvents(cl_set))

    def _one_step_resolvents(self, clauses: List[Clause]) -> Set[Clause]:
        res: Set[Clause] = set()
        for c1, c2 in itertools.combinations(clauses, 2):
            for v, pol in c1:
                if (v, not pol) in c2:
                    merged = (c1 - {(v, pol)}) | (c2 - {(v, not pol)})
                    if not self._is_tautology(merged):
                        res.add(frozenset(merged))
        return res

    def _fmt_clause(self, cl: Clause) -> str:
        if not cl:
            return "□"
        lits = sorted(cl, key=lambda x: (x[0], not x[1]))
        return "(" + " ∨ ".join((v if pol else f"¬{v}") for v, pol in lits) + ")"

    def _descr(self, language):
        ru = language == "ru"
        cs = " ∧ ".join(self._fmt_clause(c) for c in self.clauses)
        if self.task_type == "unsat":
            return ((f"Дан набор дизъюнктов (в КНФ):\n{cs}\nМетодом резолюции определите, "
                     f"выводима ли пустая клауза, то есть является ли набор невыполнимым. (да/нет)")
                    if ru else
                    (f"Given a set of clauses (CNF):\n{cs}\nUsing resolution, determine whether the "
                     f"empty clause is derivable, i.e. whether the set is unsatisfiable. (yes/no)"))
        return ((f"Дан набор дизъюнктов:\n{cs}\nСколько различных нетавтологичных резольвент "
                 f"(как множеств литералов) можно получить за один шаг резолюции, перебрав все "
                 f"пары клауз и все комплементарные литералы?") if ru else
                (f"Given a set of clauses:\n{cs}\nHow many distinct non-tautological resolvents "
                 f"(as literal sets) can be obtained in one resolution step, over all clause pairs "
                 f"and all complementary literals?"))

    def solve(self):
        ru = self.language == "ru"
        if self.task_type == "unsat":
            self.solution_steps = [
                ("Строим резольвенты, пока не выведем пустую клаузу; эквивалентно проверке "
                 "невыполнимости перебором означиваний." if ru else
                 "Derive resolvents until the empty clause appears; equivalently, check "
                 "unsatisfiability by truth assignments."),
                (("Пустая клауза выводима — набор невыполним." if self.answer_bool else
                  "Пустая клауза не выводима — набор выполним.") if ru else
                 ("The empty clause is derivable — the set is unsatisfiable." if self.answer_bool
                  else "The empty clause is not derivable — the set is satisfiable."))]
            self.final_answer = ("да" if self.answer_bool else "нет") if ru else \
                ("yes" if self.answer_bool else "no")
        else:
            self.solution_steps = [
                ("Для каждой пары клауз с комплементарными литералами строим резольвенту "
                 "(объединение без пары), отбрасывая тавтологии; считаем различные." if ru else
                 "For each clause pair with complementary literals form the resolvent (union "
                 "minus the pair), drop tautologies, count the distinct ones."),
                (f"Число резольвент: {self.answer_int}." if ru else
                 f"Number of resolvents: {self.answer_int}.")]
            self.final_answer = str(self.answer_int)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "unsat":
            return U.verify_bool(prediction, self.answer_bool)
        return U.verify_int(prediction, int(self.answer_int))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
