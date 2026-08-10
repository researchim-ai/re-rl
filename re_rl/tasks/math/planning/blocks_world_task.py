"""BlocksWorldTask — классическая задача планирования (blocks world / STRIPS).

Дано начальное и целевое расположение блоков в стопках; за один ход можно
переместить свободный (верхний) блок на стол или на другой свободный блок.
Нужно выдать корректную последовательность ходов.

Верификация проверяет *валидность* плана (симуляция ходов из начального
состояния приводит к целевому), а не совпадение со «своим» эталоном — планов
может быть много.
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Optional, Tuple

import re

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.prompts import PROMPT_TEMPLATES, get_template

State = Dict[str, str]  # block -> support ('table' или другой блок)


class BlocksWorldTask(BaseMathTask):
    """Планирование в мире блоков (валидация плана при проверке)."""

    TASK_TYPE = "blocks_world"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"num_blocks": 3},
        2: {"num_blocks": 3},
        3: {"num_blocks": 3},
        4: {"num_blocks": 4},
        5: {"num_blocks": 4},
        6: {"num_blocks": 4},
        7: {"num_blocks": 5},
        8: {"num_blocks": 5},
        9: {"num_blocks": 5},
        10: {"num_blocks": 6},
    }

    def __init__(
        self,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        output_format: OutputFormat = "text",
        reasoning_mode: bool = False,
        augment: bool = True,
        num_blocks: Optional[int] = None,
    ):
        preset = self._interpolate_difficulty(difficulty)
        self.num_blocks = int(num_blocks if num_blocks is not None else preset.get("num_blocks", 4))
        self.num_blocks = max(2, min(6, self.num_blocks))
        self.augment = augment

        self.blocks = [chr(ord("A") + i) for i in range(self.num_blocks)]
        self._init_state = self._random_config()
        self._goal_state = self._random_config()
        attempts = 0
        while self._goal_state == self._init_state and attempts < 50:
            self._goal_state = self._random_config()
            attempts += 1

        self._plan = self._bfs_plan(self._init_state, self._goal_state)

        description = get_template(
            PROMPT_TEMPLATES["blocks_world"], "problem", language,
            augment=augment,
            init=self._render_state(self._init_state),
            goal=self._render_state(self._goal_state),
        )
        super().__init__(
            description=description,
            language=language,
            detail_level=detail_level,
            output_format=output_format,
            reasoning_mode=reasoning_mode,
        )

    # ------------------------------------------------------------------
    # Генерация и представление состояний
    # ------------------------------------------------------------------
    def _random_config(self) -> State:
        order = self.blocks[:]
        random.shuffle(order)
        on: State = {}
        i = 0
        while i < len(order):
            stack_len = random.randint(1, len(order) - i)
            stack = order[i:i + stack_len]
            on[stack[0]] = "table"
            for j in range(1, len(stack)):
                on[stack[j]] = stack[j - 1]
            i += stack_len
        return on

    @staticmethod
    def _clear(state: State, block: str) -> bool:
        return all(support != block for support in state.values())

    def _render_state(self, state: State) -> str:
        bottoms = [b for b in self.blocks if state.get(b) == "table"]
        bottoms.sort()
        lines = []
        for bottom in bottoms:
            stack = [bottom]
            # Идём вверх по стопке.
            while True:
                top = stack[-1]
                nxt = [b for b in self.blocks if state.get(b) == top]
                if not nxt:
                    break
                stack.append(nxt[0])
            lines.append("  table -> " + " -> ".join(stack))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Планировщик (BFS)
    # ------------------------------------------------------------------
    @staticmethod
    def _key(state: State) -> Tuple:
        return tuple(sorted(state.items()))

    def _successors(self, state: State) -> List[Tuple[str, State]]:
        succ = []
        clear_blocks = [b for b in self.blocks if self._clear(state, b)]
        for b in clear_blocks:
            # На стол.
            if state[b] != "table":
                ns = dict(state)
                ns[b] = "table"
                succ.append((f"move {b} onto table", ns))
            # На другой свободный блок.
            for c in clear_blocks:
                if c == b or state[b] == c:
                    continue
                ns = dict(state)
                ns[b] = c
                succ.append((f"move {b} onto {c}", ns))
        return succ

    def _bfs_plan(self, init: State, goal: State) -> List[str]:
        if init == goal:
            return []
        goal_key = self._key(goal)
        start_key = self._key(init)
        visited = {start_key}
        queue = deque([(init, [])])
        while queue:
            state, path = queue.popleft()
            for move, ns in self._successors(state):
                k = self._key(ns)
                if k in visited:
                    continue
                new_path = path + [move]
                if k == goal_key:
                    return new_path
                visited.add(k)
                queue.append((ns, new_path))
        return []  # теоретически недостижимо для blocks world

    # ------------------------------------------------------------------
    def solve(self):
        section = PROMPT_TEMPLATES["blocks_world"]
        plan_str = "; ".join(self._plan) if self._plan else "no moves needed"
        self.solution_steps.append(get_template(section, "step_plan", self.language, augment=False, plan=plan_str))
        self.solution_steps.append(get_template(section, "result", self.language, augment=False, plan=plan_str))
        self.final_answer = plan_str

    # ------------------------------------------------------------------
    def _parse_moves(self, text: str) -> List[Tuple[str, str]]:
        moves = []
        pattern = re.compile(r"move\s+([A-Za-z])\s+(?:onto|on|to)\s+(table|стол|[A-Za-z])", re.IGNORECASE)
        for m in pattern.finditer(text):
            block = m.group(1).upper()
            target = m.group(2)
            target = "table" if target.lower() in ("table", "стол") else target.upper()
            moves.append((block, target))
        return moves

    def verify(self, prediction: str) -> float:
        """Симулирует план из предсказания; 1.0, если достигнуто целевое состояние."""
        from re_rl.rewards import extract_reasoning_and_answer

        if self.final_answer is None:
            self.solve()

        _, answer = extract_reasoning_and_answer(prediction)
        text = answer or prediction
        moves = self._parse_moves(text)

        state = dict(self._init_state)
        if not moves:
            return 1.0 if state == self._goal_state else 0.0

        for block, target in moves:
            if block not in self.blocks:
                return 0.0
            if not self._clear(state, block):
                return 0.0
            if target == "table":
                if state[block] == "table":
                    return 0.0  # бессмысленный ход
                state[block] = "table"
            else:
                if target not in self.blocks or target == block:
                    return 0.0
                if not self._clear(state, target):
                    return 0.0
                state[block] = target
        return 1.0 if state == self._goal_state else 0.0

    @classmethod
    def generate_random_task(
        cls,
        language: str = "ru",
        detail_level: int = 3,
        difficulty: int = 5,
        reasoning_mode: bool = False,
        augment: bool = True,
        **kwargs,
    ) -> "BlocksWorldTask":
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
