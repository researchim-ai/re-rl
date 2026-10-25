"""TrieNodeTask — новые узлы префиксного дерева.

Слова состоят из символов 0 и 1. Общий префикс новых узлов не создаёт. Корень не считается.
Число слов растёт с уровнем.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Sequence, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

Word = Tuple[int, int]


def trie_trace(words: Sequence[Word]) -> List[Tuple[int, int]]:
    root: Dict[int, Dict] = {}
    nodes = 0
    fresh = 0
    trace = []
    for word in words:
        node = root
        created = 0
        for symbol in word:
            if symbol not in node:
                node[symbol] = {}
                nodes += 1
                created += 1
            node = node[symbol]
        if created:
            fresh += 1
        trace.append((nodes, fresh))
    return trace


class TrieNodeTask(BaseMathTask):
    TASK_TYPE = "trie_node"
    TASK_TYPES = ["nodes", "fresh"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 4}, 4: {"n": 5},
        5: {"n": 6}, 6: {"n": 7}, 7: {"n": 8}, 8: {"n": 10},
        9: {"n": 12}, 10: {"n": 14},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self.n = max(2, int(p["n"]))
        self.words = [(random.randint(0, 1), random.randint(0, 1)) for _ in range(self.n)]
        self.trace = trie_trace(self.words)
        self.nodes = self.trace[-1][0]
        self.fresh = self.trace[-1][1]
        self.answer = self.nodes if self.task_type == "nodes" else self.fresh
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        shown = "; ".join(f"{left} {right}" for left, right in self.words)
        key = "s0" if self.task_type == "nodes" else "s1"
        return texts.t(key, language, n=self.n, words=shown)

    def solve(self):
        steps = [
            texts.t("s2", self.language, i=index, left=left, right=right, nodes=nodes, fresh=fresh)
            for index, ((left, right), (nodes, fresh)) in enumerate(zip(self.words, self.trace), 1)
        ]
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
