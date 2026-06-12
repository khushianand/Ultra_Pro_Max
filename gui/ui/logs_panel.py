from __future__ import annotations
import customtkinter as ctk


class LogsPanel(ctk.CTkFrame):
    def __init__(self, master, palette: dict, open_output_command=None):
        super().__init__(
            master,
            corner_radius=12,
            fg_color=palette["panel"],
            border_width=1,
            border_color=palette.get("card_border", palette["border"]),
        )
        self.search_var = ctk.StringVar()
        self.open_output_command = open_output_command
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(8, 4))
        ctk.CTkLabel(top, text="● Live Logs", text_color=palette.get("status_ready", palette.get("green", "#22C55E")), font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkLabel(top, text="⌁⌁⌁", text_color=palette["primary"]).pack(side="right", padx=(8, 0))
        controls = ctk.CTkFrame(self, fg_color="transparent")
        controls.pack(fill="x", padx=12, pady=(2, 6))
        ctk.CTkEntry(
            controls,
            textvariable=self.search_var,
            placeholder_text="Search logs...",
            fg_color=palette.get("input_bg", palette["panel"]),
            border_color=palette.get("input_border", palette["border"]),
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            controls,
            text="▣ Open Output File",
            font=("Consolas", 14),
            width=160,
            fg_color=palette.get("button_blue", palette["primary"]),
            command=self._open_output_file,
        ).pack(side="left", padx=3)
        self.text = ctk.CTkTextbox(
            self,
            height=120,
            font=("Consolas", 11),
            fg_color=palette.get("log_bg", "#0b1020"),
            text_color=palette["text"],
            border_color=palette.get("border", "#334155"),
            border_width=1,
        )
        self.text.pack(fill="both", expand=True, padx=12, pady=(0, 10))

    def append(self, msg: str):
        self.text.insert("end", msg + "\n")
        self.text.see("end")

    def _open_output_file(self):
        if self.open_output_command:
            self.open_output_command()
