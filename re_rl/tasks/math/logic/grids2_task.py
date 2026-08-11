"""Сеточные головоломки с проверкой по правилам (засчитывается любое корректное
решение): нонограмма, бинарная головоломка (такузу), хитори, «Битва звёзд»
(Star Battle) и «Морской бой» (Battleship solitaire).
"""

import random
from collections import deque
from typing import Any, ClassVar, Dict, List, Optional, Tuple

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


def _runs(bits: List[int]) -> List[int]:
    res, cur = [], 0
    for b in bits:
        if b == 1:
            cur += 1
        elif cur:
            res.append(cur); cur = 0
    if cur:
        res.append(cur)
    return res


class _GridBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


class NonogramTask(_GridBase):
    TASK_TYPE = "nonogram"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 3, "c": 3}, 2: {"r": 4, "c": 4}, 3: {"r": 5, "c": 5}, 4: {"r": 5, "c": 5},
        5: {"r": 5, "c": 6}, 6: {"r": 6, "c": 6}, 7: {"r": 6, "c": 7}, 8: {"r": 7, "c": 7},
        9: {"r": 7, "c": 8}, 10: {"r": 8, "c": 8},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.r, self.c = int(p["r"]), int(p["c"])
        self.augment = augment
        self.sol = [[1 if random.random() < 0.55 else 0 for _ in range(self.c)]
                    for _ in range(self.r)]
        self.row_clues = [_runs(self.sol[i]) for i in range(self.r)]
        self.col_clues = [_runs([self.sol[i][j] for i in range(self.r)]) for j in range(self.c)]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _clue_str(self, clue):
        return " ".join(map(str, clue)) if clue else "0"

    def _descr(self, language):
        ru = language == "ru"
        rows = "\n".join(f"  строка {i+1}: {self._clue_str(self.row_clues[i])}" for i in range(self.r)) if ru \
            else "\n".join(f"  row {i+1}: {self._clue_str(self.row_clues[i])}" for i in range(self.r))
        cols = "\n".join(f"  столбец {j+1}: {self._clue_str(self.col_clues[j])}" for j in range(self.c)) if ru \
            else "\n".join(f"  col {j+1}: {self._clue_str(self.col_clues[j])}" for j in range(self.c))
        return ((f"Нонограмма {self.r}×{self.c}. Числа задают длины подряд идущих закрашенных клеток "
                 f"(1) в строке/столбце по порядку; 0 — пустая линия.\nПодсказки по строкам:\n{rows}\n"
                 f"Подсказки по столбцам:\n{cols}\n"
                 f"Заполните сетку (1 — закрашено, 0 — пусто), выпишите все {self.r*self.c} клеток по строкам.") if ru else
                (f"{self.r}×{self.c} nonogram. Numbers give the lengths of consecutive filled cells (1) "
                 f"in each line, in order; 0 means an empty line.\nRow clues:\n{rows}\nColumn clues:\n{cols}\n"
                 f"Fill the grid (1 filled, 0 empty) and list all {self.r*self.c} cells row by row."))

    def solve(self):
        ru = self.language == "ru"
        flat = " ".join(str(self.sol[i][j]) for i in range(self.r) for j in range(self.c))
        self.solution_steps = [
            ("Сопоставляем подсказки строк и столбцов, определяя закрашенные клетки." if ru else
             "Cross-reference row and column clues to determine filled cells."),
            (f"Решение (по строкам): {flat}." if ru else f"Solution (row by row): {flat}."),
        ]
        self.final_answer = flat

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < self.r * self.c:
            return 0.0
        flat = ints[-self.r * self.c:]
        grid = [flat[i * self.c:(i + 1) * self.c] for i in range(self.r)]
        for i in range(self.r):
            if _runs(grid[i]) != self.row_clues[i]:
                return 0.0
        for j in range(self.c):
            if _runs([grid[i][j] for i in range(self.r)]) != self.col_clues[j]:
                return 0.0
        return 1.0


class BinaryPuzzleTask(_GridBase):
    TASK_TYPE = "binary_puzzle"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4, "blanks": 6}, 2: {"n": 4, "blanks": 8}, 3: {"n": 4, "blanks": 9},
        4: {"n": 6, "blanks": 12}, 5: {"n": 6, "blanks": 15}, 6: {"n": 6, "blanks": 18},
        7: {"n": 6, "blanks": 20}, 8: {"n": 8, "blanks": 26}, 9: {"n": 8, "blanks": 32},
        10: {"n": 8, "blanks": 38},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.blanks = int(p["blanks"])
        self.augment = augment
        self.sol = self._generate_board()
        self._make_puzzle()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _generate_board(self):
        n = self.n
        for _ in range(500):
            grid = [[-1] * n for _ in range(n)]
            if self._fill(grid, 0):
                cols = [tuple(grid[i][j] for i in range(n)) for j in range(n)]
                rows = [tuple(row) for row in grid]
                if len(set(rows)) == n and len(set(cols)) == n:
                    return grid
        return grid  # fallback

    def _fill(self, grid, pos):
        n = self.n
        if pos == n * n:
            return True
        r, c = divmod(pos, n)
        vals = [0, 1]
        random.shuffle(vals)
        for v in vals:
            grid[r][c] = v
            if self._ok(grid, r, c):
                if self._fill(grid, pos + 1):
                    return True
        grid[r][c] = -1
        return False

    def _ok(self, grid, r, c):
        n = self.n
        row = grid[r]
        col = [grid[i][c] for i in range(n)]
        # не более n/2 единиц/нулей
        for line, idx in ((row, c), (col, r)):
            filled = [x for x in line if x != -1]
            if filled.count(0) > n // 2 or filled.count(1) > n // 2:
                return False
        # нет трёх подряд
        if c >= 2 and grid[r][c] == grid[r][c-1] == grid[r][c-2] != -1:
            return False
        if r >= 2 and grid[r][c] == grid[r-1][c] == grid[r-2][c] != -1:
            return False
        return True

    def _make_puzzle(self):
        n = self.n
        cells = [(i, j) for i in range(n) for j in range(n)]
        random.shuffle(cells)
        self.hidden = set(cells[:self.blanks])
        self.given = {(i, j): self.sol[i][j] for (i, j) in cells[self.blanks:]}

    def _grid_str(self):
        rows = []
        for i in range(self.n):
            rows.append(" ".join(str(self.sol[i][j]) if (i, j) not in self.hidden else "?"
                                  for j in range(self.n)))
        return "\n".join(rows)

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Бинарная головоломка {self.n}×{self.n}. Правила: в каждой строке и столбце поровну "
                 f"0 и 1; не более двух одинаковых подряд; все строки различны и все столбцы различны. "
                 f"Заполните «?» и выпишите все {self.n*self.n} клеток по строкам.\n{self._grid_str()}") if ru else
                (f"{self.n}×{self.n} binary puzzle. Rules: each row and column has equally many 0s and 1s; "
                 f"no more than two equal cells in a row; all rows distinct and all columns distinct. "
                 f"Fill the «?» and list all {self.n*self.n} cells row by row.\n{self._grid_str()}"))

    def solve(self):
        ru = self.language == "ru"
        flat = " ".join(str(self.sol[i][j]) for i in range(self.n) for j in range(self.n))
        self.solution_steps = [
            ("Используем запреты трёх подряд и баланс 0/1, чтобы вывести значения." if ru else
             "Use the no-three-in-a-row and 0/1 balance rules to deduce the values."),
            (f"Решение (по строкам): {flat}." if ru else f"Solution (row by row): {flat}."),
        ]
        self.final_answer = flat

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        n = self.n
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < n * n:
            return 0.0
        flat = ints[-n * n:]
        grid = [flat[i * n:(i + 1) * n] for i in range(n)]
        for (i, j), v in self.given.items():
            if grid[i][j] != v:
                return 0.0
        for i in range(n):
            if grid[i].count(1) != n // 2:
                return 0.0
            col = [grid[k][i] for k in range(n)]
            if col.count(1) != n // 2:
                return 0.0
            for k in range(n - 2):
                if grid[i][k] == grid[i][k+1] == grid[i][k+2]:
                    return 0.0
                if col[k] == col[k+1] == col[k+2]:
                    return 0.0
        rows = [tuple(r) for r in grid]
        cols = [tuple(grid[i][j] for i in range(n)) for j in range(n)]
        if len(set(rows)) != n or len(set(cols)) != n:
            return 0.0
        return 1.0


class HitoriTask(_GridBase):
    TASK_TYPE = "hitori"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 7},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _pick_shaded(self):
        n = self.n
        for _ in range(300):
            shaded = set()
            for i in range(n):
                for j in range(n):
                    if random.random() < 0.18:
                        # не соседняя с уже затенёнными
                        if all((i + di, j + dj) not in shaded for di, dj in
                               ((1, 0), (-1, 0), (0, 1), (0, -1))):
                            shaded.add((i, j))
            if shaded and self._complement_connected(shaded) and self._each_row_col_has_free(shaded):
                return shaded
        # запасной вариант: одна клетка (всегда корректно и не вырождено)
        return {(random.randrange(n), random.randrange(n))}

    def _each_row_col_has_free(self, shaded):
        n = self.n
        for i in range(n):
            if all((i, j) in shaded for j in range(n)):
                return False
        for j in range(n):
            if all((i, j) in shaded for i in range(n)):
                return False
        return True

    def _complement_connected(self, shaded):
        n = self.n
        free = [(i, j) for i in range(n) for j in range(n) if (i, j) not in shaded]
        if not free:
            return False
        seen = {free[0]}
        q = deque([free[0]])
        while q:
            i, j = q.popleft()
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nb = (i + di, j + dj)
                if 0 <= nb[0] < n and 0 <= nb[1] < n and nb not in shaded and nb not in seen:
                    seen.add(nb); q.append(nb)
        return len(seen) == len(free)

    def _build(self):
        n = self.n
        self.shaded = self._pick_shaded()
        base = [[(i + j) % n + 1 for j in range(n)] for i in range(n)]  # латинский квадрат
        grid = [row[:] for row in base]
        for (i, j) in self.shaded:
            free_cols = [c for c in range(n) if (i, c) not in self.shaded and c != j]
            if free_cols:
                c2 = random.choice(free_cols)
                grid[i][j] = base[i][c2]  # дубликат в строке -> клетку нужно затенить
        self.grid = grid

    def _descr(self, language):
        ru = language == "ru"
        rows = "\n".join(" ".join(str(self.grid[i][j]) for j in range(self.n)) for i in range(self.n))
        return ((f"Хитори {self.n}×{self.n}. Затените часть клеток так, чтобы: (1) в каждой строке и "
                 f"столбце среди НЕзатенённых не было повторяющихся чисел; (2) затенённые клетки не "
                 f"касались рёбрами; (3) все незатенённые клетки были связны (по рёбрам). "
                 f"Сетка (строки сверху вниз, столбцы слева направо, нумерация с 1):\n{rows}\n"
                 f"Перечислите координаты (строка, столбец) затеняемых клеток.") if ru else
                (f"{self.n}×{self.n} Hitori. Shade some cells so that: (1) no number repeats among the "
                 f"UNSHADED cells of any row or column; (2) shaded cells are not edge-adjacent; "
                 f"(3) all unshaded cells are connected (via edges). "
                 f"Grid (rows top-to-bottom, columns left-to-right, 1-indexed):\n{rows}\n"
                 f"List the (row, column) coordinates of the cells to shade."))

    def solve(self):
        ru = self.language == "ru"
        coords = ", ".join(f"({i+1}, {j+1})" for (i, j) in sorted(self.shaded))
        self.solution_steps = [
            ("Затеняем дубликаты так, чтобы затенённые не касались и незатенённые оставались связными." if ru else
             "Shade duplicates so shaded cells don't touch and unshaded cells stay connected."),
            (f"Затеняемые клетки: {coords}." if ru else f"Cells to shade: {coords}."),
        ]
        self.final_answer = coords if coords else ("нет" if ru else "none")

    def _valid_shading(self, shaded) -> bool:
        n = self.n
        if any(not (0 <= i < n and 0 <= j < n) for (i, j) in shaded):
            return False
        for (i, j) in shaded:  # не соседние
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if (i + di, j + dj) in shaded:
                    return False
        for i in range(n):  # нет дубликатов среди незатенённых
            vals = [self.grid[i][j] for j in range(n) if (i, j) not in shaded]
            if len(vals) != len(set(vals)):
                return False
        for j in range(n):
            vals = [self.grid[i][j] for i in range(n) if (i, j) not in shaded]
            if len(vals) != len(set(vals)):
                return False
        return self._complement_connected(shaded)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        ints = U.parse_ints(prediction)
        if len(ints) % 2 == 1:
            ints = ints[:-1]
        shaded = set()
        for k in range(0, len(ints), 2):
            shaded.add((ints[k] - 1, ints[k + 1] - 1))
        return 1.0 if self._valid_shading(shaded) else 0.0


class StarBattleTask(_GridBase):
    TASK_TYPE = "star_battle"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 4}, 2: {"n": 4}, 3: {"n": 5}, 4: {"n": 5}, 5: {"n": 5},
        6: {"n": 6}, 7: {"n": 6}, 8: {"n": 6}, 9: {"n": 7}, 10: {"n": 7},
    }
    _LET = "ABCDEFGHIJ"

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _gen_stars(self):
        n = self.n
        for _ in range(2000):
            cols = list(range(n))
            random.shuffle(cols)
            ok = all(abs(cols[r] - cols[r + 1]) >= 2 for r in range(n - 1))
            if ok:
                return [(r, cols[r]) for r in range(n)]
        return [(r, r) for r in range(n)]

    def _partition(self, stars):
        n = self.n
        region = [[-1] * n for _ in range(n)]
        q = deque()
        for idx, (r, c) in enumerate(stars):
            region[r][c] = idx
            q.append((r, c))
        while q:
            r, c = q.popleft()
            neigh = [(r + dr, c + dc) for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            random.shuffle(neigh)
            for nr, nc in neigh:
                if 0 <= nr < n and 0 <= nc < n and region[nr][nc] == -1:
                    region[nr][nc] = region[r][c]
                    q.append((nr, nc))
        return region

    def _build(self):
        self.stars = self._gen_stars()
        self.region = self._partition(self.stars)

    def _descr(self, language):
        ru = language == "ru"
        rows = "\n".join(" ".join(self._LET[self.region[i][j]] for j in range(self.n))
                         for i in range(self.n))
        return ((f"«Битва звёзд» {self.n}×{self.n}. Поле разбито на {self.n} областей (буквы). Разместите "
                 f"звёзды так, чтобы в каждой строке, каждом столбце и каждой области было ровно по одной "
                 f"звезде, и никакие две звезды не соприкасались (даже по диагонали).\nОбласти:\n{rows}\n"
                 f"Перечислите координаты (строка, столбец) звёзд, нумерация с 1.") if ru else
                (f"{self.n}×{self.n} Star Battle. The board is split into {self.n} regions (letters). Place "
                 f"stars so each row, column and region has exactly one star, and no two stars touch (even "
                 f"diagonally).\nRegions:\n{rows}\n"
                 f"List the (row, column) coordinates of the stars, 1-indexed."))

    def solve(self):
        ru = self.language == "ru"
        coords = ", ".join(f"({r+1}, {c+1})" for (r, c) in sorted(self.stars))
        self.solution_steps = [
            ("По одной звезде в строке/столбце/области, без касаний — единственное согласованное размещение." if ru else
             "One star per row/column/region, no touching — place them consistently."),
            (f"Звёзды: {coords}." if ru else f"Stars: {coords}."),
        ]
        self.final_answer = coords

    def _valid_stars(self, stars) -> bool:
        n = self.n
        if len(stars) != n:
            return False
        if any(not (0 <= r < n and 0 <= c < n) for (r, c) in stars):
            return False
        if len({r for r, _ in stars}) != n or len({c for _, c in stars}) != n:
            return False
        if len({self.region[r][c] for (r, c) in stars}) != n:
            return False
        star_list = list(stars)
        for a in range(len(star_list)):
            for b in range(a + 1, len(star_list)):
                (r1, c1), (r2, c2) = star_list[a], star_list[b]
                if max(abs(r1 - r2), abs(c1 - c2)) <= 1:
                    return False
        return True

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        ints = U.parse_ints(prediction)
        if len(ints) % 2 == 1:
            ints = ints[:-1]
        stars = set()
        for k in range(0, len(ints), 2):
            stars.add((ints[k] - 1, ints[k + 1] - 1))
        return 1.0 if self._valid_stars(stars) else 0.0


class BattleshipTask(_GridBase):
    TASK_TYPE = "battleship"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"n": 5, "fleet": [2, 1, 1]}, 2: {"n": 5, "fleet": [3, 2, 1]},
        3: {"n": 6, "fleet": [3, 2, 1, 1]}, 4: {"n": 6, "fleet": [3, 2, 2, 1]},
        5: {"n": 6, "fleet": [3, 3, 2, 1]}, 6: {"n": 7, "fleet": [4, 3, 2, 1]},
        7: {"n": 7, "fleet": [4, 3, 2, 2]}, 8: {"n": 8, "fleet": [4, 3, 2, 2, 1]},
        9: {"n": 8, "fleet": [4, 3, 3, 2, 1]}, 10: {"n": 8, "fleet": [5, 4, 3, 2, 1]},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.n = int(p["n"])
        self.fleet = list(p["fleet"])
        self.augment = augment
        self._build()
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _build(self):
        n = self.n
        for _ in range(500):
            grid = [[0] * n for _ in range(n)]
            if self._place_all(grid, sorted(self.fleet, reverse=True)):
                self.sol = grid
                self.row_counts = [sum(grid[i]) for i in range(n)]
                self.col_counts = [sum(grid[i][j] for i in range(n)) for j in range(n)]
                return
        self.sol = [[0] * n for _ in range(n)]
        self.row_counts = [0] * n
        self.col_counts = [0] * n

    def _place_all(self, grid, ships):
        if not ships:
            return True
        size = ships[0]
        n = self.n
        placements = []
        for r in range(n):
            for c in range(n):
                for dr, dc in ((0, 1), (1, 0)):
                    cells = [(r + dr * k, c + dc * k) for k in range(size)]
                    if all(0 <= x < n and 0 <= y < n for x, y in cells) and self._can_place(grid, cells):
                        placements.append(cells)
        random.shuffle(placements)
        for cells in placements:
            for x, y in cells:
                grid[x][y] = 1
            if self._place_all(grid, ships[1:]):
                return True
            for x, y in cells:
                grid[x][y] = 0
        return False

    def _can_place(self, grid, cells):
        n = self.n
        for x, y in cells:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 1:
                        return False
        return True

    def _descr(self, language):
        ru = language == "ru"
        fleet = ", ".join(map(str, sorted(self.fleet, reverse=True)))
        rc = ", ".join(map(str, self.row_counts))
        cc = ", ".join(map(str, self.col_counts))
        return ((f"«Морской бой» {self.n}×{self.n}. Разместите корабли длин [{fleet}] (по одной клетке в "
                 f"ширину, горизонтально или вертикально) так, чтобы они не касались друг друга (даже по "
                 f"диагонали). Число занятых клеток по строкам: {rc}; по столбцам: {cc}.\n"
                 f"Выпишите поле: {self.n*self.n} значений по строкам (1 — корабль, 0 — вода).") if ru else
                (f"{self.n}×{self.n} Battleship. Place ships of lengths [{fleet}] (one cell wide, horizontal "
                 f"or vertical) so they don't touch each other (even diagonally). Occupied cells per row: "
                 f"{rc}; per column: {cc}.\n"
                 f"Output the board: {self.n*self.n} values row by row (1 ship, 0 water)."))

    def solve(self):
        ru = self.language == "ru"
        flat = " ".join(str(self.sol[i][j]) for i in range(self.n) for j in range(self.n))
        self.solution_steps = [
            ("Используем счётчики по строкам/столбцам и правило непересечения, чтобы расставить корабли." if ru else
             "Use the row/column counts and the non-touching rule to place the ships."),
            (f"Решение (по строкам): {flat}." if ru else f"Solution (row by row): {flat}."),
        ]
        self.final_answer = flat

    def _valid_board(self, grid) -> bool:
        n = self.n
        if [sum(grid[i]) for i in range(n)] != self.row_counts:
            return False
        if [sum(grid[i][j] for i in range(n)) for j in range(n)] != self.col_counts:
            return False
        # компоненты (орто) — прямые отрезки; длины = флот; без касаний по диагонали
        seen = [[False] * n for _ in range(n)]
        comps = []
        for i in range(n):
            for j in range(n):
                if grid[i][j] == 1 and not seen[i][j]:
                    cells = []
                    q = deque([(i, j)]); seen[i][j] = True
                    while q:
                        x, y = q.popleft(); cells.append((x, y))
                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < n and 0 <= ny < n and grid[nx][ny] == 1 and not seen[nx][ny]:
                                seen[nx][ny] = True; q.append((nx, ny))
                    comps.append(cells)
        lengths = []
        for cells in comps:
            rs = {x for x, _ in cells}
            cs = {y for _, y in cells}
            if len(rs) != 1 and len(cs) != 1:  # не прямая линия
                return False
            lengths.append(len(cells))
        if sorted(lengths, reverse=True) != sorted(self.fleet, reverse=True):
            return False
        # непересечение: соседи по диагонали должны быть той же компоненты (значит — не касаются)
        comp_id = {}
        for idx, cells in enumerate(comps):
            for cell in cells:
                comp_id[cell] = idx
        for (x, y), idx in comp_id.items():
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nb = (x + dx, y + dy)
                    if nb in comp_id and comp_id[nb] != idx:
                        return False
        return True

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        n = self.n
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < n * n:
            return 0.0
        flat = ints[-n * n:]
        grid = [flat[i * n:(i + 1) * n] for i in range(n)]
        return 1.0 if self._valid_board(grid) else 0.0
