"""GridNavigationTask — пространственная навигация.

Подтипы:
- position: конечные координаты робота после команд (вперёд/поворот);
- heading: конечное направление (С/В/Ю/З);
- maze: длина кратчайшего пути в лабиринте (BFS), -1 если недостижимо.
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

# Направления по часовой: N, E, S, W. dx,dy для оси x (восток+) и y (север+).
_DIRS = [("N", 0, 1), ("E", 1, 0), ("S", 0, -1), ("W", -1, 0)]
_DIR_RU = {"N": "север", "E": "восток", "S": "юг", "W": "запад"}
_DIR_EN = {"N": "north", "E": "east", "S": "south", "W": "west"}


class GridNavigationTask(BaseMathTask):
    TASK_TYPE = "grid_navigation"
    TASK_TYPES = ["position", "heading", "maze"]

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"cmds": 3, "maze": 4}, 2: {"cmds": 4, "maze": 4}, 3: {"cmds": 5, "maze": 5},
        4: {"cmds": 6, "maze": 5}, 5: {"cmds": 7, "maze": 6}, 6: {"cmds": 8, "maze": 6},
        7: {"cmds": 10, "maze": 7}, 8: {"cmds": 12, "maze": 8}, 9: {"cmds": 14, "maze": 9},
        10: {"cmds": 16, "maze": 10},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, subtype: Optional[str] = None, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.num_cmds = int(preset["cmds"])
        self.maze_size = int(preset["maze"])
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        if self.subtype in ("position", "heading"):
            self.start_dir = random.randrange(4)
            self.commands: List[Tuple[str, int]] = []
            x = y = 0
            d = self.start_dir
            for _ in range(self.num_cmds):
                kind = random.choice(["fwd", "left", "right", "fwd", "fwd"])
                if kind == "fwd":
                    k = random.randint(1, 5)
                    _, dx, dy = _DIRS[d]
                    x += dx * k
                    y += dy * k
                    self.commands.append(("fwd", k))
                elif kind == "left":
                    d = (d - 1) % 4
                    self.commands.append(("left", 0))
                else:
                    d = (d + 1) % 4
                    self.commands.append(("right", 0))
            self.end_x, self.end_y, self.end_dir = x, y, d
        else:  # maze
            self._build_maze()

    def _build_maze(self):
        n = self.maze_size
        # 0 — свободно, 1 — стена. Гарантируем путь по случайному блужданию.
        grid = [[1] * n for _ in range(n)]
        x = y = 0
        grid[0][0] = 0
        path = [(0, 0)]
        steps = n * n
        for _ in range(steps):
            dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n:
                grid[ny][nx] = 0
                x, y = nx, ny
                path.append((x, y))
        grid[n - 1][n - 1] = 0
        # Добавим немного случайных проходов.
        for _ in range(n):
            grid[random.randrange(n)][random.randrange(n)] = 0
        self.grid = grid
        self.maze_n = n
        self._answer_maze = self._bfs_maze()

    def _bfs_maze(self):
        n = self.maze_n
        start, goal = (0, 0), (n - 1, n - 1)
        seen = {start}
        q = deque([(start, 0)])
        while q:
            (cx, cy), dist = q.popleft()
            if (cx, cy) == goal:
                return dist
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < n and 0 <= ny < n and self.grid[ny][nx] == 0 and (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append(((nx, ny), dist + 1))
        return -1

    def _cmd_text(self, cmd, ru: bool) -> str:
        kind, k = cmd
        if kind == "fwd":
            return (f"пройти вперёд на {k}" if ru else f"move forward {k}")
        if kind == "left":
            return ("повернуть налево" if ru else "turn left")
        return ("повернуть направо" if ru else "turn right")

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        if self.subtype in ("position", "heading"):
            dname = (_DIR_RU if ru else _DIR_EN)[_DIRS[self.start_dir][0]]
            head = (f"Робот стоит в точке (0, 0) и смотрит на {dname}. Ось X — на восток, ось Y — на север.\n"
                    f"Команды по порядку: " if ru else
                    f"A robot is at (0, 0) facing {dname}. X axis points east, Y axis points north.\n"
                    f"Commands in order: ")
            head += "; ".join(self._cmd_text(c, ru) for c in self.commands) + "."
            if self.subtype == "position":
                head += ("\nКакие итоговые координаты (x, y)?" if ru else "\nWhat are the final coordinates (x, y)?")
            else:
                head += ("\nВ каком направлении (север/восток/юг/запад) робот смотрит в конце?" if ru else
                         "\nWhich direction (north/east/south/west) does the robot face at the end?")
            return head
        # maze
        n = self.maze_n
        rows = []
        for r in range(n):
            rows.append("".join("#" if self.grid[r][c] else "." for c in range(n)))
        grid_str = "\n".join(rows)
        return (("Лабиринт (# — стена, . — свободно). Старт — левый верхний угол (0,0), "
                 f"цель — правый нижний ({n-1},{n-1}). Разрешены ходы вверх/вниз/влево/вправо.\n"
                 f"{grid_str}\n"
                 "Найдите длину кратчайшего пути (число шагов; -1, если пути нет).") if ru else
                ("Maze (# — wall, . — free). Start at top-left (0,0), "
                 f"goal at bottom-right ({n-1},{n-1}). Moves: up/down/left/right.\n"
                 f"{grid_str}\n"
                 "Find the shortest path length (number of steps; -1 if unreachable)."))

    def solve(self):
        ru = self.language == "ru"
        if self.subtype == "position":
            self.solution_steps = [
                ("Отслеживаем координаты и направление, применяя команды по очереди." if ru else
                 "Track coordinates and heading, applying commands one by one."),
                (f"Итоговые координаты: ({self.end_x}, {self.end_y})." if ru else
                 f"Final coordinates: ({self.end_x}, {self.end_y})."),
            ]
            self.final_answer = f"({self.end_x}, {self.end_y})"
        elif self.subtype == "heading":
            dcode = _DIRS[self.end_dir][0]
            dname = (_DIR_RU if ru else _DIR_EN)[dcode]
            self.solution_steps = [
                ("Каждый поворот меняет направление на 90°, движение вперёд его не меняет." if ru else
                 "Each turn rotates the heading by 90°; moving forward keeps it."),
                (f"Итоговое направление: {dname}." if ru else f"Final heading: {dname}."),
            ]
            self.final_answer = dname
        else:
            self.solution_steps = [
                ("Запускаем BFS по свободным клеткам от старта к цели." if ru else
                 "Run BFS over free cells from start to goal."),
                (f"Длина кратчайшего пути = {self._answer_maze}." if ru else
                 f"Shortest path length = {self._answer_maze}."),
            ]
            self.final_answer = str(self._answer_maze)

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        if self.subtype == "position":
            ints = U.parse_ints(prediction)
            return 1.0 if len(ints) >= 2 and ints[-2:] == [self.end_x, self.end_y] else 0.0
        if self.subtype == "heading":
            ru = self.language == "ru"
            dcode = _DIRS[self.end_dir][0]
            syn = [_DIR_RU[dcode], _DIR_EN[dcode], dcode]
            return U.verify_label(prediction, syn)
        return U.verify_int(prediction, int(self._answer_maze))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
