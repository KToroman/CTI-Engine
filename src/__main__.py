import multiprocessing
import time
from multiprocessing import Queue, Process
import sys
from threading import Event, Thread
import click
from PyQt5.QtCore import pyqtSignal

from src.app.App import App
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


def initialize_app(shutdown_event_param: Event) -> App:
    app = App(shutdown_event=shutdown_event_param, passive_mode_event=passive_mode_event,
              load_event=load_event, load_path_queue=load_path_queue, source_file_name_queue=source_file_name_queue,
              visualize_signal=visualize_signal, error_queue=error_queue, error_signal=error_signal,
              status_queue=status_queue,
              model_queue=model_queue, cancel_event=cancel_event, restart_event=restart_event,
              status_signal=status_signal)
    return app


def initialize_gui(shutdown_event_param: Event) -> UIInterface:
    gui: UIInterface = prepare_gui(shutdown_event=shutdown_event_param, status_queue=status_queue,
                                   model_queue=model_queue,
                                   error_queue=error_queue, load_path_queue=load_path_queue, cancel_event=cancel_event,
                                   active_mode_queue=source_file_name_queue, restart_event=restart_event)

    return gui


if __name__ == "__main__":
    shutdown_event = multiprocessing.Event()
    active_mode_event = multiprocessing.Event()
    passive_mode_event = multiprocessing.Event()
    passive_mode_event.set()
    load_event = multiprocessing.Event()
    # Queues for GUI messages
    load_path_queue = Queue(1)
    source_file_name_queue = Queue(1)
    error_queue = Queue(5)
    status_queue = Queue()
    model_queue = Queue()
    cancel_event = Event()
    restart_event = Event()
    gui = initialize_gui(shutdown_event)
    visualize_signal = gui.visualize_signal
    status_signal = gui.status_signal
    error_signal = gui.error_signal
    app: App = initialize_app(shutdown_event)
    app.prepare_threads()
    passive_mode_event.set()
    app_process = Process(target=app.start)
    try:
        app_process.start()
        gui.execute()
        app_process.join()
    except KeyboardInterrupt:
        shutdown_event.set()

        app_process.join()
