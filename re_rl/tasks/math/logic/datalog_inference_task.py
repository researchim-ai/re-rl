"""Прямой логический вывод (forward chaining / Datalog).

Дана база фактов об объектах и правила вида «если объект обладает A и B,
то он обладает C». Применяя правила до неподвижной точки, нужно определить,
обладает ли объект целевым свойством, либо сколько объектов им обладают.
Масштаб задаётся числом объектов, свойств и правил.
"""

import random
import string
from typing import Any, ClassVar, Dict, List, Set, Tuple

from re_rl.tasks.base_task import BaseMathTask
from re_rl.tasks.math.logic import _logic_utils as U


class DatalogInferenceTask(BaseMathTask):
    TASK_TYPE = "datalog_inference"
    TASK_TYPES = ["has_property", "count_with"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"objs": 2, "props": 4, "rules": 2}, 2: {"objs": 2, "props": 5, "rules": 3},
        3: {"objs": 3, "props": 5, "rules": 3}, 4: {"objs": 3, "props": 6, "rules": 4},
        5: {"objs": 4, "props": 6, "rules": 5}, 6: {"objs": 4, "props": 7, "rules": 6},
        7: {"objs": 5, "props": 8, "rules": 7}, 8: {"objs": 5, "props": 9, "rules": 8},
        9: {"objs": 6, "props": 10, "rules": 10}, 10: {"objs": 7, "props": 11, "rules": 12},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format="text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.n_objs, self.n_props, self.n_rules = int(p["objs"]), int(p["props"]), int(p["rules"])
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.props = list(string.ascii_uppercase[:self.n_props])
        self.objects = [f"o{i+1}" for i in range(self.n_objs)]
        # Первые треть свойств — базовые (могут быть фактами), остальные выводятся.
        n_base = max(2, self.n_props // 3)
        base = self.props[:n_base]
        derived = self.props[n_base:]

        # Правила: голова — выводимое свойство, тело — из «более ранних» свойств.
        self.rules: List[Tuple[List[str], str]] = []
        for head in derived:
            earlier = self.props[:self.props.index(head)]
            k = random.randint(1, min(2, len(earlier)))
            body = random.sample(earlier, k)
            self.rules.append((sorted(body), head))
        # Добираем дополнительные правила до нужного числа.
        while len(self.rules) < self.n_rules and derived:
            head = random.choice(derived)
            earlier = self.props[:self.props.index(head)]
            k = random.randint(1, min(2, len(earlier)))
            self.rules.append((sorted(random.sample(earlier, k)), head))
        random.shuffle(self.rules)

        # Факты: каждому объекту случайное подмножество базовых свойств.
        self.facts: Dict[str, Set[str]] = {}
        for o in self.objects:
            kf = random.randint(1, len(base))
            self.facts[o] = set(random.sample(base, kf))

        self.closure = {o: self._forward_chain(set(self.facts[o])) for o in self.objects}
        target_pool = derived if derived else self.props
        self.target = random.choice(target_pool)
        if self.task_type == "has_property":
            self.query_obj = random.choice(self.objects)
            self.answer_bool = self.target in self.closure[self.query_obj]
        else:  # count_with
            self.answer_int = sum(1 for o in self.objects if self.target in self.closure[o])

    def _forward_chain(self, known: Set[str]) -> Set[str]:
        changed = True
        while changed:
            changed = False
            for body, head in self.rules:
                if head not in known and all(b in known for b in body):
                    known.add(head)
                    changed = True
        return known

    def _fmt_rule(self, body, head, ru: bool) -> str:
        conj = " и " if ru else " and "
        b = conj.join(body)
        return (f"если объект обладает {b}, то он обладает {head}" if ru else
                f"if an object has {b}, then it has {head}")

    def _descr(self, language):
        ru = language == "ru"
        facts_lines = "\n".join(
            (f"- объект {o} обладает свойствами: " + ", ".join(sorted(self.facts[o]))) if ru else
            (f"- object {o} has properties: " + ", ".join(sorted(self.facts[o])))
            for o in self.objects)
        rules_lines = "\n".join("- " + self._fmt_rule(b, h, ru) for b, h in self.rules)
        if self.task_type == "has_property":
            q = (f"Вопрос: обладает ли объект {self.query_obj} свойством {self.target}? (да/нет)"
                 if ru else
                 f"Question: does object {self.query_obj} have property {self.target}? (yes/no)")
        else:
            q = (f"Вопрос: сколько объектов в итоге обладают свойством {self.target}?" if ru else
                 f"Question: how many objects end up having property {self.target}?")
        head = ("Факты:\n{f}\nПравила:\n{r}\n{q}" if ru else
                "Facts:\n{f}\nRules:\n{r}\n{q}")
        return head.format(f=facts_lines, r=rules_lines, q=q)

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Прямой вывод: применяем правила к фактам каждого объекта до неподвижной точки."
             if ru else
             "Forward chaining: apply rules to each object's facts until a fixpoint.")]
        if self.task_type == "has_property":
            cl = ", ".join(sorted(self.closure[self.query_obj]))
            self.solution_steps.append(
                (f"Замыкание для {self.query_obj}: {cl}." if ru else
                 f"Closure for {self.query_obj}: {cl}."))
            self.final_answer = ("да" if self.answer_bool else "нет") if ru else \
                ("yes" if self.answer_bool else "no")
        else:
            self.solution_steps.append(
                (f"Объектов со свойством {self.target}: {self.answer_int}." if ru else
                 f"Objects with property {self.target}: {self.answer_int}."))
            self.final_answer = str(self.answer_int)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        if self.task_type == "has_property":
            return U.verify_bool(prediction, self.answer_bool)
        return U.verify_int(prediction, int(self.answer_int))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
