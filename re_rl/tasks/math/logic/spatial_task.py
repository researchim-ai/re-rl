"""Пространственное мышление: развёртка куба (противоположные грани), игральный
кубик (сумма 7), повороты/отражения фигуры, складывание бумаги."""

import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U


class _SpatialBase(BaseMathTask):
    @classmethod
    def generate_random_task(cls, language="ru", detail_level=3, difficulty=5,
                             reasoning_mode=False, augment=True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task


class CubeNetTask(_SpatialBase):
    TASK_TYPE = "cube_net"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}
    # позиции креста и пары противоположных граней
    _OPP = {"F": "B", "B": "F", "T": "Bo", "Bo": "T", "L": "R", "R": "L"}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        self.augment = augment
        labels = random.sample("ABCDEFGHIJKLMNPQ", 6)
        self.pos = dict(zip(["T", "L", "F", "R", "B", "Bo"], labels))
        self.query_pos = random.choice(list(self.pos))
        self.query_label = self.pos[self.query_pos]
        self.answer = self.pos[self._OPP[self.query_pos]]
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _net(self):
        sp = "  "
        p = self.pos
        return (f"{sp*3}[{p['T']}]\n"
                f"[{p['L']}][{p['F']}][{p['R']}][{p['B']}]\n"
                f"{sp*3}[{p['Bo']}]")

    def _descr(self, language):
        ru = language == "ru"
        return ((f"Развёртка куба (крест):\n{self._net()}\nЕсли сложить её в куб, какая грань окажется "
                 f"противоположной грани {self.query_label}?") if ru else
                (f"Cube net (cross):\n{self._net()}\nWhen folded into a cube, which face is opposite "
                 f"face {self.query_label}?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("В кресте противоположны: центр и дальняя грань ряда, а также верх и низ." if ru else
             "In a cross net, opposite pairs are: the center and the far face of the row, and top vs bottom."),
            (f"Противоположная грани {self.query_label} — {self.answer}." if ru else
             f"The face opposite {self.query_label} is {self.answer}."),
        ]
        self.final_answer = self.answer

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_label(prediction, [self.answer])


class DiceReasoningTask(_SpatialBase):
    TASK_TYPE = "dice_reasoning"
    TASK_TYPES = ["opposite", "corner_sum"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {i: {} for i in range(1, 11)}

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        self.augment = augment
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        if self.subtype == "opposite":
            self.v = random.randint(1, 6)
            self.answer = 7 - self.v
        else:
            self.faces = [random.choice(list(pair)) for pair in ((1, 6), (2, 5), (3, 4))]
            random.shuffle(self.faces)
            self.answer = 21 - sum(self.faces)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        if self.subtype == "opposite":
            return ((f"На стандартном игральном кубике сумма противоположных граней равна 7. На одной "
                     f"грани число {self.v}. Что на противоположной грани?") if ru else
                    (f"On a standard die opposite faces sum to 7. One face shows {self.v}. What is on the "
                     f"opposite face?"))
        fs = ", ".join(map(str, self.faces))
        return ((f"На стандартном кубике сумма противоположных граней равна 7. В одном углу видны три "
                 f"грани: {fs}. Чему равна сумма трёх граней, противоположных этим?") if ru else
                (f"On a standard die opposite faces sum to 7. At one corner three faces are visible: {fs}. "
                 f"What is the sum of the three faces opposite to them?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Противоположная грань = 7 минус видимая." if ru else
             "The opposite face = 7 minus the visible one."),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))


class RotationReflectionTask(_SpatialBase):
    TASK_TYPE = "rotation_reflection"
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"r": 2, "c": 2}, 2: {"r": 2, "c": 3}, 3: {"r": 3, "c": 3}, 4: {"r": 3, "c": 3},
        5: {"r": 3, "c": 4}, 6: {"r": 4, "c": 4}, 7: {"r": 4, "c": 4}, 8: {"r": 4, "c": 5},
        9: {"r": 5, "c": 5}, 10: {"r": 5, "c": 6},
    }
    _OPS = ["rot90cw", "rot90ccw", "rot180", "flip_h", "flip_v", "transpose"]

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.r, self.c = int(p["r"]), int(p["c"])
        self.augment = augment
        self.op = random.choice(self._OPS)
        self.grid = [[random.randint(0, 1) for _ in range(self.c)] for _ in range(self.r)]
        self.result = self._apply(self.grid, self.op)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    @staticmethod
    def _apply(g, op):
        if op == "rot90cw":
            return [list(row) for row in zip(*g[::-1])]
        if op == "rot90ccw":
            return [list(row) for row in zip(*g)][::-1]
        if op == "rot180":
            return [row[::-1] for row in g[::-1]]
        if op == "flip_h":
            return [row[::-1] for row in g]
        if op == "flip_v":
            return g[::-1]
        return [list(row) for row in zip(*g)]  # transpose

    def _op_text(self, ru):
        return {
            "rot90cw": ("поворот на 90° по часовой стрелке" if ru else "rotate 90° clockwise"),
            "rot90ccw": ("поворот на 90° против часовой стрелки" if ru else "rotate 90° counterclockwise"),
            "rot180": ("поворот на 180°" if ru else "rotate 180°"),
            "flip_h": ("отражение по горизонтали (лево-право)" if ru else "flip horizontally (left-right)"),
            "flip_v": ("отражение по вертикали (верх-низ)" if ru else "flip vertically (top-bottom)"),
            "transpose": ("транспонирование" if ru else "transpose"),
        }[self.op]

    @staticmethod
    def _grid_str(g):
        return "\n".join(" ".join(map(str, row)) for row in g)

    def _descr(self, language):
        ru = language == "ru"
        rr, cc = len(self.result), len(self.result[0])
        return ((f"Дана фигура {self.r}×{self.c} (0/1):\n{self._grid_str(self.grid)}\n"
                 f"Примените преобразование: {self._op_text(True)}. Выпишите получившуюся сетку "
                 f"({rr}×{cc}) — все {rr*cc} клеток по строкам.") if ru else
                (f"Given a {self.r}×{self.c} pattern (0/1):\n{self._grid_str(self.grid)}\n"
                 f"Apply the transformation: {self._op_text(False)}. Output the resulting grid "
                 f"({rr}×{cc}) — all {rr*cc} cells row by row."))

    def solve(self):
        ru = self.language == "ru"
        flat = " ".join(str(x) for row in self.result for x in row)
        self.solution_steps = [
            ("Применяем геометрическое преобразование к каждой клетке." if ru else
             "Apply the geometric transformation to every cell."),
            (f"Результат (по строкам): {flat}." if ru else f"Result (row by row): {flat}."),
        ]
        self.final_answer = flat

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        flat = [x for row in self.result for x in row]
        ints = [x for x in U.parse_ints(prediction) if x in (0, 1)]
        if len(ints) < len(flat):
            return 0.0
        return 1.0 if ints[-len(flat):] == flat else 0.0


class PaperFoldingTask(_SpatialBase):
    TASK_TYPE = "paper_folding"
    TASK_TYPES = ["holes", "layers"]
    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"kmax": 3, "hmax": 2}, 2: {"kmax": 4, "hmax": 2}, 3: {"kmax": 4, "hmax": 3},
        4: {"kmax": 5, "hmax": 3}, 5: {"kmax": 5, "hmax": 4}, 6: {"kmax": 6, "hmax": 4},
        7: {"kmax": 6, "hmax": 5}, 8: {"kmax": 7, "hmax": 5}, 9: {"kmax": 7, "hmax": 6},
        10: {"kmax": 8, "hmax": 6},
    }

    def __init__(self, language="ru", detail_level=3, difficulty=5, output_format="text",
                 reasoning_mode=False, augment=True, subtype=None, **kwargs):
        p = self._interpolate_difficulty(difficulty)
        self.subtype = subtype or random.choice(self.TASK_TYPES)
        self.augment = augment
        self.k = random.randint(1, int(p["kmax"]))
        self.h = random.randint(1, int(p["hmax"]))
        if self.subtype == "layers":
            self.answer = 2 ** self.k
        else:
            self.answer = self.h * (2 ** self.k)
        super().__init__(description=self._descr(language), language=language,
                         detail_level=detail_level, output_format=output_format,
                         reasoning_mode=reasoning_mode)

    def _descr(self, language):
        ru = language == "ru"
        if self.subtype == "layers":
            return ((f"Лист бумаги складывают пополам {self.k} раз(а). Сколько слоёв бумаги получится?") if ru else
                    (f"A sheet of paper is folded in half {self.k} time(s). How many layers of paper result?"))
        return ((f"Лист бумаги складывают пополам {self.k} раз(а), затем насквозь пробивают {self.h} "
                 f"отверстий. Сколько отверстий будет на полностью развёрнутом листе?") if ru else
                (f"A sheet of paper is folded in half {self.k} time(s), then {self.h} holes are punched "
                 f"through all layers. How many holes are on the fully unfolded sheet?"))

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            (f"Каждое складывание удваивает число слоёв: 2^{self.k} = {2**self.k}." if ru else
             f"Each fold doubles the layers: 2^{self.k} = {2**self.k}."),
            (f"Ответ: {self.answer}." if ru else f"Answer: {self.answer}."),
        ]
        self.final_answer = str(self.answer)

    def verify(self, prediction):
        if self.final_answer is None:
            self.solve()
        return U.verify_int(prediction, int(self.answer))
