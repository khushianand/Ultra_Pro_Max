from __future__ import annotations
import customtkinter as ctk


class SummaryCards(ctk.CTkFrame):
    def __init__(self, master, palette: dict):
        super().__init__(master, fg_color="transparent")
        self.cards = {}
        self.tags = {}
        card_specs = [
            ("Vulnerabilities Processed", "🛡", "Total sheet count: {value}", palette["primary"]),
            ("Unique Vulnerabilities", "🧩", "Unique sheet count: {value}", palette.get("green", palette["primary"])),
            ("Processing Time", "⏱", "Elapsed time: {value}", palette.get("purple", palette["secondary"])),
            ("Success Rate", "📈", "Completion: {value}", palette.get("orange", palette["secondary"])),
        ]
        for i, (name, icon, tag_template, accent) in enumerate(card_specs):
            card = ctk.CTkFrame(
                self,
                corner_radius=12,
                fg_color=palette["panel"],
                border_width=1,
                border_color=palette.get("card_border", palette["border"]),
            )
            card.grid(row=0, column=i, sticky="nsew", padx=7, pady=2)
            self.grid_columnconfigure(i, weight=1)
            value = ctk.StringVar(value="0")
            tag = ctk.StringVar(value=tag_template.format(value="0"))
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=12)
            ctk.CTkLabel(
                row,
                text=icon,
                width=44,
                height=44,
                corner_radius=22,
                fg_color=accent,
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=28),
            ).pack(side="left", padx=(0, 10))
            text = ctk.CTkFrame(row, fg_color="transparent")
            text.pack(side="left", fill="both", expand=True)
            ctk.CTkLabel(text, text=name, text_color=palette["text"], font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w")
            ctk.CTkLabel(text, textvariable=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=accent).pack(anchor="w")
            #ctk.CTkLabel(text, textvariable=tag, text_color=accent, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w")
            #ctk.CTkLabel(row, text="⌁⌁⌁", text_color=accent, font=ctk.CTkFont(size=20)).pack(side="right")
            self.cards[name] = value
            self.tags[name] = (tag, tag_template)

    def update_metrics(self, **values):
        for k, v in values.items():
            if k in self.cards:
                value = str(v)
                self.cards[k].set(value)
                tag, template = self.tags[k]
                tag.set(template.format(value=value))
