import re
import tkinter as tk


WPM_MIN = 100
WPM_MAX = 1200
TEXT_SIZE_MIN = 32
TEXT_SIZE_MAX = 110

THEMES = {
    "dark": {
        "window": "#1F2937",
        "panel": "#111827",
        "text": "#F9FAFB",
        "muted": "#9CA3AF",
        "accent": "#E0F2FE",
        "input_bg": "#F3F4F6",
        "input_text": "#111827",
        "highlight_bg": "#075985",
        "highlight_text": "#F0F9FF",
        "slider_track": "#374151",
        "slider_fill": "#38BDF8",
        "slider_thumb": "#F9FAFB",
        "button_bg": "#7A7A7A",
        "button_active": "#8A8A8A",
        "button_text": "#F9FAFB",
    },
    "light": {
        "window": "#EEF2F7",
        "panel": "#F8FAFC",
        "text": "#1F2937",
        "muted": "#64748B",
        "accent": "#075985",
        "input_bg": "#FFFFFF",
        "input_text": "#111827",
        "highlight_bg": "#BAE6FD",
        "highlight_text": "#0F172A",
        "slider_track": "#D7DEE8",
        "slider_fill": "#0EA5E9",
        "slider_thumb": "#FFFFFF",
        "button_bg": "#CBD5E1",
        "button_active": "#B6C2D1",
        "button_text": "#1F2937",
    },
}


class RoundedSlider(tk.Canvas):
    def __init__(
        self,
        master,
        from_,
        to,
        variable,
        command,
        height=22,
        track_height=8,
        thumb_radius=8,
        **kwargs,
    ):
        super().__init__(
            master,
            height=height,
            borderwidth=0,
            highlightthickness=0,
            **kwargs,
        )
        self.min_value = from_
        self.max_value = to
        self.variable = variable
        self.command = command
        self.track_height = track_height
        self.thumb_radius = thumb_radius
        self.colors = {
            "panel": "#111827",
            "track": "#374151",
            "fill": "#38BDF8",
            "thumb": "#F9FAFB",
        }

        self.bind("<Configure>", lambda event: self._draw())
        self.bind("<Button-1>", self._set_from_event)
        self.bind("<B1-Motion>", self._set_from_event)

    def apply_theme(self, colors):
        self.colors = {
            "panel": colors["panel"],
            "track": colors["slider_track"],
            "fill": colors["slider_fill"],
            "thumb": colors["slider_thumb"],
        }
        self.configure(bg=colors["panel"])
        self._draw()

    def set_value(self, value):
        clamped = min(self.max_value, max(self.min_value, int(round(value))))
        self.variable.set(clamped)
        self.command(clamped)
        self._draw()

    def _set_from_event(self, event):
        x = min(self._right(), max(self._left(), event.x))
        ratio = (x - self._left()) / max(1, self._right() - self._left())
        self.set_value(self.min_value + ratio * (self.max_value - self.min_value))
        return "break"

    def _draw(self):
        self.delete("all")
        left = self._left()
        right = self._right()
        center_y = self.winfo_height() / 2
        track_top = center_y - self.track_height / 2
        track_bottom = center_y + self.track_height / 2
        radius = self.track_height / 2
        ratio = (
            (self.variable.get() - self.min_value)
            / max(1, self.max_value - self.min_value)
        )
        thumb_x = left + ratio * (right - left)

        self._rounded_rect(
            left,
            track_top,
            right,
            track_bottom,
            radius,
            fill=self.colors["track"],
        )
        self._rounded_rect(
            left,
            track_top,
            thumb_x,
            track_bottom,
            radius,
            fill=self.colors["fill"],
        )
        self.create_oval(
            thumb_x - self.thumb_radius,
            center_y - self.thumb_radius,
            thumb_x + self.thumb_radius,
            center_y + self.thumb_radius,
            fill=self.colors["thumb"],
            outline=self.colors["fill"],
            width=2,
        )

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        if x2 - x1 <= 0:
            return
        kwargs.setdefault("outline", kwargs.get("fill", ""))
        radius = min(radius, (x2 - x1) / 2)
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        self.create_oval(x1, y1, x1 + radius * 2, y2, **kwargs)
        self.create_oval(x2 - radius * 2, y1, x2, y2, **kwargs)

    def _left(self):
        return self.thumb_radius + 2

    def _right(self):
        return max(self._left(), self.winfo_width() - self.thumb_radius - 2)


class CanvasButton(tk.Canvas):
    def __init__(self, master, text, command, height=30, **kwargs):
        super().__init__(
            master,
            height=height,
            borderwidth=0,
            highlightthickness=0,
            **kwargs,
        )
        self.text = text
        self.command = command
        self.pressed = False
        self.colors = {
            "bg": "#1F2937",
            "face": "#7A7A7A",
            "active": "#8A8A8A",
            "text": "#F9FAFB",
        }

        self.configure(cursor="hand2")
        self.bind("<Configure>", lambda event: self._draw())
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)

    def apply_theme(self, colors):
        self.colors = {
            "bg": colors["window"],
            "face": colors["button_bg"],
            "active": colors["button_active"],
            "text": colors["button_text"],
        }
        self.configure(bg=colors["window"])
        self._draw()

    def _press(self, event):
        self.pressed = True
        self._draw()
        return "break"

    def _release(self, event):
        was_pressed = self.pressed
        self.pressed = False
        self._draw()
        if was_pressed and 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            self.command()
        return "break"

    def _draw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            return

        face = self.colors["active"] if self.pressed else self.colors["face"]
        self._rounded_rect(1, 1, width - 1, height - 1, 6, fill=face)
        self.create_text(
            width / 2,
            height / 2,
            text=self.text,
            fill=self.colors["text"],
            font=("Segoe UI", 11, "bold"),
        )

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        kwargs.setdefault("outline", kwargs.get("fill", ""))
        radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)
        self.create_oval(x1, y1, x1 + radius * 2, y1 + radius * 2, **kwargs)
        self.create_oval(x2 - radius * 2, y1, x2, y1 + radius * 2, **kwargs)
        self.create_oval(x1, y2 - radius * 2, x1 + radius * 2, y2, **kwargs)
        self.create_oval(x2 - radius * 2, y2 - radius * 2, x2, y2, **kwargs)


class CanvasCheckbutton(tk.Canvas):
    def __init__(self, master, text, variable, command, height=30, **kwargs):
        super().__init__(
            master,
            width=150,
            height=height,
            borderwidth=0,
            highlightthickness=0,
            **kwargs,
        )
        self.text = text
        self.variable = variable
        self.command = command
        self.colors = {
            "bg": "#1F2937",
            "text": "#F9FAFB",
            "accent": "#38BDF8",
            "track": "#374151",
        }

        self.configure(cursor="hand2")
        self.bind("<Configure>", lambda event: self._draw())
        self.bind("<Button-1>", self._toggle)

    def apply_theme(self, colors):
        self.colors = {
            "bg": colors["window"],
            "text": colors["text"],
            "accent": colors["slider_fill"],
            "track": colors["slider_track"],
        }
        self.configure(bg=colors["window"])
        self._draw()

    def _toggle(self, event):
        self.variable.set(not self.variable.get())
        self.command()
        self._draw()
        return "break"

    def _draw(self):
        self.delete("all")
        height = self.winfo_height()
        box_size = 18
        box_x = 2
        box_y = (height - box_size) / 2
        fill = self.colors["accent"] if self.variable.get() else self.colors["bg"]
        outline = self.colors["accent"] if self.variable.get() else self.colors["track"]

        self._rounded_rect(
            box_x,
            box_y,
            box_x + box_size,
            box_y + box_size,
            4,
            fill=fill,
            outline=outline,
        )
        if self.variable.get():
            self.create_line(
                box_x + 4,
                box_y + 9,
                box_x + 8,
                box_y + 13,
                box_x + 14,
                box_y + 5,
                fill="#FFFFFF",
                width=3,
                capstyle="round",
                joinstyle="round",
            )
        self.create_text(
            box_x + box_size + 8,
            height / 2,
            text=self.text,
            anchor="w",
            fill=self.colors["text"],
            font=("Segoe UI", 11),
        )

    def _rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, **kwargs)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, **kwargs)
        self.create_oval(x1, y1, x1 + radius * 2, y1 + radius * 2, **kwargs)
        self.create_oval(x2 - radius * 2, y1, x2, y1 + radius * 2, **kwargs)
        self.create_oval(x1, y2 - radius * 2, x1 + radius * 2, y2, **kwargs)
        self.create_oval(x2 - radius * 2, y2 - radius * 2, x2, y2, **kwargs)


class SpeedReaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SPEADER")
        self.dark_mode = tk.BooleanVar(value=True)
        self.configure(bg=THEMES["dark"]["window"])

        self.word_list = []
        self.current_word_index = 0
        self.highlighted_word_index = None
        self.running = False
        self.wpm = tk.IntVar(value=300)
        self.wpm_text = tk.StringVar(value=str(self.wpm.get()))
        self.text_size = tk.IntVar(value=70)
        self.text_size_text = tk.StringVar(value=str(self.text_size.get()))

        self._build_ui()
        self._apply_theme()
        self._fit_initial_window()
        self._update_status()

    def _build_ui(self):
        header = tk.Label(
            self,
            text="Off-Brand Speed Reading Application",
            bg="#111827",
            fg="#F9FAFB",
            font=("Segoe UI", 24, "bold"),
            pady=12,
        )
        header.pack(fill="x", padx=10, pady=(10, 4))

        display_frame = tk.Frame(self, bg="#111827")
        display_frame.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        self.word_display = tk.Label(
            display_frame,
            text="Ready",
            bg="#111827",
            fg="#E0F2FE",
            font=("Segoe UI", self.text_size.get(), "bold"),
            wraplength=760,
            justify="center",
        )
        self.word_display.pack(expand=True, pady=16)

        controls_frame = tk.Frame(self, bg="#111827")
        controls_frame.pack(fill="x", padx=10, pady=(0, 8))

        speed_frame = tk.Frame(controls_frame, bg="#111827")
        speed_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))

        speed_label = tk.Label(
            speed_frame,
            text="Speed (WPM)",
            bg="#111827",
            fg="#F9FAFB",
            font=("Segoe UI", 12, "bold"),
        )
        speed_label.pack(anchor="w")

        self.speed_slider = RoundedSlider(
            speed_frame,
            from_=WPM_MIN,
            to=WPM_MAX,
            variable=self.wpm,
            command=self._on_speed_change,
        )
        self.speed_slider.pack(fill="x", pady=(8, 4))

        speed_value_frame = tk.Frame(speed_frame, bg="#111827")
        speed_value_frame.pack(anchor="e")

        self.speed_value_entry = tk.Entry(
            speed_value_frame,
            textvariable=self.wpm_text,
            font=("Segoe UI", 11),
            width=5,
            justify="right",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
        )
        self.speed_value_entry.pack(side="left")
        self.speed_value_entry.bind("<Return>", self._on_wpm_entry_commit)
        self.speed_value_entry.bind("<FocusOut>", self._on_wpm_entry_commit)

        speed_unit_label = tk.Label(
            speed_value_frame,
            text=" WPM",
            bg="#111827",
            fg="#F9FAFB",
            font=("Segoe UI", 11),
        )
        speed_unit_label.pack(side="left")

        text_size_frame = tk.Frame(controls_frame, bg="#111827")
        text_size_frame.pack(side="left", fill="x", expand=True, padx=(8, 0))

        text_size_label = tk.Label(
            text_size_frame,
            text="Text size",
            bg="#111827",
            fg="#F9FAFB",
            font=("Segoe UI", 12, "bold"),
        )
        text_size_label.pack(anchor="w")

        self.text_size_slider = RoundedSlider(
            text_size_frame,
            from_=TEXT_SIZE_MIN,
            to=TEXT_SIZE_MAX,
            variable=self.text_size,
            command=self._on_text_size_change,
        )
        self.text_size_slider.pack(fill="x", pady=(8, 4))

        text_size_value_frame = tk.Frame(text_size_frame, bg="#111827")
        text_size_value_frame.pack(anchor="e")

        self.text_size_value_entry = tk.Entry(
            text_size_value_frame,
            textvariable=self.text_size_text,
            font=("Segoe UI", 11),
            width=4,
            justify="right",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
        )
        self.text_size_value_entry.pack(side="left")
        self.text_size_value_entry.bind(
            "<Return>", self._on_text_size_entry_commit)
        self.text_size_value_entry.bind(
            "<FocusOut>", self._on_text_size_entry_commit)

        text_size_unit_label = tk.Label(
            text_size_value_frame,
            text=" pt",
            bg="#111827",
            fg="#F9FAFB",
            font=("Segoe UI", 11),
        )
        text_size_unit_label.pack(side="left")

        self.button_frame = tk.Frame(self, bg="#1F2937")
        self.button_frame.pack(fill="x", padx=10, pady=(0, 10))

        start_button = CanvasButton(
            self.button_frame,
            text="Start",
            command=self.start,
        )
        start_button.pack(side="left", expand=True, fill="x", padx=(0, 4))

        pause_button = CanvasButton(
            self.button_frame,
            text="Pause",
            command=self.pause,
        )
        pause_button.pack(side="left", expand=True, fill="x", padx=4)

        reset_button = CanvasButton(
            self.button_frame,
            text="Reset",
            command=self.reset,
        )
        reset_button.pack(side="left", expand=True, fill="x", padx=(4, 0))

        theme_toggle = CanvasCheckbutton(
            self.button_frame,
            text="Dark mode",
            variable=self.dark_mode,
            command=self._on_theme_toggle,
        )
        theme_toggle.pack(side="left", padx=(12, 0))

        self.text_label = tk.Label(
            self,
            text="Paste text here",
            bg="#111827",
            fg="#F9FAFB",
            font=("Segoe UI", 12, "bold"),
        )
        self.text_label.pack(anchor="w", padx=10, pady=(8, 0))

        self.text_input = tk.Text(
            self,
            wrap="word",
            font=("Segoe UI", 12),
            bg="#F3F4F6",
            fg="#111827",
            relief="flat",
            height=5,
            padx=10,
            pady=10,
        )
        self.text_input.pack(fill="x", padx=10, pady=(4, 10))
        self.text_input.tag_configure("current_word")
        self.text_input.bind("<<Modified>>", self._on_text_change)
        self.text_input.bind("<Button-1>", self._on_text_click)

        self.status_label = tk.Label(
            self,
            text="Words: 0    Position: 0 / 0",
            bg="#1F2937",
            fg="#9CA3AF",
            font=("Segoe UI", 10),
        )
        self.status_label.pack(fill="x", padx=10, pady=(0, 10))

    def _fit_initial_window(self):
        self.update_idletasks()
        min_width = 760
        initial_width = max(820, self.winfo_reqwidth(), min_width)
        min_height = self.winfo_reqheight()

        self.minsize(min_width, min_height)
        self.geometry(f"{initial_width}x{min_height}")

    def _fit_height_to_content(self):
        self.update_idletasks()
        min_width = 760
        required_height = self.winfo_reqheight()
        current_width = self.winfo_width()
        current_height = self.winfo_height()

        self.minsize(min_width, required_height)
        if current_height < required_height:
            self.geometry(f"{current_width}x{required_height}")

    def _current_theme(self):
        return THEMES["dark"] if self.dark_mode.get() else THEMES["light"]

    def _apply_theme(self):
        colors = self._current_theme()
        self.configure(bg=colors["window"])

        def apply_to(widget):
            if isinstance(widget, tk.Frame):
                bg = colors["window"] if widget is self.button_frame else colors["panel"]
                widget.configure(bg=bg)
            elif isinstance(widget, RoundedSlider):
                widget.apply_theme(colors)
            elif isinstance(widget, (CanvasButton, CanvasCheckbutton)):
                widget.apply_theme(colors)
            elif isinstance(widget, tk.Label):
                if widget is self.status_label:
                    widget.configure(bg=colors["window"], fg=colors["muted"])
                elif widget is self.text_label:
                    widget.configure(bg=colors["window"], fg=colors["text"])
                elif widget is self.word_display:
                    widget.configure(bg=colors["panel"], fg=colors["accent"])
                else:
                    widget.configure(bg=colors["panel"], fg=colors["text"])
            elif isinstance(widget, tk.Text):
                widget.configure(
                    bg=colors["input_bg"],
                    fg=colors["input_text"],
                    insertbackground=colors["input_text"],
                )
                widget.tag_configure(
                    "current_word",
                    background=colors["highlight_bg"],
                    foreground=colors["highlight_text"],
                )
            elif isinstance(widget, tk.Entry):
                if widget in (self.speed_value_entry, self.text_size_value_entry):
                    widget.configure(
                        bg=colors["panel"],
                        fg=colors["text"],
                        insertbackground=colors["text"],
                    )
                else:
                    widget.configure(
                        bg=colors["input_bg"],
                        fg=colors["input_text"],
                        insertbackground=colors["input_text"],
                    )

            for child in widget.winfo_children():
                apply_to(child)

        for child in self.winfo_children():
            apply_to(child)

    def _on_theme_toggle(self):
        self._apply_theme()

    def _on_speed_change(self, value):
        self.wpm_text.set(str(int(float(value))))

    def _on_wpm_entry_commit(self, event=None):
        value = self.wpm_text.get().strip()
        try:
            wpm = int(value)
        except ValueError:
            wpm = self.wpm.get()

        wpm = min(WPM_MAX, max(WPM_MIN, wpm))
        self.wpm.set(wpm)
        self.wpm_text.set(str(wpm))
        self.speed_slider._draw()

    def _on_text_size_change(self, value):
        size = int(float(value))
        self.text_size_text.set(str(size))
        self.word_display.config(font=("Segoe UI", size, "bold"))
        self._fit_height_to_content()

    def _on_text_size_entry_commit(self, event=None):
        value = self.text_size_text.get().strip()
        try:
            size = int(value)
        except ValueError:
            size = self.text_size.get()

        size = min(TEXT_SIZE_MAX, max(TEXT_SIZE_MIN, size))
        self.text_size.set(size)
        self.text_size_text.set(str(size))
        self.word_display.config(font=("Segoe UI", size, "bold"))
        self.text_size_slider._draw()
        self._fit_height_to_content()

    def _on_text_change(self, event):
        if self.text_input.edit_modified():
            self.current_word_index = 0
            self.highlighted_word_index = None
            self.word_list = []
            self.running = False
            self.word_display.config(text="Ready")
            self._clear_word_highlight()
            self._update_status()
            self.text_input.edit_modified(False)

    def _on_text_click(self, event):
        if not self.word_list:
            self._refresh_word_list()

        clicked_index = self.text_input.index(f"@{event.x},{event.y}")
        word_index = self._word_index_at_text_position(clicked_index)
        if word_index is None:
            return

        self._show_word_at_index(word_index)
        self.current_word_index = word_index + 1 if self.running else word_index
        self._update_status()

    def _update_status(self):
        total = len(self.word_list)
        if self.highlighted_word_index is not None:
            pos = self.highlighted_word_index + 1
        else:
            pos = self.current_word_index if total else 0
        self.status_label.config(
            text=f"Words: {total}    Position: {pos} / {total}")

    def _refresh_word_list(self):
        raw_text = self.text_input.get("1.0", "end-1c")
        self.word_list = []

        for match in re.finditer(r"\S+", raw_text):
            start = f"1.0 + {match.start()} chars"
            end = f"1.0 + {match.end()} chars"
            self.word_list.append({
                "text": match.group(),
                "start": start,
                "end": end,
            })

    def _clear_word_highlight(self):
        self.text_input.tag_remove("current_word", "1.0", "end")

    def _highlight_word_at_index(self, word_index):
        self._clear_word_highlight()
        if not 0 <= word_index < len(self.word_list):
            self.highlighted_word_index = None
            return

        word = self.word_list[word_index]
        self.text_input.tag_add("current_word", word["start"], word["end"])
        self.text_input.see(word["start"])
        self.highlighted_word_index = word_index

    def _show_word_at_index(self, word_index):
        if not 0 <= word_index < len(self.word_list):
            return

        word = self.word_list[word_index]
        self.word_display.config(text=word["text"])
        self._highlight_word_at_index(word_index)

    def _word_index_at_text_position(self, text_index):
        for index, word in enumerate(self.word_list):
            if (
                self.text_input.compare(word["start"], "<=", text_index)
                and self.text_input.compare(text_index, "<", word["end"])
            ):
                return index
        return None

    def start(self):
        self._refresh_word_list()
        if not self.word_list:
            self.word_display.config(text="Paste some text to begin.")
            self.current_word_index = 0
            self.highlighted_word_index = None
            self.running = False
            self._clear_word_highlight()
            self._update_status()
            return

        if self.current_word_index >= len(self.word_list):
            self.current_word_index = 0

        self.running = True
        self._update_status()
        self._schedule_next_word()

    def pause(self):
        self.running = False
        self.word_display.config(text="Paused")
        self._update_status()

    def reset(self):
        self.running = False
        self.current_word_index = 0
        self.word_list = []
        self.highlighted_word_index = None
        self.word_display.config(text="Ready")
        self._clear_word_highlight()
        self._update_status()

    def _schedule_next_word(self):
        if not self.running:
            return
        if self.current_word_index >= len(self.word_list):
            self.running = False
            self.word_display.config(text="Finished")
            self._clear_word_highlight()
            self._update_status()
            return

        self._show_word_at_index(self.current_word_index)
        self.current_word_index += 1
        self._update_status()

        delay_ms = int(60000 / max(1, self.wpm.get()))
        self.after(delay_ms, self._schedule_next_word)


if __name__ == "__main__":
    app = SpeedReaderApp()
    app.mainloop()
