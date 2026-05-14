from __future__ import annotations

import tkinter as tk
from typing import Callable

from PIL import Image, ImageTk

from .theme import Theme


class GUIManager:
    canvas_size = 560
    toolbar_height = 64
    status_height = 40

    def __init__(
        self,
        root: tk.Tk,
        on_load: Callable[[], None],
        on_reveal: Callable[[], None],
        on_click: Callable[[int, int], None],
    ) -> None:
        self.root = root
        self.on_load = on_load
        self.on_reveal = on_reveal
        self.on_click = on_click
        self._status_after_id = None

        self._orig_image_tk: ImageTk.PhotoImage | None = None
        self._mod_image_tk: ImageTk.PhotoImage | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        self.root.title("Spot the Difference")
        self.root.geometry("1280x740")
        self.root.resizable(False, False)
        self.root.configure(bg=Theme.window_bg)

        self._build_toolbar()
        self._build_canvases()
        self._build_status_bar()

        self.set_status("Load an image to begin playing", Theme.text_dim)
        self.set_reveal_enabled(False)

    def _build_toolbar(self) -> None:
        toolbar = tk.Frame(self.root, bg=Theme.toolbar_bg, height=self.toolbar_height)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)

        left = tk.Frame(toolbar, bg=Theme.toolbar_bg)
        left.pack(side="left", padx=16)

        self.load_button = self._create_button(
            left,
            "Load Image",
            self.on_load,
            style="filled",
        )
        self.reveal_button = self._create_button(
            left,
            "Reveal All",
            self.on_reveal,
            style="outline",
        )
        self.reveal_button.pack(side="left", padx=(8, 0))

        right = tk.Frame(toolbar, bg=Theme.toolbar_bg)
        right.pack(side="right", padx=20)

        self.remaining_value = self._stat_block(right, "remaining")
        self._divider(right)
        self.mistakes_value = self._stat_block(right, "mistakes")
        self._divider(right)
        self.found_value = self._stat_block(right, "found")

    def _build_canvases(self) -> None:
        content = tk.Frame(self.root, bg=Theme.window_bg)
        content.pack(padx=20, pady=28)

        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0)
        content.grid_columnconfigure(2, weight=1)

        self.original_canvas = self._canvas_panel(
            content,
            "ORIGINAL",
            Theme.text_dim,
            column=0,
        )

        divider = tk.Frame(content, bg=Theme.border, width=1, height=self.canvas_size + 24)
        divider.grid(row=0, column=1, padx=16)

        self.modified_canvas = self._canvas_panel(
            content,
            "FIND THE DIFFERENCES",
            Theme.accent,
            column=2,
            clickable=True,
        )

    def _build_status_bar(self) -> None:
        status = tk.Frame(self.root, bg=Theme.toolbar_bg, height=self.status_height)
        status.pack(fill="x")
        status.pack_propagate(False)

        self.status_label = tk.Label(
            status,
            text="",
            font=Theme.font_status,
            bg=Theme.toolbar_bg,
            fg=Theme.text_dim,
        )
        self.status_label.pack(side="left", padx=16)

        credit = tk.Label(
            status,
            text="HIT137 Assignment 3",
            font=Theme.font_credit,
            bg=Theme.toolbar_bg,
            fg=Theme.border,
        )
        credit.pack(side="right", padx=16)

    def _create_button(self, parent: tk.Widget, text: str, command, style: str) -> tk.Button:
        if style == "filled":
            style_config = {
                "bg": Theme.accent,
                "fg": "#ffffff",
                "hover_bg": Theme.accent_hover,
                "hover_fg": "#ffffff",
                "disabled_bg": Theme.toolbar_bg,
                "disabled_fg": Theme.text_dim,
                "highlight_bg": Theme.accent,
                "active_bg": Theme.accent_hover,
                "active_fg": "#ffffff",
            }
        else:
            style_config = {
                "bg": Theme.toolbar_bg,
                "fg": Theme.danger,
                "hover_bg": Theme.danger,
                "hover_fg": "#ffffff",
                "disabled_bg": Theme.toolbar_bg,
                "disabled_fg": Theme.text_dim,
                "highlight_bg": Theme.danger,
                "active_bg": Theme.danger_hover,
                "active_fg": "#ffffff",
            }

        button = tk.Button(
            parent,
            text=text,
            command=command,
            font=Theme.font_button,
            bg=style_config["bg"],
            fg=style_config["fg"],
            activebackground=style_config["active_bg"],
            activeforeground=style_config["active_fg"],
            relief="flat",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            highlightthickness=1,
            highlightbackground=style_config["highlight_bg"],
        )
        button.pack(side="left")
        button._style_config = style_config
        button.bind("<Enter>", self._on_button_hover)
        button.bind("<Leave>", self._on_button_leave)
        return button

    def _on_button_hover(self, event) -> None:
        button = event.widget
        if str(button["state"]) == "disabled":
            return
        style = button._style_config
        button.configure(bg=style["hover_bg"], fg=style["hover_fg"])

    def _on_button_leave(self, event) -> None:
        button = event.widget
        if str(button["state"]) == "disabled":
            return
        style = button._style_config
        button.configure(bg=style["bg"], fg=style["fg"])

    def _stat_block(self, parent: tk.Widget, label_text: str) -> tk.Label:
        frame = tk.Frame(parent, bg=Theme.toolbar_bg, padx=12)
        frame.pack(side="left")

        value = tk.Label(
            frame,
            text="0",
            font=Theme.font_stat_num,
            bg=Theme.toolbar_bg,
            fg=Theme.text_primary,
        )
        value.pack()

        tk.Label(
            frame,
            text=label_text,
            font=Theme.font_stat_label,
            bg=Theme.toolbar_bg,
            fg=Theme.text_muted,
        ).pack()

        return value

    def _divider(self, parent: tk.Widget) -> None:
        tk.Frame(parent, bg=Theme.border, width=1, height=32).pack(side="left", padx=12)

    def _canvas_panel(
        self,
        parent: tk.Widget,
        label_text: str,
        label_color: str,
        column: int,
        clickable: bool = False,
    ) -> tk.Canvas:
        panel = tk.Frame(parent, bg=Theme.window_bg)
        panel.grid(row=0, column=column)

        tk.Label(
            panel,
            text=label_text,
            font=Theme.font_canvas_label,
            bg=Theme.window_bg,
            fg=label_color,
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        border = tk.Frame(panel, bg=Theme.border, padx=2, pady=2)
        border.pack()

        inner = tk.Frame(border, bg=Theme.card_bg)
        inner.pack()

        canvas = tk.Canvas(
            inner,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=Theme.card_bg,
            highlightthickness=0,
        )
        canvas.pack()

        if clickable:
            canvas.bind("<Button-1>", lambda event: self.on_click(event.x, event.y))

        return canvas

    def set_images(
        self,
        original: Image.Image,
        modified: Image.Image,
        offset_x: int,
        offset_y: int,
    ) -> None:
        self._orig_image_tk = ImageTk.PhotoImage(original)
        self._mod_image_tk = ImageTk.PhotoImage(modified)

        self.original_canvas.delete("all")
        self.modified_canvas.delete("all")

        self.original_canvas.create_image(
            offset_x, offset_y, anchor="nw", image=self._orig_image_tk, tags="img"
        )
        self.modified_canvas.create_image(
            offset_x, offset_y, anchor="nw", image=self._mod_image_tk, tags="img"
        )

    def clear_marks(self) -> None:
        self.original_canvas.delete("mark")
        self.modified_canvas.delete("mark")

    def draw_circle(self, cx: int, cy: int, radius: int, color: str) -> None:
        x0, y0 = cx - radius, cy - radius
        x1, y1 = cx + radius, cy + radius
        for canvas in (self.original_canvas, self.modified_canvas):
            canvas.create_oval(
                x0,
                y0,
                x1,
                y1,
                outline=color,
                width=3,
                tags="mark",
            )

    def update_stats(self, remaining: int, mistakes: int, found: int) -> None:
        remaining_color = Theme.success if remaining > 0 else Theme.accent
        self.remaining_value.config(text=str(remaining), fg=remaining_color)

        if mistakes == 0:
            mistake_color = Theme.text_primary
        elif mistakes == 1:
            mistake_color = Theme.warning
        else:
            mistake_color = Theme.danger
        self.mistakes_value.config(text=f"{mistakes} / 3", fg=mistake_color)

        self.found_value.config(text=f"{found} / 5", fg=Theme.text_primary)

    def flash_found(self) -> None:
        self.found_value.config(fg=Theme.success)
        self.root.after(300, lambda: self.found_value.config(fg=Theme.text_primary))

    def set_status(self, message: str, color: str | None = None) -> None:
        self.status_label.config(text=message, fg=color or Theme.text_muted)

    def set_status_temporary(
        self, message: str, color: str, reset_message: str, reset_color: str, timeout_ms: int = 2000
    ) -> None:
        if self._status_after_id:
            self.root.after_cancel(self._status_after_id)
        self.set_status(message, color)
        self._status_after_id = self.root.after(
            timeout_ms, lambda: self.set_status(reset_message, reset_color)
        )

    def set_reveal_enabled(self, enabled: bool) -> None:
        button = self.reveal_button
        style = button._style_config
        if enabled:
            button.config(state="normal", cursor="hand2", bg=style["bg"], fg=style["fg"])
        else:
            button.config(
                state="disabled",
                cursor="arrow",
                bg=style["disabled_bg"],
                fg=style["disabled_fg"],
            )
