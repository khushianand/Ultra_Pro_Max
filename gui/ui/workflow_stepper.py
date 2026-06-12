from __future__ import annotations
import customtkinter as ctk


class WorkflowStepper(ctk.CTkFrame):
    STEPS = ["Inputs", "Parse", "Compare", "Enrich", "Write"]

    def __init__(self, master, palette: dict):
        super().__init__(master, corner_radius=12, fg_color=palette["panel"], border_width=1, border_color=palette["border"])
        self.palette = palette
        self.labels = []
        divider_color = palette.get("divider", palette.get("border", "#E4EAF3"))
        for i, step in enumerate(self.STEPS):
            lbl = ctk.CTkLabel(self, text=f"○ {step}")
            lbl.grid(row=0, column=i * 2, padx=(8, 2), pady=8, sticky="w")
            self.labels.append(lbl)
            if i < len(self.STEPS) - 1:
                ctk.CTkLabel(self, text="────", text_color=divider_color).grid(row=0, column=i * 2 + 1, sticky="ew")

    def set_active(self, step_name: str):
        try:
            active_idx = self.STEPS.index(step_name)
        except ValueError:
            active_idx = -1
        for i, lbl in enumerate(self.labels):
            if i < active_idx:
                lbl.configure(text=f"✔ {self.STEPS[i]}", text_color=self.palette.get("success", self.palette.get("green", "#22C55E")))
            elif i == active_idx:
                lbl.configure(text=f"◉ {self.STEPS[i]}", text_color=self.palette.get("primary", "#2563EB"))
            else:
                lbl.configure(text=f"○ {self.STEPS[i]}", text_color=self.palette.get("muted", "#6B7280"))
