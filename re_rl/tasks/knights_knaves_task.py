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

    def _create_problem_text(self) -> str:
        """
        Формируем строку с постановкой задачи:
          - intro (сколько персонажей, какие имена)
          - список высказываний
          - footer
        """
        kn_templates = PROMPT_TEMPLATES["knights_knaves"]
        intro_tmpl = kn_templates["intro"][self.language]
        line_fmt = kn_templates["line_format"][self.language]
        footer_tmpl = kn_templates["footer"][self.language]

        names_joined = ", ".join(self.names)
        num_persons_text = self._number_to_text(self.num_persons, self.language)
        
        # Добавляем правильное согласование
        if self.language == "ru":
            plural = "а" if self.num_persons == 1 else "ей"
        else:
            plural = "" if self.num_persons == 1 else "s"
            
        text = intro_tmpl.format(
            num_persons=num_persons_text,
            names=names_joined,
            plural=plural
        )

        # Добавляем каждое высказывание
        for st in self.statements:
            text += line_fmt.format(statement=st["text"]) + "\n"

        text += footer_tmpl
        return text

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
        """
        1) p[i]: True => knight, False => knave
        2) Для каждого высказывания st: 
             (p[speaker] => expr) AND (not p[speaker] => not expr)
        3) Проверяем sat / no solution
        4) Формируем chain-of-thought (solution_steps) согласно detail_level
        5) Формируем final_answer — список, кто knight, кто knave
        """
        p = [z3.Bool(f"p{i}") for i in range(self.num_persons)]
        solver = z3.Solver()

        for st in self.statements:
            expr = self._build_expr(st["form_key"], p, st["speaker"], st["y"], st["z"])
            solver.add(z3.Implies(p[st["speaker"]], expr))
            solver.add(z3.Implies(z3.Not(p[st["speaker"]]), z3.Not(expr)))

        result = solver.check()
        if result != z3.sat:
            # Contradictory
            no_sol_text = PROMPT_TEMPLATES["knights_knaves"]["no_solution"][self.language]
            self.solution_steps = [no_sol_text]
            self.final_answer = no_sol_text
            return

        # Считали модель
        model = solver.model()

        # Генерируем chain-of-thought (solution_steps)
        all_steps = PROMPT_TEMPLATES["knights_knaves"]["solution_steps"][self.language]
        steps_filled = []
        for i, step_text in enumerate(all_steps, start=1):
            replaced = step_text.format(n=self.num_persons, st_idx=i)
            steps_filled.append(replaced)
            
        # Добавляем шаги решения до достижения detail_level
        while len(steps_filled) < self.detail_level:
            steps_filled.append(steps_filled[-1])  # Повторяем последний шаг
            
        self.solution_steps = steps_filled[:self.detail_level]

        # Собираем финальный ответ (список ролей)
        roles = []
        for i in range(self.num_persons):
            val = model[p[i]]
            if self.language == "ru":
                role_str = "рыцарь" if val else "лжец"
            else:
                role_str = "knight" if val else "knave"
            roles.append(f"{self.names[i]}: {role_str}")

        self.final_answer = ", ".join(roles)

    def _build_expr(self, form_key, p, speaker, y, z):
        """Возвращает z3-выражение для содержимого высказывания."""
        if form_key == "y_is_liar":
            return z3.Not(p[y])
        elif form_key == "y_is_honest":
            return p[y]
        elif form_key == "y_and_z_both_honest":
            return z3.And(p[y], p[z])
        elif form_key == "y_and_z_both_liars":
            return z3.And(z3.Not(p[y]), z3.Not(p[z]))
        elif form_key == "y_eq_z":
            return p[y] == p[z]
        elif form_key == "y_neq_z":
            return p[y] != p[z]
        else:
            return z3.BoolVal(True)

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
