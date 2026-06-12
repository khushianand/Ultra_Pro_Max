from __future__ import annotations
import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    ITEMS = [
        ("⌂", "Dashboard"),
        ("▣", "Make Report"),
        ("▧", "Generate Tracking"),
        ("◉", "Add VAMS Data"),
        ("▣", "Show Summary"),
        ("☷", "Logs"),
        ("⚙", "Settings"),
    ]

    def __init__(self, master, palette: dict, on_select):
        super().__init__(
            master,
            corner_radius=12,
            fg_color=palette.get("sidebar_bg", palette["panel"]),
            border_width=1,
            border_color=palette.get("card_border", palette["border"]),
            width=190,
        )
        self.palette = palette
        self.on_select = on_select
        self.buttons = {}
        self.grid_columnconfigure(0, weight=1)

        for i, (icon, label) in enumerate(self.ITEMS):
            btn = ctk.CTkButton(
                self,
                text=f"{icon}  {label}",
                fg_color="transparent",
                hover_color=palette.get("nav_hover", palette["secondary"]),
                text_color=palette["text"],
                anchor="w",
                command=lambda name=label: self._select(name),
            )
            btn.grid(row=i, column=0, sticky="ew", padx=10, pady=4)
            self.buttons[label] = btn

        self.grid_rowconfigure(len(self.ITEMS), weight=1)
        ctk.CTkLabel(
            self,
            text="Stronger today,\nSafer tomorrow.",
            text_color=palette.get("muted", palette["text"]),
            font=ctk.CTkFont(size=13, weight="bold"),
            justify="center",
        ).grid(row=len(self.ITEMS) + 1, column=0, sticky="s", padx=14, pady=(16, 18))

    def _select(self, name: str):
        for label, btn in self.buttons.items():
            active = label == name
            btn.configure(
                fg_color=(self.palette.get("sidebar_active", self.palette["secondary"]) if active else "transparent"),
                text_color=(self.palette.get("primary", self.palette["text"]) if active else self.palette["text"]),
            )
        self.on_select(name)
