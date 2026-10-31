"""Numeric analogy in a public finite rule family, with an identifiable prediction."""
import random
import re
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.math.logic._logic_utils import clean
from .solver import infer

texts = TaskTexts(__file__)


class AnalogicalTask(BaseMathTask):
    TASK_TYPE = 'analogical'
    DIFFICULTY_PRESETS = {d:dict(coefficient_bound=2 if d <= 3 else 3 if d <= 6 else 5,
                               offset_bound=3 if d <= 3 else 5 if d <= 6 else 8,
                               max_power=1 if d <= 3 else 2 if d <= 6 else 3) for d in range(1,11)}

    def __init__(self,description=None,language='en',detail_level=3,output_format='text',reasoning_mode=False,
                 difficulty=5,examples=None,query=None,coefficient_bound=None,offset_bound=None,max_power=None,augment=True,task_type=None):
        if task_type is not None:raise ValueError("invalid_subtype")
        p = self._interpolate_difficulty(difficulty)
        self.coefficient_bound = p['coefficient_bound'] if coefficient_bound is None else coefficient_bound
        self.offset_bound = p['offset_bound'] if offset_bound is None else offset_bound
        self.max_power = p['max_power'] if max_power is None else max_power
        for value,lo,hi in ((self.coefficient_bound,1,8),(self.offset_bound,0,20),(self.max_power,1,3)):
            if type(value) is not int or not lo <= value <= hi:raise ValueError('invalid_rule_bounds')
        if description is not None and examples is None:raise ValueError('structured_examples_required')
        if examples is None:
            if query is not None and type(query) is not int:raise ValueError('invalid_query')
            a = random.choice([i for i in range(-self.coefficient_bound,self.coefficient_bound+1) if i])
            b = random.randint(-self.offset_bound,self.offset_bound);power = random.randint(1,self.max_power)
            xs = random.sample(range(-10,11),3)
            self.examples = [(x,a*x**power+b) for x in xs]
            self.query = random.choice([x for x in range(-10,11) if x not in xs]) if query is None else query
            remaining = [x for x in range(-10,11) if x not in xs and x != self.query];random.shuffle(remaining)
            while True:
                try:self.answer = infer(self.examples,self.query,self.coefficient_bound,self.offset_bound,self.max_power);break
                except ValueError as error:
                    if str(error) != 'ambiguous_prediction' or not remaining:raise
                    x = remaining.pop();self.examples.append((x,a*x**power+b))
        else:
            if not isinstance(examples,(list,tuple)) or not examples or len(examples) > 21:
                raise ValueError('invalid_examples')
            if any(not isinstance(pair,(list,tuple)) or len(pair) != 2 or any(type(v) is not int for v in pair) for pair in examples):
                raise ValueError('invalid_examples')
            self.examples = [tuple(pair) for pair in examples]
            if type(query) is not int:raise ValueError('invalid_query')
            self.query = query
            self.answer = infer(self.examples,self.query,self.coefficient_bound,self.offset_bound,self.max_power)
        problem = texts.t('problem',language,examples='; '.join(str(x)+' → '+str(y) for x,y in self.examples),
                         query=self.query,a=self.coefficient_bound,b=self.offset_bound,p=self.max_power)
        if description is not None:problem = description+'\n'+problem
        super().__init__(problem,language,detail_level,output_format,reasoning_mode)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = []
        self.final_answer = str(self.answer)

    def verify(self,prediction):
        try:expected = infer(self.examples,self.query,self.coefficient_bound,self.offset_bound,self.max_power)
        except ValueError:return 0.0
        text = clean(prediction)
        return float(bool(re.fullmatch(r'[+-]?[0-9]+',text)) and int(text) == expected)
