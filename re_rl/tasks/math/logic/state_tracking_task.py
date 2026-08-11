"""StateTrackingTask — отслеживание состояния мира после серии действий.

Люди перемещаются между комнатами, берут и кладут предметы. Нужно определить,
в какой комнате окажется указанный предмет в конце. Симулятор детерминирован.
"""

import random
from typing import Any, ClassVar, Dict, List, Optional

from re_rl.tasks.base_task import BaseMathTask, OutputFormat
from re_rl.tasks.math.logic import _logic_utils as U

_ROOMS_RU = ["кухня", "спальня", "гостиная", "кабинет", "прихожая", "сад"]
_ROOMS_EN = ["kitchen", "bedroom", "living room", "study", "hallway", "garden"]
_PEOPLE_RU = ["Аня", "Боря", "Вика", "Дима"]
_PEOPLE_EN = ["Ann", "Bob", "Vicky", "Dan"]
_ITEMS_RU = ["ключ", "книга", "яблоко", "лампа", "мяч"]
_ITEMS_EN = ["key", "book", "apple", "lamp", "ball"]


class StateTrackingTask(BaseMathTask):
    TASK_TYPE = "state_tracking"

    DIFFICULTY_PRESETS: ClassVar[Dict[int, Dict[str, Any]]] = {
        1: {"rooms": 2, "people": 1, "items": 2, "steps": 3},
        2: {"rooms": 2, "people": 2, "items": 2, "steps": 4},
        3: {"rooms": 3, "people": 2, "items": 2, "steps": 5},
        4: {"rooms": 3, "people": 2, "items": 3, "steps": 6},
        5: {"rooms": 3, "people": 3, "items": 3, "steps": 8},
        6: {"rooms": 4, "people": 3, "items": 3, "steps": 10},
        7: {"rooms": 4, "people": 3, "items": 4, "steps": 12},
        8: {"rooms": 5, "people": 4, "items": 4, "steps": 14},
        9: {"rooms": 5, "people": 4, "items": 5, "steps": 16},
        10: {"rooms": 6, "people": 4, "items": 5, "steps": 20},
    }

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        preset = self._interpolate_difficulty(difficulty)
        self.language = language
        ru = language == "ru"
        self.rooms = (_ROOMS_RU if ru else _ROOMS_EN)[:preset["rooms"]]
        self.people = (_PEOPLE_RU if ru else _PEOPLE_EN)[:preset["people"]]
        self.items = (_ITEMS_RU if ru else _ITEMS_EN)[:preset["items"]]
        self.num_steps = preset["steps"]
        self.augment = augment
        self._build()
        description = self._make_description(language)
        super().__init__(description=description, language=language, detail_level=detail_level,
                         output_format=output_format, reasoning_mode=reasoning_mode)

    def _build(self):
        ru = self.language == "ru"
        # Начальное состояние.
        self.person_room = {p: random.choice(self.rooms) for p in self.people}
        # Предмет либо лежит в комнате (room, name), либо у человека (person, name).
        item_loc = {it: ("room", random.choice(self.rooms)) for it in self.items}

        self.actions: List[str] = []
        init_lines = []
        for p in self.people:
            init_lines.append((f"{p} находится в комнате «{self.person_room[p]}»." if ru else
                               f"{p} is in the {self.person_room[p]}."))
        for it in self.items:
            init_lines.append((f"Предмет «{it}» лежит в комнате «{item_loc[it][1]}»." if ru else
                               f"The {it} is in the {item_loc[it][1]}."))
        self.init_lines = init_lines

        for _ in range(self.num_steps):
            p = random.choice(self.people)
            choice = random.random()
            carried = [it for it, loc in item_loc.items() if loc == ("person", p)]
            here = [it for it, loc in item_loc.items() if loc == ("room", self.person_room[p])]
            if choice < 0.45 or (not carried and not here):
                new_room = random.choice([r for r in self.rooms if r != self.person_room[p]] or self.rooms)
                self.person_room[p] = new_room
                self.actions.append((f"{p} переходит в комнату «{new_room}»." if ru else
                                     f"{p} moves to the {new_room}."))
            elif here and choice < 0.75:
                it = random.choice(here)
                item_loc[it] = ("person", p)
                self.actions.append((f"{p} берёт предмет «{it}»." if ru else
                                     f"{p} picks up the {it}."))
            elif carried:
                it = random.choice(carried)
                item_loc[it] = ("room", self.person_room[p])
                self.actions.append((f"{p} кладёт предмет «{it}» в текущей комнате." if ru else
                                     f"{p} drops the {it} in the current room."))
            else:
                it = random.choice(here)
                item_loc[it] = ("person", p)
                self.actions.append((f"{p} берёт предмет «{it}»." if ru else
                                     f"{p} picks up the {it}."))

        self.target_item = random.choice(self.items)
        loc = item_loc[self.target_item]
        self.answer_room = loc[1] if loc[0] == "room" else self.person_room[loc[1]]
        self._final_item_loc = item_loc

    def _make_description(self, language: str) -> str:
        ru = language == "ru"
        head = ("Начальное состояние:\n" if ru else "Initial state:\n")
        head += "\n".join(f"- {l}" for l in self.init_lines)
        acts = ("\n\nДействия по порядку:\n" if ru else "\n\nActions in order:\n")
        acts += "\n".join(f"{i + 1}. {a}" for i, a in enumerate(self.actions))
        q = (f"\n\nВ какой комнате окажется предмет «{self.target_item}» в конце? "
             f"Назовите комнату." if ru else
             f"\n\nWhich room will the {self.target_item} be in at the end? Name the room.")
        return head + acts + q

    def solve(self):
        ru = self.language == "ru"
        self.solution_steps = [
            ("Последовательно применяем каждое действие, обновляя, где находится предмет и кто его несёт." if ru else
             "Apply each action in order, updating where the item is and who carries it."),
            (f"Итог: предмет «{self.target_item}» находится в комнате «{self.answer_room}»." if ru else
             f"Result: the {self.target_item} is in the {self.answer_room}."),
        ]
        self.final_answer = self.answer_room

    def verify(self, prediction: str) -> float:
        if self.final_answer is None:
            self.solve()
        return U.verify_label(prediction, [self.answer_room])

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment, **kwargs)
        task.solve()
        return task
