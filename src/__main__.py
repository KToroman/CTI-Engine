import multiprocessing
from multiprocessing import Queue

import click
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from src.app.App import App
from src.model.Model import Model
from src.model.core.StatusSettings import StatusSettings
from src.view.UIInterface import UIInterface
from src.view.CommandLineUI import CommandLineUI
from src.view.GUI.prepare_gui import prepare_gui


@click.command()
@click.option("--gui/--nogui", default=True, help="Use --gui or --nogui to run the app with or without gui. Default: gui")
@click.option("--load-file", "-f", default="", help="provide a file Path to immediately load on app startup.")
@click.option("--active", "-a", default="", help="provide a header from a loaded project to run active analysis on. Only used with --load-file.")
def run(gui: bool, load_file: str, active: str) -> None:
    run_with_gui = gui

    # init gui
    ui: UIInterface = initialize_gui(run_with_gui)
    visualize_signal: pyqtSignal = ui.visualize_signal  # type: ignore[call-overload]
    status_signal: pyqtSignal = ui.status_signal  # type: ignore[call-overload]
    error_signal: pyqtSignal = ui.error_signal  # type: ignore[call-overload]

    # init app
    app: App = App(shutdown_event=shutdown_event, passive_mode_event=passive_mode_event,
                   load_event=load_event, load_path_queue=load_path_queue,
                   source_file_name_queue=source_file_name_queue,
                   visualize_signal=visualize_signal, error_queue=error_queue, error_signal=error_signal,
                   status_queue=status_queue,
                   project_queue=project_queue, cancel_event=cancel_event, restart_event=restart_event,
                   status_signal=status_signal, model=model)
    app.prepare_threads()

    # perform immediate actions
    if load_file != "":
        load_path_queue.put(load_file)
        if active != "":
            source_file_name_queue.put(active)
    else:
        passive_mode_event.set()

    # exec
    try:
        app.start()
        ui.execute()
        app.stop()
    except KeyboardInterrupt:
        print("\033[91mKeyboard Interrupt, shutting down...\033[0m")
        shutdown_event.set()
        app.stop()


def initialize_gui(run_with_gui: bool) -> UIInterface:
    if run_with_gui:
        gui: UIInterface = prepare_gui(shutdown_event=shutdown_event, status_queue=status_queue,
                                       project_queue=project_queue, error_queue=error_queue,
                                       load_path_queue=load_path_queue, cancel_event=cancel_event,
                                       active_mode_queue=source_file_name_queue, restart_event=restart_event,
                                       model=model)
    else:
        qapp = QApplication([])
        gui = CommandLineUI(qapp, error_queue, shutdown_event)  # type: ignore[abstract]

    return gui


if __name__ == "__main__":

    # init Model
    model: Model = Model()

    # Events for backend coordination
    shutdown_event = multiprocessing.Event()
    active_mode_event = multiprocessing.Event()
    passive_mode_event = multiprocessing.Event()
    passive_mode_event.set()
    load_event = multiprocessing.Event()

    # Queues for GUI messages
    load_path_queue: "Queue[str]" = Queue(3)
    source_file_name_queue: "Queue[str]" = Queue(10)
    error_queue: "Queue[BaseException]" = Queue(10)
    status_queue: "Queue[StatusSettings]" = Queue()
    project_queue: "Queue[str]" = Queue()
    cancel_event = multiprocessing.Event()
    restart_event = multiprocessing.Event()

    run()
