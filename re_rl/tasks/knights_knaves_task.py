# re_rl/tasks/knights_knaves_task.py

import random
import z3
from re_rl.tasks.base_task import BaseTask
from re_rl.tasks.prompts import PROMPT_TEMPLATES

class KnightsKnavesTask(BaseTask):
    """
    Генерирует задачу Knights & Knaves с параметрами:
      - language: 'ru' или 'en'
      - detail_level: сколько шагов решения выводить
      - complexity: управляет числом персонажей и высказываний
    """

    def __init__(
        self,
        language: str = "en",
        detail_level: int = 3,
        complexity: int = 2
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: сколько шагов chain-of-thought
        :param complexity: уровень сложности (задаёт num_persons, num_statements и т.п.)
        """
        self.language = language.lower()
        self.detail_level = detail_level
        self.complexity = complexity

        # Определяем число персонажей / высказываний по уровню сложности
        self.num_persons, self.num_statements = self._compute_params_by_complexity(self.complexity)

        # Берём пул имён из prompts
        all_names = PROMPT_TEMPLATES["knights_knaves"]["names_pool"][self.language]
        random.shuffle(all_names)
        self.names = all_names[:self.num_persons]

        # Генерируем случайные высказывания
        self.statements = self._generate_random_statements(self.num_statements)

        # Формируем текст задачи (problem)
        description = self._create_problem_text()
        super().__init__(description)

    def _compute_params_by_complexity(self, lvl: int):
        """
        Примерная логика сложности:
          lvl=1 => 2 персонажа, 2 высказывания
          lvl=2 => 3 персонажа, 3 высказывания
          lvl=3 => 4 персонажа, 5 высказываний
          ...
        """
        if lvl <= 1:
            return (2, 2)
        elif lvl == 2:
            return (3, 3)
        elif lvl == 3:
            return (4, 5)
        else:
            # при больших значениях ещё увеличиваем
            return (5, 7)

    def _number_to_text(self, n: int, language: str) -> str:
        """Преобразует число в текстовый формат на нужном языке."""
        if language == "ru":
            if n == 2:
                return "два"
            elif n == 3:
                return "три"
            elif n == 4:
                return "четыре"
            elif n == 5:
                return "пять"
            else:
                return str(n)
        else:
            if n == 2:
                return "two"
            elif n == 3:
                return "three"
            elif n == 4:
                return "four"
            elif n == 5:
                return "five"
            else:
                return str(n)

    def _create_problem_text(self):
        # Генерируем имена персонажей
        names = self._generate_names()
        
        # Определяем роли персонажей
        roles = self._generate_roles()
        
        # Генерируем высказывания
        statements = self._generate_statements(names, roles)
        
        # Получаем шаблоны для текущего языка
        templates = PROMPT_TEMPLATES["knights_knaves"].get(self.language, PROMPT_TEMPLATES["knights_knaves"]["en"])
        
        # Определяем правильное согласование для числа персонажей
        num_persons_text = self._number_to_text(self.num_persons, self.language)
        plural = "" if self.num_persons == 1 else "ей" if self.language == "ru" else "s"
        
        # Формируем текст задачи с расширенными инструкциями
        problem_text = templates["intro"].format(
            num_persons=num_persons_text,
            plural=plural,
            names=", ".join(names)
        )
        
        # Добавляем инструкции по решению
        problem_text += "\n\n" + templates["instructions"]
        
        # Добавляем пример решения
        problem_text += "\n\n" + templates["example"]
        
        # Добавляем высказывания персонажей
        problem_text += "\n\n" + templates["statements"].format(
            statements="\n".join(statements)
        )
        
        # Добавляем заключительную часть
        problem_text += "\n\n" + templates["conclusion"]
        
        return problem_text

    def _generate_random_statements(self, m: int):
        """
        Генерирует m высказываний. Каждое - dict:
          {
            "speaker": int,
            "text": str,
            "form_key": str,
            "y": int,
            "z": int or None
          }
        """
        forms_dict = PROMPT_TEMPLATES["knights_knaves"]["forms"][self.language]
        possible_forms = list(forms_dict.keys())  # [y_is_liar, y_is_honest, ...]

        statements = []
        for _ in range(m):
            speaker = random.randrange(self.num_persons)
            form_key = random.choice(possible_forms)

            # Выбираем y (и z) - разные от speaker
            all_others = [i for i in range(self.num_persons) if i != speaker]
            if not all_others:
                # fallback (если всего 1 персонаж - хотя такого не бывает по логике complexity)
                form_key = "y_is_liar"
                y_idx = speaker
                z_idx = None
            else:
                y_idx = random.choice(all_others)
                z_idx = None
                # Если форма требует двух distinct, пробуем взять z
                if form_key in ("y_and_z_both_honest", "y_and_z_both_liars", "y_eq_z", "y_neq_z"):
                    if len(all_others) < 2:
                        form_key = "y_is_liar"
                    else:
                        remain = [x for x in all_others if x != y_idx]
                        z_idx = random.choice(remain)

            st_text = self._build_statement_text(form_key, speaker, y_idx, z_idx)
            statements.append({
                "speaker": speaker,
                "form_key": form_key,
                "y": y_idx,
                "z": z_idx,
                "text": st_text
            })
        return statements

    def _build_statement_text(self, form_key, speaker, y_idx, z_idx):
        """
        Берём шаблон 'forms'[form_key], подставляем {nameY}, {nameZ} и оборачиваем в
        "{nameSpeaker} says: ..." (en) или "{nameSpeaker} говорит: ..." (ru)
        """
        kn_forms = PROMPT_TEMPLATES["knights_knaves"]["forms"][self.language]
        form_template = kn_forms[form_key]

        name_speaker = self.names[speaker]
        name_y = self.names[y_idx] if y_idx is not None else ""
        name_z = self.names[z_idx] if z_idx is not None else ""

        core_text = form_template.format(nameY=name_y, nameZ=name_z)

        if self.language == "ru":
            return f"{name_speaker} говорит: {core_text}"
        else:
            return f"{name_speaker} says: {core_text}"

    def solve(self):
        steps = []
        
        # Базовый шаг с общей стратегией
        base_step = PROMPT_TEMPLATES["knights_knaves"]["step1"].get(
            self.language, 
            PROMPT_TEMPLATES["knights_knaves"]["step1"]["en"]
        )
        steps.append(base_step)
        
        # Анализ каждого персонажа
        for i, name in enumerate(self.names):
            if self.language == "ru":
                step = f"Анализ высказывания {name}:\n"
                step += f"- {self.statements[i]}\n"
                step += f"- Возможные роли: {', '.join(['рыцарь', 'лжец'])}\n"
                step += f"- Логические следствия:"
            else:
                step = f"Analysis of {name}'s statement:\n"
                step += f"- {self.statements[i]}\n"
                step += f"- Possible roles: {', '.join(['knight', 'knave'])}\n"
                step += f"- Logical implications:"
            steps.append(step)
        
        # Анализ противоречий
        contradictions = self._find_contradictions()
        if contradictions:
            if self.language == "ru":
                step = "Найденные противоречия:\n"
                for c in contradictions:
                    step += f"- {c}\n"
            else:
                step = "Found contradictions:\n"
                for c in contradictions:
                    step += f"- {c}\n"
            steps.append(step)
        
        # Финальный вывод
        final_step = PROMPT_TEMPLATES["knights_knaves"]["final_step"].get(
            self.language,
            PROMPT_TEMPLATES["knights_knaves"]["final_step"]["en"]
        )
        steps.append(final_step)
        
        # Если нужно больше шагов, повторяем последний
        while len(steps) < self.detail_level:
            steps.append(steps[-1])
        
        self.solution_steps = steps
        
        # Формируем финальный ответ
        final_answer = PROMPT_TEMPLATES["knights_knaves"]["final_answer"].get(
            self.language,
            PROMPT_TEMPLATES["knights_knaves"]["final_answer"]["en"]
        )
        
        # Добавляем объяснение
        explanation = PROMPT_TEMPLATES["knights_knaves"]["explanation"].get(
            self.language,
            PROMPT_TEMPLATES["knights_knaves"]["explanation"]["en"]
        )
        
        # Формируем список ролей
        roles_list = []
        for name, role in zip(self.names, self.roles):
            if self.language == "ru":
                roles_list.append(f"{name}: {'рыцарь' if role == 'knight' else 'лжец'}")
            else:
                roles_list.append(f"{name}: {role}")
        
        self.final_answer = f"{final_answer.format(roles=', '.join(roles_list))}\n\n{explanation}"

    def _find_contradictions(self):
        """Находит противоречия в высказываниях персонажей"""
        contradictions = []
        for i, (name1, stmt1) in enumerate(zip(self.names, self.statements)):
            for j, (name2, stmt2) in enumerate(zip(self.names, self.statements)):
                if i < j:  # Проверяем только уникальные пары
                    if self._are_statements_contradictory(stmt1, stmt2):
                        contradictions.append(f"{name1} и {name2} противоречат друг другу")
        return contradictions

    def _are_statements_contradictory(self, stmt1, stmt2):
        """Проверяет, противоречат ли два высказывания друг другу"""
        # Здесь можно добавить более сложную логику проверки противоречий
        return False  # Заглушка

    def get_result(self):
        if not self.solution_steps or self.final_answer is None:
            self.solve()
        return {
            "problem": self.description,
            "prompt": self.generate_prompt(),
            "solution_steps": self.solution_steps,
            "final_answer": self.final_answer
        }

    def get_task_type(self):
        return "knights_knaves"
