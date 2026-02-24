import random
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class BayesianReasoningTask(BaseMathTask):
    """Bayesian and base-rate reasoning tasks."""

    TASK_TYPE = "bayesian_reasoning"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"task_type": "bayes_basic"},
        2: {"task_type": "bayes_basic"},
        3: {"task_type": "bayes_basic"},
        4: {"task_type": "base_rate"},
        5: {"task_type": "base_rate"},
        6: {"task_type": "base_rate"},
        7: {"task_type": "bayes_chain"},
        8: {"task_type": "bayes_chain"},
        9: {"task_type": "mixed"},
        10: {"task_type": "mixed"},
    }

    def __init__(
        self,
        task_type: Optional[str] = None,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.task_type = task_type or str(preset.get("task_type", "mixed"))
        if self.task_type == "mixed":
            self.task_type = random.choice(["bayes_basic", "base_rate", "bayes_chain"])
        self.augment = augment
        super().__init__("", language=language, detail_level=detail_level, output_format=output_format, reasoning_mode=reasoning_mode)

    def solve(self):
        section = PROMPT_TEMPLATES["bayesian_reasoning"]
        if self.task_type == "bayes_basic":
            p_d = random.choice([0.01, 0.02, 0.05, 0.1])
            sens = random.choice([0.85, 0.9, 0.95])
            spec = random.choice([0.9, 0.95, 0.98])
            self.description = get_template(
                section, "problem_basic", self.language, augment=self.augment, p_d=p_d, sens=sens, spec=spec
            )
            numerator = sens * p_d
            denominator = numerator + (1 - spec) * (1 - p_d)
            posterior = numerator / denominator
            self.solution_steps.append(get_template(section, "step_bayes_formula", self.language, augment=False))
            self.final_answer = f"P(D|+)={posterior:.4f}"
            return

        if self.task_type == "base_rate":
            p_d = random.choice([0.005, 0.01, 0.02])
            sens = random.choice([0.9, 0.95, 0.99])
            fpr = random.choice([0.02, 0.05, 0.1])
            self.description = get_template(
                section, "problem_base_rate", self.language, augment=self.augment, p_d=p_d, sens=sens, fpr=fpr
            )
            numerator = sens * p_d
            denominator = numerator + fpr * (1 - p_d)
            posterior = numerator / denominator
            self.solution_steps.append(get_template(section, "step_total_probability", self.language, augment=False))
            self.final_answer = f"P(D|+)={posterior:.4f}"
            return

        p_a = random.choice([0.2, 0.3, 0.4])
        p_b_a = random.choice([0.6, 0.7, 0.8])
        p_c_b = random.choice([0.7, 0.8, 0.9])
        p_b_not_a = random.choice([0.1, 0.2, 0.3])
        p_c_not_b = random.choice([0.1, 0.2, 0.3])
        self.description = get_template(
            section,
            "problem_chain",
            self.language,
            augment=self.augment,
            p_a=p_a,
            p_b_a=p_b_a,
            p_c_b=p_c_b,
            p_b_not_a=p_b_not_a,
            p_c_not_b=p_c_not_b,
        )
        p_b = p_b_a * p_a + p_b_not_a * (1 - p_a)
        p_c = p_c_b * p_b + p_c_not_b * (1 - p_b)
        self.solution_steps.append(get_template(section, "step_chain_rule", self.language, augment=False))
        self.final_answer = f"P(C)={p_c:.4f}"

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "BayesianReasoningTask":
        task = cls(
            language=language,
            detail_level=detail_level,
            difficulty=difficulty,
            reasoning_mode=reasoning_mode,
            augment=augment,
            **kwargs,
        )
        task.solve()
        return task
