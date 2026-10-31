"""Non-dispersive mechanical waves and signed subsonic Doppler data."""
import random
from typing import Any,ClassVar,Dict
from fractions import Fraction
from re_rl.tasks.base_task import BaseMathTask,OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.physics.conservation_models import number
from re_rl.tasks.physics.spectrum_models import validate,solve_task,verify_task
texts=TaskTexts(__file__)


class WavesTask(BaseMathTask):
    TASK_TYPE="waves"
    TASK_TYPES=["wavelength","frequency","period","sound_speed","doppler"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_f": 1000, "max_v": 350, "max_lambda": 10},
        2: {"max_f": 5000, "max_v": 500, "max_lambda": 50},
        3: {"max_f": 10000, "max_v": 1000, "max_lambda": 100},
        4: {"max_f": 20000, "max_v": 2000, "max_lambda": 200},
        5: {"max_f": 50000, "max_v": 5000, "max_lambda": 500},
        6: {"max_f": 100000, "max_v": 10000, "max_lambda": 1000},
        7: {"max_f": 500000, "max_v": 20000, "max_lambda": 5000},
        8: {"max_f": 1000000, "max_v": 30000, "max_lambda": 10000},
        9: {"max_f": 10000000, "max_v": 50000, "max_lambda": 100000},
        10: {"max_f": 100000000, "max_v": 100000, "max_lambda": 1000000},
    }
    
    def __init__(self,task_type="wavelength",f=None,f0=None,v=None,v_s=None,lambda_=None,
                 language="ru",detail_level=3,difficulty=5,output_format: OutputFormat="text",
                 reasoning_mode=False,v_o=None,**kwargs):
        self.task_type=task_type.lower() if isinstance(task_type,str) else "wavelength" if task_type is None else task_type
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        self.difficulty=difficulty;p=self._interpolate_difficulty(difficulty)
        frequency=lambda value: value if value is not None else random.randint(100,p["max_f"])
        speed=lambda value: value if value is not None else random.randint(50,p["max_v"])
        if self.task_type=="wavelength":
            self.f=frequency(f);self.v=speed(v);inputs=dict(f=self.f,v=self.v)
        elif self.task_type=="frequency":
            self.v=speed(v);self.lambda_=lambda_ if lambda_ is not None else round(random.uniform(0.01,p["max_lambda"]),4)
            inputs=dict(v=self.v,lambda_=self.lambda_)
        elif self.task_type=="period":
            self.f=frequency(f);inputs=dict(f=self.f)
        elif self.task_type=="sound_speed":
            # A generated pair must correspond to a supported mechanical propagation speed.
            if f is not None and lambda_ is not None:self.f,self.lambda_=f,lambda_
            elif lambda_ is not None:
                length=number(lambda_)
                if length<=0:raise ValueError("nonpositive_wavelength")
                self.lambda_=lambda_;self.f=Fraction(speed(None))/length
            else:
                self.f=frequency(f);freq=number(self.f)
                if freq<=0:raise ValueError("nonpositive_frequency")
                self.lambda_=Fraction(speed(None))/freq
            inputs=dict(f=self.f,lambda_=self.lambda_)
        else:
            self.v=speed(v);medium=number(self.v)
            self.f0=frequency(f0)
            self.v_s=v_s if v_s is not None else medium*Fraction(random.randint(1,8),10)
            self.v_o=0 if v_o is None else v_o
            inputs=dict(f0=self.f0,v=self.v,v_s=self.v_s,v_o=self.v_o)
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
