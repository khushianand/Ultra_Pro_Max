"""Tab 2: Generate tracking by comparing required master and raw inputs."""

import customtkinter as ctk

from tabs.generate_tracking.logic import (
    aggregate_unique,
    build_comparison_debug_df,
    build_template_sheet_df,
    classify_new_old,
    comparison_non_empty_counts,
    comparison_values_preview,
    resolve_comparison_columns,
)
from tabs.generate_tracking.comparison_logic import _comparison_key
from tabs.generate_tracking.excel_writer import write_output
from tabs.generate_tracking.excel_writer.formatting import apply_table_formatting
from tabs.generate_tracking.parser import parse_scan_file
from tabs.generate_tracking.excel_writer import (
    build_3uk_qualys_template_sheet_df,
    build_3uk_qualys_total_sheet_df,
    build_3uk_qualys_unique_sheet_df,
    read_sheet_as_df,
)
from utils.file_handler import list_excel_sheets, validate_file
from gui.qt_dialogs import DialogService


class GenerateTrackingTab(ctk.CTkFrame):
    """Core workflow: parse -> compare -> aggregate -> write output."""
    def __init__(self, master, app_state, logger):
        super().__init__(master)
        self.state = app_state
        self.logger = logger

        self.master_file = ctk.StringVar()
        self.master_sheet = ctk.StringVar()
        self.raw_file = ctk.StringVar()
        self.raw_sheet = ctk.StringVar()
        self.output_file = ctk.StringVar()
        self._entry_widgets = []
        self.dialogs = DialogService()

        self._build_ui()
        self._bind_validation()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.master_combo = ctk.CTkComboBox(self, values=[""], variable=self.master_sheet)
        self.raw_combo = ctk.CTkComboBox(self, values=[""], variable=self.raw_sheet)
        backend_text = f"Dialog backend: {self.dialogs.backend_name} (PySide/PyQt when available)"
        ctk.CTkLabel(self, text=backend_text, text_color="#60a5fa").grid(row=0, column=0, sticky="w", padx=12, pady=(4, 0))
        self._file_row(1, "📂 Master File (required)", self.master_file, self._browse_master)
        self.master_combo.grid(row=2, column=0, sticky="w", padx=12, pady=(0,8))
        self._file_row(3, "📊 Raw File", self.raw_file, self._browse_raw)
        self.raw_combo.grid(row=4, column=0, sticky="w", padx=12, pady=(0,8))
        self._file_row(5, "📄 Output File", self.output_file, self._browse_output)
        self.run_btn = ctk.CTkButton(self, text="▶ Run Assessment", command=self.run)
        self.run_btn.grid(row=6, column=0, sticky="e", padx=12, pady=10)
        self.form_status = ctk.CTkLabel(self, text="Fill required fields to enable Run", text_color="#f59e0b")
        self.form_status.grid(row=6, column=0, sticky="w", padx=12, pady=10)
        self.run_btn.configure(state="disabled")

    def _file_row(self, row, label, var, browse_command, save=False):
        card = ctk.CTkFrame(self, corner_radius=12)
        card.grid(row=row, column=0, sticky="ew", padx=10, pady=8)
        card.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(card, text=label).grid(row=0, column=0, sticky="w", padx=12, pady=(8,4))
        entry = ctk.CTkEntry(card, textvariable=var)
        entry.grid(row=1, column=0, sticky="ew", padx=12, pady=(0,8))
        self._entry_widgets.append(entry)
        ctk.CTkButton(card, text="Browse", command=browse_command, width=110).grid(row=1, column=1, padx=12)

    def _bind_validation(self):
        for var in (self.master_file, self.master_sheet, self.raw_file, self.raw_sheet, self.output_file):
            var.trace_add("write", lambda *_: self._validate_form())
        for entry in self._entry_widgets:
            entry.bind("<KeyRelease>", lambda _e: self._validate_form())
        self.master_combo.bind("<<ComboboxSelected>>", lambda _e: self._validate_form())
        self.raw_combo.bind("<<ComboboxSelected>>", lambda _e: self._validate_form())
        self._validate_form()

    def _validate_form(self):
        required_ok = bool(
            self.master_file.get().strip()
            and self.master_sheet.get().strip()
            and self.raw_file.get().strip()
            and self.raw_sheet.get().strip()
            and self.output_file.get().strip()
        )
        self.run_btn.configure(state="normal" if required_ok else "disabled")
        self.form_status.configure(
            text="Ready to run" if required_ok else "Select master, raw, sheets, and output to enable Run",
            text_color="#22c55e" if required_ok else "#f59e0b",
        )
        return required_ok

    def _load_sheets(self, path, combo, var):
        sheets = list_excel_sheets(path)
        combo.configure(values=sheets or [""])
        if sheets:
            var.set(sheets[0])

    def _browse_master(self):
        path = self.dialogs.open_excel_file()
        if path:
            self.master_file.set(path)
            self._load_sheets(path, self.master_combo, self.master_sheet)

    def _browse_raw(self):
        path = self.dialogs.open_excel_file()
        if path:
            self.raw_file.set(path)
            self._load_sheets(path, self.raw_combo, self.raw_sheet)

    def _browse_output(self):
        path = self.dialogs.save_excel_file()
        if path:
            self.output_file.set(path)

    def _validate_inputs(self):
        if not self._validate_form():
            raise ValueError("Please select master file/sheet, raw file/sheet, and output file")
        validate_file(self.master_file.get())
        if not self.master_sheet.get():
            raise ValueError("Please select master sheet")
        validate_file(self.raw_file.get())
        if not self.raw_sheet.get():
            raise ValueError("Please select raw sheet")
        if not self.output_file.get():
            raise ValueError("Please select output file")

    def _parse_selected_standard_sheet(self, path: str, sheet: str):
        """Parse one selected standard scanner sheet without dropping Raw rows."""
        return parse_scan_file(
            path,
            sheet,
            self.state["selected_scanner"],
            self.state["selected_project"],
            require_rows_after_filter=False,
            apply_severity_filter=False,
        ).df

    def _is_3uk_qualys_workflow(self) -> bool:
        return (
            self.state["selected_project"].strip().casefold() == "3uk"
            and self.state["selected_scanner"].strip().casefold() == "qualys"
        )

    def _normalized_sheet_name(self, sheet_name: str) -> str:
        return " ".join(str(sheet_name).strip().casefold().replace("_", " ").split())

    def _is_tracker_vulnerability_sheet(self, sheet_name: str) -> bool:
        return self._normalized_sheet_name(sheet_name) in {
            "total vulnerabilities",
            "new vulnerabilities",
            "old vulnerabilities",
            "unique vulnerabilities",
            "total data",
            "unique data",
        }

    def _is_qualys_total_master_sheet(self, sheet_name: str) -> bool:
        return self._normalized_sheet_name(sheet_name) in {
            "total vulnerabilities",
            "total vulnerability",
            "total vulnerability sheet",
            "total data",
        }

    def _selected_input_paths(self) -> dict[str, str]:
        """Capture the explicitly selected files and sheets for this run only."""
        return {
            "master_file": self.master_file.get().strip(),
            "master_sheet": self.master_sheet.get().strip(),
            "raw_file": self.raw_file.get().strip(),
            "raw_sheet": self.raw_sheet.get().strip(),
            "output_file": self.output_file.get().strip(),
        }

    def _load_selected_raw_sheet(self, selected: dict[str, str]):
        """Load only the Raw file sheet selected in the Raw Sheet dropdown."""
        if self._is_3uk_qualys_workflow():
            return build_3uk_qualys_total_sheet_df(
                selected["raw_file"],
                selected["raw_sheet"],
            )

        return self._parse_selected_standard_sheet(
            selected["raw_file"],
            selected["raw_sheet"],
        )

    def _load_selected_master_sheet(self, selected: dict[str, str]):
        """Load only the Master file sheet selected in the Master Sheet dropdown."""
        master_sheet = selected["master_sheet"]

        if self._is_3uk_qualys_workflow() and self._is_qualys_total_master_sheet(master_sheet):
            return build_3uk_qualys_total_sheet_df(
                selected["master_file"],
                master_sheet,
            )

        if self._is_tracker_vulnerability_sheet(master_sheet):
            return read_sheet_as_df(
                selected["master_file"],
                master_sheet,
            )

        return self._parse_selected_standard_sheet(
            selected["master_file"],
            master_sheet,
        )


    def _print_comparison_column_health(self, label: str, df, columns, counts):
        row_count = len(df)
        for field_name, column in columns.items():
            if column is None:
                print(f"{label} COMPARISON COLUMN WARNING: {field_name} did not resolve to a column")
                continue

            non_empty_count = counts[field_name]
            if non_empty_count == 0:
                print(f"{label} COMPARISON COLUMN WARNING: {field_name} column {column!r} is entirely blank")
            elif row_count and non_empty_count / row_count < 0.2:
                print(
                    f"{label} COMPARISON COLUMN WARNING: {field_name} column {column!r} is mostly blank "
                    f"({non_empty_count}/{row_count} non-empty)"
                )

    def _resolved_comparison_sample(self, df, columns):
        resolved = [
            columns[field_name]
            for field_name in ("Name", "Host / Image", "Port", "CVE")
            if columns[field_name] is not None
        ]
        return df[resolved].head(20) if resolved else df.iloc[0:0]



    def run(self):

        try:
            hooks = self.state.get("ui_hooks", {})
            hooks.get("set_run_state", lambda *_: None)("Running")
            hooks.get("set_stage", lambda *_: None)("Validate Inputs", 1)

            self.run_btn.configure(
                state="disabled"
            )

            self._validate_inputs()
            selected = self._selected_input_paths()

            # -------------------------------------------------
            # PARSE SELECTED RAW AND MASTER SHEETS ONLY
            # -------------------------------------------------

            hooks.get("set_stage", lambda *_: None)("Parse", 2)
            self.logger.info(
                "Generate Tracking comparison scope: raw sheet %r vs master sheet %r",
                selected["raw_sheet"],
                selected["master_sheet"],
            )

            raw_df = self._load_selected_raw_sheet(selected)
            master_df = self._load_selected_master_sheet(selected)
            # -------------------------------------------------
            # CLASSIFICATION
            # -------------------------------------------------
            hooks.get("set_stage", lambda *_: None)("Compare", 3)

            raw_comparison_columns = resolve_comparison_columns(raw_df)
            master_comparison_columns = resolve_comparison_columns(master_df)
            raw_counts = comparison_non_empty_counts(raw_df, raw_comparison_columns)
            master_counts = comparison_non_empty_counts(master_df, master_comparison_columns)

            print("RAW COLUMNS")
            print(raw_df.columns.tolist())

            print("MASTER COLUMNS")
            print(master_df.columns.tolist())

            print("RAW COMPARISON COLUMNS")
            print(
                raw_comparison_columns["Name"],
                raw_comparison_columns["Host / Image"],
                raw_comparison_columns["Port"],
                raw_comparison_columns["CVE"],
            )

            print("MASTER COMPARISON COLUMNS")
            print(
                master_comparison_columns["Name"],
                master_comparison_columns["Host / Image"],
                master_comparison_columns["Port"],
                master_comparison_columns["CVE"],
            )

            print("RAW COMPARISON NON-EMPTY COUNTS")
            print(raw_counts["Name"])
            print(raw_counts["Host / Image"])
            print(raw_counts["Port"])
            print(raw_counts["CVE"])

            print("MASTER COMPARISON NON-EMPTY COUNTS")
            print(master_counts["Name"])
            print(master_counts["Host / Image"])
            print(master_counts["Port"])
            print(master_counts["CVE"])

            self._print_comparison_column_health("RAW", raw_df, raw_comparison_columns, raw_counts)
            self._print_comparison_column_health("MASTER", master_df, master_comparison_columns, master_counts)

            print("RAW RESOLVED COMPARISON SAMPLE")
            print(self._resolved_comparison_sample(raw_df, raw_comparison_columns))

            print("MASTER RESOLVED COMPARISON SAMPLE")
            print(self._resolved_comparison_sample(master_df, master_comparison_columns))

            print("RAW SAMPLE")
            print(raw_df.head())

            print("MASTER SAMPLE")
            print(master_df.head())

            print("RAW COMPARISON VALUES")
            print(comparison_values_preview(raw_df))

            print("MASTER COMPARISON VALUES")
            print(comparison_values_preview(master_df))

            print("RAW KEYS")
            print(_comparison_key(raw_df).head(20).tolist())

            print("MASTER KEYS")
            print(_comparison_key(master_df).head(20).tolist())

            comparison_debug_df = build_comparison_debug_df(raw_df, master_df)

            new_df, old_df = classify_new_old(
                raw_df,
                master_df,
            )
            if self._is_3uk_qualys_workflow():

                total_df = raw_df
                new_df = build_3uk_qualys_template_sheet_df(new_df)
                old_df = build_3uk_qualys_template_sheet_df(old_df)
                unique_df = build_3uk_qualys_unique_sheet_df(raw_df)

            else:

                total_df = build_template_sheet_df(raw_df)
                new_df = build_template_sheet_df(new_df)
                old_df = build_template_sheet_df(old_df)
                unique_df = aggregate_unique(raw_df)

            hooks.get("update_metrics", lambda **_: None)(
                total_vulns=len(raw_df),
                unique_vulns=len(unique_df),
            )


            # -------------------------------------------------
            # WRITE OUTPUT
            # -------------------------------------------------
            hooks.get("set_stage", lambda *_: None)("Write", 5)

            output = write_output(
                selected["output_file"],
                new_df,
                old_df,
                unique_df,
                self.state["selected_project"],
                self.state["selected_scanner"],
                total_df=total_df,
                comparison_debug_df=comparison_debug_df,
            )

            # -------------------------------------------------
            # APPLY PROFESSIONAL FORMATTING
            # -------------------------------------------------

            from openpyxl import load_workbook

            from tabs.generate_tracking.excel_writer.formatting import apply_table_formatting

            wb = load_workbook(output)

            bordered_sheets = {
                "Total Vulnerabilities",
                "Unique Vulnerabilities",
                "New Vulnerabilities",
                "Old Vulnerabilities",
                "Total Data",
                "Unique Data",
            }
            for ws in wb.worksheets:
                apply_table_formatting(
                    ws,
                    include_borders=ws.title in bordered_sheets,
                )

            wb.save(output)

            wb.close()

            # -------------------------------------------------
            # SUCCESS LOGGING
            # -------------------------------------------------

            self.logger.info(
                "Tracking sheet created: %s",
                output,
            )

            self.state["last_output_file"] = output
            self.dialogs.show_info(
                "Success",
                f"Tracking sheet created:\n{output}",
            )
            hooks.get("set_run_state", lambda *_: None)("Success")

        except Exception as exc:

            self.logger.exception(
                "Update Tracking Sheet failed"
            )

            self.dialogs.show_error(
                "Error",
                str(exc),
            )
            hooks.get("set_run_state", lambda *_: None)("Failed")

        finally:

            self._validate_form()



    def reset(self):
        for var in (self.master_file, self.master_sheet, self.raw_file, self.raw_sheet, self.output_file):
            var.set("")
        self.master_combo.configure(values=[""])
        self.raw_combo.configure(values=[""])
        self._validate_form()
