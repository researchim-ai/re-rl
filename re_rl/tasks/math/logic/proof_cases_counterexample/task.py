"""Universal integer claims solved by exhaustive residues or polynomial identity."""
import random
import re
import math
from typing import Any, ClassVar, Dict
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.math.logic import _logic_utils as U
from .solver import analyse,validate_claim,is_counterexample
texts=TaskTexts(__file__)


class ProofCasesCounterexampleTask(BaseMathTask):
    TASK_TYPE="proof_cases_counterexample"
    TASK_TYPES=["parity_quadratic","divisibility_linear","modular_claim","factorization_form"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"task_type": "parity_quadratic", "truth_bias": 0.8},
        2: {"task_type": "parity_quadratic", "truth_bias": 0.7},
        3: {"task_type": "divisibility_linear", "truth_bias": 0.7},
        4: {"task_type": "divisibility_linear", "truth_bias": 0.6},
        5: {"task_type": "modular_claim", "truth_bias": 0.5},
        6: {"task_type": "modular_claim", "truth_bias": 0.5},
        7: {"task_type": "factorization_form", "truth_bias": 0.5},
        8: {"task_type": "factorization_form", "truth_bias": 0.4},
        9: {"task_type": "mixed", "truth_bias": 0.5},
        10: {"task_type": "mixed", "truth_bias": 0.5},
    }

    def __init__(self, task_type=None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat="text", reasoning_mode=False, augment=True,
                 truth_bias=None, coefficients=None, modulus=None, shift=1):
        preset=self._interpolate_difficulty(difficulty)
        self.task_type=preset["task_type"] if task_type is None else task_type
        if self.task_type not in self.TASK_TYPES+["mixed"]:raise ValueError("invalid_task_type")
        self.truth_bias=preset["truth_bias"] if truth_bias is None else truth_bias
        if isinstance(self.truth_bias,bool) or not isinstance(self.truth_bias,(int,float)) or not math.isfinite(self.truth_bias) or not 0 <= self.truth_bias <= 1:
            raise ValueError("invalid_truth_bias")
        if type(shift) is not int or not 1 <= shift <= 1000:raise ValueError("invalid_shift")
        self.augment=augment
        mode=random.choice(self.TASK_TYPES) if self.task_type=="mixed" else self.task_type
        true_case=random.random()<self.truth_bias
        if mode=="factorization_form":
            if coefficients is not None or modulus is not None:raise ValueError("incompatible_parameters")
            self.claim=dict(kind="identity",shift=shift,linear=2*shift,constant=shift**2+(0 if true_case else 1))
            claim_text=texts.t("identity",language,**self.claim)
        else:
            if mode=="parity_quadratic":
                coeff=[0 if true_case else 1,1,1];m=2;premise=1;residues=[0]
            elif mode=="divisibility_linear":
                coeff=[0,-1,0,1] if true_case else [0,1,1];m=3 if true_case else 4;premise=1;residues=[0]
            else:
                coeff=[0,0,1];m=2 if true_case else 8;premise=2;residues=[1]
                # The legacy true claim is odd -> odd: n²-1 is divisible by 2.
                if true_case:coeff[0]=-1
            self.claim=dict(kind="divisible",coefficients=list(coefficients) if coefficients is not None else coeff,
                            modulus=m if modulus is None else modulus,premise_modulus=premise,premise_residues=residues)
            validate_claim(self.claim)
            polynomial=" + ".join(f"({c})*n^{i}" for i,c in enumerate(self.claim["coefficients"]) if c) or "0"
            claim_text=texts.t("divisible",language,polynomial=polynomial,**self.claim)
        validate_claim(self.claim)
        description=texts.t("problem",language,claim=claim_text)
        super().__init__(description,language=language,detail_level=detail_level,
                         output_format=output_format,reasoning_mode=reasoning_mode)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solve()

    def verify(self, prediction):
        text=U.clean(prediction).strip()
        if text.upper()=="TRUE":return float(analyse(self.claim,[])[0])
        match=re.fullmatch(r"FALSE\s*;\s*n\s*=\s*([+-]?\d+)",text,re.IGNORECASE)
        if not match:return 0.0
        validate_claim(self.claim)
        return float(is_counterexample(self.claim,int(match.group(1))))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task=cls(language=language,detail_level=detail_level,difficulty=difficulty,
                 reasoning_mode=reasoning_mode,augment=augment,**kwargs)
        task.solve()
        return task
