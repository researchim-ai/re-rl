import random
from re_rl.tasks.base_task import BaseTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class KnightsKnavesTask(BaseTask):
    """
    Задача о «рыцарях и лжецах» (Knights and Knaves) с большой вариативностью.
    - Случайные имена персонажей
    - Случайный выбор сценария (из трех)
    - Случайный выбор синонимов для "good_role" и "bad_role"
    """

    def __init__(self, language: str = "ru", detail_level: int = 5):
        """
        :param language: 'ru' или 'en' (можно расширять).
        :param detail_level: сколько шагов (строк) решения выводить.
        """
        self.language = language.lower()
        self.detail_level = detail_level
        
        # 1) Выберем роли: good_role и bad_role (случайно из списков)
        roles_data = PROMPT_TEMPLATES["knights_knaves"]["roles_synonyms"][self.language]
        self.good_role = random.choice(roles_data["good"])
        self.bad_role = random.choice(roles_data["bad"])
        
        # 2) Выберем 3 случайных имени
        self.names = self._choose_random_names()
        
        # 3) Выберем один из сценариев (scenario1, scenario2, scenario3)
        self.scenario_key = random.choice(["scenario1", "scenario2", "scenario3"])
        self.scenario_data = PROMPT_TEMPLATES["knights_knaves"][self.scenario_key]
        
        # Формируем описание задачи (problem)
        problem_text = self._create_problem_text()
        
        super().__init__(problem_text)  # BaseTask ожидает description в конструкторе

    def _choose_random_names(self):
        """Выбираем 3 случайных имени в зависимости от языка."""
        if self.language == "ru":
            pool = ["Аня", "Борис", "Валя", "Глеб", "Даша", "Егор", "Жора", "Ира", "Коля", "Лена"]
        else:
            pool = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hank", "Ivy", "Jack"]
        return random.sample(pool, 3)  # 3 имени
    
    def _create_problem_text(self):
        """
        Создаем текст постановки задачи, используя шаблон problem,
        и подменяя {good_role}, {bad_role}, {name1}, {name2}, {name3}, {statement1}, {statement2}, {statement3}.
        """
        problem_template = PROMPT_TEMPLATES["knights_knaves"]["problem"][self.language]
        
        # Извлекаем массив statements для выбранного scenario
        statements_templates = self.scenario_data["statements"][self.language]
        # Для каждой строки подставим {nameX}, {good_role}, {bad_role}
        statement1 = statements_templates[0].format(
            name1=self.names[0], name2=self.names[1], name3=self.names[2],
            good_role=self.good_role, bad_role=self.bad_role
        )
        statement2 = statements_templates[1].format(
            name1=self.names[0], name2=self.names[1], name3=self.names[2],
            good_role=self.good_role, bad_role=self.bad_role
        )
        statement3 = statements_templates[2].format(
            name1=self.names[0], name2=self.names[1], name3=self.names[2],
            good_role=self.good_role, bad_role=self.bad_role
        )
        
        # Теперь сам problem_template
        problem_text = problem_template.format(
            name1=self.names[0],
            name2=self.names[1],
            name3=self.names[2],
            good_role=self.good_role,
            bad_role=self.bad_role,
            statement1=statement1,
            statement2=statement2,
            statement3=statement3
        )
        return problem_text
    
    def solve(self):
        """
        Собираем шаги (solution_steps) и формируем final_answer
        из сценария scenario_data["steps"], ["final_answer"], ["roles"].
        """
        steps_templates = self.scenario_data["steps"][self.language]
        # Подставляем имена и роли
        all_steps = []
        for stpl in steps_templates:
            step_str = stpl.format(
                name1=self.names[0],
                name2=self.names[1],
                name3=self.names[2],
                good_role=self.good_role,
                bad_role=self.bad_role
            )
            all_steps.append(step_str)
        
        # Усекаем до detail_level, если нужно
        self.solution_steps = all_steps[:self.detail_level]
        
        # Формируем итоговое распределение ролей (roles = ["bad","good","good"], например)
        roles_order = self.scenario_data["roles"]  # ["bad","good","good"]
        # сопоставим: name1 -> roles_order[0], name2 -> roles_order[1], ...
        role_map = {
            "bad": self.bad_role,
            "good": self.good_role
        }
        final_assignment = [
            f"{self.names[i]}: {role_map[roles_order[i]]}"
            for i in range(3)
        ]
        
        # Итоговый ответ
        final_ans_templ = self.scenario_data["final_answer"][self.language]
        self.final_answer = final_ans_templ.format(
            name1=self.names[0],  name2=self.names[1],  name3=self.names[2],
            good_role=self.good_role, bad_role=self.bad_role,
            # Если нужно, передаем конкретно: {name1}: {bad_role} ...
        )
        # Можно, например, дополнительно в конец дописать " => " + ", ".join(final_assignment)
        # Или оставить как есть, если сценарий сам всё описывает.

    def get_result(self):
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),  # BaseTask генерирует промт из self.description + общий шаблон
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }
