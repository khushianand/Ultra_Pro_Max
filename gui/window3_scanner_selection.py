"""Window 3: modern scanner selection."""
import customtkinter as ctk
from gui.ui.themes import palette


SCANNERS = ["Nessus", "Qualys", "Anchor"]
HINTS = {
    "Nessus": "Best for network/IP vulnerability inventories.",
    "Qualys": "Strong for enterprise VM and ticket-driven remediation flows.",
    "Anchor": "Container image and software composition security context.",
}


class Window3ScannerSelection(ctk.CTkFrame):
    def __init__(self, master, state, on_prev, on_next):
        super().__init__(master)
        self.state = state
        self.on_prev = on_prev
        self.on_next = on_next
        self.colors = palette(self.state.get("theme_name", "Dark"))
        self.scanner_var = ctk.StringVar(value=state.get("selected_scanner", SCANNERS[0]))
        self.hint_var = ctk.StringVar(value=HINTS.get(self.scanner_var.get(), ""))
        self.configure(fg_color=self.colors["bg"])
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self, corner_radius=12, fg_color=self.colors["panel"], border_width=1, border_color=self.colors["border"])
        card.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(card, text="📡 Select Scanner", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=20, pady=(20, 8))
        combo = ctk.CTkComboBox(card, values=SCANNERS, variable=self.scanner_var, command=self._on_scanner_change)
        combo.pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkLabel(card, textvariable=self.hint_var).pack(anchor="w", padx=20, pady=(0, 12))
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(footer, text="← Previous", fg_color=self.colors["secondary"], command=self.on_prev).pack(side="left")
        ctk.CTkButton(footer, text="Launch Dashboard →", fg_color=self.colors["primary"], command=self._next).pack(side="right")

    def _on_scanner_change(self, value: str):
        self.hint_var.set(HINTS.get(value, ""))

    def _next(self):
        self.state["selected_scanner"] = self.scanner_var.get().strip()
        self.on_next()
