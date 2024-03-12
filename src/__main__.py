import multiprocessing
import time
from multiprocessing import Queue, Process
import sys
import click
from PyQt5.QtCore import pyqtSignal

from src.app.App import App
from src.model.Model import Model
from src.view.UIInterface import UIInterface
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.prepare_gui import prepare_gui


@click.command()
@click.option('--source_file_name', prompt='Enter a filepath', help='filepath for active measurement')
@click.argument('source_file_name')
@click.argument('path')
def start_active_measurement_command(self, source_file_name: str, path: str):
    initialize_app()
    active_mode_event.set()


def run_without_gui():
    initialize_app()


@click.group(invoke_without_command=True)
@click.pass_context
def mycommands(ctx):
    if ctx.invoked_subcommand is None:
        run_without_gui()
        pass


mycommands.add_command(start_active_measurement_command, "actv")


def initialize_app() -> App:
    app = App(shutdown_event=shutdown_event, passive_mode_event=passive_mode_event,
              load_event=load_event, load_path_queue=load_path_queue, source_file_name_queue=source_file_name_queue,
              visualize_signal=visualize_signal, error_queue=error_queue, error_signal=error_signal,
              status_queue=status_queue,
              project_queue=project_queue, cancel_event=cancel_event, restart_event=restart_event,
              status_signal=status_signal, model=model)
    return app


def initialize_gui() -> UIInterface:
    gui: UIInterface = prepare_gui(shutdown_event=shutdown_event, status_queue=status_queue,
                                   project_queue=project_queue,
                                   error_queue=error_queue, load_path_queue=load_path_queue, cancel_event=cancel_event,
                                   active_mode_queue=source_file_name_queue, restart_event=restart_event, model=model)

    return gui


if __name__ == "__main__":
    model: Model = Model()
    shutdown_event = multiprocessing.Event()
    active_mode_event = multiprocessing.Event()
    passive_mode_event = multiprocessing.Event()
    passive_mode_event.set()
    load_event = multiprocessing.Event()
    # Queues for GUI messages
    load_path_queue = Queue(3)
    source_file_name_queue = Queue(1)

    error_queue: Queue = Queue(4)

    status_queue = Queue()
    project_queue = Queue()
    cancel_event = multiprocessing.Event()
    restart_event = multiprocessing.Event()
    gui = initialize_gui()
    visualize_signal = gui.visualize_signal
    status_signal = gui.status_signal
    error_signal = gui.error_signal
    app: App = initialize_app()
    app.prepare_threads()
    passive_mode_event.set()
    try:
        app.start()
        gui.execute()
        app.stop()
    except KeyboardInterrupt:
        shutdown_event.set()
        app.stop()
