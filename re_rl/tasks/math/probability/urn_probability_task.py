# re_rl/tasks/urn_probability_task.py
import random
import math
from re_rl.tasks.base_task import BaseTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class UrnProbabilityTask(BaseTask):
    def __init__(self, language="en", count_containers=None, draws=None, output_format: OutputFormat = "text", reasoning_mode: bool = False):
        self.language = language.lower()
        self._output_format = output_format
        self._reasoning_mode = reasoning_mode
        syn = PROMPT_TEMPLATES["urn_probability"]["synonyms"][self.language]

        if count_containers is None:
            count_containers = random.randint(2, 4)
        self.count_containers = count_containers

        if draws is None:
            draws = random.randint(1, 3)
        self.draws = draws

        self.container_syn = random.choice(syn["containers"])
        self.item_syn = random.choice(syn["items"])

        # Генерируем несколько возможных цветов
        available_colors = random.sample(syn["colors"], k=random.randint(2,3))
        self.colors = available_colors

        # Для каждого контейнера распределяем предметы по цветам
        self.containers = []
        for _ in range(self.count_containers):
            total_items = random.randint(4, 8)
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

        self.question_str = self._choose_question()

        desc = self._create_problem_text()
        super().__init__(desc, language=self.language)
        self.reasoning_mode = reasoning_mode

    def _choose_question(self):
        questions_list = PROMPT_TEMPLATES["urn_probability"]["questions_pool"][self.language]
        chosen_template = random.choice(questions_list)
        color_choice = random.choice(self.colors)
        # Если шаблон требует x
        if "{x}" in chosen_template:
            x_val = random.randint(1, self.draws)  # "exactly x out of draws are color"
            return chosen_template.format(
                draws=self.draws,
                item_syn=self.item_syn,
                color=color_choice,
                x=x_val
            )
        else:
            return chosen_template.format(
                draws=self.draws,
                item_syn=self.item_syn,
                color=color_choice
            )

    def _create_problem_text(self):
        p = PROMPT_TEMPLATES["urn_probability"]["problem"][self.language]
        details_lines = []
        for idx, dist in enumerate(self.containers, start=1):
            line_parts = []
            total_count = sum([c for _, c in dist])
            if self.language == "ru":
                line_parts.append(f"{self.container_syn} №{idx} (всего {total_count} {self.item_syn}):")
            else:
                line_parts.append(f"{self.container_syn} #{idx} (total {total_count} {self.item_syn}):")

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
        st = PROMPT_TEMPLATES["urn_probability"]["steps"][self.language]
        steps_count = min(4, len(st))
        steps_list = []
        for i in range(steps_count):
            # Выберем idx случайно
            idx_val = random.randint(1, self.count_containers)
            step_str = st[i].format(
                container_syn=self.container_syn,
                container_syn_2=self.container_syn,
                count_containers=self.count_containers,
                idx=idx_val,
                item_syn=self.item_syn
            )
            steps_list.append(step_str)
        self.solution_steps = steps_list

        event_prob = 0.0
        for dist in self.containers:
            p_container = 1.0 / self.count_containers
            p_event_in_container = self._compute_event_prob(dist)
            event_prob += p_container * p_event_in_container

        final_templ = PROMPT_TEMPLATES["urn_probability"]["final_answer"][self.language]
        self.final_answer = final_templ.format(prob_value=f"{event_prob:.4f}")

    def _compute_event_prob(self, dist):
        total_in_container = sum(c for _, c in dist)
        if total_in_container < self.draws:
            return 0.0

        # Определим, какой сценарий вопроса
        # "all draws are color" / "at least one color" / "exactly x color" ...
        txt = self.question_str
        # Найдём color
        color_found = None
        for col in self.colors:
            if col in txt:
                color_found = col
                break
        if not color_found:
            return 0.0

        # Ищем число x
        import re
        x_val = None
        match = re.search(r"exactly (\d+)", txt)
        if match:
            x_val = int(match.group(1))

        if ("все" in txt or "all" in txt) and "drawn" in txt:
            # all draws are color_found
            color_count = 0
            for (col, cnt) in dist:
                if col == color_found:
                    color_count = cnt
                    break
            return self._hypergeom(color_count, total_in_container, self.draws, self.draws)
        elif ("хотя бы один" in txt or "at least one" in txt):
            color_count = 0
            for (col, cnt) in dist:
                if col == color_found:
                    color_count = cnt
                    break
            # P(>=1 color_found) = 1 - P(0 color_found)
            p_none = self._hypergeom_zero(color_count, total_in_container, self.draws)
            return 1.0 - p_none
        elif ("exactly" in txt or "ровно" in txt) and x_val is not None:
            color_count = 0
            for (col, cnt) in dist:
                if col == color_found:
                    color_count = cnt
                    break
            return self._hypergeom(color_count, total_in_container, self.draws, x_val)
        return 0.0

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

    def get_task_type(self):
        return "urn_probability"

    def get_result(self):
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
