"""Truth-consistent island puzzles; any public-statement model is accepted."""
import random
from re_rl.tasks.i18n import TaskTexts
from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.math.logic.puzzle_inference import statement_value,knight_models
from re_rl.tasks.math.logic._logic_utils import clean

texts = TaskTexts(__file__)


class KnightsKnavesTask(BaseMathTask):
    TASK_TYPE = 'knights_knaves'
    DIFFICULTY_PRESETS = {d:{'complexity':(d+1)//2} for d in range(1,11)}

    def __init__(self,language='en',detail_level=3,complexity=None,difficulty=None,
                 output_format='text',reasoning_mode=False):
        if complexity is None:
            complexity = self._interpolate_difficulty(difficulty)['complexity'] if difficulty is not None else 2
        if type(complexity) is not int or not 1 <= complexity <= 5:
            raise ValueError('invalid_complexity')
        self.language = language.lower();self.complexity = complexity;self.difficulty = difficulty
        self.num_persons,self.num_statements = self._compute_params_by_complexity(complexity)
        self.names = random.sample(PROMPT_TEMPLATES['knights_knaves']['names_pool'][self.language],self.num_persons)
        witness = tuple(bool(random.getrandbits(1)) for _ in self.names)
        self.roles = ['knight' if role else 'knave' for role in witness]
        self.statements = self._generate_random_statements(self.num_statements,witness)
        description = self._create_problem_text()
        super().__init__(description,self.language,detail_level,output_format,reasoning_mode)

    def _compute_params_by_complexity(self,lvl):
        return lvl+1, (2,3,5,7,9)[lvl-1]

    def _generate_random_statements(self,count,witness):
        forms = ['about_self','about_other','and','or','same','different','at_least_one','exactly_one']
        statements = []
        for index in range(count):
            speaker = index % self.num_persons
            others = [i for i in range(self.num_persons) if i != speaker]
            for attempt in range(128):
                form = random.choice(forms)
                if form in ('and','or','same','different') and len(others) < 2:continue
                y = random.choice(others)
                z = random.choice([i for i in others if i != y]) if len(others) > 1 else None
                statement = dict(speaker=speaker,form_key=form,y=y,z=z,polarity=bool(random.getrandbits(1)))
                if statement_value(statement,witness) == witness[speaker]:break
            else:
                y = others[0]
                statement = dict(speaker=speaker,form_key='about_other',y=y,z=None,
                                 polarity=witness[y] if witness[speaker] else not witness[y])
            statement['text'] = self._build_statement_text(statement)
            statements.append(statement)
        return statements

    def _build_statement_text(self,statement):
        forms = PROMPT_TEMPLATES['knights_knaves']['forms'][self.language]
        y,z = statement['y'],statement['z']
        core = forms[statement['form_key']].format(name=self.names[y],other_name='' if z is None else self.names[z],
                 role=texts.t('s12' if statement['polarity'] else 's13',self.language))
        return forms['statement'].format(name=self.names[statement['speaker']],text=core)

    def _create_problem_text(self):
        section = PROMPT_TEMPLATES['knights_knaves']
        return (section['instructions'][self.language]+'\n\n'+section['intro'][self.language].format(
                names=', '.join(self.names),num_persons=self.num_persons)+'\n\n'+
                section['problem'][self.language].format(statements='\n'.join(s['text'] for s in self.statements)))

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        self.solution_steps = []
        if self.roles is None:
            self.final_answer = texts.t('s18',self.language)
        else:
            roles = ', '.join(name+': '+texts.t('s12' if role == 'knight' else 's13',self.language)
                              for name,role in zip(self.names,self.roles))
            self.final_answer = PROMPT_TEMPLATES['knights_knaves']['final_answer'][self.language].format(roles=roles)

    def verify(self,prediction):
        text = clean(prediction)
        if text in (texts.t('s18','ru'),texts.t('s18','en')):
            return float(not knight_models(self.num_persons,self.statements,[]))
        for language in ('ru','en'):
            header = PROMPT_TEMPLATES['knights_knaves']['final_answer'][language].split('{roles}')[0]
            if text.startswith(header):text = text[len(header):]
        assignment = {}
        for part in text.split(','):
            fields = part.strip().split(':')
            if len(fields) != 2:return 0.0
            name,role = map(str.strip,fields)
            if name not in self.names or name in assignment:return 0.0
            if role in (texts.t('s12','ru'),texts.t('s12','en')):assignment[name] = True
            elif role in (texts.t('s13','ru'),texts.t('s13','en')):assignment[name] = False
            else:return 0.0
        if set(assignment) != set(self.names):return 0.0
        roles = [assignment[name] for name in self.names]
        return float(all(roles[s['speaker']] == statement_value(s,roles) for s in self.statements))

    def get_result(self,detail_level=None):
        return super().get_result()

    def get_task_type(self):
        return self.TASK_TYPE
