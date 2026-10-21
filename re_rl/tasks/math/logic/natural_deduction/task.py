"""Проверка корректности пропозиционального вывода (natural deduction).

Дан список пронумерованных строк: посылки и выводы по правилам MP, MT, ∧I, ∧E
со ссылками на предыдущие строки. Нужно определить, корректен ли вывод (да/нет).
Эталон определяется детерминированным проверяющим (checker).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_ATOMS = ["p", "q", "r", "s", "t"]


def _render(f):
    k = f[0]
    if k == "atom":
        return f[1]
    if k == "not":
        return f"¬{_render(f[1])}"
    if k == "imp":
        return f"({_render(f[1])} → {_render(f[2])})"
    return f"({_render(f[1])} ∧ {_render(f[2])})"


def _check_line(line, prior):
    """Проверяет одну выводимую строку по её правилу и ссылкам."""
    rule, refs, F = line["rule"], line["refs"], line["formula"]
    if any(r < 0 or r >= len(prior) for r in refs):
        return False
    forms = [prior[r] for r in refs]
    if rule == "MP":
        if len(forms) != 2:
            return False
        for a, b in ((0, 1), (1, 0)):
            if forms[b][0] == "imp" and forms[a] == forms[b][1] and F == forms[b][2]:
                return True
        return False
    if rule == "MT":
        if len(forms) != 2:
            return False
        for a, b in ((0, 1), (1, 0)):
            if forms[b][0] == "imp" and forms[a] == ("not", forms[b][2]) and F == ("not", forms[b][1]):
                return True
        return False
    if rule == "AND_I":
        if len(forms) != 2:
            return False
        return F == ("and", forms[0], forms[1]) or F == ("and", forms[1], forms[0])
    if rule == "AND_E1":
        return len(forms) == 1 and forms[0][0] == "and" and F == forms[0][1]
    if rule == "AND_E2":
        return len(forms) == 1 and forms[0][0] == "and" and F == forms[0][2]
    return False


def _check_proof(lines):
    prior = []
    for line in lines:
        if line["rule"] == "premise":
            prior.append(line["formula"])
            continue
        if not _check_line(line, prior):
            return False
        prior.append(line["formula"])
    return True


class NaturalDeductionTask(BaseMathTask):
    TASK_TYPE = "natural_deduction"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"derived": 2}, 2: {"derived": 2}, 3: {"derived": 3}, 4: {"derived": 3},
        5: {"derived": 4}, 6: {"derived": 4}, 7: {"derived": 5}, 8: {"derived": 5},
        9: {"derived": 6}, 10: {"derived": 7},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.target_derived = int(p["derived"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _seed_premises(self):
        atoms = random.sample(_ATOMS, k=min(4, len(_ATOMS)))
        a, b, c, d = (atoms + atoms)[:4]
        prem = [("atom", a), ("imp", ("atom", a), ("atom", b)),
                ("imp", ("atom", b), ("atom", c)),
                ("and", ("atom", c), ("atom", d)),
                ("imp", ("atom", d), ("atom", a)), ("not", ("atom", b))]
        random.shuffle(prem)
        return prem

    def _candidates(self, known):
        cands = []
        n = len(known)
        for i in range(n):
            fi = known[i]
            if fi[0] == "and":
                cands.append((fi[1], "AND_E1", [i]))
                cands.append((fi[2], "AND_E2", [i]))
            for j in range(n):
                if i == j:
                    continue
                fj = known[j]
                if fj[0] == "imp" and fi == fj[1]:
                    cands.append((fj[2], "MP", [i, j]))
                if fj[0] == "imp" and fi == ("not", fj[2]):
                    cands.append((("not", fj[1]), "MT", [i, j]))
        if random.random() < 0.3 and n >= 2:  # изредка ∧I
            i, j = random.sample(range(n), 2)
            cands.append((("and", known[i], known[j]), "AND_I", [i, j]))
        return [c for c in cands if c[0] not in known]

    def _build(self):
        for _ in range(200):
            prem = self._seed_premises()
            lines = [{"formula": f, "rule": "premise", "refs": []} for f in prem]
            known = list(prem)
            derived = 0
            while derived < self.target_derived:
                cands = self._candidates(known)
                if not cands:
                    break
                F, rule, refs = random.choice(cands)
                lines.append({"formula": F, "rule": rule, "refs": refs})
                known.append(F)
                derived += 1
            if derived < self.target_derived:
                continue
            assert _check_proof(lines)
            self.n_premises = len(prem)
            if random.random() < 0.5:
                self.lines = lines
                self.valid = True
            else:
                corrupted = self._corrupt(lines)
                if corrupted is None:
                    continue
                self.lines = corrupted
                self.valid = False
            return
        # запасной вариант — валидный минимальный вывод MP
        prem = [("atom", "p"), ("imp", ("atom", "p"), ("atom", "q"))]
        self.lines = [{"formula": prem[0], "rule": "premise", "refs": []},
                      {"formula": prem[1], "rule": "premise", "refs": []},
                      {"formula": ("atom", "q"), "rule": "MP", "refs": [0, 1]}]
        self.n_premises = 2
        self.valid = True

    def _corrupt(self, lines):
        derived_idx = [i for i, l in enumerate(lines) if l["rule"] != "premise"]
        for _ in range(30):
            cp = [dict(l, refs=list(l["refs"])) for l in lines]
            k = random.choice(derived_idx)
            if random.random() < 0.5:  # подменяем формулу
                cp[k]["formula"] = ("not", ("atom", random.choice(_ATOMS)))
            else:  # ломаем ссылку
                if cp[k]["refs"]:
                    pos = random.randrange(len(cp[k]["refs"]))
                    cp[k]["refs"][pos] = random.randrange(max(1, k))
            if not _check_proof(cp):
                return cp
        return None

    def _rule_name(self, rule):
        return {"MP": "MP", "MT": "MT", "AND_I": texts.t('s8', self.language), "AND_E1": texts.t('s9', self.language),
                "AND_E2": texts.t('s10', self.language), "premise": texts.t('s11', self.language)}[rule]

    def _descr(self, language):
        rows = []
        for i, l in enumerate(lines := self.lines, 1):
            if l["rule"] == "premise":
                tag = ((texts.t('s5', language)))
                rows.append(f"{i}. {_render(l['formula'])}   [{tag}]")
            else:
                refs = ", ".join(str(r + 1) for r in l["refs"])
                rn = ({"ru": (self._rule_name(l['rule'])), "en": (l['rule'].replace('AND_', '∧'))}.get(language, (l['rule'].replace('AND_', '∧'))))
                rows.append(f"{i}. {_render(l['formula'])}   [{rn}: {refs}]")
        body = "\n".join(rows)
        if {"ru": True, "en": False}.get(language, False):
            return (texts.t('s7', language, body=body))
        return (texts.t('s6', language, body=body))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s2', self.language))),
            ((texts.t('s3', self.language) if self.valid else
               texts.t('s4', self.language))),
        ]
        self.final_answer = (texts.t('s0', self.language) if self.valid else texts.t('s1', self.language))

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_bool(prediction, bool(self.valid))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
