from __future__ import annotations

import random

import cv2
import numpy as np


class ImageEffect:
    name = "Base"

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        raise NotImplementedError


class ColorShiftEffect(ImageEffect):
    name = "Color Shift"

    def __init__(self) -> None:
        self.hue_shift = random.randint(20, 60) * random.choice([-1, 1])
        self.sat_scale = random.uniform(0.7, 1.4)

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        roi = image[y : y + h, x : x + w].copy()
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV).astype(np.int32)
        hsv[:, :, 0] = (hsv[:, :, 0] + self.hue_shift) % 180
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * self.sat_scale, 0, 255)
        image[y : y + h, x : x + w] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


class GaussianBlurEffect(ImageEffect):
    name = "Gaussian Blur"

    def __init__(self) -> None:
        self.kernel = random.choice([9, 11, 13])

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        roi = image[y : y + h, x : x + w]
        blurred = cv2.GaussianBlur(roi, (self.kernel, self.kernel), 0)
        image[y : y + h, x : x + w] = blurred


class BrightnessContrastEffect(ImageEffect):
    name = "Brightness/Contrast"

    def __init__(self) -> None:
        self.alpha = random.uniform(0.8, 1.3)  # contrast
        self.beta = random.randint(-30, 30)    # brightness

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        roi = image[y : y + h, x : x + w]
        adjusted = cv2.convertScaleAbs(roi, alpha=self.alpha, beta=self.beta)
        image[y : y + h, x : x + w] = adjusted


class PixelationEffect(ImageEffect):
    name = "Pixelation"
    block = 10

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        roi = image[y : y + h, x : x + w]
        small = cv2.resize(
            roi,
            (max(1, w // self.block), max(1, h // self.block)),
            interpolation=cv2.INTER_LINEAR,
        )
        pixelated = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
        image[y : y + h, x : x + w] = pixelated


class SharpenFilterEffect(ImageEffect):
    name = "Sharpen Filter"

    def __init__(self) -> None:
        self.strength = random.uniform(0.8, 1.4)

    def apply(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
        roi = image[y : y + h, x : x + w]
        kernel = np.array(
            [[0, -1, 0], [-1, 5 + self.strength, -1], [0, -1, 0]], dtype=np.float32
        )
        sharpened = cv2.filter2D(roi, -1, kernel)
        image[y : y + h, x : x + w] = sharpened
