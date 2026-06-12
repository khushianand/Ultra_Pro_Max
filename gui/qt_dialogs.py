"""Optional PySide/PyQt dialog bridge for the Tk-based workflow UI.

The main application is still hosted in CustomTkinter, but this module lets tabs
use native Qt file and message dialogs when a supported PySide/PyQt binding is
installed.  It falls back to tkinter dialogs automatically when Qt bindings are
not available.
"""

from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass
from tkinter import filedialog, messagebox

_QT_BINDINGS = (
    ("PySide6", "PySide6.QtWidgets"),
    ("PyQt6", "PyQt6.QtWidgets"),
    ("PySide2", "PySide2.QtWidgets"),
    ("PyQt5", "PyQt5.QtWidgets"),
)


@dataclass(frozen=True)
class QtBinding:
    name: str
    widgets_module: object


def _available_qt_binding() -> QtBinding | None:
    for binding_name, widgets_module_name in _QT_BINDINGS:
        if importlib.util.find_spec(binding_name) is None:
            continue
        widgets_module = importlib.import_module(widgets_module_name)
        return QtBinding(binding_name, widgets_module)
    return None


class DialogService:
    """Use PySide/PyQt dialogs when available, otherwise tkinter dialogs."""

    def __init__(self):
        self.binding = _available_qt_binding()
        self._app = None

    @property
    def backend_name(self) -> str:
        return self.binding.name if self.binding is not None else "tkinter"

    def _qt_app(self):
        if self.binding is None:
            return None

        QApplication = self.binding.widgets_module.QApplication
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        self._app = app
        return app

    def open_excel_file(self, *, title: str = "Select Excel file", save_workbook_only: bool = False) -> str:
        filetypes = [("Excel", "*.xlsx")] if save_workbook_only else [("Excel", "*.xlsx *.xls *.xlsm")]
        qt_filter = "Excel Files (*.xlsx)" if save_workbook_only else "Excel Files (*.xlsx *.xls *.xlsm)"

        if self.binding is None:
            return filedialog.askopenfilename(filetypes=filetypes)

        self._qt_app()
        QFileDialog = self.binding.widgets_module.QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            None,
            title,
            "",
            qt_filter,
        )
        return path


    def save_file(
        self,
        *,
        title: str = "Save file",
        default_extension: str = "",
        filetypes: list[tuple[str, str]] | None = None,
        qt_filter: str = "All Files (*)",
        initialfile: str = "",
    ) -> str:
        if self.binding is None:
            return filedialog.asksaveasfilename(
                defaultextension=default_extension,
                filetypes=filetypes or [("All Files", "*.*")],
                initialfile=initialfile,
            )

        self._qt_app()
        QFileDialog = self.binding.widgets_module.QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            None,
            title,
            initialfile,
            qt_filter,
        )
        if path and default_extension and not path.lower().endswith(default_extension.lower()):
            path = f"{path}{default_extension}"
        return path

    def save_excel_file(self) -> str:
        if self.binding is None:
            return filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])

        self._qt_app()
        QFileDialog = self.binding.widgets_module.QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            None,
            "Save Excel workbook",
            "",
            "Excel Files (*.xlsx)",
        )
        if path and not path.lower().endswith(".xlsx"):
            path = f"{path}.xlsx"
        return path

    def show_info(self, title: str, message: str):
        if self.binding is None:
            messagebox.showinfo(title, message)
            return

        self._qt_app()
        QMessageBox = self.binding.widgets_module.QMessageBox
        QMessageBox.information(None, title, message)

    def show_warning(self, title: str, message: str):
        if self.binding is None:
            messagebox.showwarning(title, message)
            return

        self._qt_app()
        QMessageBox = self.binding.widgets_module.QMessageBox
        QMessageBox.warning(None, title, message)

    def show_error(self, title: str, message: str):
        if self.binding is None:
            messagebox.showerror(title, message)
            return

        self._qt_app()
        QMessageBox = self.binding.widgets_module.QMessageBox
        QMessageBox.critical(None, title, message)
