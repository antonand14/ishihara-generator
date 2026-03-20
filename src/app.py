"""
Tkinter UI for the Ishihara plate generator.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import ImageTk
import threading

import generator
from generator import generate_plate


DEFAULT_FG = "#E07020"  # orange-red (text circles)
DEFAULT_BG = "#60A840"  # green (background circles)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ishihara Plate Generator")
        self.resizable(False, False)

        self._fg_color = DEFAULT_FG
        self._bg_color = DEFAULT_BG
        self._current_image = None

        self._build_ui()

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        pad = {"padx": 8, "pady": 4}

        controls = ttk.Frame(self)
        controls.pack(fill="x", **pad)

        # Text input
        ttk.Label(controls, text="Text:").grid(row=0, column=0, sticky="w", **pad)
        self._text_var = tk.StringVar(value="12")
        ttk.Entry(controls, textvariable=self._text_var, width=20).grid(row=0, column=1, sticky="w", **pad)

        # Circle size sliders
        ttk.Label(controls, text="Min radius:").grid(row=1, column=0, sticky="w", **pad)
        self._min_r = tk.IntVar(value=generator.MIN_R)
        ttk.Spinbox(controls, from_=2, to=20, textvariable=self._min_r, width=5).grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(controls, text="Max radius:").grid(row=2, column=0, sticky="w", **pad)
        self._max_r = tk.IntVar(value=generator.MAX_R)
        ttk.Spinbox(controls, from_=2, to=40, textvariable=self._max_r, width=5).grid(row=2, column=1, sticky="w", **pad)

        # Color pickers
        ttk.Label(controls, text="Text color:").grid(row=3, column=0, sticky="w", **pad)
        self._fg_btn = tk.Button(controls, width=4, bg=self._fg_color, command=self._pick_fg)
        self._fg_btn.grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(controls, text="Background color:").grid(row=4, column=0, sticky="w", **pad)
        self._bg_btn = tk.Button(controls, width=4, bg=self._bg_color, command=self._pick_bg)
        self._bg_btn.grid(row=4, column=1, sticky="w", **pad)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", **pad)

        ttk.Button(btn_frame, text="Generate", command=self._generate).pack(side="left", **pad)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side="left", **pad)
        ttk.Button(btn_frame, text="Clear", command=self._clear).pack(side="left", **pad)

        # Status label
        self._status_var = tk.StringVar(value="Enter text and click Generate.")
        ttk.Label(self, textvariable=self._status_var, foreground="gray").pack(**pad)

        # Canvas for plate preview
        self._canvas = tk.Canvas(self, width=600, height=600, bg="#f0f0f0")
        self._canvas.pack(**pad)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _pick_fg(self):
        color = colorchooser.askcolor(color=self._fg_color, title="Pick text color")[1]
        if color:
            self._fg_color = color
            self._fg_btn.config(bg=color)

    def _pick_bg(self):
        color = colorchooser.askcolor(color=self._bg_color, title="Pick background color")[1]
        if color:
            self._bg_color = color
            self._bg_btn.config(bg=color)

    def _generate(self):
        text = self._text_var.get().strip()
        if not text:
            messagebox.showwarning("Input needed", "Please enter some text.")
            return

        self._status_var.set("Generating…")
        self.update_idletasks()

        def run():
            img = generate_plate(text, self._fg_color, self._bg_color,
                                 self._min_r.get(), self._max_r.get())
            self._current_image = img
            tk_img = ImageTk.PhotoImage(img)
            self._canvas.image = tk_img  # keep reference
            self._canvas.create_image(0, 0, anchor="nw", image=tk_img)
            self._status_var.set(f"Done — {len(text)} character(s), text color {self._fg_color}, bg {self._bg_color}")

        threading.Thread(target=run, daemon=True).start()

    def _save(self):
        if self._current_image is None:
            messagebox.showinfo("Nothing to save", "Generate a plate first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg")],
        )
        if path:
            self._current_image.save(path)
            self._status_var.set(f"Saved to {path}")

    def _clear(self):
        self._canvas.delete("all")
        self._current_image = None
        self._status_var.set("Cleared.")


if __name__ == "__main__":
    App().mainloop()
