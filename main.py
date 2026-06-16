"""Application entry point and window-router for the Tkinter UI flow."""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from gui.window1_entry import Window1Entry
from gui.window2_project_selection import Window2ProjectSelection
from gui.window3_scanner_selection import Window3ScannerSelection
from gui.window4_main import Window4Main
from state.app_state import LiveMetrics
from utils.logger import get_logger


class App(ctk.CTk):
    """Main Tkinter application controller."""
    """Root app that stores shared state and navigates between wizard windows."""
    def __init__(self):
        """initializes the desktop application."""
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.title("Vulnerability Management Excel Automation")
        self.geometry("500x600")
        self.minsize(500, 600)
        self.resizable(True, True)
        self._configure_styles()
        self.state_data = {
            "entry_mode": "VNF",
            "selected_project": "Select Project",
            "selected_scanner": "Select Scanner",
            "theme_name": "Dark",
            "last_output_file": "",
            "live_metrics": LiveMetrics(),
        }
        self.logger = get_logger()
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.current = None
        self.show_window1()

    def _configure_styles(self):
        """Configure a cleaner, modern visual style with colored action buttons."""
        style = ttk.Style(self)
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))

    def toggle_theme_mode(self):
        current = self.state_data.get("theme_name", "Dark")
        order = ["Dark", "Light", "Cybersecurity Neon"]
        self.state_data["theme_name"] = order[(order.index(current) + 1) % len(order)]

    def _swap(self, frame):
        """Replaces the currently displayed GUI frame/window"""
        if self.current:
            self.current.destroy()
        self.current = frame
        self.current.pack(fill="both", expand=True)

    def show_window1(self):
        """Opens Entry Mode selection screen-> CNF/VNF """
        self._swap(Window1Entry(self.container, self.state_data, self.show_window2))

    def show_window2(self):
        """Opens Project Selection screen"""
        self._swap(Window2ProjectSelection(self.container, self.state_data, self.show_window1, self.show_window3))

    def show_window3(self):
        """Opens Scanner Selection screen."""
        self._swap(Window3ScannerSelection(self.container, self.state_data, self.show_window2, self.show_window4))

    def start_again(self):
        """Reset workflow selections and return to the first window."""
        self.state_data["entry_mode"] = "VNF"
        self.state_data["selected_project"] = "Select Project"
        self.state_data["selected_scanner"] = "Select Scanner"
        self.state_data["last_output_file"] = ""
        metrics = self.state_data.get("live_metrics")
        if metrics:
            metrics.reset()
        self.show_window1()

    def show_window4(self):
        """Opens Main Dashboard containing workflow tabs"""
        frame = Window4Main(self.container, self.state_data, self.logger, self.start_again)
        self._swap(frame)
        frame.attach_log_handler()


if __name__ == "__main__":
    App().mainloop()
