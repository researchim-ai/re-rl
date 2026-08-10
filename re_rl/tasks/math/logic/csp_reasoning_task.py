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
        self._kakuro_sums: Dict[str, int] = {}
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

    def _regenerate_solvable_latin(self, max_attempts: int = 20) -> List[List[int]]:
        """Генерирует латинский квадрат, гарантированно решаемый z3."""
        for _ in range(max_attempts):
            self._solution_grid = self._generate_latin_solution()
            self._puzzle_grid = self._latin_puzzle_from_solution(self._solution_grid)
            solved = self._solve_latin_square(self._puzzle_grid)
            if solved:
                return solved
        # Fallback: сам сгенерированный солюшн заведомо валиден.
        return self._solution_grid

    def solve(self):
        section = PROMPT_TEMPLATES["csp_reasoning"]
        if self.task_type == "kakuro_mini":
            sums = self._build_kakuro_instance()
            self._kakuro_sums = sums
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
            if not sol:
                # Инстанс невыполним — перегенерируем заведомо решаемый.
                while not sol:
                    sums = self._build_kakuro_instance()
                    sol = self._solve_kakuro(sums)
                self._kakuro_sums = sums
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
            self.solution_steps.append(
                get_template(section, "kakuro_step_result", self.language, augment=False).format(
                    a=sol["A"], b=sol["B"], c=sol["C"], d=sol["D"]
                )
            )
            self.final_answer = f"A={sol['A']},B={sol['B']},C={sol['C']},D={sol['D']}"
            return

        solved = self._regenerate_solvable_latin()
        self.description = get_template(
            section,
            "latin_problem",
            self.language,
            augment=self.augment,
            size=self.size,
            grid=self._format_grid(self._puzzle_grid),
        )
        self.solution_steps.append(get_template(section, "latin_step_constraints", self.language, augment=False))
        self.solution_steps.append(
            get_template(section, "latin_step_solution", self.language, augment=False).format(grid=self._format_grid(solved))
        )
        self.final_answer = ";".join(",".join(str(v) for v in row) for row in solved)

    def _is_valid_latin(self, grid: List[List[int]]) -> bool:
        """Проверяет, что grid — валидное решение (совместимо с clues)."""
        n = self.size
        if len(grid) != n or any(len(row) != n for row in grid):
            return False
        expected = set(range(1, n + 1))
        for row in grid:
            if set(row) != expected:
                return False
        for c in range(n):
            if set(grid[r][c] for r in range(n)) != expected:
                return False
        # Совместимость с заданными подсказками (clues).
        for r in range(n):
            for c in range(n):
                if self._puzzle_grid[r][c] != 0 and grid[r][c] != self._puzzle_grid[r][c]:
                    return False
        return True

    def verify(self, prediction: str) -> float:
        """Проверяет валидность решения (у латинского квадрата решений может быть несколько)."""
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()

        _, answer = extract_reasoning_and_answer(prediction)
        text = answer or prediction

        if self.task_type == "latin_square":
            import re as _re
            # Ответ может быть в виде строк (через \n) или через ';' (r1;r2;r3).
            rows = [r for r in _re.split(r"[;\n]", text.strip()) if r.strip()]
            grid: List[List[int]] = []
            for row in rows:
                nums = [int(x) for x in _re.findall(r"\d+", row)]
                if nums:
                    grid.append(nums)
            return 1.0 if self._is_valid_latin(grid) else 0.0

        # kakuro_mini: проверяем, что найденные значения удовлетворяют суммам.
        import re as _re
        pairs = dict(_re.findall(r"([ABCD])\s*=\s*(\d+)", text.upper()))
        if not all(k in pairs for k in ("A", "B", "C", "D")):
            return 0.0
        a, b, c, d = (int(pairs["A"]), int(pairs["B"]), int(pairs["C"]), int(pairs["D"]))
        s = self._kakuro_sums
        if not s:
            return 1.0 if str(self.final_answer).strip() == text.strip() else 0.0
        ok = (
            1 <= a <= 9 and 1 <= b <= 9 and 1 <= c <= 9 and 1 <= d <= 9
            and a != b and c != d
            and a + b == s["S1"] and c + d == s["S2"]
            and a + c == s["S3"] and b + d == s["S4"]
        )
        return 1.0 if ok else 0.0

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
