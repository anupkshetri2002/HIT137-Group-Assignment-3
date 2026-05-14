from __future__ import annotations

from dataclasses import dataclass
import math

from .effects import ImageEffect


@dataclass
class Difference:
    x: int
    y: int
    w: int
    h: int
    effect: ImageEffect
    found: bool = False

    def center(self) -> tuple[int, int]:
        return self.x + self.w // 2, self.y + self.h // 2

    def contains_point(self, px: int, py: int, tolerance: int = 40) -> bool:
        cx, cy = self.center()
        return math.hypot(px - cx, py - cy) <= tolerance

    def overlaps(self, other: "Difference", margin: int = 20) -> bool:
        return not (
            self.x + self.w + margin < other.x
            or other.x + other.w + margin < self.x
            or self.y + self.h + margin < other.y
            or other.y + other.h + margin < self.y
        )
