"""Трассировка выполнения мини-программы (присваивания, циклы, условия) над
целочисленными переменными. Нужно выдать финальное значение переменной."""

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
                lines.append(f"{pad}повторить {st[1]} раз:")
                lines.extend(self._render(st[2], indent + 1))
            elif st[0] == "if":
                lines.append(f"{pad}если {st[1]}:")
                lines.extend(self._render(st[2], indent + 1))
        return lines

    def _descr(self, language):
        ru = language == "ru"
        code = "\n".join(self._render(self.prog))
        if ru:
            return (f"Выполните программу (все переменные целые, изначально 0; «==» — сравнение на "
                    f"равенство):\n\n{code}\n\nКакое значение будет у переменной {self.query} в конце?")
        code_en = code.replace("повторить", "repeat").replace(" раз:", " times:").replace("если", "if")
        return (f"Execute the program (all variables are integers, initially 0; '==' is equality):\n\n"
                f"{code_en}\n\nWhat is the final value of variable {self.query}?")

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Выполняем инструкции по порядку, обновляя значения переменных." if ru else
             "Execute the statements in order, updating variable values."),
            (f"Итоговое значение {self.query} = {self._answer}." if ru else
             f"Final value of {self.query} = {self._answer}."),
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
