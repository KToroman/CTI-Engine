import threading
import time

from multiprocessing import Event, Process, Queue, Manager

import click
from PyQt5.QtCore import pyqtSignal

from colorama import Fore

from src.app.App import App
from src.app.SecondApp import SecondApp
from src.view.GUI.MainWindow import MainWindow
from src.view.GUI.prepare_gui import prepare_gui


@click.group(invoke_without_command=True)
@click.pass_context
def mycommands(ctx):
    if ctx.invoked_subcommand is None:
        run_app()
        pass


@click.command()
@click.option('--source_file_name', prompt='Enter a filepath', help='filepath for active measurement')
@click.argument('source_file_name')
@click.argument('path')
def start_active_measurement_command(self, source_file_name: str, path: str):
    app: App = App(model_queue=model_queue, status_queue=status_queue, shutdown_event=shutdown_event,
                   active_mode_event=active_mode_event, passive_mode_event=passive_mode_event, load_event=load_event,
                   load_path_queue=load_path_queue, active_mode_queue=active_mode_queue, error_queue=error_queue,
                   visualize_event=visualize_event, start_with_gui=False)
    app.load_path_queue.put([path])
    app.load_event.set()
    app.active_mode_queue.put([source_file_name])
    app.active_mode_event.set()
    # TODO wait or lock or something between load and active mode
    app.run()


def run_app():
    # Events for GUI
    shutdown_event = Event()
    active_mode_event = Event()
    passive_mode_event = Event()
    passive_mode_event.set()
    load_event = Event()
    # Queues for GUI messages
    manager = Manager()
    load_path_queue = manager.Queue(1)
    active_mode_queue = manager.Queue(1)
    error_queue = manager.Queue(5)
    visualize_event = Event()
    status_queue = manager.Queue()
    model_queue = manager.Queue()

    app: App = App(model_queue=model_queue, status_queue=status_queue,
                   shutdown_event=shutdown_event, active_mode_event=active_mode_event,
                   passive_mode_event=passive_mode_event, load_event=load_event,
                   load_path_queue=load_path_queue, active_mode_queue=active_mode_queue, error_queue=error_queue,
                   visualize_event=visualize_event, start_with_gui=True)
    main_window: MainWindow = prepare_gui(app=app, visualize_event=visualize_event, status_queue=status_queue,
                                          model_queue=model_queue, error_queue=error_queue)

    app.set_ui(main_window)


mycommands.add_command(start_active_measurement_command, "actv")

if __name__ == "__main__":
    # print("process_started")
    # mycommands()
    shutdown_event = Event()
    active_mode_event = Event()
    passive_mode_event = Event()
    passive_mode_event.set()
    load_event = Event()
    # Queues for GUI messages
    manager = Manager()
    load_path_queue = manager.Queue(1)
    active_mode_queue = manager.Queue(1)
    error_queue = manager.Queue(5)
    visualize_event = Event()
    cancel_event = Event()
    restart_event = Event()
    status_queue = manager.Queue()
    model_queue = manager.Queue()
    visualize_signal = pyqtSignal()

    app = SecondApp([], None, False, active_mode_event, passive_mode_event, load_event,
                    load_path_queue, active_mode_queue, visualize_signal, error_queue, cancel_event, restart_event)
    is_running = True
    try:
        print(Fore.CYAN + "[Main]   started, active threads: " + threading.active_count().__str__() + Fore.RESET)
        app.start()
        print(Fore.GREEN + "[main]   Ready" + Fore.RESET)
        print(Fore.CYAN + "[Main]   active threads: " + threading.active_count().__str__() + Fore.RESET)
        while is_running:
            time.sleep(10)
        app.stop()
    except KeyboardInterrupt as a:
        is_running = False
        print(Fore.GREEN + "[main]   stop sig sent" + Fore.RESET)
        app.stop()
        print(Fore.CYAN + "[Main]   stopped, active threads:" + threading.active_count().__str__() + Fore.RESET)
