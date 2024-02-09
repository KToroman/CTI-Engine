import click

from src.app.App import App

@click.group(invoke_without_command=True)
@click.pass_context
def mycommands(ctx):
    if ctx.invoked_subcommand is None:
        run_app()
        pass 


@click.command()
@click.argument('path')
def load_from_directory_command(path: str):
    app = App(start_with_gui=False)
    app.load_from_directory(path)

@click.command()
@click.option('--source_file_name', prompt='Enter a filepath', help='filepath for active measurement')
@click.argument('source_file_name')
@click.argument('path')
def start_active_measurement_command(self, source_file_name: str, path: str):
    app = App(False)
    app.load_from_directory(path)
    app.start_active_measurement(source_file_name)
    app.run()


def run_app():
    app: App = App(True)
    app.run()

mycommands.add_command(load_from_directory_command, "load")
mycommands.add_command(start_active_measurement_command, "actv")


if __name__ == "__main__":
    mycommands()
