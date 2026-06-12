from __future__ import annotations

import customtkinter as ctk


class HeaderPanel(ctk.CTkFrame):
    def __init__(self, master, palette: dict, get_theme_name):
        super().__init__(
            master,
            corner_radius=12,
            fg_color=palette["panel"],
            border_width=1,
            border_color=palette.get("card_border", palette["border"]),
        )
        self.get_theme_name = get_theme_name
        self.status_var = ctk.StringVar(value="Ready")
        self.theme_var = ctk.StringVar(value=self.get_theme_name())

        self.grid_columnconfigure(1, weight=1)
        icon = ctk.CTkLabel(self, text="🛡", font=ctk.CTkFont(size=34), text_color=palette["primary"])
        icon.grid(row=0, column=0, rowspan=2, sticky="w", padx=(18, 10), pady=12)
        ctk.CTkLabel(
            self,
            text="Vulnerability Management Automation Tool",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=palette["text"],
        ).grid(row=0, column=1, sticky="w", pady=(12, 0))
        ctk.CTkLabel(
            self,
            text="Automate vulnerability assessment & reporting with ease",
            text_color=palette.get("secondary_text", palette["muted"]),
        ).grid(row=1, column=1, sticky="w", pady=(0, 12))
        self.meta = ctk.CTkLabel(
            self,
            textvariable=self._meta_text(),
            text_color=palette["text"],
            fg_color=palette.get("card_alt", palette["panel"]),
            corner_radius=8,
            padx=12,
            pady=8,
        )
        self.meta.grid(row=0, column=2, rowspan=2, sticky="e", padx=18)

    def _meta_text(self):
        var = ctk.StringVar()

        def refresh(*_):
            var.set(f"Theme: {self.theme_var.get()}   |   Run Status: ● {self.status_var.get()}")

        self.theme_var.trace_add("write", refresh)
        self.status_var.trace_add("write", refresh)
        refresh()
        return var
