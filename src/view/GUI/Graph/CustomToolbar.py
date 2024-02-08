from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


class CustomToolbar(NavigationToolbar):
    """CustomToolbar for the GraphWidget and BarChart"""
    toolitems = [t for t in NavigationToolbar.toolitems if t[0] in ("Pan", "Zoom", "Save")]