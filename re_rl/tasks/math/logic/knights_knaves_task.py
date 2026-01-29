# re_rl/tasks/knights_knaves_task.py

import random
import z3
from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES
from typing import Optional, Dict, Any, ClassVar

class KnightsKnavesTask(BaseMathTask):
    """
    Генерирует задачу Knights & Knaves.
    
    Параметры сложности:
      - difficulty 1-2: 2 персонажа, простые высказывания
      - difficulty 3-4: 3 персонажа
      - difficulty 5-6: 4 персонажа
      - difficulty 7-8: 5 персонажей
      - difficulty 9-10: 6+ персонажей, сложные высказывания
    """
    
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"complexity": 1},
        2: {"complexity": 1},
        3: {"complexity": 2},
        4: {"complexity": 2},
        5: {"complexity": 3},
        6: {"complexity": 3},
        7: {"complexity": 4},
        8: {"complexity": 4},
        9: {"complexity": 5},
        10: {"complexity": 5},
    }

    def __init__(
        self,
        language: str = "en",
        detail_level: int = 3,
        complexity: int = None,
        difficulty: int = None
    ):
        """
        :param language: 'ru' или 'en'
        :param detail_level: сколько шагов chain-of-thought
        :param complexity: уровень сложности (задаёт num_persons, num_statements)
        :param difficulty: уровень сложности (1-10), альтернатива complexity
        """
        # Если указан difficulty, берём параметры из пресета
        if difficulty is not None:
            preset = self._interpolate_difficulty(difficulty)
            if complexity is None:
                complexity = preset.get("complexity", 2)
        elif complexity is None:
            complexity = 2
        
        self.language = language.lower()
        self.detail_level = detail_level
        self.complexity = complexity
        self.difficulty = difficulty
        self._output_format = output_format

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
        super().__init__(description, language, detail_level, output_format)

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
        self.names = self._generate_names()
        
        # Определяем роли персонажей
        self.roles = self._generate_roles()
        
        # Генерируем высказывания
        self.statements = self._generate_random_statements(self.num_statements)
        
        # Формируем текст задачи с расширенными инструкциями
        templates = PROMPT_TEMPLATES["knights_knaves"]
        
        # Добавляем инструкции по решению
        problem_text = templates["instructions"][self.language]
        
        # Добавляем представление персонажей
        plural = "ы" if self.num_persons > 1 else ""
        problem_text += "\n\n" + templates["intro"][self.language].format(
            names=", ".join(self.names),
            plural=plural,
            num_persons=self.num_persons
        )
        
        # Добавляем высказывания персонажей
        problem_text += "\n\n" + templates["problem"][self.language].format(
            statements="\n".join(stmt["text"] for stmt in self.statements)
        )
        
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
        possible_forms = ["about_self", "about_other", "and", "or", "same", "different", "at_least_one", "exactly_one"]

        statements = []
        for _ in range(m):
            speaker = random.randrange(self.num_persons)
            form_key = random.choice(possible_forms)

            # Выбираем y (и z) - разные от speaker
            all_others = [i for i in range(self.num_persons) if i != speaker]
            if not all_others:
                # fallback (если всего 1 персонаж - хотя такого не бывает по логике complexity)
                form_key = "about_self"
                y_idx = speaker
                z_idx = None
            else:
                y_idx = random.choice(all_others)
                z_idx = None
                # Если форма требует двух distinct, пробуем взять z
                if form_key in ("and", "or", "same", "different"):
                    if len(all_others) < 2:
                        form_key = "about_other"
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
        Берём шаблон 'forms'[form_key], подставляем параметры и оборачиваем в
        "{nameSpeaker} says: ..." (en) или "{nameSpeaker} говорит: ..." (ru)
        """
        kn_forms = PROMPT_TEMPLATES["knights_knaves"]["forms"][self.language]
        form_template = kn_forms[form_key]

        name_speaker = self.names[speaker]
        name_y = self.names[y_idx] if y_idx is not None else ""
        name_z = self.names[z_idx] if z_idx is not None else ""

        if form_key == "about_self":
            core_text = form_template.format(role="knight" if random.random() < 0.5 else "knave")
        elif form_key == "about_other":
            core_text = form_template.format(name=name_y, role="knight" if random.random() < 0.5 else "knave")
        elif form_key == "and":
            core_text = form_template.format(name=name_y, other_name=name_z, role="knight" if random.random() < 0.5 else "knave")
        elif form_key == "or":
            core_text = form_template.format(name=name_y, other_name=name_z, role="knight" if random.random() < 0.5 else "knave")
        elif form_key == "same":
            core_text = form_template.format(name=name_y, other_name=name_z)
        elif form_key == "different":
            core_text = form_template.format(name=name_y, other_name=name_z)
        elif form_key == "at_least_one":
            core_text = form_template.format(role="knight" if random.random() < 0.5 else "knave")
        else:  # exactly_one
            core_text = form_template.format(role="knight" if random.random() < 0.5 else "knave")

        statement_template = kn_forms["statement"]
        return statement_template.format(name=name_speaker, text=core_text)

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
            if len(steps) >= self.detail_level:
                break
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
        if len(steps) < self.detail_level:
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
        if len(steps) < self.detail_level:
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

    def get_result(self, detail_level: Optional[int] = None) -> Dict[str, Any]:
        """
        Возвращает результат решения с заданным уровнем детализации.
        
        Args:
            detail_level: Уровень детализации решения. Если не указан, используется self.detail_level
            
        Returns:
            Dict[str, Any]: Результат решения
        """
        if detail_level is None:
            detail_level = self.detail_level
            
        result = super().get_result()
        
        # Решаем задачу, если еще не решена
        if not self.solution_steps:
            self.solve()
            
        result["final_answer"] = self.final_answer
        return result

    def get_task_type(self):
        return "knights_knaves"

    def _generate_names(self):
        """
        Генерирует список имен персонажей.
        
        Returns:
            List[str]: Список имен
        """
        # Берём пул имён из prompts
        all_names = PROMPT_TEMPLATES["knights_knaves"]["names_pool"][self.language]
        random.shuffle(all_names)
        return all_names[:self.num_persons]

    def _generate_roles(self):
        """
        Генерирует роли персонажей (knight/knave).
        
        Returns:
            List[str]: Список ролей
        """
        roles = []
        for _ in range(self.num_persons):
            roles.append("knight" if random.random() < 0.5 else "knave")
        return roles

    def _generate_statements(self, names, roles):
        """
        Генерирует высказывания персонажей.
        
        Args:
            names: Список имен персонажей
            roles: Список ролей персонажей
            
        Returns:
            List[str]: Список высказываний
        """
        statements = []
        for i in range(self.num_statements):
            speaker = random.randrange(self.num_persons)
            form_key = random.choice(list(PROMPT_TEMPLATES["knights_knaves"]["forms"][self.language].keys()))
            
            # Выбираем y (и z) - разные от speaker
            all_others = [j for j in range(self.num_persons) if j != speaker]
            y_idx = random.choice(all_others)
            z_idx = None
            
            # Если форма требует двух distinct, пробуем взять z
            if form_key in ("y_and_z_both_honest", "y_and_z_both_liars", "y_eq_z", "y_neq_z"):
                if len(all_others) >= 2:
                    remain = [j for j in all_others if j != y_idx]
                    z_idx = random.choice(remain)
                else:
                    form_key = "y_is_liar"
            
            statement = self._build_statement_text(form_key, speaker, y_idx, z_idx)
            statements.append(statement)
            
        return statements
