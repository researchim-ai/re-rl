"""AlgorithmComplexityTask — анализ асимптотической сложности.

Подтипы:
- ``loops``          — по псевдокоду с (вложенными) циклами определить Θ времени работы;
- ``master_theorem`` — по рекурренте T(n)=a·T(n/b)+Θ(n^d) применить мастер-теорему.

Ответ — класс сложности: Θ(1), Θ(log n), Θ(n), Θ(n log n), Θ(n^2),
Θ(n^2 log n), Θ(n^3), Θ(n^3 log n), Θ(2^n). Проверка сравнивает нормализованный
класс, поэтому принимаются записи вида ``O(n^2)``, ``n*n``, ``Θ(n²)`` и т.п.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math._verify_utils import extract_answer_text

_PRETTY = {
    "1": "Θ(1)", "logn": "Θ(log n)", "n": "Θ(n)", "nlogn": "Θ(n log n)",
    "n^2": "Θ(n^2)", "n^2logn": "Θ(n^2 log n)", "n^3": "Θ(n^3)",
    "n^3logn": "Θ(n^3 log n)", "2^n": "Θ(2^n)",
}


def _norm_complexity(s: str) -> str:
    t = extract_answer_text(s).lower()
    for a, b in [("²", "^2"), ("³", "^3"), ("·", ""), ("−", "-"), ("₂", "2"),
                 ("{", ""), ("}", ""), ("log2", "log"), ("log_2", "log"),
                 ("lg", "log"), ("ln", "log"), ("theta", ""), ("θ", ""),
                 ("ω", ""), ("omega", ""), ("big-o", ""), ("bigo", "")]:
        t = t.replace(a, b)
    t = t.replace(" ", "")
    t = t.replace("n*n*n", "n^3").replace("n*n", "n^2").replace("*", "")
    t = t.replace("o(", "(")  # снимаем обёртку большого-O (в 'log(' нет 'o(')
    t = t.replace("(", "").replace(")", "")
    return t


def canon_complexity(s: str) -> Optional[str]:
    t = _norm_complexity(s)
    if not t:
        return None
    if "2^n" in t:
        return "2^n"
    has_log = "logn" in t
    core = t.replace("logn", "")  # снимаем логарифмический множитель
    if "n^3" in core:
        poly = "n^3"
    elif "n^2" in core:
        poly = "n^2"
    elif "n" in core:
        poly = "n"
    elif core in ("", "1", "c", "const", "constant", "o1"):
        poly = "1"
    else:
        return "logn" if (has_log and core == "") else None
    if poly == "1":
        return "logn" if has_log else "1"
    if has_log:
        return {"n": "nlogn", "n^2": "n^2logn", "n^3": "n^3logn"}[poly]
    return poly


class AlgorithmComplexityTask(BaseMathTask):
    TASK_TYPE = "algorithm_complexity"
    TASK_TYPES = ["loops", "master_theorem"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"pool": ["n", "logn"]},
        2: {"pool": ["n", "logn"]},
        3: {"pool": ["n", "logn", "n^2"]},
        4: {"pool": ["n", "n^2", "nlogn"]},
        5: {"pool": ["n", "n^2", "nlogn"]},
        6: {"pool": ["n^2", "nlogn", "n^3"]},
        7: {"pool": ["n^2", "nlogn", "n^3"]},
        8: {"pool": ["n^2", "n^3", "nlogn"]},
        9: {"pool": ["n^2", "n^3", "nlogn"]},
        10: {"pool": ["n^2", "n^3", "nlogn"]},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.difficulty = difficulty
        self.pool = list(p["pool"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    # ---- построение ----
    def _build(self):
        if self.task_type == "loops":
            self.answer = random.choice(self.pool)
            self.code = self._make_code(self.answer)
        else:
            self._build_master()

    def _make_code(self, token: str) -> str:
        body = "        work()"
        snippets = {
            "logn": "i = 1\nwhile i < n:\n    i = i * 2\n    work()",
            "n": texts.t('s4', self.language),
            "nlogn": texts.t('s5', self.language),
            "n^2": texts.t('s6', self.language),
            "n^3": texts.t('s7', self.language),
        }
        code = snippets[token]
        # На высоких уровнях иногда добавляем доминируемый последовательный цикл O(n).
        if self.difficulty >= 6 and token in ("n^2", "n^3", "nlogn") and random.random() < 0.5:
            code = texts.t('s8', self.language, code=code)
        return code

    def _build_master(self):
        b = random.choice([2, 3, 4])
        pexp = random.choice([1, 2, 3])          # a = b^pexp  => log_b(a) = pexp
        a = b ** pexp
        d = random.choice([0, 1, 2, 3])
        self.a, self.b, self.d = a, b, d
        self.crit = pexp                          # log_b a
        if pexp > d:
            tok = {1: "n", 2: "n^2", 3: "n^3"}[pexp]
            self.case = 1
        elif pexp == d:
            tok = {1: "nlogn", 2: "n^2logn", 3: "n^3logn"}[pexp]
            self.case = 2
        else:
            tok = {0: "1", 1: "n", 2: "n^2", 3: "n^3"}[d]
            self.case = 3
        self.answer = tok

    def _fn_term(self) -> str:
        return {0: "Θ(1)", 1: "Θ(n)", 2: "Θ(n^2)", 3: "Θ(n^3)"}[self.d]

    # ---- описание ----
    def _descr(self, language):
        if self.task_type == "loops":
            head = ((texts.t('s1', language)))
            return head + "```\n" + self.code + "\n```"
        recur = f"T(n) = {self.a}·T(n/{self.b}) + {self._fn_term()}"
        return ((texts.t('s0', language, recur=recur)))

    # ---- решение / проверка ----
    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        pretty = _PRETTY[self.answer]
        if self.task_type == "loops":
            step = ((texts.t('s2', self.language)))
        else:
            comp = ("<" if self.case == 1 else "=" if self.case == 2 else ">")
            step = ((texts.t('s3', self.language, d=self.d, b=self.b, a=self.a, crit=self.crit, comp=comp, case=self.case)))
        self.solution_steps = [step, ((texts.common('answer_line', self.language, answer=pretty)))]
        self.final_answer = pretty

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        c = canon_complexity(prediction)
        return 1.0 if c is not None and c == self.answer else 0.0

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
