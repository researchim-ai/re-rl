"""Визуальный вариант «Мастермайнда»: доска догадок с цветными фишками (PIL).

Наследует логику от :class:`MastermindTask`: по подсказкам восстановить код.
Цвет фишки соответствует цифре (легенда сверху); ответ — цифры кода.
Чёрные колышки = «точных», белые = «частичных». `verify` без изменений.
"""

from PIL import Image, ImageDraw

from re_rl.tasks.base_task import OutputFormat
from re_rl.tasks.math.logic.mastermind_task import MastermindTask
from re_rl.tasks.visual._visual_utils import VisualTaskMixin, get_font

# Цвета для цифр 1..8.
_PEG_COLORS = [
    (220, 50, 47), (38, 139, 210), (46, 160, 67), (245, 205, 0),
    (211, 54, 130), (255, 140, 0), (108, 113, 196), (42, 161, 152),
]


class MastermindVisualTask(VisualTaskMixin, MastermindTask):
    TASK_TYPE = "mastermind_image"
    PEG = 40
    GAP = 12

    def __init__(self, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                 output_format: OutputFormat = "text", reasoning_mode: bool = False,
                 augment: bool = True, **kwargs):
        super().__init__(language=language, detail_level=detail_level, difficulty=difficulty,
                         output_format=output_format, reasoning_mode=reasoning_mode,
                         augment=augment)
        self.description = self._descr_visual(language)

    def _color(self, digit):
        return _PEG_COLORS[(digit - 1) % len(_PEG_COLORS)]

    def render_image(self):
        P, G = self.PEG, self.GAP
        L, C = self.L, self.C
        font = get_font(int(P * 0.5))
        small = get_font(16)
        legend_h = P + 2 * G + 24
        fb_w = 2 * (P // 2 + 4)  # место под колышки-подсказки
        row_h = P + G
        width = G + L * (P + G) + fb_w + 2 * G
        height = legend_h + len(self.guesses) * row_h + G
        img = Image.new("RGB", (max(width, C * (P + G) + 2 * G), height), (250, 250, 250))
        draw = ImageDraw.Draw(img)
        # легенда: цифра -> цвет
        draw.text((G, 4), "Легенда:", fill=(0, 0, 0), font=small)
        for d in range(1, C + 1):
            x0 = G + (d - 1) * (P + G)
            y0 = 24
            draw.ellipse([x0, y0, x0 + P, y0 + P], fill=self._color(d), outline=(0, 0, 0))
            bb = draw.textbbox((0, 0), str(d), font=font)
            draw.text((x0 + (P - (bb[2] - bb[0])) / 2, y0 + (P - (bb[3] - bb[1])) / 2 - bb[1]),
                      str(d), fill=(255, 255, 255), font=font)
        # догадки
        for gi, (guess, (exact, partial)) in enumerate(self.guesses):
            y0 = legend_h + gi * row_h
            for j, d in enumerate(guess):
                x0 = G + j * (P + G)
                draw.ellipse([x0, y0, x0 + P, y0 + P], fill=self._color(d), outline=(0, 0, 0))
            # колышки-подсказки справа: точные (чёрные), частичные (белые)
            fx = G + L * (P + G) + G
            r = 7
            pegs = [(0, 0, 0)] * exact + [(255, 255, 255)] * partial
            for pi, col in enumerate(pegs):
                px = fx + (pi % 2) * (2 * r + 4)
                py = y0 + (pi // 2) * (2 * r + 4)
                draw.ellipse([px, py, px + 2 * r, py + 2 * r], fill=col, outline=(0, 0, 0))
        return img

    def _descr_visual(self, language):
        ru = language == "ru"
        return ((f"На рисунке — доска «Мастермайнда». Сверху легенда: цвет фишки = цифра "
                 f"(1..{self.C}). Каждая строка — догадка из {self.L} цветных фишек; справа "
                 f"колышки-подсказки: чёрные — число «точных» совпадений (верная цифра на своём "
                 f"месте), белые — «частичных» (верная цифра не на своём месте). Определите "
                 f"скрытый код — {self.L} цифр по порядку.") if ru else
                (f"The figure shows a Mastermind board. Top legend: peg color = digit (1..{self.C}). "
                 f"Each row is a guess of {self.L} colored pegs; on the right are key pegs: black = "
                 f"number of 'exact' matches (right digit, right place), white = 'partial' (right "
                 f"digit, wrong place). Determine the secret code — {self.L} digits in order."))

    @classmethod
    def generate_random_task(cls, language: str = "ru", detail_level: int = 3, difficulty: int = 5,
                             reasoning_mode: bool = False, augment: bool = True, **kwargs):
        task = cls(language=language, detail_level=detail_level, difficulty=difficulty,
                   reasoning_mode=reasoning_mode, augment=augment)
        task.solve()
        return task
