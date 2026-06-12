"""Generate Tracking workflow package."""

__all__ = ["GenerateTrackingTab"]


def __getattr__(name):
    if name == "GenerateTrackingTab":
        from tabs.generate_tracking.generate_tracking import GenerateTrackingTab

        return GenerateTrackingTab
    raise AttributeError(name)
