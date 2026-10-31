"""One-dimensional paths, ideal projectiles and uniform circles with exact inputs."""
import random
from typing import Any,ClassVar,Dict
from re_rl.tasks.base_task import BaseMathTask,OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.conservation_models import number
from re_rl.tasks.physics.trajectory_models import validate,solve_task,verify_task
texts=TaskTexts(__file__)


class KinematicsTask(BaseMathTask):
    TASK_TYPE="kinematics"
    TASK_TYPES=["uniform_motion","find_velocity","accelerated_distance","accelerated_velocity",
                "projectile_max_height","projectile_range","circular_velocity","circular_acceleration"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_v": 10, "max_t": 10, "max_a": 2, "simple": True},
        2: {"max_v": 20, "max_t": 15, "max_a": 3, "simple": True},
        3: {"max_v": 30, "max_t": 20, "max_a": 5, "simple": True},
        4: {"max_v": 50, "max_t": 30, "max_a": 5, "simple": False},
        5: {"max_v": 50, "max_t": 30, "max_a": 10, "simple": False},
        6: {"max_v": 100, "max_t": 60, "max_a": 10, "simple": False},
        7: {"max_v": 100, "max_t": 60, "max_a": 15, "simple": False},
        8: {"max_v": 200, "max_t": 100, "max_a": 15, "simple": False},
        9: {"max_v": 200, "max_t": 100, "max_a": 20, "simple": False},
        10: {"max_v": 300, "max_t": 120, "max_a": 20, "simple": False},
    }
    
    def __init__(self,task_type="uniform_motion",v=None,v0=None,t=None,s=None,a=None,r=None,T=None,angle=None,
                 language="ru",detail_level=3,difficulty=5,output_format: OutputFormat="text",
                 reasoning_mode=False,g=None,**kwargs):
        self.task_type=task_type.lower() if isinstance(task_type,str) else "uniform_motion" if task_type is None else task_type
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        self.difficulty=difficulty;p=self._interpolate_difficulty(difficulty)
        if self.task_type=="uniform_motion":
            self.v=v if v is not None else random.randint(-p["max_v"],p["max_v"])
            self.t=t if t is not None else random.randint(2,p["max_t"])
            inputs=dict(v=self.v,t=self.t)
        elif self.task_type=="find_velocity":
            self.t=t if t is not None else random.randint(2,p["max_t"])
            self.s=s if s is not None else random.randint(-p["max_v"],p["max_v"])*number(self.t)
            inputs=dict(s=self.s,t=self.t)
        elif self.task_type in ("accelerated_distance","accelerated_velocity"):
            self.v0=v0 if v0 is not None else 0 if self.task_type=="accelerated_distance" else random.randint(-p["max_v"]//2,p["max_v"]//2)
            self.a=a if a is not None else random.randint(-p["max_a"],p["max_a"])
            self.t=t if t is not None else random.randint(2,p["max_t"])
            inputs=dict(v0=self.v0,a=self.a,t=self.t)
        elif self.task_type in ("projectile_max_height","projectile_range"):
            self.v0=v0 if v0 is not None else v if v is not None else random.randint(5000,p["max_v"]*1000)/1000
            self.v=self.v0
            self.g=get_constant("g") if g is None else g
            inputs=dict(v0=self.v0,g=self.g)
            if self.task_type=="projectile_range":
                self.angle=angle if angle is not None else random.choice([0,30,45,60,90])
                inputs['angle']=self.angle
        elif self.task_type=="circular_velocity":
            self.r=r if r is not None else random.randint(1,50)
            self.T=T if T is not None else random.randint(1,20)
            inputs=dict(r=self.r,T=self.T)
        else:
            self.r=r if r is not None else random.randint(1,50)
            self.v=v if v is not None else random.randint(0,p["max_v"])
            inputs=dict(r=self.r,v=self.v)
        validate(self.TASK_TYPE,self.task_type,inputs)
        description=texts.t("problem_"+self.task_type,language,**inputs)
        super().__init__(description,language,detail_level,output_format,reasoning_mode)

    def solve(self):return solve_task(self)
    def _solve_before_trace(self):self.solve()
    def verify(self,prediction):return verify_task(self,prediction)
    def get_task_type(self):return self.TASK_TYPE

    @classmethod
    def generate_random_task(cls,task_type=None,language="ru",detail_level=3,difficulty=5,
                             output_format="text",reasoning_mode=False,**kwargs):
        task=cls(task_type=task_type or random.choice(cls.TASK_TYPES),language=language,detail_level=detail_level,
                 difficulty=difficulty,output_format=output_format,reasoning_mode=reasoning_mode,**kwargs)
        task.solve();return task
