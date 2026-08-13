"""Утилиты для визуальных (мультимодальных / VLM) задач.

`VisualTaskMixin` добавляет задаче способность рендерить изображение
(`render_image()` → :class:`PIL.Image.Image`) и сохранять его на диск
(`save_image(path)`). Ответ задачи остаётся текстовым, поэтому вся логика
проверки (`verify`) работает без изменений.

Рендеринг matplotlib выполняется в неинтерактивном бэкенде ``Agg``.
"""

from __future__ import annotations

import io
import random
from pathlib import Path
from typing import ClassVar, List, Optional, Sequence

import matplotlib

matplotlib.use("Agg")  # безопасный бэкенд без дисплея
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

# Палитра ARC-подобных задач: индекс цвета → RGB (0 — фон).
ARC_PALETTE = [
    (0, 0, 0), (38, 139, 210), (220, 50, 47), (46, 160, 67), (245, 205, 0),
    (150, 150, 150), (211, 54, 130), (255, 140, 0), (38, 200, 220), (140, 30, 30),
]

_FONT_PATH = font_manager.findfont("DejaVu Sans")


def get_font(size: int = 20) -> "ImageFont.FreeTypeFont":
    """Масштабируемый шрифт (DejaVu Sans из matplotlib) с запасным вариантом."""
    try:
        return ImageFont.truetype(_FONT_PATH, size)
    except Exception:  # pragma: no cover
        return ImageFont.load_default()


def fig_to_image(fig, dpi: int = 100) -> Image.Image:
    """Конвертирует matplotlib-фигуру в независимый :class:`PIL.Image`."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).convert("RGB").copy()
    buf.close()
    return img


def _draw_centered(draw, x0, y0, cell, text, font, fill=(0, 0, 0)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((x0 + (cell - tw) / 2, y0 + (cell - th) / 2 - bbox[1]), text, fill=fill, font=font)


def render_number_grid(grid, cell: int = 44, blanks: Sequence = (None, 0, "", "."),
                       origin=(0, 0), img: Optional[Image.Image] = None,
                       thick_every: int = 0) -> Image.Image:
    """Рисует сетку чисел (для судоку / пятнашек). ``blanks`` — значения-пустышки."""
    n_r, n_c = len(grid), len(grid[0])
    if img is None:
        img = Image.new("RGB", (n_c * cell + 1, n_r * cell + 1), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = get_font(int(cell * 0.5))
    ox, oy = origin
    for i in range(n_r):
        for j in range(n_c):
            x0, y0 = ox + j * cell, oy + i * cell
            draw.rectangle([x0, y0, x0 + cell, y0 + cell], outline=(0, 0, 0))
            v = grid[i][j]
            if v not in blanks:
                _draw_centered(draw, x0, y0, cell, str(v), font)
    if thick_every:
        for k in range(0, n_r + 1, thick_every):
            draw.line([(ox, oy + k * cell), (ox + n_c * cell, oy + k * cell)], fill=(0, 0, 0), width=3)
        for k in range(0, n_c + 1, thick_every):
            draw.line([(ox + k * cell, oy), (ox + k * cell, oy + n_r * cell)], fill=(0, 0, 0), width=3)
    return img


def render_color_grid(grid, palette=ARC_PALETTE, cell: int = 30,
                      origin=(0, 0), img: Optional[Image.Image] = None) -> Image.Image:
    """Рисует сетку цветных клеток (для ARC-подобных задач)."""
    n_r, n_c = len(grid), len(grid[0])
    if img is None:
        img = Image.new("RGB", (n_c * cell + 1, n_r * cell + 1), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    ox, oy = origin
    for i in range(n_r):
        for j in range(n_c):
            x0, y0 = ox + j * cell, oy + i * cell
            rgb = palette[grid[i][j] % len(palette)]
            draw.rectangle([x0, y0, x0 + cell, y0 + cell], fill=rgb, outline=(80, 80, 80))
    return img


def augment_image(img: Image.Image, seed: Optional[int] = None,
                  max_rotate: float = 5.0) -> Image.Image:
    """Лёгкая аугментация: небольшой поворот на белом фоне (для устойчивости VLM).

    Верификация текстовая, поэтому аугментация не влияет на корректность ответа.
    """
    rnd = random.Random(seed)
    angle = rnd.uniform(-max_rotate, max_rotate)
    return img.convert("RGB").rotate(angle, expand=True, fillcolor=(255, 255, 255))


class VisualTaskMixin:
    """Примесь для задач с изображением. Ставится ПЕРЕД базовым классом задачи."""

    IS_VISUAL: ClassVar[bool] = True

    def render_image(self) -> Image.Image:
        """Возвращает изображение задачи. Переопределяется подклассом."""
        raise NotImplementedError

    def save_image(self, path: str) -> str:
        """Рендерит и сохраняет PNG, возвращает фактический путь."""
        img = self.render_image()
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        img.save(p)
        return str(p)
