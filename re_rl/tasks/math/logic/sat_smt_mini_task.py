import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from z3 import Bool, Not, Or, Solver, sat

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class SATSMTMiniTask(BaseMathTask):
    """Mini SAT/SMT proofs: satisfiable/unsatisfiable with witness or contradiction."""

    TASK_TYPE = "sat_smt_mini"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_vars": 2, "num_clauses": 2, "target": "sat"},
        2: {"num_vars": 2, "num_clauses": 3, "target": "sat"},
        3: {"num_vars": 3, "num_clauses": 3, "target": "sat"},
        4: {"num_vars": 3, "num_clauses": 4, "target": "mixed"},
        5: {"num_vars": 4, "num_clauses": 5, "target": "mixed"},
        6: {"num_vars": 4, "num_clauses": 6, "target": "mixed"},
        7: {"num_vars": 5, "num_clauses": 7, "target": "mixed"},
        8: {"num_vars": 5, "num_clauses": 8, "target": "unsat"},
        9: {"num_vars": 6, "num_clauses": 9, "target": "unsat"},
        10: {"num_vars": 6, "num_clauses": 10, "target": "unsat"},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_vars: Optional[int] = None,
        num_clauses: Optional[int] = None,
        target: Optional[str] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_vars = num_vars if num_vars is not None else int(preset.get("num_vars", 4))
        self.num_clauses = num_clauses if num_clauses is not None else int(preset.get("num_clauses", 5))
        self.target = target or str(preset.get("target", "mixed"))
        self.augment = augment
        self._cnf: List[List[Tuple[int, bool]]] = []
        super().__init__("", language=language, detail_level=detail_level, output_format=output_format, reasoning_mode=reasoning_mode)

    def _build_cnf(self) -> List[List[Tuple[int, bool]]]:
        cnf: List[List[Tuple[int, bool]]] = []
        for _ in range(self.num_clauses):
            k = random.randint(2, min(3, self.num_vars))
            vars_idx = random.sample(range(self.num_vars), k=k)
            clause = [(idx, bool(random.getrandbits(1))) for idx in vars_idx]
            cnf.append(clause)
        if self.target == "unsat" or (self.target == "mixed" and random.random() < 0.5):
            idx = random.randrange(self.num_vars)
            cnf.append([(idx, True)])
            cnf.append([(idx, False)])
        return cnf

    def _clause_to_text(self, clause: List[Tuple[int, bool]]) -> str:
        parts = []
        for idx, is_pos in clause:
            var_name = f"x{idx + 1}"
            parts.append(var_name if is_pos else f"not {var_name}")
        return "(" + " OR ".join(parts) + ")"

    def _solve_cnf(self, cnf: List[List[Tuple[int, bool]]]) -> Tuple[bool, Dict[str, bool]]:
        vars_z3 = [Bool(f"x{i + 1}") for i in range(self.num_vars)]
        solver = Solver()
        for clause in cnf:
            lits = []
            for idx, is_pos in clause:
                lit = vars_z3[idx] if is_pos else Not(vars_z3[idx])
                lits.append(lit)
            solver.add(Or(*lits))
        if solver.check() != sat:
            return False, {}
        model = solver.model()
        assignment = {f"x{i + 1}": bool(model.eval(vars_z3[i], model_completion=True)) for i in range(self.num_vars)}
        return True, assignment

    def solve(self):
        section = PROMPT_TEMPLATES["sat_smt_mini"]
        self._cnf = self._build_cnf()
        cnf_text = " AND ".join(self._clause_to_text(cl) for cl in self._cnf)
        self.description = get_template(section, "problem", self.language, augment=self.augment, formula=cnf_text)
        self.solution_steps.append(get_template(section, "step_encode", self.language, augment=False))
        is_sat, assignment = self._solve_cnf(self._cnf)
        if is_sat:
            assign_str = ",".join(f"{k}={str(v)}" for k, v in sorted(assignment.items()))
            self.solution_steps.append(get_template(section, "step_sat", self.language, augment=False).format(assignment=assign_str))
            self.final_answer = f"SAT:{assign_str}"
        else:
            self.solution_steps.append(get_template(section, "step_unsat", self.language, augment=False))
            self.final_answer = "UNSAT"

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "SATSMTMiniTask":
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
