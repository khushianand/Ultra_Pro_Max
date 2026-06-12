"""Window 1: modern entry mode selection (CNF / VNF)."""
import customtkinter as ctk
from gui.ui.themes import palette


class Window1Entry(ctk.CTkFrame):
    def __init__(self, master, state, on_next):
        super().__init__(master)
        self.state = state
        self.on_next = on_next
        self.colors = palette(self.state.get("theme_name", "Dark"))
        self.mode = ctk.StringVar(value=state.get("entry_mode", "VNF"))
        self.configure(fg_color=self.colors["bg"])
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self, corner_radius=12, fg_color=self.colors["panel"], border_width=1, border_color=self.colors["border"])
        card.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(card, text="🛡 Select Assessment Mode", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=20, pady=(20, 8))
        ctk.CTkLabel(card, text="Choose VNF for IP-based scans, or CNF for image/cloud-native assessments.").pack(anchor="w", padx=20, pady=(0, 12))
        ctk.CTkRadioButton(card, text="VNF (Recommended)", variable=self.mode, value="VNF").pack(anchor="w", padx=20, pady=6)
        ctk.CTkRadioButton(card, text="CNF", variable=self.mode, value="CNF").pack(anchor="w", padx=20, pady=6)
        ctk.CTkButton(card, text="Next →", fg_color=self.colors["primary"], command=self._next).pack(anchor="e", padx=20, pady=20)

    def _next(self):
        self.state["entry_mode"] = self.mode.get()
        self.on_next()
