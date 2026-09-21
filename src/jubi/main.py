import click
import jubi.client.commands as cmd
from pyfiglet import Figlet


class JubiGroup(click.Group):
    def format_help(self, ctx, formatter):
        click.echo(Figlet(font="banner").renderText("Jubi"))
        super().format_help(ctx, formatter)

@click.group(cls=JubiGroup)
def cli():
    """Welcome to Jubi. A Job Tracker CLI made by Hackerdroid"""
    pass
    

cli.add_command(cmd.init)
cli.add_command(cmd.add)
cli.add_command(cmd.list_jobs)
cli.add_command(cmd.delete)
cli.add_command(cmd.update)


