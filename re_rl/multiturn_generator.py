"""
Генератор multi-turn диалогов для обучения LLM.

Поддерживает 4 типа диалогов:
- chain: Последовательные задачи (результат предыдущей используется в следующей)
- followup: Уточняющие вопросы (объяснения, альтернативные методы)
- variations: Вариации задачи (изменение параметров)
- correction: Исправление ошибок (для RLHF)
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__, 'multiturn_generator_i18n.json')


import random
import math
from typing import List, Dict, Any, Optional, Literal, Tuple
from dataclasses import dataclass, field

from re_rl.tasks.prompts import PROMPT_TEMPLATES
from re_rl.tasks.generators import ALL_TASK_GENERATORS
from re_rl.tasks.physics.generators import ALL_PHYSICS_TASK_GENERATORS


# Типы multi-turn диалогов
MultiturnMode = Literal["chain", "followup", "variations", "correction", "mixed"]


def get_prompt(category: str, key: str, language: str, **kwargs) -> str:
    """
    Получает промпт из PROMPT_TEMPLATES["multiturn"].
    
    Args:
        category: Категория (chain, followup, variations, correction, common)
        key: Ключ промпта
        language: Язык (ru/en)
        **kwargs: Параметры для форматирования
    
    Returns:
        Отформатированная строка промпта
    """
    templates = PROMPT_TEMPLATES.get("multiturn", {})
    category_templates = templates.get(category, {})
    template_dict = category_templates.get(key, {})
    
    template = template_dict.get(language, template_dict.get("en", f"[{category}.{key}]"))
    
    try:
        return template.format(**kwargs) if kwargs else template
    except KeyError:
        return template


@dataclass
class MultiturnDialogue:
    """Структура для хранения multi-turn диалога."""
    
    messages: List[Dict[str, str]] = field(default_factory=list)
    mode: str = "chain"
    language: str = "ru"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_user(self, content: str) -> "MultiturnDialogue":
        """Добавляет сообщение пользователя."""
        self.messages.append({"role": "user", "content": content})
        return self
    
    def add_assistant(self, content: str) -> "MultiturnDialogue":
        """Добавляет сообщение ассистента."""
        self.messages.append({"role": "assistant", "content": content})
        return self
    
    def add_system(self, content: str) -> "MultiturnDialogue":
        """Добавляет системное сообщение (в начало)."""
        self.messages.insert(0, {"role": "system", "content": content})
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует в словарь для сохранения."""
        return {
            "messages": self.messages,
            "metadata": {
                "mode": self.mode,
                "language": self.language,
                **self.metadata
            }
        }
    
    @property
    def num_turns(self) -> int:
        """Количество turns (пар user-assistant)."""
        return sum(1 for m in self.messages if m["role"] == "user")


class MultiturnGenerator:
    """
    Генератор multi-turn диалогов.
    
    Пример использования:
        generator = MultiturnGenerator()
        
        # Генерация цепочки арифметических задач
        dialogues = generator.generate_chain_dialogues(
            task_type="arithmetic",
            num_dialogues=100,
            turns=3,
            language="ru"
        )
        
        # Генерация диалогов с уточняющими вопросами
        dialogues = generator.generate_followup_dialogues(
            task_type="quadratic",
            num_dialogues=100,
            language="ru"
        )
        
        # Генерация смешанного датасета
        dataset = generator.generate_multiturn_dataset(
            modes=["chain", "followup", "variations", "correction"],
            num_samples=1000,
            language="ru"
        )
    """
    
    def __init__(self):
        self.all_generators = {**ALL_TASK_GENERATORS, **ALL_PHYSICS_TASK_GENERATORS}
        
        # Задачи, хорошо подходящие для каждого типа multi-turn
        self.chain_compatible = [
            "arithmetic", "linear", "quadratic", "kinematics", "dynamics"
        ]
        self.followup_compatible = list(self.all_generators.keys())
        self.variation_compatible = [
            "arithmetic", "linear", "quadratic", "cubic", "kinematics", 
            "dynamics", "projectile_motion", "energy"
        ]
        self.correction_compatible = [
            "arithmetic", "linear", "quadratic", "kinematics"
        ]
    
    # =========================================================================
    # CHAIN — Последовательные задачи
    # =========================================================================
    
    def generate_chain_dialogue(
        self,
        task_type: str = "arithmetic",
        turns: int = 3,
        language: str = "ru",
        difficulty: int = 5,
        reasoning_mode: bool = True,
    ) -> MultiturnDialogue:
        """
        Генерирует диалог с цепочкой связанных задач.
        
        Результат каждой задачи используется в следующей.
        """
        dialogue = MultiturnDialogue(mode="chain", language=language)
        dialogue.metadata["task_type"] = task_type
        dialogue.metadata["difficulty"] = difficulty
        dialogue.metadata["reasoning_mode"] = reasoning_mode
        
        # Добавляем системный промпт
        if reasoning_mode:
            system_prompt = get_prompt("common", "system_reasoning", language)
        else:
            system_prompt = get_prompt("common", texts.t('s75', language), language)
        dialogue.add_system(system_prompt)
        
        if task_type == "arithmetic":
            self._generate_arithmetic_chain(dialogue, turns, difficulty, reasoning_mode)
        elif task_type in ["linear", "quadratic"]:
            self._generate_equation_chain(dialogue, task_type, turns, difficulty, reasoning_mode)
        elif task_type in ["kinematics", "dynamics"]:
            self._generate_physics_chain(dialogue, task_type, turns, difficulty, reasoning_mode)
        else:
            # Fallback to arithmetic
            self._generate_arithmetic_chain(dialogue, turns, difficulty, reasoning_mode)
        
        return dialogue
    
    def _generate_arithmetic_chain(
        self,
        dialogue: MultiturnDialogue,
        turns: int,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует цепочку арифметических задач."""
        lang = dialogue.language
        
        # Начальные значения зависят от сложности
        max_num = 10 + difficulty * 10
        a = random.randint(1, max_num)
        b = random.randint(1, max_num)
        
        # Первая задача
        ops = ["+", "-", "*"]
        op = random.choice(ops)
        
        if op == "+":
            result = a + b
            expr = f"{a} + {b}"
            step = (texts.t('s9', lang, a=a, b=b, result=result))
        elif op == "-":
            result = a - b
            expr = f"{a} - {b}"
            step = (texts.t('s27', lang, a=a, b=b, result=result))
        else:
            result = a * b
            expr = f"{a} * {b}"
            step = (texts.t('s28', lang, a=a, b=b, result=result))
        
        user_msg = get_prompt("chain", "first_task", lang, expression=expr)
        dialogue.add_user(user_msg)
        
        if reasoning_mode:
            assistant_msg = texts.t('s62', dialogue.language, step=step, result=result)
        else:
            answer_prefix = (texts.t('s10', lang))
            assistant_msg = f"{step}\n\n{answer_prefix} {result}"
        dialogue.add_assistant(assistant_msg)
        
        # Последующие turns
        current_result = result
        operations = [
            ("continue_add", lambda x, v: x + v, lambda x, v, l: texts.t('s118', dialogue.language, x=x, v=v, v2=x + v) if l == "ru" else f"addition {x} + {v} = {x + v}"),
            ("continue_subtract", lambda x, v: x - v, lambda x, v, l: texts.t('s119', dialogue.language, x=x, v=v, v2=x - v) if l == "ru" else f"subtraction {x} - {v} = {x - v}"),
            ("continue_multiply", lambda x, v: x * v, lambda x, v, l: texts.t('s120', dialogue.language, x=x, v=v, v2=x * v) if l == "ru" else f"multiplication {x} * {v} = {x * v}"),
        ]
        
        for _ in range(turns - 1):
            op_key, op_func, step_func = random.choice(operations)
            value = random.randint(2, 10 + difficulty)
            
            # Избегаем деления на ноль и слишком больших чисел
            if op_key == "continue_multiply" and abs(current_result) > 1000:
                op_key = "continue_add"
                op_func = lambda x, v: x + v
                step_func = lambda x, v, l: texts.t('s121', dialogue.language, x=x, v=v, v2=x + v) if l == "ru" else f"addition {x} + {v} = {x + v}"
            
            user_msg = get_prompt("chain", op_key, lang, value=value)
            dialogue.add_user(user_msg)
            
            new_result = op_func(current_result, value)
            step_text = step_func(current_result, value, lang)
            
            if reasoning_mode:
                assistant_msg = texts.t('s76', dialogue.language, step_text=step_text, new_result=new_result)
            else:
                answer_prefix = (texts.t('s29', lang))
                assistant_msg = f"{step_text}\n\n{answer_prefix} {new_result}"
            
            dialogue.add_assistant(assistant_msg)
            current_result = new_result
    
    def _generate_equation_chain(
        self,
        dialogue: MultiturnDialogue,
        task_type: str,
        turns: int,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует цепочку уравнений."""
        lang = dialogue.language
        
        # Генерируем первое уравнение
        if task_type == "linear":
            a = random.randint(1, 5 + difficulty)
            b = random.randint(-10, 10)
            c = random.randint(-20, 20)
            # ax + b = c -> x = (c - b) / a
            x = (c - b) / a
            equation = f"{a}x + {b} = {c}" if b >= 0 else f"{a}x - {abs(b)} = {c}"
            
            step1 = (texts.t('s11', lang, b=b, a=a, c=c, b_2=b, v4=c - b))
            step2 = (texts.t('s12', lang, a=a, v1=c - b, a_2=a, x=x))
            steps = f"{step1}\n{step2}"
        else:  # quadratic
            # x^2 + bx + c = 0 с простыми корнями
            x1 = random.randint(-5, 5)
            x2 = random.randint(-5, 5)
            b = -(x1 + x2)
            c = x1 * x2
            equation = f"x² + {b}x + {c} = 0" if b >= 0 else f"x² - {abs(b)}x + {c} = 0"
            x = x1  # используем первый корень
            
            D = b*b - 4*c
            step1 = (f"D = {b}² - 4·1·{c} = {D}")
            step2 = f"x₁ = {x1}, x₂ = {x2}"
            steps = f"{step1}\n{step2}"
        
        user_msg = get_prompt("chain", texts.t('s63', dialogue.language), lang, equation=equation)
        dialogue.add_user(user_msg)
        
        if reasoning_mode:
            assistant_msg = texts.t('s64', dialogue.language, steps=steps, x=x)
        else:
            answer_prefix = (texts.t('s13', lang))
            assistant_msg = f"{steps}\n\n{answer_prefix} x = {x}"
        dialogue.add_assistant(assistant_msg)
        
        # Продолжаем с подстановками
        current_value = x
        for i in range(turns - 1):
            multiplier = random.randint(2, 5)
            addend = random.randint(-10, 10)
            expression = f"{multiplier}x + {addend}" if addend >= 0 else f"{multiplier}x - {abs(addend)}"
            
            user_msg = get_prompt("chain", texts.t('s77', dialogue.language), lang, expression=expression)
            dialogue.add_user(user_msg)
            
            result = multiplier * current_value + addend
            step_text = (texts.t('s14', lang, multiplier=multiplier, current_value=current_value, addend=addend, result=result))
            
            if reasoning_mode:
                assistant_msg = texts.t('s78', dialogue.language, current_value=current_value, step_text=step_text, result=result)
            else:
                answer_prefix = (texts.t('s30', lang))
                subst_text = (texts.t('s31', lang))
                assistant_msg = f"{subst_text} x = {current_value}:\n{step_text}\n\n{answer_prefix} {result}"
            
            dialogue.add_assistant(assistant_msg)
            current_value = result
    
    def _generate_physics_chain(
        self,
        dialogue: MultiturnDialogue,
        task_type: str,
        turns: int,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует цепочку физических задач."""
        lang = dialogue.language
        
        if task_type == "kinematics":
            # v = v0 + at, s = v0*t + at²/2
            v0 = random.randint(0, 10 + difficulty * 2)
            a = random.randint(1, 5 + difficulty)
            t = random.randint(1, 5 + difficulty)
            
            # Первая задача: найти скорость
            v = v0 + a * t
            problem = (texts.t('s15', lang, v0=v0, a=a, t=t))
            
            steps = (texts.t('s16', lang, v0=v0, a=a, t=t, v=v))
            
            user_msg = get_prompt("chain", texts.t('s79', dialogue.language), lang, problem=problem)
            dialogue.add_user(user_msg)
            
            if reasoning_mode:
                assistant_msg = texts.t('s80', dialogue.language, steps=steps, v=v)
            else:
                answer_prefix = (texts.t('s32', lang))
                assistant_msg = texts.t('s81', dialogue.language, steps=steps, answer_prefix=answer_prefix, v=v)
            dialogue.add_assistant(assistant_msg)
            
            # Второй turn: найти перемещение
            if turns >= 2:
                s = v0 * t + a * t * t / 2
                quantity = (texts.t('s33', lang))
                user_msg = get_prompt("chain", texts.t('s97', dialogue.language), lang, quantity=quantity)
                dialogue.add_user(user_msg)
                
                steps = (texts.t('s34', lang, v0=v0, t=t, a=a, t_2=t, v4=v0 * t, v5=a * t * t / 2, s=s))
                
                if reasoning_mode:
                    assistant_msg = texts.t('s98', dialogue.language, steps=steps, s=s)
                else:
                    answer_prefix = (texts.t('s50', lang))
                    assistant_msg = texts.t('s99', dialogue.language, steps=steps, answer_prefix=answer_prefix, s=s)
                dialogue.add_assistant(assistant_msg)
            
            # Третий turn: что если изменить параметр
            if turns >= 3:
                new_a = a * 2
                user_msg = get_prompt("chain", texts.t('s100', dialogue.language), lang, 
                                     parameter=(texts.t('s59', lang)),
                                     new_value=texts.t('s122', dialogue.language, new_a=new_a))
                dialogue.add_user(user_msg)
                
                new_v = v0 + new_a * t
                new_s = v0 * t + new_a * t * t / 2
                
                steps = texts.t('s17', lang, new_a=new_a, v0=v0, new_a_2=new_a, t=t, new_v=new_v, v0_2=v0, t_2=t, new_a_3=new_a, t_3=t, new_s=new_s)
                
                if reasoning_mode:
                    assistant_msg = texts.t('s101', dialogue.language, steps=steps, new_v=new_v, new_s=new_s)
                else:
                    answer_prefix = (texts.t('s51', lang))
                    assistant_msg = texts.t('s102', dialogue.language, steps=steps, answer_prefix=answer_prefix, new_v=new_v, new_s=new_s)
                dialogue.add_assistant(assistant_msg)
        
        else:  # dynamics: F = ma
            m = random.randint(1, 10 + difficulty * 2)
            F = random.randint(10, 50 + difficulty * 10)
            a = round(F / m, 2)
            
            problem = (texts.t('s18', lang, m=m, F=F))
            
            steps = texts.t('s65', dialogue.language, F=F, m=m, a=a)
            
            user_msg = get_prompt("chain", texts.t('s82', dialogue.language), lang, problem=problem)
            dialogue.add_user(user_msg)
            
            if reasoning_mode:
                assistant_msg = texts.t('s83', dialogue.language, steps=steps, a=a)
            else:
                answer_prefix = (texts.t('s35', lang))
                assistant_msg = texts.t('s84', dialogue.language, steps=steps, answer_prefix=answer_prefix, a=a)
            dialogue.add_assistant(assistant_msg)
            
            # Продолжение: найти скорость через время t
            if turns >= 2:
                t = random.randint(2, 10)
                v = round(a * t, 2)
                quantity = (texts.t('s36', lang, t=t))
                user_msg = get_prompt("chain", texts.t('s103', dialogue.language), lang, quantity=quantity)
                dialogue.add_user(user_msg)
                
                steps = texts.t('s85', dialogue.language, a=a, t=t, v=v)
                
                if reasoning_mode:
                    assistant_msg = texts.t('s104', dialogue.language, steps=steps, v=v)
                else:
                    answer_prefix = (texts.t('s52', lang))
                    assistant_msg = texts.t('s105', dialogue.language, steps=steps, answer_prefix=answer_prefix, v=v)
                dialogue.add_assistant(assistant_msg)
    
    # =========================================================================
    # FOLLOWUP — Уточняющие вопросы
    # =========================================================================
    
    def generate_followup_dialogue(
        self,
        task_type: str = "quadratic",
        num_followups: int = 2,
        language: str = "ru",
        difficulty: int = 5,
        reasoning_mode: bool = True,
    ) -> MultiturnDialogue:
        """
        Генерирует диалог с уточняющими вопросами после решения задачи.
        """
        dialogue = MultiturnDialogue(mode="followup", language=language)
        dialogue.metadata["task_type"] = task_type
        dialogue.metadata["difficulty"] = difficulty
        dialogue.metadata["reasoning_mode"] = reasoning_mode
        
        # Добавляем системный промпт
        if reasoning_mode:
            system_prompt = get_prompt("common", "system_reasoning", language)
        else:
            system_prompt = get_prompt("common", texts.t('s86', language), language)
        dialogue.add_system(system_prompt)
        
        # Генерируем основную задачу
        try:
            generator = self.all_generators.get(task_type)
            if generator:
                task = generator(language=language, difficulty=difficulty, detail_level=5)
                if hasattr(task, 'reasoning_mode'):
                    task.reasoning_mode = reasoning_mode
                task.solve()
                result = task.get_result()
                
                # Первый turn: задача
                dialogue.add_user(result["problem"])
                
                # Формируем ответ
                steps_text = "\n".join(result.get("solution_steps", []))
                final_answer = result["final_answer"]
                
                if reasoning_mode:
                    assistant_msg = texts.t('s106', language, steps_text=steps_text, final_answer=final_answer)
                else:
                    answer_prefix = (texts.t('s53', language))
                    assistant_msg = f"{steps_text}\n\n{answer_prefix} {final_answer}"
                dialogue.add_assistant(assistant_msg)
                
                # Генерируем уточняющие вопросы
                followup_types = ["why_method", "alternative_method", "check_answer", "edge_cases"]
                selected_followups = random.sample(followup_types, min(num_followups, len(followup_types)))
                
                for followup_type in selected_followups:
                    self._add_followup_turn(dialogue, followup_type, task_type, result, language, reasoning_mode)
                
            else:
                # Fallback: арифметическая задача
                self._generate_arithmetic_with_followups(dialogue, num_followups, difficulty, reasoning_mode)
                
        except Exception:
            # Fallback: арифметическая задача
            self._generate_arithmetic_with_followups(dialogue, num_followups, difficulty, reasoning_mode)
        
        return dialogue
    
    def _add_followup_turn(
        self,
        dialogue: MultiturnDialogue,
        followup_type: str,
        task_type: str,
        result: Dict[str, Any],
        language: str,
        reasoning_mode: bool
    ):
        """Добавляет один уточняющий вопрос и ответ."""
        
        if followup_type == "why_method":
            user_msg = get_prompt("followup", "why_method", language)
            dialogue.add_user(user_msg)
            
            # Генерируем объяснение в зависимости от типа задачи
            method_explanations = {
                "quadratic": {
                    "ru": texts.t('s107', language),
                    "en": texts.t('s108', language)
                },
                "linear": {
                    "ru": texts.t('s109', language),
                    "en": texts.t('s110', language)
                },
                "kinematics": {
                    "ru": texts.t('s111', language),
                    "en": texts.t('s112', language)
                }
            }
            
            explanation = method_explanations.get(task_type, {}).get(language, 
                (texts.t('s37', language)))
            dialogue.add_assistant(explanation)
        
        elif followup_type == "alternative_method":
            user_msg = get_prompt("followup", "alternative_method", language)
            dialogue.add_user(user_msg)
            
            alternatives = {
                "quadratic": {
                    "ru": texts.t('s123', language),
                    "en": texts.t('s124', language)
                },
                "linear": {
                    "ru": texts.t('s125', language),
                    "en": texts.t('s126', language)
                },
                "arithmetic": {
                    "ru": texts.t('s127', language),
                    "en": texts.t('s128', language)
                }
            }
            
            alternative = alternatives.get(task_type, {}).get(language,
                (texts.t('s54', language)))
            dialogue.add_assistant(alternative)
        
        elif followup_type == "check_answer":
            user_msg = get_prompt("followup", "check_answer", language)
            dialogue.add_user(user_msg)
            
            check_text = texts.t('s38', language)
            dialogue.add_assistant(check_text)
        
        elif followup_type == "edge_cases":
            user_msg = get_prompt("followup", "edge_cases", language)
            dialogue.add_user(user_msg)
            
            edge_cases = {
                "quadratic": {
                    "ru": texts.t('s135', language),
                    "en": texts.t('s136', language)
                },
                "linear": {
                    "ru": texts.t('s137', language),
                    "en": texts.t('s138', language)
                },
                "kinematics": {
                    "ru": texts.t('s139', language),
                    "en": texts.t('s140', language)
                }
            }
            
            edge_case = edge_cases.get(task_type, {}).get(language,
                (texts.t('s60', language)))
            dialogue.add_assistant(edge_case)
    
    def _generate_arithmetic_with_followups(
        self,
        dialogue: MultiturnDialogue,
        num_followups: int,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует арифметическую задачу с уточняющими вопросами."""
        lang = dialogue.language
        
        # Простая арифметическая задача
        a = random.randint(10, 50 + difficulty * 10)
        b = random.randint(5, 30 + difficulty * 5)
        result = a * b
        
        problem = (texts.t('s1', lang, a=a, b=b))
        dialogue.add_user(problem)
        
        step = (texts.t('s2', lang, a=a, b=b, result=result))
        
        if reasoning_mode:
            assistant_msg = texts.t('s66', dialogue.language, step=step, result=result)
        else:
            answer_prefix = (texts.t('s19', lang))
            assistant_msg = f"{step}\n\n{answer_prefix} {result}"
        dialogue.add_assistant(assistant_msg)
        
        # Уточняющие вопросы
        for _ in range(num_followups):
            self._add_followup_turn(dialogue, "alternative_method", "arithmetic", {"final_answer": result}, lang, reasoning_mode)
    
    # =========================================================================
    # VARIATIONS — Вариации задачи
    # =========================================================================
    
    def generate_variation_dialogue(
        self,
        task_type: str = "arithmetic",
        num_variations: int = 2,
        language: str = "ru",
        difficulty: int = 5,
        reasoning_mode: bool = True,
    ) -> MultiturnDialogue:
        """
        Генерирует диалог с вариациями исходной задачи.
        """
        dialogue = MultiturnDialogue(mode="variations", language=language)
        dialogue.metadata["task_type"] = task_type
        dialogue.metadata["difficulty"] = difficulty
        dialogue.metadata["reasoning_mode"] = reasoning_mode
        
        # Добавляем системный промпт
        if reasoning_mode:
            system_prompt = get_prompt("common", "system_reasoning", language)
        else:
            system_prompt = get_prompt("common", texts.t('s87', language), language)
        dialogue.add_system(system_prompt)
        
        if task_type == "arithmetic":
            self._generate_arithmetic_variations(dialogue, num_variations, difficulty, reasoning_mode)
        elif task_type in ["linear", "quadratic"]:
            self._generate_equation_variations(dialogue, task_type, num_variations, difficulty, reasoning_mode)
        elif task_type in ["kinematics", "dynamics"]:
            self._generate_physics_variations(dialogue, task_type, num_variations, difficulty, reasoning_mode)
        else:
            self._generate_arithmetic_variations(dialogue, num_variations, difficulty, reasoning_mode)
        
        return dialogue
    
    def _generate_arithmetic_variations(
        self,
        dialogue: MultiturnDialogue,
        num_variations: int,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует арифметические вариации."""
        lang = dialogue.language
        
        # Исходная задача
        a = random.randint(5, 20 + difficulty * 5)
        b = random.randint(5, 20 + difficulty * 5)
        result = a + b
        
        problem = (texts.t('s3', lang, a=a, b=b))
        dialogue.add_user(problem)
        
        step = (texts.t('s4', lang, a=a, b=b, result=result))
        
        if reasoning_mode:
            assistant_msg = texts.t('s67', dialogue.language, step=step, result=result)
        else:
            answer_prefix = (texts.t('s20', lang))
            assistant_msg = f"{step}\n\n{answer_prefix} {result}"
        dialogue.add_assistant(assistant_msg)
        
        # Вариации
        variation_types = [texts.t('s68', dialogue.language), texts.t('s69', dialogue.language), texts.t('s70', dialogue.language)]
        
        for i in range(num_variations):
            var_type = variation_types[i % len(variation_types)]
            
            if var_type == texts.t('s88', dialogue.language):
                param_name = (texts.t('s39', lang))
                user_msg = get_prompt("variations", texts.t('s113', dialogue.language), lang, param_name=param_name)
                dialogue.add_user(user_msg)
                
                new_a = a * 2
                new_result = new_a + b
                step = f"{new_a} + {b} = {new_result}"
                
            elif var_type == texts.t('s114', dialogue.language):
                new_b = random.randint(50, 100)
                param_name = (texts.t('s55', lang))
                user_msg = get_prompt("variations", texts.t('s129', dialogue.language), lang, param_name=param_name, new_value=new_b)
                dialogue.add_user(user_msg)
                
                new_result = a + new_b
                step = f"{a} + {new_b} = {new_result}"
                
            else:  # what_if_negative
                param_name = (texts.t('s56', lang))
                user_msg = get_prompt("variations", texts.t('s130', dialogue.language), lang, param_name=param_name)
                dialogue.add_user(user_msg)
                
                new_b = -b
                new_result = a + new_b
                step = f"{a} + ({new_b}) = {new_result}"
            
            if reasoning_mode:
                assistant_msg = texts.t('s89', dialogue.language, step=step, new_result=new_result)
            else:
                answer_prefix = (texts.t('s40', lang))
                assistant_msg = f"{step}\n\n{answer_prefix} {new_result}"
            dialogue.add_assistant(assistant_msg)
    
    def _generate_equation_variations(
        self,
        dialogue: MultiturnDialogue,
        task_type: str,
        num_variations: int,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует вариации уравнений."""
        lang = dialogue.language
        
        if task_type == "quadratic":
            # x² - 5x + 6 = 0 -> (x-2)(x-3) = 0
            b = -5
            c = 6
            x1, x2 = 2, 3
            
            equation = f"x² - 5x + 6 = 0"
            problem = (texts.t('s21', lang, equation=equation))
            dialogue.add_user(problem)
            
            D = b*b - 4*c
            steps = f"D = 25 - 24 = 1\nx₁ = (5 + 1)/2 = 3\nx₂ = (5 - 1)/2 = 2"
            
            if reasoning_mode:
                assistant_msg = texts.t('s90', dialogue.language, steps=steps)
            else:
                answer_prefix = (texts.t('s41', lang))
                assistant_msg = f"{steps}\n\n{answer_prefix} x = 2, x = 3"
            dialogue.add_assistant(assistant_msg)
            
            # Вариации
            for i in range(num_variations):
                if i == 0:
                    # Изменяем коэффициент b
                    new_b = -7
                    param_name = (texts.t('s57', lang))
                    user_msg = get_prompt("variations", texts.t('s131', dialogue.language), lang, param_name=param_name, new_value=new_b)
                    dialogue.add_user(user_msg)
                    
                    # x² - 7x + 6 = 0 -> x = 1, x = 6
                    new_D = 49 - 24
                    steps = f"x² - 7x + 6 = 0\nD = 49 - 24 = 25\nx₁ = (7 + 5)/2 = 6\nx₂ = (7 - 5)/2 = 1"
                    answer = "x = 1, x = 6"
                else:
                    # Что если D < 0
                    user_msg = get_prompt("followup", texts.t('s132', dialogue.language), lang)
                    dialogue.add_user(user_msg)
                    
                    steps = texts.t('s42', lang)
                    answer = texts.t('s43', lang)
                
                if reasoning_mode:
                    assistant_msg = texts.t('s115', dialogue.language, steps=steps, answer=answer)
                else:
                    answer_prefix = (texts.t('s58', lang))
                    assistant_msg = f"{steps}\n\n{answer_prefix} {answer}"
                dialogue.add_assistant(assistant_msg)
        else:
            # linear variations
            self._generate_arithmetic_variations(dialogue, num_variations, difficulty, reasoning_mode)
    
    def _generate_physics_variations(
        self,
        dialogue: MultiturnDialogue,
        task_type: str,
        num_variations: int,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует вариации физических задач."""
        lang = dialogue.language
        
        # Базовая задача кинематики
        v0 = 10
        a = 2
        t = 5
        
        problem = texts.t('s0', lang, v0=v0, a=a, t=t)
        
        dialogue.add_user(problem)
        
        v = v0 + a * t
        steps = texts.t('s61', dialogue.language, v0=v0, a=a, t=t, v=v)
        
        if reasoning_mode:
            assistant_msg = texts.t('s71', dialogue.language, steps=steps, v=v)
        else:
            answer_prefix = (texts.t('s22', lang))
            assistant_msg = texts.t('s72', dialogue.language, steps=steps, answer_prefix=answer_prefix, v=v)
        dialogue.add_assistant(assistant_msg)
        
        # Вариации
        for i in range(num_variations):
            if i == 0:
                # Удвоить ускорение
                param_name = (texts.t('s44', lang))
                user_msg = get_prompt("variations", texts.t('s116', dialogue.language), lang, param_name=param_name)
                dialogue.add_user(user_msg)
                
                new_a = a * 2
                new_v = v0 + new_a * t
                steps = texts.t('s91', dialogue.language, new_a=new_a, v0=v0, new_a_2=new_a, t=t, new_v=new_v)
                answer = texts.t('s92', dialogue.language, new_v=new_v)
            else:
                # Отрицательное ускорение (торможение)
                param_name = (texts.t('s45', lang))
                user_msg = get_prompt("variations", texts.t('s117', dialogue.language), lang, param_name=param_name)
                dialogue.add_user(user_msg)
                
                new_a = -a
                new_v = v0 + new_a * t
                steps = texts.t('s23', lang, new_a=new_a, v0=v0, new_a_2=new_a, t=t, new_v=new_v)
                answer = (texts.t('s46', lang, new_v=new_v))
            
            if reasoning_mode:
                assistant_msg = texts.t('s93', dialogue.language, steps=steps, answer=answer)
            else:
                answer_prefix = (texts.t('s47', lang))
                assistant_msg = f"{steps}\n\n{answer_prefix} {answer}"
            dialogue.add_assistant(assistant_msg)
    
    # =========================================================================
    # CORRECTION — Исправление ошибок
    # =========================================================================
    
    def generate_correction_dialogue(
        self,
        task_type: str = "arithmetic",
        language: str = "ru",
        difficulty: int = 5,
        reasoning_mode: bool = True,
    ) -> MultiturnDialogue:
        """
        Генерирует диалог с исправлением ошибки.
        
        Полезно для RLHF: модель сначала даёт неправильный ответ,
        получает feedback и исправляется.
        """
        dialogue = MultiturnDialogue(mode="correction", language=language)
        dialogue.metadata["task_type"] = task_type
        dialogue.metadata["difficulty"] = difficulty
        dialogue.metadata["reasoning_mode"] = reasoning_mode
        
        # Добавляем системный промпт
        if reasoning_mode:
            system_prompt = get_prompt("common", "system_reasoning", language)
        else:
            system_prompt = get_prompt("common", texts.t('s94', language), language)
        dialogue.add_system(system_prompt)
        
        if task_type == "arithmetic":
            self._generate_arithmetic_correction(dialogue, difficulty, reasoning_mode)
        elif task_type in ["linear", "quadratic"]:
            self._generate_equation_correction(dialogue, task_type, difficulty, reasoning_mode)
        else:
            self._generate_arithmetic_correction(dialogue, difficulty, reasoning_mode)
        
        return dialogue
    
    def _generate_arithmetic_correction(
        self,
        dialogue: MultiturnDialogue,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует арифметическую задачу с ошибкой и исправлением."""
        lang = dialogue.language
        
        # Задача
        a = random.randint(10, 30 + difficulty * 5)
        b = random.randint(10, 30 + difficulty * 5)
        correct_result = a * b
        
        # Типичная ошибка: ошибка в умножении
        wrong_result = correct_result + random.randint(1, 20) * random.choice([-1, 1])
        
        problem = (texts.t('s5', lang, a=a, b=b))
        dialogue.add_user(problem)
        
        # Неправильный ответ
        wrong_step = (texts.t('s6', lang, a=a, b=b, wrong_result=wrong_result))
        
        if reasoning_mode:
            wrong_msg = texts.t('s73', dialogue.language, wrong_step=wrong_step, wrong_result=wrong_result)
        else:
            answer_prefix = (texts.t('s24', lang))
            wrong_msg = f"{wrong_step}\n\n{answer_prefix} {wrong_result}"
        dialogue.add_assistant(wrong_msg)
        
        # Указание на ошибку
        correction_prompt = get_prompt("correction", "check_calculation", lang)
        dialogue.add_user(correction_prompt)
        
        # Исправленный ответ
        acknowledgment = get_prompt("correction", "correction_acknowledgment", lang)
        correct_step = (texts.t('s7', lang, a=a, b=b, correct_result=correct_result))
        
        if reasoning_mode:
            correct_msg = texts.t('s74', dialogue.language, acknowledgment=acknowledgment, correct_step=correct_step, correct_result=correct_result)
        else:
            answer_prefix = (texts.t('s25', lang))
            correct_msg = f"{acknowledgment}\n{correct_step}\n\n{answer_prefix} {correct_result}"
        dialogue.add_assistant(correct_msg)
    
    def _generate_equation_correction(
        self,
        dialogue: MultiturnDialogue,
        task_type: str,
        difficulty: int,
        reasoning_mode: bool
    ):
        """Генерирует уравнение с ошибкой и исправлением."""
        lang = dialogue.language
        
        if task_type == "quadratic":
            # x² - 5x + 6 = 0
            equation = "x² - 5x + 6 = 0"
            correct_answer = "x = 2, x = 3"
            wrong_answer = "x = 2, x = 4"  # Ошибка в вычислении
            
            problem = (texts.t('s26', lang, equation=equation))
            dialogue.add_user(problem)
            
            # Неправильное решение (ошибка в дискриминанте)
            wrong_steps = texts.t('s8', lang)
            
            if reasoning_mode:
                wrong_msg = texts.t('s95', dialogue.language, wrong_steps=wrong_steps, wrong_answer=wrong_answer)
            else:
                answer_prefix = (texts.t('s48', lang))
                wrong_msg = f"{wrong_steps}\n\n{answer_prefix} {wrong_answer}"
            dialogue.add_assistant(wrong_msg)
            
            # Указание на ошибку
            correction_prompt = get_prompt("correction", "check_calculation", lang)
            dialogue.add_user(correction_prompt)
            
            # Исправление
            acknowledgment = get_prompt("correction", "correction_acknowledgment", lang)
            correct_steps = "D = 25 - 24 = 1\nx₁ = (5 + 1)/2 = 3\nx₂ = (5 - 1)/2 = 2  ✓"
            
            if reasoning_mode:
                correct_msg = texts.t('s96', dialogue.language, acknowledgment=acknowledgment, correct_steps=correct_steps, correct_answer=correct_answer)
            else:
                answer_prefix = (texts.t('s49', lang))
                correct_msg = f"{acknowledgment}\n{correct_steps}\n\n{answer_prefix} {correct_answer}"
            dialogue.add_assistant(correct_msg)
        else:
            # Fallback to arithmetic
            self._generate_arithmetic_correction(dialogue, difficulty, reasoning_mode)
    
    # =========================================================================
    # Главные методы генерации датасетов
    # =========================================================================
    
    def generate_chain_dialogues(
        self,
        task_type: str = "arithmetic",
        num_dialogues: int = 100,
        turns: int = 3,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
    ) -> List[Dict[str, Any]]:
        """Генерирует датасет chain-диалогов."""
        if difficulties is None:
            difficulties = list(range(1, 11))
        
        dialogues = []
        for _ in range(num_dialogues):
            difficulty = random.choice(difficulties)
            dialogue = self.generate_chain_dialogue(
                task_type=task_type,
                turns=turns,
                language=language,
                difficulty=difficulty,
                reasoning_mode=reasoning_mode,
            )
            dialogues.append(dialogue.to_dict())
        
        return dialogues
    
    def generate_followup_dialogues(
        self,
        task_type: str = "quadratic",
        num_dialogues: int = 100,
        num_followups: int = 2,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
    ) -> List[Dict[str, Any]]:
        """Генерирует датасет followup-диалогов."""
        if difficulties is None:
            difficulties = list(range(1, 11))
        
        dialogues = []
        for _ in range(num_dialogues):
            difficulty = random.choice(difficulties)
            dialogue = self.generate_followup_dialogue(
                task_type=task_type,
                num_followups=num_followups,
                language=language,
                difficulty=difficulty,
                reasoning_mode=reasoning_mode,
            )
            dialogues.append(dialogue.to_dict())
        
        return dialogues
    
    def generate_variation_dialogues(
        self,
        task_type: str = "arithmetic",
        num_dialogues: int = 100,
        num_variations: int = 2,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
    ) -> List[Dict[str, Any]]:
        """Генерирует датасет variation-диалогов."""
        if difficulties is None:
            difficulties = list(range(1, 11))
        
        dialogues = []
        for _ in range(num_dialogues):
            difficulty = random.choice(difficulties)
            dialogue = self.generate_variation_dialogue(
                task_type=task_type,
                num_variations=num_variations,
                language=language,
                difficulty=difficulty,
                reasoning_mode=reasoning_mode,
            )
            dialogues.append(dialogue.to_dict())
        
        return dialogues
    
    def generate_correction_dialogues(
        self,
        task_type: str = "arithmetic",
        num_dialogues: int = 100,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
    ) -> List[Dict[str, Any]]:
        """Генерирует датасет correction-диалогов."""
        if difficulties is None:
            difficulties = list(range(1, 11))
        
        dialogues = []
        for _ in range(num_dialogues):
            difficulty = random.choice(difficulties)
            dialogue = self.generate_correction_dialogue(
                task_type=task_type,
                language=language,
                difficulty=difficulty,
                reasoning_mode=reasoning_mode,
            )
            dialogues.append(dialogue.to_dict())
        
        return dialogues
    
    def generate_multiturn_dataset(
        self,
        modes: Optional[List[MultiturnMode]] = None,
        task_types: Optional[List[str]] = None,
        num_samples: int = 1000,
        language: str = "ru",
        difficulties: Optional[List[int]] = None,
        reasoning_mode: bool = True,
        turns: int = 3,
        show_progress: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Генерирует смешанный multi-turn датасет.
        
        Args:
            modes: Типы диалогов ["chain", "followup", "variations", "correction"]
            task_types: Типы задач (None = подходящие для каждого mode)
            num_samples: Общее количество диалогов
            language: Язык
            difficulties: Уровни сложности
            reasoning_mode: Использовать <think>/<answer> теги
            turns: Количество turns для chain-диалогов
            show_progress: Показывать прогресс
        
        Returns:
            Список диалогов в формате chat
        """
        if modes is None:
            modes = ["chain", "followup", "variations", "correction"]
        
        if difficulties is None:
            difficulties = list(range(1, 11))
        
        try:
            from tqdm import tqdm
        except ImportError:
            def tqdm(x, **kwargs):
                return x
        
        samples_per_mode = num_samples // len(modes)
        dataset = []
        
        mode_generators = {
            "chain": (self.generate_chain_dialogue, self.chain_compatible),
            "followup": (self.generate_followup_dialogue, self.followup_compatible),
            "variations": (self.generate_variation_dialogue, self.variation_compatible),
            "correction": (self.generate_correction_dialogue, self.correction_compatible),
        }
        
        for mode in modes:
            generator_func, compatible_tasks = mode_generators[mode]
            
            # Выбираем задачи
            if task_types:
                selected_tasks = [t for t in task_types if t in compatible_tasks]
                if not selected_tasks:
                    selected_tasks = compatible_tasks[:3]
            else:
                selected_tasks = compatible_tasks[:5]
            
            iterator = range(samples_per_mode)
            if show_progress:
                iterator = tqdm(iterator, desc=texts.t('s133', language, mode=mode), unit=texts.t('s134', language))
            
            for _ in iterator:
                task_type = random.choice(selected_tasks)
                difficulty = random.choice(difficulties)
                
                try:
                    if mode == "chain":
                        dialogue = generator_func(
                            task_type=task_type,
                            turns=turns,
                            language=language,
                            difficulty=difficulty,
                            reasoning_mode=reasoning_mode,
                        )
                    elif mode == "followup":
                        dialogue = generator_func(
                            task_type=task_type,
                            num_followups=turns - 1,
                            language=language,
                            difficulty=difficulty,
                            reasoning_mode=reasoning_mode,
                        )
                    elif mode == "variations":
                        dialogue = generator_func(
                            task_type=task_type,
                            num_variations=turns - 1,
                            language=language,
                            difficulty=difficulty,
                            reasoning_mode=reasoning_mode,
                        )
                    else:  # correction
                        dialogue = generator_func(
                            task_type=task_type,
                            language=language,
                            difficulty=difficulty,
                            reasoning_mode=reasoning_mode,
                        )
                    
                    dataset.append(dialogue.to_dict())
                except Exception:
                    continue
        
        random.shuffle(dataset)
        return dataset[:num_samples]
