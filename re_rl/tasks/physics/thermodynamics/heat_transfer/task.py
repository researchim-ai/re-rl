"""Constant-capacity, phase-change and cyclic-engine models with explicit domains."""
import random
from typing import Any,ClassVar,Dict
from re_rl.tasks.base_task import BaseMathTask,OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.physics.conservation_models import solve_task,verify_task,validate_inputs,number
texts=TaskTexts(__file__)

# Удельные теплоёмкости (Дж/(кг·°C))
SPECIFIC_HEAT = {
    "water": {"c": 4186, "name_ru": texts.literal('literals.s1'), "name_en": texts.t("material_water","en")},
    "ice": {"c": 2090, "name_ru": texts.literal('literals.s2'), "name_en": texts.t("material_ice","en")},
    "aluminum": {"c": 897, "name_ru": texts.literal('literals.s3'), "name_en": texts.t("material_aluminum","en")},
    "iron": {"c": 449, "name_ru": texts.literal('literals.s4'), "name_en": texts.t("material_iron","en")},
    "copper": {"c": 385, "name_ru": texts.literal('literals.s5'), "name_en": texts.t("material_copper","en")},
    "lead": {"c": 128, "name_ru": texts.literal('literals.s6'), "name_en": texts.t("material_lead","en")},
}

# Удельные теплоты (Дж/кг)
LATENT_HEAT = {
    "ice_melting": {"lambda": 334000, "name_ru": texts.literal('literals.s7'), "name_en": texts.t("process_ice_melting","en")},
    "water_vaporization": {"lambda": 2260000, "name_ru": texts.literal('literals.s8'), "name_en": texts.t("process_water_vaporization","en")},
}



class HeatTransferTask(BaseMathTask):
    TASK_TYPE="heat_transfer"
    TASK_TYPES=["heat_capacity","mixing","phase_change","efficiency"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"max_m": 2, "max_dT": 50, "max_Q": 100000},
        2: {"max_m": 5, "max_dT": 80, "max_Q": 500000},
        3: {"max_m": 10, "max_dT": 100, "max_Q": 1000000},
        4: {"max_m": 20, "max_dT": 150, "max_Q": 2000000},
        5: {"max_m": 50, "max_dT": 200, "max_Q": 5000000},
        6: {"max_m": 100, "max_dT": 300, "max_Q": 10000000},
        7: {"max_m": 100, "max_dT": 500, "max_Q": 20000000},
        8: {"max_m": 200, "max_dT": 500, "max_Q": 50000000},
        9: {"max_m": 500, "max_dT": 1000, "max_Q": 100000000},
        10: {"max_m": 1000, "max_dT": 1000, "max_Q": 500000000},
    }
    
    def __init__(self,task_type="heat_capacity",m=None,m1=None,m2=None,T1=None,T2=None,
                 substance=None,Q1=None,Q2=None,language="ru",detail_level=3,difficulty=5,
                 output_format: OutputFormat="text",reasoning_mode=False,**kwargs):
        self.difficulty=difficulty
        self.task_type=task_type.lower() if isinstance(task_type,str) else "heat_capacity" if task_type is None else task_type
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        if substance is not None and (not isinstance(substance,str) or substance not in SPECIFIC_HEAT):raise ValueError("invalid_substance")
        p=self._interpolate_difficulty(difficulty)
        mass=lambda value: value if value is not None else round(random.uniform(0.1,p["max_m"]),2)
        if self.task_type in ("heat_capacity","mixing"):
            self.substance=(random.choice(list(SPECIFIC_HEAT)) if substance is None else substance) if self.task_type=="heat_capacity" else ("water" if substance is None else substance)
            if self.substance not in SPECIFIC_HEAT or (self.task_type=="mixing" and self.substance!="water"):
                raise ValueError("invalid_substance")
            self.c=SPECIFIC_HEAT[self.substance]["c"]
            if self.task_type=="heat_capacity":
                self.m=mass(m)
                self.T1=T1 if T1 is not None else random.randint(-min(100,p["max_dT"]),-1) if self.substance=="ice" else random.randint(0,50)
                upper=0 if self.substance=="ice" else 100 if self.substance=="water" else 200
                # Validate the first temperature before using it to generate another.
                validate_inputs(self.TASK_TYPE,self.task_type,dict(m=self.m,T1=self.T1,T2=self.T1,c=self.c,substance=self.substance))
                self.T2=T2 if T2 is not None else min(upper,self.T1+random.randint(0,p["max_dT"]))
                inputs=dict(m=self.m,T1=self.T1,T2=self.T2,c=self.c,substance=self.substance)
            else:
                self.m1=mass(m1);self.m2=mass(m2)
                self.T1=T1 if T1 is not None else random.randint(0,50)
                self.T2=T2 if T2 is not None else random.randint(50,100)
                inputs=dict(m1=self.m1,m2=self.m2,T1=self.T1,T2=self.T2,c=self.c)
        elif self.task_type=="phase_change":
            if substance not in (None,"ice"):raise ValueError("invalid_substance")
            self.substance="ice";self.m=mass(m);self.lambda_ice=LATENT_HEAT["ice_melting"]["lambda"]
            inputs=dict(m=self.m,lambda_ice=self.lambda_ice)
        else:
            self.Q1=Q1 if Q1 is not None else random.randint(10000,p["max_Q"])
            self.Q2=Q2 if Q2 is not None else number(self.Q1)*random.randint(1,9)/10
            inputs=dict(Q1=self.Q1,Q2=self.Q2)
        validate_inputs(self.TASK_TYPE,self.task_type,inputs)
        description_inputs=dict(inputs)
        if self.task_type=="heat_capacity":
            description_inputs['substance']=texts.t("material_"+self.substance,language)
        description=texts.t("problem_"+self.task_type,language,**description_inputs)
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
