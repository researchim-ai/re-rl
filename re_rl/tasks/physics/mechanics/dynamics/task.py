"""Explicit ideal Newtonian models with signed values and executable balances."""
import random
from typing import Any,ClassVar,Dict
from re_rl.tasks.base_task import BaseMathTask,OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.mechanical_models import validate,solve_task,verify_task
texts=TaskTexts(__file__)


class DynamicsTask(BaseMathTask):
    TASK_TYPE="dynamics"
    TASK_TYPES=["newton_second","find_force","weight","friction","inclined_plane","tension"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_m": 10, "max_F": 50, "max_a": 5},
        2: {"max_m": 20, "max_F": 100, "max_a": 10},
        3: {"max_m": 30, "max_F": 200, "max_a": 10},
        4: {"max_m": 50, "max_F": 300, "max_a": 15},
        5: {"max_m": 50, "max_F": 500, "max_a": 15},
        6: {"max_m": 100, "max_F": 500, "max_a": 20},
        7: {"max_m": 100, "max_F": 1000, "max_a": 20},
        8: {"max_m": 200, "max_F": 1000, "max_a": 25},
        9: {"max_m": 200, "max_F": 2000, "max_a": 25},
        10: {"max_m": 500, "max_F": 5000, "max_a": 30},
    }
    
    def __init__(self,task_type="newton_second",m=None,m1=None,m2=None,F=None,a=None,mu=None,angle=None,
                 language="ru",detail_level=3,difficulty=5,output_format: OutputFormat="text",
                 reasoning_mode=False,g=None,**kwargs):
        self.task_type=task_type.lower() if isinstance(task_type,str) else "newton_second" if task_type is None else task_type
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        self.difficulty=difficulty;p=self._interpolate_difficulty(difficulty)
        if self.task_type=="tension":
            self.m1=m1 if m1 is not None else random.randint(1,p["max_m"])
            self.m2=m2 if m2 is not None else random.randint(1,p["max_m"])
            self.g=get_constant("g") if g is None else g
            inputs=dict(m1=self.m1,m2=self.m2,g=self.g)
        else:
            self.m=m if m is not None else random.randint(1,p["max_m"])
            inputs=dict(m=self.m)
            if self.task_type=="newton_second":
                self.F=F if F is not None else random.randint(-p["max_F"],p["max_F"])
                inputs['F']=self.F
            elif self.task_type=="find_force":
                self.a=a if a is not None else random.randint(-p["max_a"],p["max_a"])
                inputs['a']=self.a
            else:
                self.g=get_constant("g") if g is None else g
                inputs['g']=self.g
                if self.task_type=="friction":
                    self.mu=mu if mu is not None else round(random.uniform(0.1,0.5),2)
                    inputs['mu']=self.mu
                elif self.task_type=="inclined_plane":
                    self.angle=angle if angle is not None else random.choice([0,15,30,45,60,90])
                    inputs['angle']=self.angle
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
