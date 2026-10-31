from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

# re_rl/tasks/urn_probability_task.py
import random
import math
from re_rl.tasks.base_task import BaseTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class UrnProbabilityTask(BaseTask):
    TASK_TYPE = "urn_probability"
    def __init__(self, language="en", count_containers=None, draws=None, output_format: OutputFormat = "text", reasoning_mode: bool = False):
        self.language = language.lower()
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        syn = PROMPT_TEMPLATES["urn_probability"]["synonyms"][self.language]

        if count_containers is None:
            count_containers = random.randint(2, 4)
        if type(count_containers) is not int or count_containers < 1:
            raise ValueError("invalid_count_containers")
        self.count_containers = count_containers

        if draws is None:
            draws = random.randint(1, 3)
        if type(draws) is not int or draws < 1:
            raise ValueError("invalid_draws")
        self.draws = draws

        self.container_syn = random.choice(syn["containers"])
        self.item_syn = random.choice(syn["items"])

        # Генерируем несколько возможных цветов
        available_colors = random.sample(syn["colors"], k=random.randint(2,3))
        self.colors = available_colors

        # Для каждого контейнера распределяем предметы по цветам
        self.containers = []
        for _ in range(self.count_containers):
            total_items = random.randint(max(4,self.draws),max(8,self.draws))
            # Разобъём total_items на случайные доли
            remain = total_items
            color_dist = []
            for c_i, col in enumerate(self.colors):
                if c_i == len(self.colors)-1:
                    color_count = remain
                else:
                    color_count = random.randint(0, remain)
                remain -= color_count
                color_dist.append((col, color_count))
            self.containers.append(color_dist)

        self.question_kind = "at_least"
        self.color_choice = self.colors[0]
        self.x_val = None
        self.question_str = self._choose_question()

        desc = self._create_problem_text()
        super().__init__(desc, language=self.language)
        self.reasoning_mode = reasoning_mode

    def _choose_question(self):
        questions_list = PROMPT_TEMPLATES["urn_probability"]["questions_pool"][self.language]
        chosen_template = random.choice(questions_list)
        self.color_choice = random.choice(self.colors)
        if "{x}" in chosen_template:
            self.question_kind = "exactly"
            self.x_val = random.randint(1, self.draws)
        elif texts.t("s1", self.language) in chosen_template:
            self.question_kind = "all"
            self.x_val = None
        else:
            self.question_kind = "at_least"
            self.x_val = None
        return chosen_template.format(
            draws=self.draws,
            item_syn=self.item_syn,
            color=self.color_choice,
            x=self.x_val if self.x_val is not None else 0,
        )

    def _create_problem_text(self):
        p = PROMPT_TEMPLATES["urn_probability"]["problem"][self.language]
        details_lines = []
        for idx, dist in enumerate(self.containers, start=1):
            line_parts = []
            total_count = sum([c for _, c in dist])
            line_parts.append(texts.t('s0', self.language, container_syn=self.container_syn, idx=idx, total_count=total_count, item_syn=self.item_syn))

            color_info = []
            for (col, cnt) in dist:
                if cnt > 0:
                    color_info.append(f"{col}={cnt}")
            joined_col = ", ".join(color_info)
            line_parts.append(joined_col)
            details_lines.append(" ".join(line_parts))

        details_str = "\n".join(details_lines)
        return p.format(
            count_containers=self.count_containers,
            container_syn=self.container_syn,
            item_syn=self.item_syn,
            item_syn_2=self.item_syn,  # Можно варьировать
            details=details_str,
            draws=self.draws,
            question=self.question_str
        )

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        return solve_reviewed(self)

    def _solve_before_trace(self):
        event_prob = sum(self._compute_event_prob(dist) for dist in self.containers)/self.count_containers
        self.final_answer = PROMPT_TEMPLATES['urn_probability']['final_answer'][self.language].format(prob_value=format(event_prob,'.4f'))
        self.solution_steps = []

    def _compute_event_prob(self, dist):
        total_in_container = sum(c for _, c in dist)
        if total_in_container < self.draws:
            return 0.0

        color_count = 0
        for col, cnt in dist:
            if col == self.color_choice:
                color_count = cnt
                break
        if self.question_kind == "all":
            return self._hypergeom(color_count, total_in_container, self.draws, self.draws)
        if self.question_kind == "at_least":
            return 1.0 - self._hypergeom_zero(color_count, total_in_container, self.draws)
        return self._hypergeom(color_count, total_in_container, self.draws, self.x_val)

    def _hypergeom(self, color_cnt, total_cnt, draws, success_needed):
        if success_needed > color_cnt:
            return 0.0
        import math
        top = math.comb(color_cnt, success_needed)
        bottom = math.comb(total_cnt, draws)
        if draws - success_needed > total_cnt - color_cnt:
            return 0.0
        return top * math.comb(total_cnt - color_cnt, draws - success_needed) / bottom

    def _hypergeom_zero(self, color_cnt, total_cnt, draws):
        # P(0 items are color_cnt)
        import math
        if draws > total_cnt - color_cnt:
            return 0.0
        top = math.comb(total_cnt - color_cnt, draws)
        bottom = math.comb(total_cnt, draws)
        return top / bottom

    def verify(self,prediction):
        from re_rl.tasks.math.probability.inference_traces import verify_probability
        return verify_probability(self,prediction)

    def get_task_type(self):
        return "urn_probability"

    def get_result(self):
        return super().get_result()
