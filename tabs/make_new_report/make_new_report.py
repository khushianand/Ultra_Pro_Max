"""Tab 1: Create a new report from a raw file (no master comparison)."""

import customtkinter as ctk

from tabs.make_new_report.logic import aggregate_unique
from tabs.make_new_report.excel_writer import write_output
from tabs.make_new_report.excel_writer.formatting import apply_table_formatting
from tabs.make_new_report.excel_writer import build_3uk_qualys_total_sheet_df, build_3uk_qualys_unique_sheet_df
from tabs.make_new_report.parser import parse_scan_file
from utils.file_handler import list_excel_sheets, validate_file
from utils.memory import memory_session, release_large_objects
from gui.qt_dialogs import DialogService


class MakeNewReportTab(ctk.CTkFrame):
    def __init__(self, master, app_state, logger):
        super().__init__(master, fg_color="transparent")
        self.state = app_state
        self.logger = logger
        self.raw_file = ctk.StringVar()
        self.raw_sheet = ctk.StringVar()
        self.output_file = ctk.StringVar()
        self.dialogs = DialogService()
        self._build_ui()
        self._bind_validation()

    def _field(self, row, label, var, browse_cmd=None, combo_values=None):
        card = ctk.CTkFrame(self, corner_radius=12)
        card.grid(row=row, column=0, sticky="ew", padx=10, pady=8)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=label).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))
        if combo_values is None:
            ctk.CTkEntry(card, textvariable=var).grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        else:
            self.raw_sheet_combo = ctk.CTkComboBox(card, values=combo_values, variable=var)
            self.raw_sheet_combo.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 8))
        if browse_cmd:
            ctk.CTkButton(card, text="Browse", command=browse_cmd, width=110).grid(row=1, column=1, padx=12)

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        backend_text = f"Dialog backend: {self.dialogs.backend_name} (PySide/PyQt when available)"
        ctk.CTkLabel(self, text=backend_text, text_color="#60a5fa").grid(row=0, column=0, sticky="w", padx=12, pady=(4, 0))
        self._field(1, "📊 Raw File", self.raw_file, self._browse_raw)
        self._field(2, "🧾 Raw Sheet", self.raw_sheet, combo_values=["Select sheet"])
        self._field(3, "📄 Output File", self.output_file, self._browse_output)
        self.run_btn = ctk.CTkButton(self, text="▶ Run Assessment", command=self.run)
        self.run_btn.grid(row=4, column=0, sticky="e", padx=12, pady=10)
        self.run_btn.configure(state="disabled")

    def _bind_validation(self):
        for var in (self.raw_file, self.raw_sheet, self.output_file):
            var.trace_add("write", lambda *_: self._update_run_state())

    def _update_run_state(self):
        ok = all(v.get().strip() for v in (self.raw_file, self.raw_sheet, self.output_file))
        self.run_btn.configure(state="normal" if ok else "disabled")

    def _browse_raw(self):
        path = self.dialogs.open_excel_file()
        if not path: return
        self.raw_file.set(path)
        sheets = list_excel_sheets(path)
        self.raw_sheet_combo.configure(values=sheets or ["Sheet1"])
        if sheets: self.raw_sheet.set(sheets[0])

    def _browse_output(self):
        path = self.dialogs.save_excel_file()
        if path: self.output_file.set(path)

    def _validate_inputs(self):
        validate_file(self.raw_file.get())
        if not self.raw_sheet.get(): raise ValueError("Please select a raw sheet")
        if not self.output_file.get(): raise ValueError("Please select output file")

    def run(self):
        hooks = self.state.get("ui_hooks", {})
        try:
            hooks.get("set_run_state", lambda *_: None)("Running")
            self.run_btn.configure(state="disabled")
            hooks.get("set_stage", lambda *_: None)("Validate Inputs", 1)
            with memory_session(self.logger, "TAB1 Make New Report"):
                self._validate_inputs()
                hooks.get("set_stage", lambda *_: None)("Parse", 2)
                if self.state["selected_project"].strip().casefold() == "3uk" and self.state["selected_scanner"].strip().casefold() == "qualys":
                    total_df = build_3uk_qualys_total_sheet_df(self.raw_file.get(), self.raw_sheet.get())
                    unique_df = build_3uk_qualys_unique_sheet_df(total_df)
                    summary_df = total_df
                else:
                    raw_df = parse_scan_file(self.raw_file.get(), self.raw_sheet.get(), self.state["selected_scanner"], self.state["selected_project"]).df
                    unique_df = aggregate_unique(raw_df)
                    hooks.get("update_metrics", lambda **_: None)(total_vulns=len(raw_df), unique_vulns=len(unique_df))
                    summary_df = raw_df
                hooks.get("set_stage", lambda *_: None)("Write", 5)
                output = write_output(self.output_file.get(), summary_df, summary_df.iloc[0:0], unique_df, self.state["selected_project"], self.state["selected_scanner"], include_old_sheet=False, new_sheet_name="Total Vulnerabilities", include_dashboard_sheet=True)
                from openpyxl import load_workbook
                wb = load_workbook(output)
                for ws in wb.worksheets:
                    apply_table_formatting(ws, include_borders=ws.title in {"Total Vulnerabilities","Unique Vulnerabilities","Total Data","Unique Data"})
                wb.save(output); wb.close()
            self.state["last_output_file"] = output
            self.dialogs.show_info("Success", f"Report generated:\n{output}")
            hooks.get("set_run_state", lambda *_: None)("Success")
        except Exception as exc:
            self.logger.exception("Make New Report failed")
            self.dialogs.show_error("Error", str(exc))
            hooks.get("set_run_state", lambda *_: None)("Failed")
        finally:
            release_large_objects(locals(), ["raw_df", "total_df", "unique_df", "summary_df", "wb", "output"])
            self._update_run_state()


    def reset(self):
        self.raw_file.set("")
        self.raw_sheet.set("")
        self.output_file.set("")
        if hasattr(self, "raw_sheet_combo"):
            self.raw_sheet_combo.configure(values=["Select sheet"])
        self._update_run_state()
