"""Spot the Difference - Desktop Application."""

from __future__ import annotations

from dataclasses import dataclass

import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image

from core.game_state import GameState
from core.image_processor import ImageProcessor
from ui.gui_manager import GUIManager
from ui.theme import Theme


@dataclass
class DisplayInfo:
    scale: float
    offset_x: int
    offset_y: int
    display_w: int
    display_h: int


class GameController:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.gui = GUIManager(root, self.load_image, self.reveal_differences, self.handle_click)
        self.processor: ImageProcessor | None = None
        self.state = GameState()
        self.display_info: DisplayInfo | None = None
        self._default_status = "Click on the right image to find differences"

    def load_image(self) -> None:
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp"), ("All", "*.*")],
        )
        if not path:
            return

        try:
            self.processor = ImageProcessor(path)
        except (ValueError, RuntimeError) as exc:
            messagebox.showerror("Error", str(exc))
            return

        self.state.reset_round()
        self.display_info, original_pil, modified_pil = self._prepare_display_images()
        self.gui.set_images(
            original_pil,
            modified_pil,
            offset_x=self.display_info.offset_x,
            offset_y=self.display_info.offset_y,
        )
        self.gui.clear_marks()
        self.gui.update_stats(self.state.remaining, self.state.mistakes, self.state.found_count)
        self.gui.set_reveal_enabled(True)
        self.gui.set_status(self._default_status, Theme.text_muted)

    def handle_click(self, x: int, y: int) -> None:
        if self.processor is None or self.display_info is None:
            return
        if self.state.game_over or self.state.round_won or self.state.revealed:
            return

        image_coords = self._canvas_to_image_coords(x, y)
        if image_coords is None:
            return
        ix, iy = image_coords

        hit = None
        for diff in self.processor.differences:
            if not diff.found and diff.contains_point(ix, iy):
                hit = diff
                break

        if hit:
            hit.found = True
            self.state.record_correct(self.processor.num_differences)
            self._draw_difference_circle(hit, Theme.found)
            self.gui.flash_found()
            self.gui.update_stats(self.state.remaining, self.state.mistakes, self.state.found_count)
            if self.state.round_won:
                self.gui.set_reveal_enabled(False)
                self.gui.set_status(
                    "All found! Load a new image to play again.",
                    Theme.success,
                )
                messagebox.showinfo(
                    "All Found!",
                    "You found all 5 differences.\nLoad a new image to keep playing.",
                )
            else:
                self.gui.set_status_temporary(
                    "Found one! Keep going.",
                    Theme.success,
                    self._default_status,
                    Theme.text_muted,
                )
        else:
            self.state.record_mistake()
            remaining = GameState.max_mistakes - self.state.mistakes
            self.gui.update_stats(self.state.remaining, self.state.mistakes, self.state.found_count)
            if self.state.game_over:
                self.gui.set_reveal_enabled(False)
                self.gui.set_status(
                    "Game over. Too many mistakes. Load a new image.",
                    Theme.danger,
                )
                messagebox.showwarning(
                    "Too Many Mistakes",
                    f"You made 3 mistakes and found {self.state.found_count} of 5 differences.\n"
                    "Load a new image to try again.",
                )
            else:
                self.gui.set_status_temporary(
                    f"Not quite. {remaining} mistakes remaining.",
                    Theme.danger,
                    self._default_status,
                    Theme.text_muted,
                )

    def reveal_differences(self) -> None:
        if self.processor is None or self.display_info is None:
            return
        if self.state.game_over or self.state.round_won:
            return

        confirm = messagebox.askyesno(
            "Reveal Differences?",
            "This will show all remaining differences.\nYou will not be able to continue this round.",
        )
        if not confirm:
            return

        for diff in self.processor.differences:
            if not diff.found:
                diff.found = True
                self._draw_difference_circle(diff, Theme.reveal)

        self.state.set_revealed()
        self.gui.set_reveal_enabled(False)
        self.gui.update_stats(self.state.remaining, self.state.mistakes, self.state.found_count)
        self.gui.set_status(
            "Revealed all differences. Load a new image to play again.",
            Theme.text_muted,
        )

    def _prepare_display_images(self) -> tuple[DisplayInfo, Image.Image, Image.Image]:
        assert self.processor is not None
        img_h, img_w = self.processor.original_bgr.shape[:2]
        canvas_size = self.gui.canvas_size
        scale = min(canvas_size / img_w, canvas_size / img_h)
        display_w = int(img_w * scale)
        display_h = int(img_h * scale)
        offset_x = (canvas_size - display_w) // 2
        offset_y = (canvas_size - display_h) // 2

        original_pil = self.processor.to_pil(self.processor.original_bgr)
        modified_pil = self.processor.to_pil(self.processor.modified_bgr)
        original_pil = original_pil.resize((display_w, display_h), Image.LANCZOS)
        modified_pil = modified_pil.resize((display_w, display_h), Image.LANCZOS)

        info = DisplayInfo(scale=scale, offset_x=offset_x, offset_y=offset_y,
                           display_w=display_w, display_h=display_h)
        return info, original_pil, modified_pil

    def _canvas_to_image_coords(self, x: int, y: int) -> tuple[int, int] | None:
        info = self.display_info
        if info is None:
            return None

        if (
            x < info.offset_x
            or y < info.offset_y
            or x > info.offset_x + info.display_w
            or y > info.offset_y + info.display_h
        ):
            return None

        ix = int((x - info.offset_x) / info.scale)
        iy = int((y - info.offset_y) / info.scale)
        return ix, iy

    def _draw_difference_circle(self, diff, color: str) -> None:
        info = self.display_info
        if info is None:
            return
        cx, cy = diff.center()
        canvas_x = int(cx * info.scale) + info.offset_x
        canvas_y = int(cy * info.scale) + info.offset_y
        radius = int(max(diff.w, diff.h) / 2 * info.scale) + 8
        self.gui.draw_circle(canvas_x, canvas_y, radius, color)


def main() -> None:
    root = tk.Tk()
    GameController(root)
    root.mainloop()


if __name__ == "__main__":
    main()
