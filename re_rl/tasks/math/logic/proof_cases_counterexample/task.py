from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)

import random
from typing import Any, ClassVar, Dict, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template


class ProofCasesCounterexampleTask(BaseMathTask):
    """Tasks in form 'prove or provide counterexample'."""

    TASK_TYPE = texts.literal('literals.s0')

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"task_type": "parity_quadratic", "truth_bias": 0.8},
        2: {"task_type": "parity_quadratic", "truth_bias": 0.7},
        3: {"task_type": "divisibility_linear", "truth_bias": 0.7},
        4: {"task_type": "divisibility_linear", "truth_bias": 0.6},
        5: {"task_type": "modular_claim", "truth_bias": 0.5},
        6: {"task_type": "modular_claim", "truth_bias": 0.5},
        7: {"task_type": "factorization_form", "truth_bias": 0.5},
        8: {"task_type": "factorization_form", "truth_bias": 0.4},
        9: {"task_type": "mixed", "truth_bias": 0.5},
        10: {"task_type": "mixed", "truth_bias": 0.5},
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
        truth_bias: Optional[float] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.task_type = task_type or str(preset.get("task_type", "mixed"))
        self.truth_bias = truth_bias if truth_bias is not None else float(preset.get("truth_bias", 0.5))
        self.augment = augment
        super().__init__("", language=language, detail_level=detail_level, output_format=output_format, reasoning_mode=reasoning_mode)

    def _build_claim(self) -> Dict[str, Any]:
        mode = self.task_type
        if mode == "mixed":
            mode = random.choice(["parity_quadratic", "divisibility_linear", "modular_claim", "factorization_form"])

        true_case = random.random() < self.truth_bias
        if mode == "parity_quadratic":
            if true_case:
                return {
                    "claim": texts.t('s7', self.language),
                    "truth": True,
                    "counterexample": None,
                }
            return {
                "claim": texts.t('s3', self.language),
                "truth": False,
                "counterexample": 0,
            }
        if mode == "divisibility_linear":
            if true_case:
                return {
                    "claim": texts.t('s8', self.language),
                    "truth": True,
                    "counterexample": None,
                }
            return {
                "claim": texts.t('s4', self.language),
                "truth": False,
                "counterexample": 1,
            }
        if mode == "modular_claim":
            if true_case:
                return {
                    "claim": texts.t('s9', self.language),
                    "truth": True,
                    "counterexample": None,
                }
            return {
                "claim": texts.t('s5', self.language),
                "truth": False,
                "counterexample": 3,
            }
        if true_case:
            return {
                "claim": texts.t('s6', self.language),
                "truth": True,
                "counterexample": None,
            }
        return {
            "claim": texts.t('s1', self.language),
            "truth": False,
            "counterexample": 2,
        }

    def solve(self):
        section = PROMPT_TEMPLATES[texts.t('s2', self.language)]
        data = self._build_claim()
        self.description = get_template(section, "problem", self.language, augment=self.augment, claim=data["claim"])
        self.solution_steps.append(get_template(section, "step_cases", self.language, augment=False))
        if data["truth"]:
            self.solution_steps.append(get_template(section, "step_prove", self.language, augment=False))
            self.final_answer = "TRUE"
        else:
            self.solution_steps.append(
                get_template(section, "step_counterexample", self.language, augment=False).format(n=data["counterexample"])
            )
            self.final_answer = f"FALSE;n={data['counterexample']}"

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "ProofCasesCounterexampleTask":
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
