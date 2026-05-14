from __future__ import annotations

import random

import cv2
import numpy as np

from .difference import Difference
from .effects import (
    BrightnessContrastEffect,
    ColorShiftEffect,
    GaussianBlurEffect,
    ImageEffect,
    PixelationEffect,
    SharpenFilterEffect,
)


class ImageProcessor:
    num_differences = 5
    min_size = 40
    max_size = 90

    def __init__(self, filepath: str) -> None:
        self.filepath = filepath
        bgr = cv2.imread(filepath)
        if bgr is None:
            raise ValueError(f"Cannot read image: {filepath}")
        self.original_bgr = bgr
        self.modified_bgr = bgr.copy()
        self.differences = self._generate_differences()

    def _generate_differences(self) -> list[Difference]:
        h, w = self.original_bgr.shape[:2]
        if w < self.min_size or h < self.min_size:
            raise ValueError("Image is too small to place differences.")

        effects: list[type[ImageEffect]] = [
            ColorShiftEffect,
            GaussianBlurEffect,
            BrightnessContrastEffect,
            PixelationEffect,
            SharpenFilterEffect,
        ]

        placed: list[Difference] = []
        attempts = 0
        while len(placed) < self.num_differences and attempts < 1000:
            attempts += 1
            x, y, rw, rh = self._random_region(w, h)
            effect = random.choice(effects)()
            candidate = Difference(x=x, y=y, w=rw, h=rh, effect=effect)
            if any(candidate.overlaps(existing) for existing in placed):
                continue
            effect.apply(self.modified_bgr, x, y, rw, rh)
            placed.append(candidate)

        if len(placed) < self.num_differences:
            raise RuntimeError("Could not place all differences. Try another image.")

        return placed

    def _random_region(self, img_w: int, img_h: int) -> tuple[int, int, int, int]:
        max_w = min(self.max_size, img_w - 1)
        max_h = min(self.max_size, img_h - 1)
        w = random.randint(self.min_size, max_w)
        h = random.randint(self.min_size, max_h)
        x = random.randint(0, img_w - w)
        y = random.randint(0, img_h - h)
        return x, y, w, h

    @staticmethod
    def to_pil(bgr: np.ndarray):
        from PIL import Image

        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        return Image.fromarray(rgb)
