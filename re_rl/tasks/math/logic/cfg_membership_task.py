"""Принадлежность строки контекстно-свободному языку (грамматика в НФ Хомского),
проверка алгоритмом CYK. Ответ да/нет."""

import random
from itertools import product
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_TERMS = ["a", "b"]


class CFGMembershipTask(BaseMathTask):
    TASK_TYPE = "cfg_membership"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"nt": 2, "Lmax": 3}, 2: {"nt": 2, "Lmax": 4}, 3: {"nt": 3, "Lmax": 4},
        4: {"nt": 3, "Lmax": 5}, 5: {"nt": 3, "Lmax": 5}, 6: {"nt": 4, "Lmax": 6},
        7: {"nt": 4, "Lmax": 6}, 8: {"nt": 4, "Lmax": 7}, 9: {"nt": 5, "Lmax": 7},
        10: {"nt": 5, "Lmax": 8},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.nt = int(p["nt"])
        self.Lmax = int(p["Lmax"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _random_grammar(self):
        nts = [f"N{i}" for i in range(self.nt)]
        nts[0] = "S"
        binary: Dict[str, List[Tuple[str, str]]] = {A: [] for A in nts}
        term: Dict[str, Set[str]] = {A: set() for A in nts}
        for A in nts:
            for _ in range(random.randint(1, 2)):
                if random.random() < 0.5:
                    term[A].add(random.choice(_TERMS))
                else:
                    B, C = random.choice(nts), random.choice(nts)
                    binary[A].append((B, C))
            if not binary[A] and not term[A]:
                term[A].add(random.choice(_TERMS))
        return nts, binary, term

    def _generating(self, nts, binary, term):
        gen = {A for A in nts if term[A]}
        changed = True
        while changed:
            changed = False
            for A in nts:
                if A in gen:
                    continue
                if any(B in gen and C in gen for B, C in binary[A]):
                    gen.add(A); changed = True
        return gen

    def _cyk(self, s):
        n = len(s)
        if n == 0:
            return False
        table = [[set() for _ in range(n)] for _ in range(n)]
        for i, ch in enumerate(s):
            for A in self.nts:
                if ch in self.term[A]:
                    table[i][i].add(A)
        for length in range(2, n + 1):
            for i in range(0, n - length + 1):
                j = i + length - 1
                for k in range(i, j):
                    for A in self.nts:
                        for B, C in self.binary[A]:
                            if B in table[i][k] and C in table[k + 1][j]:
                                table[i][i + length - 1].add(A)
        return "S" in table[0][n - 1]

    def _build(self):
        for _ in range(100):
            self.nts, self.binary, self.term = self._random_grammar()
            if "S" not in self._generating(self.nts, self.binary, self.term):
                continue
            inL, outL = [], []
            for length in range(1, self.Lmax + 1):
                for bits in product(_TERMS, repeat=length):
                    s = "".join(bits)
                    (inL if self._cyk(s) else outL).append(s)
            if inL and outL:
                if random.random() < 0.5:
                    self.string = random.choice(inL); self.answer = True
                else:
                    self.string = random.choice(outL); self.answer = False
                return
        # запасной вариант: S -> a
        self.nts = ["S"]; self.binary = {"S": []}; self.term = {"S": {"a"}}
        self.string = random.choice(["a", "b"])
        self.answer = self.string == "a"

    def _grammar_str(self):
        lines = []
        for A in self.nts:
            rhs = [f"{B} {C}" for B, C in self.binary[A]] + sorted(self.term[A])
            lines.append(f"{A} → " + " | ".join(rhs))
        return "\n".join(lines)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Контекстно-свободная грамматика (стартовый символ S, терминалы a, b) в нормальной форме "
                 f"Хомского:\n{self._grammar_str()}\n\nПринадлежит ли строка «{self.string}» языку этой "
                 f"грамматики? Ответьте да/нет.") if ru else
                (f"Context-free grammar (start symbol S, terminals a, b) in Chomsky normal form:\n"
                 f"{self._grammar_str()}\n\nDoes the string '{self.string}' belong to the grammar's "
                 f"language? Answer yes/no."))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Алгоритм CYK: заполняем таблицу нетерминалов для всех подстрок снизу вверх." if ru else
             "CYK algorithm: fill the table of nonterminals for all substrings bottom-up."),
            ((("Символ S покрывает всю строку — принадлежит." if self.answer else
               "S не покрывает всю строку — не принадлежит.")) if ru else
             (("S covers the whole string — it belongs." if self.answer else
               "S does not cover the whole string — it does not belong."))),
        ]
        self.final_answer = ("да" if self.answer else "нет") if ru else ("yes" if self.answer else "no")

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
