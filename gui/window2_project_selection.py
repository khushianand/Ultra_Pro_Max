"""Window 2: modern project selection."""
import customtkinter as ctk
from gui.ui.themes import palette


PROJECTS = ["PTA", "3UK", "Airtel", "Antina", "AT&T Mexico", "AT&T US", "Fast-Web", "One NZ"]


class Window2ProjectSelection(ctk.CTkFrame):
    def __init__(self, master, state, on_prev, on_next):
        super().__init__(master)
        self.state = state
        self.on_prev = on_prev
        self.on_next = on_next
        self.colors = palette(self.state.get("theme_name", "Dark"))
        self.project_var = ctk.StringVar(value=state.get("selected_project", PROJECTS[0]))
        self.configure(fg_color=self.colors["bg"])
        self._build()

    def _build(self):
        card = ctk.CTkFrame(self, corner_radius=12, fg_color=self.colors["panel"], border_width=1, border_color=self.colors["border"])
        card.pack(fill="both", expand=True, padx=24, pady=24)
        ctk.CTkLabel(card, text="🏢 Select Project", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=20, pady=(20, 8))
        ctk.CTkComboBox(card, values=PROJECTS, variable=self.project_var).pack(fill="x", padx=20, pady=(0, 12))
        footer = ctk.CTkFrame(card, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=20)
        ctk.CTkButton(footer, text="← Previous", fg_color=self.colors["secondary"], command=self.on_prev).pack(side="left")
        ctk.CTkButton(footer, text="Next →", fg_color=self.colors["primary"], command=self._next).pack(side="right")

    def _next(self):
        self.state["selected_project"] = self.project_var.get().strip()
        self.on_next()
