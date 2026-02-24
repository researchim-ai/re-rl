import random
from typing import Any, ClassVar, Dict, List, Optional

from z3 import Distinct, Int, Solver, sat

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class CSPReasoningTask(BaseMathTask):
    """Constraint Satisfaction tasks: latin square and mini kakuro."""

    TASK_TYPE = "csp_reasoning"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"size": 3, "clues": 5, "task_type": "latin_square"},
        2: {"size": 3, "clues": 4, "task_type": "latin_square"},
        3: {"size": 4, "clues": 7, "task_type": "latin_square"},
        4: {"size": 4, "clues": 6, "task_type": "latin_square"},
        5: {"size": 4, "clues": 5, "task_type": "latin_square"},
        6: {"size": 4, "clues": 4, "task_type": "latin_square"},
        7: {"size": 3, "clues": 0, "task_type": "kakuro_mini"},
        8: {"size": 3, "clues": 0, "task_type": "kakuro_mini"},
        9: {"size": 3, "clues": 0, "task_type": "kakuro_mini"},
        10: {"size": 3, "clues": 0, "task_type": "kakuro_mini"},
    }

    def __init__(
        self,
        task_type: Optional[str] = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        size: Optional[int] = None,
        clues: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.task_type = task_type or preset.get("task_type", "latin_square")
        self.size = size if size is not None else int(preset.get("size", 4))
        self.clues = clues if clues is not None else int(preset.get("clues", 5))
        self.augment = augment
        self._solution_grid: List[List[int]] = []
        self._puzzle_grid: List[List[int]] = []
        super().__init__(
            description="",
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    def _generate_latin_solution(self) -> List[List[int]]:
        base = [[(r + c) % self.size + 1 for c in range(self.size)] for r in range(self.size)]
        random.shuffle(base)
        return base

    def _latin_puzzle_from_solution(self, solution: List[List[int]]) -> List[List[int]]:
        puzzle = [row[:] for row in solution]
        all_cells = [(r, c) for r in range(self.size) for c in range(self.size)]
        random.shuffle(all_cells)
        to_remove = max(0, self.size * self.size - self.clues)
        for r, c in all_cells[:to_remove]:
            puzzle[r][c] = 0
        return puzzle

    def _format_grid(self, grid: List[List[int]]) -> str:
        return "\n".join(" ".join(str(v) if v != 0 else "." for v in row) for row in grid)

    def _solve_latin_square(self, puzzle: List[List[int]]) -> List[List[int]]:
        solver = Solver()
        x = [[Int(f"x_{r}_{c}") for c in range(self.size)] for r in range(self.size)]
        for r in range(self.size):
            for c in range(self.size):
                solver.add(x[r][c] >= 1, x[r][c] <= self.size)
                if puzzle[r][c] != 0:
                    solver.add(x[r][c] == puzzle[r][c])
            solver.add(Distinct(*x[r]))
        for c in range(self.size):
            solver.add(Distinct(*[x[r][c] for r in range(self.size)]))
        if solver.check() != sat:
            return []
        model = solver.model()
        return [[model[x[r][c]].as_long() for c in range(self.size)] for r in range(self.size)]

    def _build_kakuro_instance(self) -> Dict[str, int]:
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        while b == a:
            b = random.randint(1, 9)
        c = random.randint(1, 9)
        d = random.randint(1, 9)
        while d == c:
            d = random.randint(1, 9)
        return {"A": a, "B": b, "C": c, "D": d, "S1": a + b, "S2": c + d, "S3": a + c, "S4": b + d}

    def _solve_kakuro(self, sums: Dict[str, int]) -> Dict[str, int]:
        solver = Solver()
        a = Int("a")
        b = Int("b")
        c = Int("c")
        d = Int("d")
        for v in [a, b, c, d]:
            solver.add(v >= 1, v <= 9)
        solver.add(Distinct(a, b))
        solver.add(Distinct(c, d))
        solver.add(a + b == sums["S1"])
        solver.add(c + d == sums["S2"])
        solver.add(a + c == sums["S3"])
        solver.add(b + d == sums["S4"])
        if solver.check() != sat:
            return {}
        model = solver.model()
        return {"A": model[a].as_long(), "B": model[b].as_long(), "C": model[c].as_long(), "D": model[d].as_long()}

    def solve(self):
        section = PROMPT_TEMPLATES["csp_reasoning"]
        if self.task_type == "kakuro_mini":
            sums = self._build_kakuro_instance()
            self.description = get_template(
                section,
                "kakuro_problem",
                self.language,
                augment=self.augment,
                s1=sums["S1"],
                s2=sums["S2"],
                s3=sums["S3"],
                s4=sums["S4"],
            )
            self.solution_steps.append(get_template(section, "kakuro_step_model", self.language, augment=False))
            sol = self._solve_kakuro(sums)
            self.solution_steps.append(
                get_template(section, "kakuro_step_result", self.language, augment=False).format(
                    a=sol["A"], b=sol["B"], c=sol["C"], d=sol["D"]
                )
            )
            self.final_answer = f"A={sol['A']},B={sol['B']},C={sol['C']},D={sol['D']}"
            return

        self._solution_grid = self._generate_latin_solution()
        self._puzzle_grid = self._latin_puzzle_from_solution(self._solution_grid)
        self.description = get_template(
            section,
            "latin_problem",
            self.language,
            augment=self.augment,
            size=self.size,
            grid=self._format_grid(self._puzzle_grid),
        )
        self.solution_steps.append(get_template(section, "latin_step_constraints", self.language, augment=False))
        solved = self._solve_latin_square(self._puzzle_grid)
        self.solution_steps.append(
            get_template(section, "latin_step_solution", self.language, augment=False).format(grid=self._format_grid(solved))
        )
        self.final_answer = ";".join(",".join(str(v) for v in row) for row in solved)

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "CSPReasoningTask":
        task = cls(
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode,
            augment=augment,
            **kwargs,
        )
        task.solve()
        return task
