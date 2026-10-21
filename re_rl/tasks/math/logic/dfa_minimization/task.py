"""DFAMinimizationTask — минимизация детерминированного конечного автомата.

Дан ДКА над алфавитом {a, b}; нужно найти число состояний эквивалентного
минимального ДКА (после удаления недостижимых состояний и слияния
неразличимых). Эталон — алгоритм Мура (разбиение по различимости).
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Set

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class DFAMinimizationTask(BaseMathTask):
    TASK_TYPE = "dfa_minimization"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"m": 3}, 2: {"m": 4}, 3: {"m": 4}, 4: {"m": 5}, 5: {"m": 6},
        6: {"m": 6}, 7: {"m": 7}, 8: {"m": 8}, 9: {"m": 9}, 10: {"m": 10},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.m = int(p["m"])
        self.alphabet = ["a", "b"]
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        self.delta = {s: {c: random.randrange(self.m) for c in self.alphabet}
                      for s in range(self.m)}
        self.accepting = set(s for s in range(self.m) if random.random() < 0.5)
        if not self.accepting or len(self.accepting) == self.m:
            self.accepting = {random.randrange(self.m)}
        self.answer = self._minimize()

    def _reachable(self) -> Set[int]:
        seen = {0}
        q = deque([0])
        while q:
            s = q.popleft()
            for c in self.alphabet:
                t = self.delta[s][c]
                if t not in seen:
                    seen.add(t)
                    q.append(t)
        return seen

    def _minimize(self) -> int:
        reach = self._reachable()
        # начальное разбиение: принимающие / непринимающие (среди достижимых)
        acc = frozenset(s for s in reach if s in self.accepting)
        non = frozenset(s for s in reach if s not in self.accepting)
        blocks = [b for b in (acc, non) if b]
        block_of = {}
        for i, b in enumerate(blocks):
            for s in b:
                block_of[s] = i
        changed = True
        while changed:
            changed = False
            new_blocks: List[frozenset] = []
            for b in blocks:
                # группируем по сигнатуре (block назначения по каждому символу)
                groups: Dict[tuple, list] = {}
                for s in b:
                    sig = tuple(block_of[self.delta[s][c]] for c in self.alphabet)
                    groups.setdefault(sig, []).append(s)
                if len(groups) == 1:
                    new_blocks.append(b)
                else:
                    changed = True
                    for g in groups.values():
                        new_blocks.append(frozenset(g))
            blocks = new_blocks
            block_of = {}
            for i, b in enumerate(blocks):
                for s in b:
                    block_of[s] = i
        return len(blocks)

    def _descr(self, language):
        trans = "; ".join(f"δ({s},{c})={self.delta[s][c]}"
                          for s in range(self.m) for c in self.alphabet)
        acc = ", ".join(map(str, sorted(self.accepting)))
        return ((texts.t('s0', language, v0=self.m - 1, acc=acc, trans=trans)))

    def solve(self):
        self.solution_steps = [
            ((texts.t('s1', self.language))),
            ((texts.t('s2', self.language, answer=self.answer)))]
        self.final_answer = str(self.answer)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
