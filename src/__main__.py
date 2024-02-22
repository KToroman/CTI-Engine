from ast import main
from multiprocessing import Event, Process, Queue, Manager
from time import sleep
import click

from src.app.App import App
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
    app: App = App(model_queue=model_queue,status_queue=status_queue, shutdown_event=shutdown_event, 
                   active_mode_event=active_mode_event,passive_mode_event=passive_mode_event, load_event=load_event, 
                   load_path_queue=load_path_queue, active_mode_queue=active_mode_queue, error_queue=error_queue, 
                   visualize_event=visualize_event, start_with_gui=False)
    app.load_path_queue.put([path])
    app.load_event.set()
    app.active_mode_queue.put([source_file_name])
    app.active_mode_event.set()
    #TODO wait or lock or something between load and active mode
    app.run()



def run_app():
    

    app.run(main_window)

mycommands.add_command(start_active_measurement_command, "actv")


if __name__ == "__main__":
    # Events for GUI
    shutdown_event = Event()
    active_mode_event = Event()
    passive_mode_event = Event()
    passive_mode_event.set()
    load_event = Event()    
    # Queues for GUI messages
    manager = Manager()
    load_path_queue = manager.Queue(1)
    active_mode_queue= manager.Queue(1)
    error_queue = manager.Queue(5)
    visualize_event = Event()
    status_queue = manager.Queue()
    model_queue = manager.Queue()
    app: App = App(model_queue=model_queue,status_queue=status_queue, 
                   shutdown_event=shutdown_event, active_mode_event=active_mode_event, 
                   passive_mode_event=passive_mode_event, load_event=load_event, 
                   load_path_queue=load_path_queue, active_mode_queue=active_mode_queue, error_queue=error_queue, 
                   visualize_event=visualize_event, start_with_gui=True)
    main_window: MainWindow = prepare_gui(app=app, visualize_event=visualize_event, status_queue=status_queue, 
                                         model_queue=model_queue, error_queue=error_queue)
    Process(target=main_window.execute).start()
    print("process_started")
    mycommands()
