from typing import List

from src.view.GUI.Graph.Plot import Plot
from src.view.GUI.Graph.Plot import Plot


class Displayable:

    def __init__(self, name: str, ram_plot: Plot, cpu_plot: Plot, runtime_plot: Plot, ram_peak: float, cpu_peak: float,
                 failed: bool) -> None:

        self.name: str = name
        self.ram_plot: Plot = ram_plot
        self.cpu_plot: Plot = cpu_plot
        self.runtime_plot: Plot = runtime_plot
        self.ram_peak: float = ram_peak
        self.cpu_peak: float = cpu_peak
        self.failed: bool = failed

