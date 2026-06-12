"""Make New Report workflow package."""

__all__ = ["MakeNewReportTab"]


def __getattr__(name):
    if name == "MakeNewReportTab":
        from tabs.make_new_report.make_new_report import MakeNewReportTab

        return MakeNewReportTab
    raise AttributeError(name)
