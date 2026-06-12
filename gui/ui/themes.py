"""Theme management for the modern SaaS/cybersecurity dashboard UI."""

from __future__ import annotations

# The palette dictionaries intentionally expose every approved hex code for the
# light and dark themes.  UI components can use semantic keys instead of hard-
# coding colors, which keeps theme behavior consistent across the dashboard.
THEMES = {
    "Light": {
        # Primary backgrounds
        "bg": "#F7F9FC",
        "window_bg": "#F7F9FC",
        "panel": "#FFFFFF",
        "center": "#F3F6FB",
        "card_alt": "#F3F6FB",
        "secondary_panel": "#F3F6FB",
        "sidebar_bg": "#FAFBFD",
        "hover_bg": "#EEF4FF",
        "nav_hover": "#EEF4FF",
        "table_alt": "#F3F6FB",

        # Borders and dividers
        "border": "#E4EAF3",
        "main_border": "#E4EAF3",
        "card_border": "#DCE4EF",
        "divider": "#E8EDF5",
        "input_border": "#D7E0EC",

        # Text
        "text": "#1F2937",
        "primary_text": "#1F2937",
        "secondary_text": "#4B5563",
        "muted": "#6B7280",
        "muted_text": "#6B7280",
        "placeholder": "#94A3B8",
        "disabled": "#94A3B8",

        # Blue theme colors
        "primary": "#2563EB",
        "primary_blue": "#2563EB",
        "secondary": "#3B82F6",
        "button_blue": "#3B82F6",
        "light_blue": "#60A5FA",
        "sidebar_active": "#EAF2FF",
        "blue_glow": "#DBEAFE",
        "version_bg": "#DBEAFE",

        # Green colors
        "green": "#22C55E",
        "success": "#22C55E",
        "success_light": "#DCFCE7",
        "status_ready": "#10B981",
        "success_badge": "#16A34A",

        # Purple colors
        "purple": "#7C3AED",
        "primary_purple": "#7C3AED",
        "purple_accent": "#8B5CF6",
        "purple_light": "#F3E8FF",
        "run_button": "#6D28D9",

        # Orange colors
        "orange": "#F59E0B",
        "orange_accent": "#F59E0B",
        "warning": "#FB923C",
        "warning_orange": "#FB923C",
        "orange_light": "#FEF3C7",

        # Red colors
        "red": "#EF4444",
        "error": "#EF4444",
        "danger": "#DC2626",
        "error_light": "#FEE2E2",

        # Inputs/logs
        "input_bg": "#FFFFFF",
        "log_bg": "#FFFFFF",
        "log_info": "#EFF6FF",
        "log_success": "#ECFDF5",
        "log_warning": "#FFF7ED",
        "log_error": "#FEF2F2",

        # Documentation-only shadow values for toolkit adapters that support CSS.
        "shadow": "0px 4px 20px rgba(37, 99, 235, 0.08)",
        "card_shadow": "0px 2px 10px rgba(15, 23, 42, 0.06)",
    },
    "Dark": {
        # Core dark slate-grey backgrounds
        "bg": "#353F4A",
        "main_bg": "#353F4A",
        "window_bg": "#2F3843",
        "secondary_bg": "#343D48",
        "panel": "#404A56",
        "center": "#444E5A",
        "card_alt": "#444E5A",
        "elevated_card": "#38414C",
        "sidebar_bg": "#38424D",
        "footer_bg": "#2A333E",
        "hover_bg": "#394451",
        "nav_hover": "#394451",
        "table_alt": "#394451",

        # Borders and surfaces
        "border": "#5B6673",
        "soft_border": "#46515D",
        "card_border": "#4A5562",
        "divider": "#56606B",
        "input_border": "#5C6672",

        # Text
        "text": "#F4F7FA",
        "primary_text": "#F4F7FA",
        "secondary_text": "#C8D0D8",
        "legacy_secondary_text": "#D1D7DE",
        "muted": "#98A3AF",
        "muted_text": "#98A3AF",
        "legacy_muted_text": "#AAB3BD",
        "disabled": "#8A949F",

        # Blue accents
        "primary": "#4A90FF",
        "primary_blue": "#4080D9",
        "secondary": "#9B6DFF",
        "bright_blue": "#4A90FF",
        "hover_blue": "#5B9DFF",
        "sidebar_active": "#2D5FAE",
        "blue_glow": "#7FB3FF",
        "version_bg": "#2F4F80",

        # Green accents
        "green": "#2EE67B",
        "success": "#22C55E",
        "bright_green": "#2EE67B",
        "success_glow": "#58F59A",
        "status_ready": "#22C55E",
        "success_badge": "#2EE67B",

        # Purple accents
        "purple": "#9B6DFF",
        "primary_purple": "#7C3AED",
        "purple_accent": "#8B5CF6",
        "purple_glow": "#B794F4",
        "run_button": "#9B6DFF",

        # Orange accents
        "orange": "#FFB020",
        "orange_accent": "#F59E0B",
        "bright_orange": "#FFB020",
        "warning": "#FFB020",
        "orange_glow": "#FFD166",

        # Red/error accents
        "red": "#EF4444",
        "error": "#EF4444",
        "danger": "#DC2626",

        # Inputs/logs
        "input_bg": "#343D48",
        "log_bg": "#303945",
        "log_hover": "#394451",
        "log_info": "#2F4F80",
        "log_success": "#255C41",
        "log_warning": "#6A4A1F",
        "log_error": "#6C2B2B",

        # Documentation-only shadow values for toolkit adapters that support CSS.
        "shadow": "0px 4px 20px rgba(74, 144, 255, 0.12)",
        "card_shadow": "0px 2px 10px rgba(15, 23, 42, 0.18)",
    },
    "Cybersecurity Neon": {
        "bg": "#0F172A",
        "panel": "#111827",
        "center": "#111827",
        "card_alt": "#1F2937",
        "sidebar_bg": "#0B1120",
        "hover_bg": "#164E63",
        "primary": "#22D3EE",
        "secondary": "#A78BFA",
        "text": "#E5E7EB",
        "secondary_text": "#CBD5E1",
        "muted": "#94A3B8",
        "disabled": "#64748B",
        "border": "#1F2937",
        "card_border": "#334155",
        "divider": "#334155",
        "input_bg": "#0F172A",
        "input_border": "#334155",
        "green": "#2EE67B",
        "success": "#22C55E",
        "purple": "#A78BFA",
        "orange": "#FFB020",
        "red": "#F87171",
        "sidebar_active": "#164E63",
        "nav_hover": "#1E293B",
        "log_bg": "#0B1020",
        "log_info": "#172554",
        "log_success": "#064E3B",
        "log_warning": "#78350F",
        "log_error": "#7F1D1D",
        "table_alt": "#111827",
        "version_bg": "#172554",
    },
}


def palette(name: str) -> dict:
    return THEMES.get(name, THEMES["Dark"])
