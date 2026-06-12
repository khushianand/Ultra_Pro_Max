"""Add VAMS Data workflow package."""

__all__ = ["AddVamsDataTab"]


def __getattr__(name):
    if name == "AddVamsDataTab":
        from tabs.add_vams_data.add_vams_data import AddVamsDataTab

        return AddVamsDataTab
    raise AttributeError(name)
