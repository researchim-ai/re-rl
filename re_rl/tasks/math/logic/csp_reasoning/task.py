"""Stable finite-domain instances; generation never occurs during solve."""
import random
import re
from typing import Any, ClassVar, Dict
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template
from re_rl.tasks.math.logic import _logic_utils as U


class CSPReasoningTask(BaseMathTask):
    TASK_TYPE = "csp_reasoning"
    TASK_TYPES = ["latin_square", "kakuro_mini"]

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

    def __init__(self, task_type=None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat="text", reasoning_mode=False, augment=True,
                 size=None, clues=None):
        preset = self._interpolate_difficulty(difficulty)
        self.task_type = task_type or preset["task_type"]
        if self.task_type not in self.TASK_TYPES:
            raise ValueError("invalid_task_type")
        self.augment = augment
        self.size = size if size is not None else (2 if self.task_type == "kakuro_mini" else preset["size"])
        self.clues = clues if clues is not None else (0 if self.task_type == "kakuro_mini" else preset["clues"])
        if type(self.size) is not int or not 2 <= self.size <= 9:
            raise ValueError("invalid_size")
        if type(self.clues) is not int or not 0 <= self.clues <= self.size**2:
            raise ValueError("invalid_clues")
        if self.task_type == "kakuro_mini" and (self.size != 2 or self.clues != 0):
            raise ValueError("fixed_kakuro_shape")
        self._puzzle_grid = []
        self._kakuro_sums = {}
        self._solution_grid = []
        section = PROMPT_TEMPLATES["csp_reasoning"]
        if self.task_type == "latin_square":
            self._solution_grid = [[(r+c)%self.size+1 for c in range(self.size)] for r in range(self.size)]
            random.shuffle(self._solution_grid)
            positions = set(random.sample(range(self.size**2),self.clues))
            self._puzzle_grid = [[v if r*self.size+c in positions else 0 for c,v in enumerate(row)]
                                 for r,row in enumerate(self._solution_grid)]
            description = get_template(section,"latin_problem",language,augment=augment,
                                       size=self.size,grid=self._format_grid(self._puzzle_grid))
        else:
            a,b = random.sample(range(1,10),2)
            c,d = random.sample(range(1,10),2)
            self._kakuro_sums = dict(S1=a+b,S2=c+d,S3=a+c,S4=b+d)
            description = get_template(section,"kakuro_problem",language,augment=augment,
                                       **{f"s{i}":self._kakuro_sums[f"S{i}"] for i in range(1,5)})
        super().__init__(description=description,language=language,detail_level=detail_level,
                         output_format=output_format,reasoning_mode=reasoning_mode)

    def _format_grid(self, grid):
        return "\n".join(" ".join(str(v) if v else "." for v in row) for row in grid)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        # Compatibility with the reviewed-task harness; there is no legacy cached solution.
        self.solve()

    def _is_valid_latin(self, grid):
        n = self.size
        if len(grid) != n or any(len(row) != n for row in grid):return False
        values = set(range(1,n+1))
        if any(set(row) != values for row in grid):return False
        if any({grid[r][c] for r in range(n)} != values for c in range(n)):return False
        return all(not v or grid[r][c] == v for r,row in enumerate(self._puzzle_grid) for c,v in enumerate(row))

    def verify(self, prediction):
        text = U.clean(prediction).strip()
        if self.task_type == "latin_square":
            rows = text.split(";") if ";" in text else text.splitlines()
            grid = []
            for row in rows:
                if not re.fullmatch(r"\s*\d+(?:[ ,]+\d+)*\s*",row):return 0.0
                grid.append([int(v) for v in re.findall(r"\d+",row)])
            return float(self._is_valid_latin(grid))
        if not re.fullmatch(r"\s*[ABCD]\s*=\s*\d+(?:\s*[,;]\s*[ABCD]\s*=\s*\d+){3}\s*",text.upper()):return 0.0
        pairs = re.findall(r"([ABCD])\s*=\s*(\d+)",text.upper())
        if len({k for k,v in pairs}) != 4:return 0.0
        a,b,c,d = (int(dict(pairs)[k]) for k in "ABCD")
        s = self._kakuro_sums
        return float(all(1 <= v <= 9 for v in (a,b,c,d)) and a != b and c != d
                     and (a+b,c+d,a+c,b+d) == tuple(s[f"S{i}"] for i in range(1,5)))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language,detail_level=detail_level,difficulty=difficulty,
                   reasoning_mode=reasoning_mode,augment=augment,**kwargs)
        task.solve()
        return task
