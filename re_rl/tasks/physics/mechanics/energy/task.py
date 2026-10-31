"""Explicit ideal Newtonian models with signed values and executable balances."""
import random
from typing import Any,ClassVar,Dict
from re_rl.tasks.base_task import BaseMathTask,OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.mechanical_models import validate,solve_task,verify_task
texts=TaskTexts(__file__)


class EnergyTask(BaseMathTask):
    TASK_TYPE="energy"
    TASK_TYPES=["work","work_angle","kinetic_energy","potential_energy","power","conservation"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_F": 50, "max_s": 20, "max_m": 10, "max_v": 10, "max_h": 10},
        2: {"max_F": 100, "max_s": 50, "max_m": 20, "max_v": 20, "max_h": 20},
        3: {"max_F": 200, "max_s": 100, "max_m": 30, "max_v": 30, "max_h": 30},
        4: {"max_F": 300, "max_s": 150, "max_m": 50, "max_v": 40, "max_h": 50},
        5: {"max_F": 500, "max_s": 200, "max_m": 50, "max_v": 50, "max_h": 50},
        6: {"max_F": 500, "max_s": 300, "max_m": 100, "max_v": 60, "max_h": 100},
        7: {"max_F": 1000, "max_s": 500, "max_m": 100, "max_v": 80, "max_h": 100},
        8: {"max_F": 1000, "max_s": 500, "max_m": 200, "max_v": 100, "max_h": 200},
        9: {"max_F": 2000, "max_s": 1000, "max_m": 200, "max_v": 150, "max_h": 200},
        10: {"max_F": 5000, "max_s": 1000, "max_m": 500, "max_v": 200, "max_h": 500},
    }
    
    def __init__(self,task_type="work",F=None,s=None,angle=None,m=None,v=None,h=None,W=None,t=None,
                 language="ru",detail_level=3,difficulty=5,output_format: OutputFormat="text",
                 reasoning_mode=False,g=None,v0=None,**kwargs):
        self.task_type=task_type.lower() if isinstance(task_type,str) else "work" if task_type is None else task_type
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        self.difficulty=difficulty;p=self._interpolate_difficulty(difficulty)
        if self.task_type in ("work","work_angle"):
            self.F=F if F is not None else random.randint(10,p["max_F"])
            self.s=s if s is not None else random.randint(5,p["max_s"])
            inputs=dict(F=self.F,s=self.s)
            if self.task_type=="work_angle":
                self.angle=angle if angle is not None else random.choice([0,30,45,60,90,120,150,180])
                inputs['angle']=self.angle
        elif self.task_type=="power":
            self.W=W if W is not None else random.randint(100,10000)
            self.t=t if t is not None else random.randint(1,60)
            inputs=dict(W=self.W,t=self.t)
        else:
            self.m=m if m is not None else random.randint(1,p["max_m"])
            if self.task_type=="kinetic_energy":
                self.v=v if v is not None else random.randint(-p["max_v"],p["max_v"])
                inputs=dict(m=self.m,v=self.v)
            else:
                self.g=get_constant("g") if g is None else g
                self.h=h if h is not None else random.randint(5,p["max_h"])
                inputs=dict(m=self.m,g=self.g,h=self.h)
                if self.task_type=="conservation":
                    self.v0=0 if v0 is None else v0
                    inputs['v0']=self.v0
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
