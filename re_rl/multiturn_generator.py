"""
Генератор multi-turn диалогов для обучения LLM.

Поддерживает 4 типа диалогов:
- chain: Последовательные задачи (результат предыдущей используется в следующей)
- followup: Уточняющие вопросы (объяснения, альтернативные методы)
- variations: Вариации задачи (изменение параметров)
- correction: Исправление ошибок (для RLHF)
"""

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
            system_prompt = get_prompt("common", "system_step_by_step", language)
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
            step = f"сложение {a} + {b} = {result}" if lang == "ru" else f"addition {a} + {b} = {result}"
        elif op == "-":
            result = a - b
            expr = f"{a} - {b}"
            step = f"вычитание {a} - {b} = {result}" if lang == "ru" else f"subtraction {a} - {b} = {result}"
        else:
            result = a * b
            expr = f"{a} * {b}"
            step = f"умножение {a} * {b} = {result}" if lang == "ru" else f"multiplication {a} * {b} = {result}"
        
        user_msg = get_prompt("chain", "first_task", lang, expression=expr)
        dialogue.add_user(user_msg)
        
        if reasoning_mode:
            assistant_msg = f"<think>\n{step}\n</think>\n<answer>{result}</answer>"
        else:
            answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
            assistant_msg = f"{step}\n\n{answer_prefix} {result}"
        dialogue.add_assistant(assistant_msg)
        
        # Последующие turns
        current_result = result
        operations = [
            ("continue_add", lambda x, v: x + v, lambda x, v, l: f"сложение {x} + {v} = {x + v}" if l == "ru" else f"addition {x} + {v} = {x + v}"),
            ("continue_subtract", lambda x, v: x - v, lambda x, v, l: f"вычитание {x} - {v} = {x - v}" if l == "ru" else f"subtraction {x} - {v} = {x - v}"),
            ("continue_multiply", lambda x, v: x * v, lambda x, v, l: f"умножение {x} * {v} = {x * v}" if l == "ru" else f"multiplication {x} * {v} = {x * v}"),
        ]
        
        for _ in range(turns - 1):
            op_key, op_func, step_func = random.choice(operations)
            value = random.randint(2, 10 + difficulty)
            
            # Избегаем деления на ноль и слишком больших чисел
            if op_key == "continue_multiply" and abs(current_result) > 1000:
                op_key = "continue_add"
                op_func = lambda x, v: x + v
                step_func = lambda x, v, l: f"сложение {x} + {v} = {x + v}" if l == "ru" else f"addition {x} + {v} = {x + v}"
            
            user_msg = get_prompt("chain", op_key, lang, value=value)
            dialogue.add_user(user_msg)
            
            new_result = op_func(current_result, value)
            step_text = step_func(current_result, value, lang)
            
            if reasoning_mode:
                assistant_msg = f"<think>\n{step_text}\n</think>\n<answer>{new_result}</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
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
            
            step1 = f"Переносим {b}: {a}x = {c} - {b} = {c - b}" if lang == "ru" else f"Move {b}: {a}x = {c} - {b} = {c - b}"
            step2 = f"Делим на {a}: x = {c - b}/{a} = {x}" if lang == "ru" else f"Divide by {a}: x = {c - b}/{a} = {x}"
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
            step1 = f"D = {b}² - 4·1·{c} = {D}" if lang == "ru" else f"D = {b}² - 4·1·{c} = {D}"
            step2 = f"x₁ = {x1}, x₂ = {x2}"
            steps = f"{step1}\n{step2}"
        
        user_msg = get_prompt("chain", "chain_equation_first", lang, equation=equation)
        dialogue.add_user(user_msg)
        
        if reasoning_mode:
            assistant_msg = f"<think>\n{steps}\n</think>\n<answer>x = {x}</answer>"
        else:
            answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
            assistant_msg = f"{steps}\n\n{answer_prefix} x = {x}"
        dialogue.add_assistant(assistant_msg)
        
        # Продолжаем с подстановками
        current_value = x
        for i in range(turns - 1):
            multiplier = random.randint(2, 5)
            addend = random.randint(-10, 10)
            expression = f"{multiplier}x + {addend}" if addend >= 0 else f"{multiplier}x - {abs(addend)}"
            
            user_msg = get_prompt("chain", "chain_equation_substitute", lang, expression=expression)
            dialogue.add_user(user_msg)
            
            result = multiplier * current_value + addend
            step_text = f"{multiplier} × {current_value} + {addend} = {result}" if lang == "ru" else f"{multiplier} × {current_value} + {addend} = {result}"
            
            if reasoning_mode:
                assistant_msg = f"<think>\nПодставляем x = {current_value}:\n{step_text}\n</think>\n<answer>{result}</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
                subst_text = "Подставляем" if lang == "ru" else "Substituting"
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
            problem = f"Тело движется с начальной скоростью {v0} м/с и ускорением {a} м/с². Найдите скорость через {t} с." if lang == "ru" else \
                      f"A body moves with initial velocity {v0} m/s and acceleration {a} m/s². Find the velocity after {t} s."
            
            steps = f"v = v₀ + at = {v0} + {a}×{t} = {v} м/с" if lang == "ru" else \
                    f"v = v₀ + at = {v0} + {a}×{t} = {v} m/s"
            
            user_msg = get_prompt("chain", "chain_physics_first", lang, problem=problem)
            dialogue.add_user(user_msg)
            
            if reasoning_mode:
                assistant_msg = f"<think>\n{steps}\n</think>\n<answer>{v} м/с</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
                assistant_msg = f"{steps}\n\n{answer_prefix} {v} м/с"
            dialogue.add_assistant(assistant_msg)
            
            # Второй turn: найти перемещение
            if turns >= 2:
                s = v0 * t + a * t * t / 2
                quantity = "перемещение за это время" if lang == "ru" else "displacement during this time"
                user_msg = get_prompt("chain", "chain_physics_continue", lang, quantity=quantity)
                dialogue.add_user(user_msg)
                
                steps = f"s = v₀t + at²/2 = {v0}×{t} + {a}×{t}²/2 = {v0*t} + {a*t*t/2} = {s} м" if lang == "ru" else \
                        f"s = v₀t + at²/2 = {v0}×{t} + {a}×{t}²/2 = {v0*t} + {a*t*t/2} = {s} m"
                
                if reasoning_mode:
                    assistant_msg = f"<think>\n{steps}\n</think>\n<answer>{s} м</answer>"
                else:
                    answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
                    assistant_msg = f"{steps}\n\n{answer_prefix} {s} м"
                dialogue.add_assistant(assistant_msg)
            
            # Третий turn: что если изменить параметр
            if turns >= 3:
                new_a = a * 2
                user_msg = get_prompt("chain", "chain_physics_what_if", lang, 
                                     parameter="ускорение" if lang == "ru" else "acceleration",
                                     new_value=f"{new_a} м/с²")
                dialogue.add_user(user_msg)
                
                new_v = v0 + new_a * t
                new_s = v0 * t + new_a * t * t / 2
                
                if lang == "ru":
                    steps = f"При a = {new_a} м/с²:\nv = {v0} + {new_a}×{t} = {new_v} м/с\ns = {v0}×{t} + {new_a}×{t}²/2 = {new_s} м"
                else:
                    steps = f"With a = {new_a} m/s²:\nv = {v0} + {new_a}×{t} = {new_v} m/s\ns = {v0}×{t} + {new_a}×{t}²/2 = {new_s} m"
                
                if reasoning_mode:
                    assistant_msg = f"<think>\n{steps}\n</think>\n<answer>v = {new_v} м/с, s = {new_s} м</answer>"
                else:
                    answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
                    assistant_msg = f"{steps}\n\n{answer_prefix} v = {new_v} м/с, s = {new_s} м"
                dialogue.add_assistant(assistant_msg)
        
        else:  # dynamics: F = ma
            m = random.randint(1, 10 + difficulty * 2)
            F = random.randint(10, 50 + difficulty * 10)
            a = round(F / m, 2)
            
            problem = f"На тело массой {m} кг действует сила {F} Н. Найдите ускорение." if lang == "ru" else \
                      f"A force of {F} N acts on a body of mass {m} kg. Find the acceleration."
            
            steps = f"F = ma → a = F/m = {F}/{m} = {a} м/с²"
            
            user_msg = get_prompt("chain", "chain_physics_first", lang, problem=problem)
            dialogue.add_user(user_msg)
            
            if reasoning_mode:
                assistant_msg = f"<think>\n{steps}\n</think>\n<answer>{a} м/с²</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
                assistant_msg = f"{steps}\n\n{answer_prefix} {a} м/с²"
            dialogue.add_assistant(assistant_msg)
            
            # Продолжение: найти скорость через время t
            if turns >= 2:
                t = random.randint(2, 10)
                v = round(a * t, 2)
                quantity = f"скорость через {t} с (начальная скорость 0)" if lang == "ru" else f"velocity after {t} s (initial velocity 0)"
                user_msg = get_prompt("chain", "chain_physics_continue", lang, quantity=quantity)
                dialogue.add_user(user_msg)
                
                steps = f"v = at = {a}×{t} = {v} м/с"
                
                if reasoning_mode:
                    assistant_msg = f"<think>\n{steps}\n</think>\n<answer>{v} м/с</answer>"
                else:
                    answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
                    assistant_msg = f"{steps}\n\n{answer_prefix} {v} м/с"
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
            system_prompt = get_prompt("common", "system_step_by_step", language)
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
                    assistant_msg = f"<think>\n{steps_text}\n</think>\n<answer>{final_answer}</answer>"
                else:
                    answer_prefix = "Ответ:" if language == "ru" else "Answer:"
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
                    "ru": "Я использовал формулу дискриминанта, потому что это стандартный метод решения квадратных уравнений. Он даёт все корни и позволяет определить их количество по знаку дискриминанта.",
                    "en": "I used the discriminant formula because it's the standard method for solving quadratic equations. It gives all roots and allows determining their number by the discriminant's sign."
                },
                "linear": {
                    "ru": "Я использовал метод переноса слагаемых и деления, потому что это самый прямой способ решения линейных уравнений.",
                    "en": "I used the method of moving terms and division because it's the most direct way to solve linear equations."
                },
                "kinematics": {
                    "ru": "Я использовал кинематические формулы равноускоренного движения, так как в задаче дано постоянное ускорение.",
                    "en": "I used kinematic equations for uniformly accelerated motion since the problem involves constant acceleration."
                }
            }
            
            explanation = method_explanations.get(task_type, {}).get(language, 
                "Этот метод наиболее подходит для данного типа задач." if language == "ru" else 
                "This method is most suitable for this type of problem.")
            dialogue.add_assistant(explanation)
        
        elif followup_type == "alternative_method":
            user_msg = get_prompt("followup", "alternative_method", language)
            dialogue.add_user(user_msg)
            
            alternatives = {
                "quadratic": {
                    "ru": "Да, можно также использовать разложение на множители или теорему Виета. Для уравнения x² + bx + c = 0 корни связаны соотношениями: x₁ + x₂ = -b и x₁ × x₂ = c.",
                    "en": "Yes, we can also use factoring or Vieta's formulas. For equation x² + bx + c = 0, the roots satisfy: x₁ + x₂ = -b and x₁ × x₂ = c."
                },
                "linear": {
                    "ru": "Можно решить графически — построить прямую y = ax + b и найти точку пересечения с горизонтальной прямой y = c.",
                    "en": "We can solve graphically — plot the line y = ax + b and find its intersection with the horizontal line y = c."
                },
                "arithmetic": {
                    "ru": "Можно группировать числа по-другому или использовать свойства операций (ассоциативность, коммутативность) для упрощения вычислений.",
                    "en": "We can group numbers differently or use operation properties (associativity, commutativity) to simplify calculations."
                }
            }
            
            alternative = alternatives.get(task_type, {}).get(language,
                "Для этой задачи использованный метод является оптимальным." if language == "ru" else
                "For this problem, the method used is optimal.")
            dialogue.add_assistant(alternative)
        
        elif followup_type == "check_answer":
            user_msg = get_prompt("followup", "check_answer", language)
            dialogue.add_user(user_msg)
            
            if language == "ru":
                check_text = f"Можно проверить подстановкой найденного значения в исходное уравнение/выражение. Если равенство выполняется — ответ верный."
            else:
                check_text = f"We can verify by substituting the found value into the original equation/expression. If the equality holds — the answer is correct."
            dialogue.add_assistant(check_text)
        
        elif followup_type == "edge_cases":
            user_msg = get_prompt("followup", "edge_cases", language)
            dialogue.add_user(user_msg)
            
            edge_cases = {
                "quadratic": {
                    "ru": "Особые случаи:\n- D < 0: нет вещественных корней\n- D = 0: один корень (кратный)\n- a = 0: уравнение становится линейным",
                    "en": "Edge cases:\n- D < 0: no real roots\n- D = 0: one root (repeated)\n- a = 0: equation becomes linear"
                },
                "linear": {
                    "ru": "Особые случаи:\n- a = 0 и b = c: бесконечно много решений\n- a = 0 и b ≠ c: нет решений",
                    "en": "Edge cases:\n- a = 0 and b = c: infinitely many solutions\n- a = 0 and b ≠ c: no solutions"
                },
                "kinematics": {
                    "ru": "Особые случаи:\n- a = 0: равномерное движение\n- v₀ = 0: движение из состояния покоя\n- t < 0: рассматриваем движение в прошлом",
                    "en": "Edge cases:\n- a = 0: uniform motion\n- v₀ = 0: motion from rest\n- t < 0: considering past motion"
                }
            }
            
            edge_case = edge_cases.get(task_type, {}).get(language,
                "Всегда проверяйте граничные значения параметров." if language == "ru" else
                "Always check boundary values of parameters.")
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
        
        problem = f"Вычислите: {a} × {b}" if lang == "ru" else f"Calculate: {a} × {b}"
        dialogue.add_user(problem)
        
        step = f"умножение {a} × {b} = {result}" if lang == "ru" else f"multiplication {a} × {b} = {result}"
        
        if reasoning_mode:
            assistant_msg = f"<think>\n{step}\n</think>\n<answer>{result}</answer>"
        else:
            answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
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
            system_prompt = get_prompt("common", "system_step_by_step", language)
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
        
        problem = f"Вычислите: {a} + {b}" if lang == "ru" else f"Calculate: {a} + {b}"
        dialogue.add_user(problem)
        
        step = f"сложение {a} + {b} = {result}" if lang == "ru" else f"addition {a} + {b} = {result}"
        
        if reasoning_mode:
            assistant_msg = f"<think>\n{step}\n</think>\n<answer>{result}</answer>"
        else:
            answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
            assistant_msg = f"{step}\n\n{answer_prefix} {result}"
        dialogue.add_assistant(assistant_msg)
        
        # Вариации
        variation_types = ["what_if_double", "what_if_param", "what_if_negative"]
        
        for i in range(num_variations):
            var_type = variation_types[i % len(variation_types)]
            
            if var_type == "what_if_double":
                param_name = "первое число" if lang == "ru" else "the first number"
                user_msg = get_prompt("variations", "what_if_double", lang, param_name=param_name)
                dialogue.add_user(user_msg)
                
                new_a = a * 2
                new_result = new_a + b
                step = f"{new_a} + {b} = {new_result}"
                
            elif var_type == "what_if_param":
                new_b = random.randint(50, 100)
                param_name = "второе число" if lang == "ru" else "the second number"
                user_msg = get_prompt("variations", "what_if_param", lang, param_name=param_name, new_value=new_b)
                dialogue.add_user(user_msg)
                
                new_result = a + new_b
                step = f"{a} + {new_b} = {new_result}"
                
            else:  # what_if_negative
                param_name = "второе число" if lang == "ru" else "the second number"
                user_msg = get_prompt("variations", "what_if_negative", lang, param_name=param_name)
                dialogue.add_user(user_msg)
                
                new_b = -b
                new_result = a + new_b
                step = f"{a} + ({new_b}) = {new_result}"
            
            if reasoning_mode:
                assistant_msg = f"<think>\n{step}\n</think>\n<answer>{new_result}</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
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
            problem = f"Решите уравнение: {equation}" if lang == "ru" else f"Solve the equation: {equation}"
            dialogue.add_user(problem)
            
            D = b*b - 4*c
            steps = f"D = 25 - 24 = 1\nx₁ = (5 + 1)/2 = 3\nx₂ = (5 - 1)/2 = 2"
            
            if reasoning_mode:
                assistant_msg = f"<think>\n{steps}\n</think>\n<answer>x = 2, x = 3</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
                assistant_msg = f"{steps}\n\n{answer_prefix} x = 2, x = 3"
            dialogue.add_assistant(assistant_msg)
            
            # Вариации
            for i in range(num_variations):
                if i == 0:
                    # Изменяем коэффициент b
                    new_b = -7
                    param_name = "коэффициент при x" if lang == "ru" else "coefficient of x"
                    user_msg = get_prompt("variations", "what_if_param", lang, param_name=param_name, new_value=new_b)
                    dialogue.add_user(user_msg)
                    
                    # x² - 7x + 6 = 0 -> x = 1, x = 6
                    new_D = 49 - 24
                    steps = f"x² - 7x + 6 = 0\nD = 49 - 24 = 25\nx₁ = (7 + 5)/2 = 6\nx₂ = (7 - 5)/2 = 1"
                    answer = "x = 1, x = 6"
                else:
                    # Что если D < 0
                    user_msg = get_prompt("followup", "when_no_solution", lang)
                    dialogue.add_user(user_msg)
                    
                    if lang == "ru":
                        steps = "Уравнение не имеет вещественных решений, когда D < 0.\nНапример, x² - 2x + 5 = 0: D = 4 - 20 = -16 < 0"
                        answer = "При D < 0 вещественных корней нет"
                    else:
                        steps = "The equation has no real solutions when D < 0.\nFor example, x² - 2x + 5 = 0: D = 4 - 20 = -16 < 0"
                        answer = "When D < 0, there are no real roots"
                
                if reasoning_mode:
                    assistant_msg = f"<think>\n{steps}\n</think>\n<answer>{answer}</answer>"
                else:
                    answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
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
        
        if lang == "ru":
            problem = f"Тело движется с начальной скоростью {v0} м/с и ускорением {a} м/с². Найдите скорость через {t} с."
        else:
            problem = f"A body moves with initial velocity {v0} m/s and acceleration {a} m/s². Find the velocity after {t} s."
        
        dialogue.add_user(problem)
        
        v = v0 + a * t
        steps = f"v = v₀ + at = {v0} + {a}×{t} = {v} м/с"
        
        if reasoning_mode:
            assistant_msg = f"<think>\n{steps}\n</think>\n<answer>{v} м/с</answer>"
        else:
            answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
            assistant_msg = f"{steps}\n\n{answer_prefix} {v} м/с"
        dialogue.add_assistant(assistant_msg)
        
        # Вариации
        for i in range(num_variations):
            if i == 0:
                # Удвоить ускорение
                param_name = "ускорение" if lang == "ru" else "acceleration"
                user_msg = get_prompt("variations", "what_if_double", lang, param_name=param_name)
                dialogue.add_user(user_msg)
                
                new_a = a * 2
                new_v = v0 + new_a * t
                steps = f"При a = {new_a} м/с²:\nv = {v0} + {new_a}×{t} = {new_v} м/с"
                answer = f"{new_v} м/с"
            else:
                # Отрицательное ускорение (торможение)
                param_name = "ускорение" if lang == "ru" else "acceleration"
                user_msg = get_prompt("variations", "what_if_negative", lang, param_name=param_name)
                dialogue.add_user(user_msg)
                
                new_a = -a
                new_v = v0 + new_a * t
                if lang == "ru":
                    steps = f"При отрицательном ускорении (торможение):\na = {new_a} м/с²\nv = {v0} + ({new_a})×{t} = {new_v} м/с"
                else:
                    steps = f"With negative acceleration (deceleration):\na = {new_a} m/s²\nv = {v0} + ({new_a})×{t} = {new_v} m/s"
                answer = f"{new_v} м/с" if lang == "ru" else f"{new_v} m/s"
            
            if reasoning_mode:
                assistant_msg = f"<think>\n{steps}\n</think>\n<answer>{answer}</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
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
            system_prompt = get_prompt("common", "system_step_by_step", language)
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
        
        problem = f"Вычислите: {a} × {b}" if lang == "ru" else f"Calculate: {a} × {b}"
        dialogue.add_user(problem)
        
        # Неправильный ответ
        wrong_step = f"умножение {a} × {b} = {wrong_result}" if lang == "ru" else f"multiplication {a} × {b} = {wrong_result}"
        
        if reasoning_mode:
            wrong_msg = f"<think>\n{wrong_step}\n</think>\n<answer>{wrong_result}</answer>"
        else:
            answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
            wrong_msg = f"{wrong_step}\n\n{answer_prefix} {wrong_result}"
        dialogue.add_assistant(wrong_msg)
        
        # Указание на ошибку
        correction_prompt = get_prompt("correction", "check_calculation", lang)
        dialogue.add_user(correction_prompt)
        
        # Исправленный ответ
        acknowledgment = get_prompt("correction", "correction_acknowledgment", lang)
        correct_step = f"умножение {a} × {b} = {correct_result}" if lang == "ru" else f"multiplication {a} × {b} = {correct_result}"
        
        if reasoning_mode:
            correct_msg = f"{acknowledgment}\n<think>\n{correct_step}\n</think>\n<answer>{correct_result}</answer>"
        else:
            answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
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
            
            problem = f"Решите уравнение: {equation}" if lang == "ru" else f"Solve the equation: {equation}"
            dialogue.add_user(problem)
            
            # Неправильное решение (ошибка в дискриминанте)
            if lang == "ru":
                wrong_steps = "D = 25 - 24 = 1\nx₁ = (5 + 1)/2 = 3\nx₂ = (5 - 1)/2 = 4  ← ошибка!"
            else:
                wrong_steps = "D = 25 - 24 = 1\nx₁ = (5 + 1)/2 = 3\nx₂ = (5 - 1)/2 = 4  ← error!"
            
            if reasoning_mode:
                wrong_msg = f"<think>\n{wrong_steps}\n</think>\n<answer>{wrong_answer}</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
                wrong_msg = f"{wrong_steps}\n\n{answer_prefix} {wrong_answer}"
            dialogue.add_assistant(wrong_msg)
            
            # Указание на ошибку
            correction_prompt = get_prompt("correction", "check_calculation", lang)
            dialogue.add_user(correction_prompt)
            
            # Исправление
            acknowledgment = get_prompt("correction", "correction_acknowledgment", lang)
            if lang == "ru":
                correct_steps = "D = 25 - 24 = 1\nx₁ = (5 + 1)/2 = 3\nx₂ = (5 - 1)/2 = 2  ✓"
            else:
                correct_steps = "D = 25 - 24 = 1\nx₁ = (5 + 1)/2 = 3\nx₂ = (5 - 1)/2 = 2  ✓"
            
            if reasoning_mode:
                correct_msg = f"{acknowledgment}\n<think>\n{correct_steps}\n</think>\n<answer>{correct_answer}</answer>"
            else:
                answer_prefix = "Ответ:" if lang == "ru" else "Answer:"
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
                iterator = tqdm(iterator, desc=f"Генерация {mode}", unit="диалогов")
            
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
                    elif mode in ["followup", "variations"]:
                        dialogue = generator_func(
                            task_type=task_type,
                            num_followups=turns - 1 if mode == "followup" else turns - 1,
                            num_variations=turns - 1 if mode == "variations" else turns - 1,
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
