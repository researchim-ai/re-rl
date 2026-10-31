"""Stable optimization instances, complete algorithm traces and semantic certificates."""
import ast
import random
import re
from typing import Any, ClassVar, Dict
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.math.logic import _logic_utils as U
from .solver import knapsack,set_cover,tsp
texts=TaskTexts(__file__)


class CombinatorialOptimizationTask(BaseMathTask):
    TASK_TYPE="combinatorial_optimization"
    TASK_TYPES=["knapsack","set_cover","tsp_small"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"task_type": "knapsack", "n": 5, "solve_mode": "exact"},
        2: {"task_type": "knapsack", "n": 6, "solve_mode": "exact"},
        3: {"task_type": "set_cover", "n": 5, "solve_mode": "exact"},
        4: {"task_type": "set_cover", "n": 6, "solve_mode": "exact"},
        5: {"task_type": "tsp_small", "n": 5, "solve_mode": "exact"},
        6: {"task_type": "tsp_small", "n": 6, "solve_mode": "exact"},
        7: {"task_type": "knapsack", "n": 9, "solve_mode": "approx"},
        8: {"task_type": "set_cover", "n": 9, "solve_mode": "approx"},
        9: {"task_type": "tsp_small", "n": 8, "solve_mode": "approx"},
        10: {"task_type": "mixed", "n": 10, "solve_mode": "approx"},
    }

    def __init__(self, task_type=None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat="text", reasoning_mode=False, augment=True,
                 solve_mode=None, n=None):
        preset=self._interpolate_difficulty(difficulty)
        kind=preset["task_type"] if task_type is None else task_type
        self.task_type=random.choice(self.TASK_TYPES) if kind=="mixed" else kind
        self.solve_mode=preset["solve_mode"] if solve_mode is None else solve_mode
        self.n=preset["n"] if n is None else n
        self.augment=augment
        if self.task_type not in self.TASK_TYPES:raise ValueError("invalid_task_type")
        if self.solve_mode not in ("exact","approx"):raise ValueError("invalid_solve_mode")
        maximum=12 if self.solve_mode=="exact" and self.task_type in ("set_cover","tsp_small") else 100
        if type(self.n) is not int or not 1 <= self.n <= maximum:raise ValueError("invalid_n")
        if self.task_type=="knapsack":
            self.items=[(random.randint(1,10),random.randint(2,30)) for _ in range(self.n)]
            self.capacity=max(8,int(sum(w for w,v in self.items)*0.4))
            data=dict(items=self.items,capacity=self.capacity)
        elif self.task_type=="set_cover":
            self.universe=set(range(1,self.n+1))
            self.sets=[set(random.sample(range(1,self.n+1),random.randint(1,min(self.n,self.n//2+1)))) for _ in range(self.n)]
            missing=self.universe-set().union(*self.sets)
            for value in sorted(missing):self.sets[random.randrange(self.n)].add(value)
            data=dict(universe=sorted(self.universe),sets=[sorted(s) for s in self.sets])
        else:
            self.matrix=[[0]*self.n for _ in range(self.n)]
            for i in range(self.n):
                for j in range(i+1,self.n):
                    self.matrix[i][j]=self.matrix[j][i]=random.randint(2,25)
            data=dict(matrix=self.matrix)
        rule=texts.t("exact_rule" if self.solve_mode=="exact" else "approx_"+self.task_type,language)
        description=texts.t("problem_"+self.task_type,language,mode=self.solve_mode,rule=rule,**data)
        super().__init__(description,language=language,detail_level=detail_level,
                         output_format=output_format,reasoning_mode=reasoning_mode)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solve()

    def verify(self, prediction):
        text=U.clean(prediction).strip()
        labels={"knapsack":("value","items"),"set_cover":("size","sets"),"tsp_small":("distance","route")}
        objective,label=labels[self.task_type]
        match=re.fullmatch(objective+r"\s*=\s*(\d+)\s*;\s*"+label+r"\s*=\s*(\[.*\])",text)
        if not match:return 0.0
        try:chosen=ast.literal_eval(match.group(2))
        except (ValueError,SyntaxError):return 0.0
        if not isinstance(chosen,list) or any(type(i) is not int for i in chosen):return 0.0
        reported=int(match.group(1))
        if self.task_type=="knapsack":
            if len(set(chosen))!=len(chosen) or any(not 0 <= i < len(self.items) for i in chosen):return 0.0
            weight=sum(self.items[i][0] for i in chosen);value=sum(self.items[i][1] for i in chosen)
            if weight>self.capacity or value!=reported:return 0.0
            baseline,_=knapsack(self.items,self.capacity,self.solve_mode)
            return float(value==baseline if self.solve_mode=="exact" else value>=baseline)
        if self.task_type=="set_cover":
            if len(set(chosen))!=len(chosen) or any(not 0 <= i < len(self.sets) for i in chosen):return 0.0
            if set().union(*(self.sets[i] for i in chosen))!=self.universe or len(chosen)!=reported:return 0.0
            baseline,_=set_cover(self.universe,self.sets,self.solve_mode)
            return float(reported<=baseline)
        n=len(self.matrix)
        if len(chosen)!=n+1 or chosen[0]!=0 or chosen[-1]!=0 or set(chosen[:-1])!=set(range(n)):return 0.0
        distance=sum(self.matrix[a][b] for a,b in zip(chosen,chosen[1:]))
        if distance!=reported:return 0.0
        baseline,_=tsp(self.matrix,self.solve_mode)
        return float(distance<=baseline)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task=cls(language=language,detail_level=detail_level,difficulty=difficulty,
                 reasoning_mode=reasoning_mode,augment=augment,**kwargs)
        task.solve()
        return task
