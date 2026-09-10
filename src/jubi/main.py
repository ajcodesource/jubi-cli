import click
import jubi.core.commands as cmd
from pyfiglet import Figlet
f = Figlet(font="banner")
print(f.renderText("Jubi"))

@click.group()
def cli():
    """Welcome to Jubi. A Job Tracker CLI for the Agentic Age!"""
    pass
    

cli.add_command(cmd.init)
cli.add_command(cmd.add)
cli.add_command(cmd.listall)
cli.add_command(cmd.delete)
cli.add_command(cmd.update)
cli.add_command(cmd.status)


