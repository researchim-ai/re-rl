"""Ideal oscillation models, complete requested outputs and dimensioned execution traces."""
import random
import math
from typing import Any,ClassVar,Dict
from fractions import Fraction
from re_rl.tasks.base_task import BaseMathTask,OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.spectrum_models import validate,solve_task,verify_task
texts=TaskTexts(__file__)


class OscillationsTask(BaseMathTask):
    TASK_TYPE="oscillations"
    TASK_TYPES=["harmonic","pendulum","spring","lc_circuit","resonance"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_A": 0.1, "max_omega": 10, "max_L": 1, "max_k": 100},
        2: {"max_A": 0.2, "max_omega": 20, "max_L": 2, "max_k": 200},
        3: {"max_A": 0.5, "max_omega": 50, "max_L": 5, "max_k": 500},
        4: {"max_A": 1.0, "max_omega": 100, "max_L": 10, "max_k": 1000},
        5: {"max_A": 2.0, "max_omega": 200, "max_L": 20, "max_k": 2000},
        6: {"max_A": 5.0, "max_omega": 500, "max_L": 50, "max_k": 5000},
        7: {"max_A": 10.0, "max_omega": 1000, "max_L": 100, "max_k": 10000},
        8: {"max_A": 20.0, "max_omega": 2000, "max_L": 200, "max_k": 20000},
        9: {"max_A": 50.0, "max_omega": 5000, "max_L": 500, "max_k": 50000},
        10: {"max_A": 100.0, "max_omega": 10000, "max_L": 1000, "max_k": 100000},
    }
    
    def __init__(self,task_type="pendulum",A=None,omega=None,phi=None,L=None,m=None,k=None,C=None,L_ind=None,
                 language="ru",detail_level=3,difficulty=5,output_format: OutputFormat="text",
                 reasoning_mode=False,g=None,**kwargs):
        self.task_type=task_type.lower() if isinstance(task_type,str) else "pendulum" if task_type is None else task_type
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        self.difficulty=difficulty;p=self._interpolate_difficulty(difficulty)
        if self.task_type=="harmonic":
            self.A=A if A is not None else round(random.uniform(0.01,p["max_A"]),3)
            self.omega=omega if omega is not None else round(random.uniform(1,p["max_omega"]),2)
            self.phi=phi if phi is not None else random.choice([0,math.pi/6,math.pi/4,math.pi/3,math.pi/2])
            inputs=dict(A=self.A,omega=self.omega,phi=self.phi)
        elif self.task_type=="pendulum":
            self.L=L if L is not None else round(random.uniform(0.1,p["max_L"]),2)
            self.g=get_constant("g") if g is None else g
            inputs=dict(L=self.L,g=self.g)
        elif self.task_type=="spring":
            self.m=m if m is not None else round(random.uniform(0.1,10),2)
            self.k=k if k is not None else round(random.uniform(10,p["max_k"]),1)
            inputs=dict(m=self.m,k=self.k)
        else:
            self.C=C if C is not None else Fraction(random.randint(1,max(1,int(p["max_L"]*10))),10**9)
            self.L_ind=L_ind if L_ind is not None else Fraction(random.randint(1,max(1,int(p["max_L"]*10))),1000)
            inputs=dict(C=self.C,L_ind=self.L_ind)
        validate(self.TASK_TYPE,self.task_type,inputs)
        description=texts.t("problem_"+self.task_type,language,**inputs)
        super().__init__(description,language,detail_level,output_format,reasoning_mode)

    def solve(self):return solve_task(self)
    def _solve_before_trace(self):self.solve()
    def verify(self,prediction):return verify_task(self,prediction)
    def get_task_type(self):return self.TASK_TYPE

    @classmethod
    def generate_random_task(cls,task_type=None,language="ru",detail_level=3,difficulty=5,reasoning_mode=False,**kwargs):
        task=cls(task_type=task_type or random.choice(cls.TASK_TYPES),language=language,detail_level=detail_level,
                 difficulty=difficulty,reasoning_mode=reasoning_mode,**kwargs)
        task.solve();return task
