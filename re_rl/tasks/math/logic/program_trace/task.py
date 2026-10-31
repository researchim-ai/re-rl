"""Трассировка выполнения мини-программы (присваивания, циклы, условия) над
целочисленными переменными. Нужно выдать финальное значение переменной."""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _safe_eval(expr: str, env: Dict[str, int]) -> int:
    return int(eval(expr, {"__builtins__": {}}, dict(env)))


class ProgramTraceTask(BaseMathTask):
    TASK_TYPE = "program_trace"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"nvars": 2, "stmts": 3, "loops": 0}, 2: {"nvars": 2, "stmts": 4, "loops": 1},
        3: {"nvars": 3, "stmts": 4, "loops": 1}, 4: {"nvars": 3, "stmts": 5, "loops": 1},
        5: {"nvars": 3, "stmts": 6, "loops": 2}, 6: {"nvars": 3, "stmts": 7, "loops": 2},
        7: {"nvars": 4, "stmts": 8, "loops": 2}, 8: {"nvars": 4, "stmts": 9, "loops": 3},
        9: {"nvars": 4, "stmts": 10, "loops": 3}, 10: {"nvars": 4, "stmts": 12, "loops": 3},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.nvars = int(p["nvars"])
        self.nstmts = int(p["stmts"])
        self.nloops = int(p["loops"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _rand_expr(self, allow_mul=True):
        v = random.choice(self.vars)
        op = random.choice(["+", "-", "*"] if allow_mul else ["+", "-"])
        if op == "*":
            return f"{v} * {random.randint(2, 3)}"
        return f"{v} {op} {random.randint(1, 4)}"

    def _gen_block(self, depth):
        body = []
        for _ in range(random.randint(1, 2)):
            v = random.choice(self.vars)
            body.append(("assign", v, f"{v} {random.choice(['+', '-'])} {random.randint(1, 3)}"))
        return body

    def _build(self):
        self.vars = ["a", "b", "c", "d"][:self.nvars]
        self.prog: List[tuple] = []
        for v in self.vars:  # инициализация
            self.prog.append(("assign", v, str(random.randint(0, 5))))
        loops_left = self.nloops
        for _ in range(self.nstmts):
            kind = random.random()
            if loops_left > 0 and kind < 0.4:
                loops_left -= 1
                self.prog.append(("loop", random.randint(2, 5), self._gen_block(1)))
            elif kind < 0.65:
                v = random.choice(self.vars)
                cond = f"{v} {random.choice(['>', '<', '=='])} {random.randint(0, 6)}"
                self.prog.append(("if", cond, self._gen_block(1)))
            else:
                v = random.choice(self.vars)
                self.prog.append(("assign", v, self._rand_expr()))
        self.query = random.choice(self.vars)
        self._answer = self._run()

    def _run(self):
        env = {v: 0 for v in self.vars}

        def exec_block(block):
            for st in block:
                if st[0] == "assign":
                    env[st[1]] = _safe_eval(st[2], env)
                elif st[0] == "loop":
                    for _ in range(st[1]):
                        exec_block(st[2])
                elif st[0] == "if":
                    if _safe_eval(st[1], env):
                        exec_block(st[2])

        exec_block(self.prog)
        return env[self.query]

    def _render(self, block, indent=0):
        pad = "    " * indent
        lines = []
        for st in block:
            if st[0] == "assign":
                lines.append(f"{pad}{st[1]} = {st[2]}")
            elif st[0] == "loop":
                lines.append(texts.t('s6', self.language, pad=pad, v1=st[1]))
                lines.extend(self._render(st[2], indent + 1))
            elif st[0] == "if":
                lines.append(texts.t('s7', self.language, pad=pad, v1=st[1]))
                lines.extend(self._render(st[2], indent + 1))
        return lines

    def _descr(self, language):
        code = "\n".join(self._render(self.prog))
        if {"ru": True, "en": False}.get(language, False):
            return (texts.t('s3', language, code=code, query=self.query))
        code_en = code.replace(texts.t('s8', language), "repeat").replace(texts.t('s5', language), " times:").replace(texts.t('s4', language), "if")
        return (texts.t('s2', language, code_en=code_en, query=self.query))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = [
            ((texts.t('s0', self.language))),
            ((texts.t('s1', self.language, query=self.query, _answer=self._answer))),
        ]
        self.final_answer = str(self._answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self._answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
