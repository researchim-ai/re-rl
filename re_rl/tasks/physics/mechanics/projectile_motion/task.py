"""Ground-to-ground ideal projectile tasks with published, unrounded initial data."""
import random
from decimal import Decimal,localcontext
import sympy as sp
from typing import Any,ClassVar,Dict
from re_rl.tasks.base_task import BaseMathTask,OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.physics.constants import get_constant
from re_rl.tasks.physics.trajectory_models import validate,solve_task,verify_task,ballistic_parameters
texts=TaskTexts(__file__)


class ProjectileMotionTask(BaseMathTask):
    TASK_TYPE="projectile_motion"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"v0_range": (5, 15), "angle_simple": True},
        2: {"v0_range": (10, 20), "angle_simple": True},
        3: {"v0_range": (10, 30), "angle_simple": False},
        4: {"v0_range": (15, 40), "angle_simple": False},
        5: {"v0_range": (20, 50), "angle_simple": False},
        6: {"v0_range": (20, 60), "angle_simple": False},
        7: {"v0_range": (30, 80), "angle_simple": False},
        8: {"v0_range": (40, 100), "angle_simple": False},
        9: {"v0_range": (50, 150), "angle_simple": False},
        10: {"v0_range": (100, 300), "angle_simple": False},
    }
    
    TASK_TYPES=["range","max_height","flight_time","velocity_at_height"]

    def __init__(self,language="ru",detail_level=3,task_type=None,v0=None,angle=None,difficulty=None,
                 output_format: OutputFormat="text",reasoning_mode=False,g=None,height_query=None,**kwargs):
        selected=random.choice(self.TASK_TYPES) if task_type is None else task_type
        self.task_type=selected.lower() if isinstance(selected,str) else selected
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        self.difficulty=difficulty
        p=self._interpolate_difficulty(5 if difficulty is None else difficulty)
        self.v0=v0 if v0 is not None else round(random.uniform(*p['v0_range']),3)
        self.angle=angle if angle is not None else random.choice([30,45,60]) if p['angle_simple'] else round(random.uniform(15,75),3)
        self.g=get_constant("g") if g is None else g
        initial=dict(v0=self.v0,angle=self.angle,g=self.g)
        validate(self.TASK_TYPE,'range',initial)
        parameters=ballistic_parameters(**initial)
        # Compatibility attributes are derived metadata, never solver inputs.
        self.vx=sp.N(parameters['vx'],40);self.vy=sp.N(parameters['vy'],40)
        self.range_val=sp.N(parameters['range'],40);self.max_height=sp.N(parameters['height'],40);self.flight_time=sp.N(parameters['time'],40)
        inputs=dict(initial)
        if self.task_type=='velocity_at_height':
            if height_query is None and parameters['height']==0:height_query=0
            if height_query is None:
                with localcontext() as context:
                    context.prec=30
                    height_query=Decimal(str(sp.N(parameters['height'],12)))*Decimal(random.randint(3,8))/Decimal(10)
            self.height_query=height_query;inputs['height_query']=self.height_query
        elif height_query is not None:raise ValueError('height_query_not_applicable')
        validate(self.TASK_TYPE,self.task_type,inputs)
        description=texts.t('problem_'+self.task_type,language,**inputs)
        super().__init__(description,language,detail_level,output_format,reasoning_mode)

    def solve(self):return solve_task(self)
    def _solve_before_trace(self):self.solve()
    def verify(self,prediction):return verify_task(self,prediction)
    def get_task_type(self):return self.TASK_TYPE

    @classmethod
    def generate_random_task(cls,reasoning_mode=False,**kwargs):
        task=cls(reasoning_mode=reasoning_mode,**kwargs);task.solve();return task
