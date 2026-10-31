"""StableMatchingTask — устойчивые паросочетания (алгоритм Гейла–Шепли).

Подтипы:
- ``partner``   — с кем сопоставлен участник стороны P (предлагающей);
- ``is_stable`` — устойчиво ли данное паросочетание (нет блокирующей пары).

Сторона P предлагает, сторона A принимает. Очередь свободных изначально
P1..Pn, отвергнутый или вытесненный встаёт в конец. Предпочтения — строгие.
"""
from re_rl.tasks.i18n import TaskTexts
texts = TaskTexts(__file__)


import random
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class StableMatchingTask(BaseMathTask):
    TASK_TYPE = "stable_matching"
    TASK_TYPES = ["partner", "is_stable"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 3}, 2: {"n": 3}, 3: {"n": 3}, 4: {"n": 4}, 5: {"n": 4},
        6: {"n": 4}, 7: {"n": 5}, 8: {"n": 5}, 9: {"n": 5}, 10: {"n": 5},
    }

    def __init__(self, task_type: str = None, language="ru", detail_level=3, difficulty=5,
                 output_format: OutputFormat = "text", reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.task_type = (task_type or random.choice(self.TASK_TYPES)).lower()
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    # --- алгоритм ---
    @staticmethod
    def gale_shapley(prefs_p: List[List[int]], prefs_a: List[List[int]]):
        """Возвращает (match_p, log). match_p[m] = w. log — список событий."""
        n = len(prefs_p)
        rank_a = [{m: r for r, m in enumerate(prefs_a[j])} for j in range(n)]
        nxt = [0] * n
        free = list(range(n))
        match_a = [-1] * n
        log = []
        while free:
            m = free.pop(0)
            w = prefs_p[m][nxt[m]]
            nxt[m] += 1
            cur = match_a[w]
            if cur == -1:
                match_a[w] = m
                log.append((m, w, "accept", None))
            elif rank_a[w][m] < rank_a[w][cur]:
                match_a[w] = m
                free.append(cur)
                log.append((m, w, "replace", cur))
            else:
                free.append(m)
                log.append((m, w, "reject", cur))
        match_p = [0] * n
        for w, m in enumerate(match_a):
            match_p[m] = w
        return match_p, log

    @staticmethod
    def blocking_pair(match_p: List[int], prefs_p, prefs_a) -> Optional[Tuple[int, int]]:
        """Первая блокирующая пара (m, w) или None, если паросочетание устойчиво."""
        n = len(match_p)
        match_a = [-1] * n
        for m, w in enumerate(match_p):
            match_a[w] = m
        rank_p = [{w: r for r, w in enumerate(prefs_p[m])} for m in range(n)]
        rank_a = [{m: r for r, m in enumerate(prefs_a[w])} for w in range(n)]
        for m in range(n):
            for w in range(n):
                if (rank_p[m][w] < rank_p[m][match_p[m]]
                        and rank_a[w][m] < rank_a[w][match_a[w]]):
                    return (m, w)
        return None

    def _build(self):
        n = self.n
        self.prefs_p = [random.sample(range(n), n) for _ in range(n)]
        self.prefs_a = [random.sample(range(n), n) for _ in range(n)]
        gs, self.log = self.gale_shapley(self.prefs_p, self.prefs_a)
        if self.task_type == "partner":
            self.match = gs
            self.who = random.randrange(n)
            self.answer = self.match[self.who]
        else:
            match = gs
            if random.random() < 0.55:
                for _ in range(30):
                    perm = list(range(n))
                    random.shuffle(perm)
                    if self.blocking_pair(perm, self.prefs_p, self.prefs_a) is not None:
                        match = perm
                        break
            self.match = match
            self.block = self.blocking_pair(match, self.prefs_p, self.prefs_a)
            self.answer = self.block is None

    def _pname(self, i):
        return f"P{i + 1}"

    def _aname(self, i):
        return f"A{i + 1}"

    def _prefs_block(self) -> str:
        lines = []
        for i, prefs in enumerate(self.prefs_p):
            lines.append(f"{self._pname(i)}: " + " > ".join(self._aname(j) for j in prefs))
        for j, prefs in enumerate(self.prefs_a):
            lines.append(f"{self._aname(j)}: " + " > ".join(self._pname(i) for i in prefs))
        return "\n".join(lines)

    def _match_str(self, match) -> str:
        return ", ".join(f"{self._pname(m)}—{self._aname(w)}" for m, w in enumerate(match))

    def _descr(self, language):
        prefs = self._prefs_block()
        rule = ((texts.t('s0', language)))
        if self.task_type == "partner":
            who = self._pname(self.who)
            ask = ((texts.t('s1', language, who=who)))
        else:
            ask = ((texts.t('s2', language, v0=self._match_str(self.match))))
        return f"{rule}\n{prefs}\n{ask}"

    def _log_text(self) -> str:
        parts = []
        for m, w, kind, other in self.log:
            if kind == "accept":
                parts.append((texts.t('s9', self.language, v0=self._pname(m), v1=self._aname(w))))
            elif kind == "replace":
                parts.append((texts.t('s10', self.language, v0=self._pname(m), v1=self._aname(w), v2=self._pname(other))))
            else:
                parts.append((texts.t('s11', self.language, v0=self._pname(m), v1=self._aname(w))))
        return "; ".join(parts)

    def solve(self):
        from re_rl.tasks.reviewed_solvers import solve_reviewed
        solve_reviewed(self)

    def _solve_before_trace(self):
        if self.task_type == "partner":
            ans = self._aname(self.answer)
            steps = [
                ((texts.t('s3', self.language, v0=self._log_text()))),
                ((texts.t('s4', self.language, v0=self._match_str(self.match)))),
                ((texts.common('answer_line', self.language, answer=ans))),
            ]
            self.final_answer = ans
        else:
            if self.block is None:
                why = ((texts.t('s5', self.language)))
                ans = (texts.t('s6', self.language))
            else:
                m, w = self.block
                why = ((texts.t('s7', self.language, v0=self._pname(m), v1=self._aname(w))))
                ans = (texts.t('s8', self.language))
            steps = [why, ((texts.common('answer_line', self.language, answer=ans)))]
            self.final_answer = ans
        self.solution_steps = steps

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.task_type == "is_stable":
            return U.verify_bool(prediction, bool(self.answer))
        target = self._aname(self.answer).lower()
        tokens = U.normalize(prediction).split()
        return 1.0 if target in tokens else 0.0

    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
