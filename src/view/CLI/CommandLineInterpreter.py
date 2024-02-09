import click
from src.view.AppRequestsInterface import AppRequestsInterface

class CommandLineInterpreter:
    def __init__(self, app_request_interface):
        self.app_request_interface : AppRequestsInterface = app_request_interface

    @click.command()
    def quit_application(self):
        """quits the application via command line"""
        result = self.app_request_interface.quit_application()
        if result:
            click.echo("Application quit")
        else:
            click.echo("Application quit failed")

    @click.command()
    @click.option('--source_file_name', prompt='Enter a filepath', help='filepath for active measurement')
    def start_active_measurement(self, source_file_name):
        """Starts an active measurement with given filename via command line"""
        self.app_request_interface.start_active_measurement(source_file_name)
        click.echo(f'Active measurement started for: {source_file_name}')

    @click.command()
    def quit_measurement(self):
        """Beendet jegliche Messung, passiv oder aktiv."""
        result = self.app_request_interface.quit_measurement()
        click.echo(f'Messung beendet: {result}')

    @click.command()
    @click.argument('path')
    def load_from_directory(self, path):
        """Lädt Dateien aus dem angegebenen Verzeichnis als neues Projekt in das Modell."""
        self.app_request_interface.load_from_directory(path)
        click.echo(f'Dateien geladen von Verzeichnis: {path}')

    @click.command()
    def pause_active_measurement(self):
        """Pausiert die aktive Messung."""
        self.app_request_interface.pause_active_measurement()
        click.echo('Aktive Messung pausiert.')

    @click.command()
    def resume_active_measurement(self):
        """Setzt eine zuvor pausierte aktive Messung fort."""
        self.app_request_interface.resume_active_measurement()
        click.echo('Aktive Messung fortgesetzt.')

    def visualize():
        pass
