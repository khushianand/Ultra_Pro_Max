"""Summary chart and dashboard generation package."""

__all__ = [
    "disposition_summary",
    "expert_severity_summary",
    "severity_chart_summary",
]


def __getattr__(name):
    if name in __all__:
        from visuals.summary import summary_generator

        return getattr(summary_generator, name)
    raise AttributeError(name)
