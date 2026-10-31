"""Stable Boolean CNF tasks, witnessed generation and deterministic DPLL."""
import random
import re
from typing import Any, ClassVar, Dict
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template
from re_rl.tasks.math.logic import _logic_utils as U
from .solver import dpll, validate_cnf


class SATSMTMiniTask(BaseMathTask):
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

    def __init__(self, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat="text", reasoning_mode=False, augment=True,
                 num_vars=None, num_clauses=None, target=None):
        preset=self._interpolate_difficulty(difficulty)
        self.num_vars=preset["num_vars"] if num_vars is None else num_vars
        self.num_clauses=preset["num_clauses"] if num_clauses is None else num_clauses
        self.target=preset["target"] if target is None else target
        if type(self.num_vars) is not int or not 1 <= self.num_vars <= 64:
            raise ValueError("invalid_num_vars")
        if type(self.num_clauses) is not int or not 0 <= self.num_clauses <= 256:
            raise ValueError("invalid_num_clauses")
        if self.target not in ("sat","unsat","mixed"):
            raise ValueError("invalid_target")
        if self.target == "unsat" and self.num_clauses < 2:
            raise ValueError("insufficient_clauses_for_unsat")
        self.augment=augment
        self._cnf=self._build_cnf()
        # Mathematical symbols avoid embedding language-specific operators in code.
        formula=" ∧ ".join("("+" ∨ ".join(("" if positive else "¬")+f"x{i+1}" for i,positive in clause)+")" for clause in self._cnf) or "⊤"
        description=get_template(PROMPT_TEMPLATES[self.TASK_TYPE],"problem",language,
                                 augment=augment,formula=formula,num_vars=self.num_vars)
        super().__init__(description,language=language,detail_level=detail_level,
                         output_format=output_format,reasoning_mode=reasoning_mode)

    def _build_cnf(self):
        unsat=self.target == "unsat" or (self.target == "mixed" and self.num_clauses >= 2 and random.random()<0.5)
        witness=[bool(random.getrandbits(1)) for _ in range(self.num_vars)]
        cnf=[]
        if unsat:
            # A forced implication chain, not a contradictory pair at every level.
            length=min(self.num_vars,self.num_clauses-1)
            chain=random.sample(range(self.num_vars),length)
            cnf.append([(chain[0],witness[chain[0]])])
            for previous,current in zip(chain,chain[1:]):
                cnf.append([(previous,not witness[previous]),(current,witness[current])])
            cnf.append([(chain[-1],not witness[chain[-1]])])
        for _ in range(self.num_clauses-len(cnf)):
            variables=random.sample(range(self.num_vars),random.randint(1,min(3,self.num_vars)))
            clause=[(i,bool(random.getrandbits(1))) for i in variables]
            if not any(witness[i]==positive for i,positive in clause):
                i,_=clause[0];clause[0]=(i,witness[i])
            cnf.append(clause)
        return cnf

    def _solve_cnf(self, cnf):
        model=dpll(self.num_vars,cnf,[])
        return model is not None, {} if model is None else {f"x{i+1}":bool(v) for i,v in enumerate(model)}

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solve()

    def verify(self, prediction):
        text=U.clean(prediction).strip()
        validate_cnf(self.num_vars,self._cnf)
        if text.upper()=="UNSAT":
            return float(dpll(self.num_vars,self._cnf,[]) is None)
        match=re.fullmatch(r"SAT\s*:\s*(.*)",text,re.IGNORECASE)
        if not match:return 0.0
        body=match.group(1)
        if not re.fullmatch(r"x[1-9]\d*\s*=\s*(?:true|false|0|1)(?:\s*,\s*x[1-9]\d*\s*=\s*(?:true|false|0|1))*",body,re.IGNORECASE):return 0.0
        pairs=re.findall(r"x([1-9]\d*)\s*=\s*(true|false|0|1)",body,re.IGNORECASE)
        if len(pairs)!=self.num_vars or {int(i) for i,v in pairs}!=set(range(1,self.num_vars+1)):return 0.0
        assignment={int(i)-1:v.lower() in ("true","1") for i,v in pairs}
        return float(all(any(assignment[i]==positive for i,positive in clause) for clause in self._cnf))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task=cls(language=language,detail_level=detail_level,difficulty=difficulty,
                 reasoning_mode=reasoning_mode,augment=augment,**kwargs)
        task.solve()
        return task
