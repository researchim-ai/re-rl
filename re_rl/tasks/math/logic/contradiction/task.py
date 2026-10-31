"""Find one false assertion using explicit definitions, with no factual truth labels."""
import random
import re
from typing import ClassVar
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.base_task import BaseTask
from re_rl.tasks.math.logic._logic_utils import clean
from .solver import OPERATIONS,evaluate,render_definition,render_claim

texts = TaskTexts(__file__)


class ContradictionTask(BaseTask):
    """Поиск единственного ложного утверждения по цепочкам целочисленных определений."""
    TASK_TYPE = 'contradiction'
    DIFFICULTY_PRESETS: ClassVar = {d:dict(num_statements=n,chain_depth=1+(d+1)//2)
                                  for d,n in enumerate((5,8,10,15,18,20,25,30,35,40),1)}

    def __init__(self,language='en',num_statements=None,difficulty=None,output_format='text',
                 reasoning_mode=False,chain_depth=None):
        preset = self._interpolate_difficulty(difficulty) if difficulty is not None else {}
        self.num_statements = preset.get('num_statements',25) if num_statements is None else num_statements
        self.chain_depth = preset.get('chain_depth',3) if chain_depth is None else chain_depth
        if type(self.num_statements) is not int or not 1 <= self.num_statements <= 500:
            raise ValueError('invalid_num_statements')
        if type(self.chain_depth) is not int or not 0 <= self.chain_depth <= 20:
            raise ValueError('invalid_chain_depth')
        self.difficulty = difficulty;self._output_format = output_format;self._reasoning_mode = reasoning_mode
        self.definitions = [dict(name='a',op='const',value=random.randint(-20,20)),
                            dict(name='b',op='const',value=random.randint(-20,20))]
        values = {d['name']:d['value'] for d in self.definitions}
        self.false_statement_index = random.randrange(self.num_statements)
        self.claims = []
        for index in range(self.num_statements):
            previous = random.choice(('a','b'))
            for depth in range(self.chain_depth):
                name = 'x'+str(index+1)+'_'+str(depth+1)
                op = random.choice(tuple(OPERATIONS));right = random.randint(2,9)
                self.definitions.append(dict(name=name,op=op,left=previous,right=right))
                values[name] = OPERATIONS[op](values[previous],right);previous = name
            actual = values[previous];relation = random.choice(('eq','ne','lt','le','gt','ge'))
            truth = index != self.false_statement_index
            delta = random.randint(1,9)
            right = {'eq':actual if truth else actual+delta,
                     'ne':actual+delta if truth else actual,
                     'lt':actual+delta if truth else actual,
                     'le':actual if truth else actual-delta,
                     'gt':actual-delta if truth else actual,
                     'ge':actual if truth else actual+delta}[relation]
            self.claims.append(dict(left=previous,relation=relation,right=right))
        self.statements = [render_claim(c) for c in self.claims]
        definitions = '\n'.join(render_definition(d) for d in self.definitions)
        statements = '\n'.join(str(i+1)+'. '+s for i,s in enumerate(self.statements))
        description = texts.t('formal_problem',language,definitions=definitions,statements=statements)
        super().__init__(description,language.lower())
        self.reasoning_mode = reasoning_mode

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.statements = [render_claim(c) for c in self.claims]
        self.solution_steps = []
        self.final_answer = texts.t('formal_answer',self.language,false_statement=self.statements[self.false_statement_index])

    def verify(self,prediction):
        try:_,indices = evaluate(self.definitions,self.claims,[])
        except (ValueError,KeyError,TypeError):return 0.0
        if len(indices) != 1:return 0.0
        index = indices[0];statement = render_claim(self.claims[index]);text = clean(prediction)
        if re.fullmatch(r'[1-9][0-9]*',text):return float(int(text) == index+1)
        aliases = [statement]+[texts.t('formal_answer',lang,false_statement=statement) for lang in ('ru','en')]
        return float(text in aliases)
