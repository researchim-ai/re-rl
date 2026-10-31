"""One-dimensional Newtonian momentum and collision models with conservation traces."""
import random
from typing import Any,ClassVar,Dict
from re_rl.tasks.base_task import BaseMathTask,OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.physics.conservation_models import solve_task,verify_task,validate_inputs
texts=TaskTexts(__file__)


class MomentumTask(BaseMathTask):
    TASK_TYPE="momentum"
    TASK_TYPES=["momentum","impulse","inelastic_collision","elastic_collision"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_m": 10, "max_v": 10, "max_F": 50, "max_t": 5},
        2: {"max_m": 20, "max_v": 20, "max_F": 100, "max_t": 10},
        3: {"max_m": 30, "max_v": 30, "max_F": 200, "max_t": 10},
        4: {"max_m": 50, "max_v": 50, "max_F": 300, "max_t": 15},
        5: {"max_m": 50, "max_v": 50, "max_F": 500, "max_t": 15},
        6: {"max_m": 100, "max_v": 100, "max_F": 500, "max_t": 20},
        7: {"max_m": 100, "max_v": 100, "max_F": 1000, "max_t": 20},
        8: {"max_m": 200, "max_v": 150, "max_F": 1000, "max_t": 30},
        9: {"max_m": 200, "max_v": 200, "max_F": 2000, "max_t": 30},
        10: {"max_m": 500, "max_v": 300, "max_F": 5000, "max_t": 60},
    }
    
    def __init__(self,task_type="momentum",m=None,m1=None,m2=None,v=None,v1=None,F=None,t=None,
                 language="ru",detail_level=3,difficulty=5,output_format: OutputFormat="text",
                 reasoning_mode=False,v2=None,**kwargs):
        self.difficulty=difficulty
        self.task_type=task_type.lower() if isinstance(task_type,str) else "momentum" if task_type is None else task_type
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        preset=self._interpolate_difficulty(difficulty)
        if self.task_type=="momentum":
            self.m=m if m is not None else random.randint(1,preset["max_m"])
            self.v=v if v is not None else random.randint(5,preset["max_v"])
            inputs=dict(m=self.m,v=self.v)
        elif self.task_type=="impulse":
            self.F=F if F is not None else random.randint(10,preset["max_F"])
            self.t=t if t is not None else random.randint(1,preset["max_t"])
            inputs=dict(F=self.F,t=self.t)
        else:
            self.m1=m1 if m1 is not None else random.randint(1,preset["max_m"])
            self.m2=m2 if m2 is not None else random.randint(1,preset["max_m"])
            self.v1=v1 if v1 is not None else random.randint(5,preset["max_v"])
            self.v2=0 if v2 is None else v2
            inputs=dict(m1=self.m1,m2=self.m2,v1=self.v1,v2=self.v2)
        validate_inputs(self.TASK_TYPE,self.task_type,inputs)
        description=texts.t("problem_"+self.task_type,language,**inputs)
        super().__init__(description,language,detail_level,output_format,reasoning_mode)

    def solve(self):return solve_task(self)

    def _solve_before_trace(self):self.solve()

    def verify(self,prediction):return verify_task(self,prediction)

    def get_task_type(self):return self.TASK_TYPE

    @classmethod
    def generate_random_task(cls,task_type=None,language="ru",detail_level=3,difficulty=5,
                             reasoning_mode=False,**kwargs):
        task=cls(task_type=task_type or random.choice(cls.TASK_TYPES),language=language,
                 detail_level=detail_level,difficulty=difficulty,reasoning_mode=reasoning_mode,**kwargs)
        task.solve()
        return task
