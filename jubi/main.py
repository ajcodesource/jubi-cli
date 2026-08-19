import click
import jubi.core.commands as cmd

@click.group()
def cli():
    pass
cli.add_command(cmd.alert)
cli.add_command(cmd.init)
cli.add_command(cmd.add)
cli.add_command(cmd.listall)
cli.add_command(cmd.delete)
cli.add_command(cmd.update)


