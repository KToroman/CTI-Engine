from typing import Any

from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar  # type: ignore[attr-defined]


class ToolbarCPU(NavigationToolbar):
    """CustomToolbar for the GraphWidget and BarChart."""
    toolitems: Any = (t for t in NavigationToolbar.toolitems if t[0] in ("Pan", "Zoom", "Save"))  # type: ignore[has-type]
