"""MobileTorqueTask — подвес, в котором каждый стержень уравновешен.

Плечи подобраны так, что момент слева равен моменту справа, массы целые.
Одна гиря в условии скрыта. Число гирь растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import math
import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def build_mobile(leaves: int, limit: int) -> Tuple[dict, List[dict], List[dict]]:
    leaf_ids = [0]
    rod_ids = [0]
    leaf_list: List[dict] = []
    rod_list: List[dict] = []

    def build(count: int) -> dict:
        if count == 1:
            leaf_ids[0] += 1
            node = {"kind": "leaf", "id": leaf_ids[0], "mass": random.randint(1, limit)}
            leaf_list.append(node)
            return node
        cut = random.randint(1, count - 1)
        left = build(cut)
        right = build(count - cut)
        divisor = math.gcd(left["mass"], right["mass"])
        rod_ids[0] += 1
        node = {
            "kind": "rod",
            "id": rod_ids[0],
            "arm_l": right["mass"] // divisor,
            "arm_r": left["mass"] // divisor,
            "left": left,
            "right": right,
            "mass": left["mass"] + right["mass"],
        }
        rod_list.append(node)
        return node

    root = build(leaves)
    return root, leaf_list, rod_list


def rod_balanced(node: dict) -> bool:
    if node["kind"] == "leaf":
        return True
    left_ok = node["arm_l"] * node["left"]["mass"] == node["arm_r"] * node["right"]["mass"]
    return left_ok and rod_balanced(node["left"]) and rod_balanced(node["right"])


class MobileTorqueTask(BaseMathTask):
    TASK_TYPE = "mobile_torque"
    TASK_TYPES = ["hidden", "load"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 2, "m": 3}, 2: {"n": 2, "m": 4}, 3: {"n": 3, "m": 4},
        4: {"n": 3, "m": 5}, 5: {"n": 4, "m": 5}, 6: {"n": 5, "m": 5},
        7: {"n": 6, "m": 6}, 8: {"n": 7, "m": 6}, 9: {"n": 8, "m": 6},
        10: {"n": 10, "m": 6},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        limit = max(1, int(p["m"]))
        self.root, self.leaves, self.rods = build_mobile(self.n, limit)
        self.k = random.choice(self.leaves)["id"]
        self.hidden_mass = next(leaf["mass"] for leaf in self.leaves if leaf["id"] == self.k)
        self.load = self.root["mass"]
        self.answer = self.hidden_mass if self.task_type == "hidden" else self.load
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _ref(self, language: str, node: dict) -> str:
        key = "s6" if node["kind"] == "leaf" else "s7"
        return texts.t(key, language, i=node["id"])

    def _descr(self, language):
        parts = []
        for leaf in self.leaves:
            if leaf["id"] == self.k:
                parts.append(texts.t("s5", language, i=leaf["id"]))
            else:
                parts.append(texts.t("s4", language, i=leaf["id"], mass=leaf["mass"]))
        for rod in self.rods:
            parts.append(texts.t(
                "s3", language, i=rod["id"],
                al=rod["arm_l"], left=self._ref(language, rod["left"]),
                ar=rod["arm_r"], right=self._ref(language, rod["right"]),
            ))
        listing = " ".join(parts)
        key = "s0" if self.task_type == "hidden" else "s1"
        return texts.t(key, language, listing=listing, k=self.k)

    def _reduce(self, node: dict, steps: list) -> Optional[int]:
        if node["kind"] == "leaf":
            if node["id"] == self.k:
                return None
            return node["mass"]
        left_mass = self._reduce(node["left"], steps)
        right_mass = self._reduce(node["right"], steps)
        if left_mass is None:
            mass = node["arm_r"] * right_mass // node["arm_l"]
            steps.append(texts.t(
                "s8", self.language, k=self.k, rod=node["id"],
                arm_s=node["arm_r"], sibling=right_mass, arm_h=node["arm_l"], mass=mass,
            ))
            return mass + right_mass
        if right_mass is None:
            mass = node["arm_l"] * left_mass // node["arm_r"]
            steps.append(texts.t(
                "s8", self.language, k=self.k, rod=node["id"],
                arm_s=node["arm_l"], sibling=left_mass, arm_h=node["arm_r"], mass=mass,
            ))
            return left_mass + mass
        total = left_mass + right_mass
        steps.append(texts.t("s9", self.language, i=node["id"], left=left_mass, right=right_mass, total=total))
        return total

    def solve(self):
        steps = []
        total = self._reduce(self.root, steps)
        steps.append(texts.t("s10", self.language, hidden=self.hidden_mass, load=total))
        steps.append(texts.common("answer_line", self.language, answer=self.answer))
        self.solution_steps = steps
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, self.answer)

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
