from src.view.GUI.Graph import Plot


class Displayable:

    name: str
    ram_plot: Plot
    cpu_plot: Plot
    runtime_plot: Plot
    ram_peak: float
    cpu_peak: float

    def __init__(self, name, ram_plot, cpu_plot, runtime_plot, ram_peak, cpu_peak):

        self.name = name
        self.ram_plot = ram_plot
        self.cpu_plot = cpu_plot
        self.runtime_plot = runtime_plot
        self.ram_peak = ram_peak
        self.cpu_peak = cpu_peak