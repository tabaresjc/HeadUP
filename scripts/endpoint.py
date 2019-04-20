# -*- coding: utf8 -*-

import click
from app import app


@click.group()
def cli():
    pass


@cli.command()
def show():
    """Show list of endpoints."""

    click.echo("****************************")

    click.echo(app.url_map)

    click.echo("****************************")
    click.echo()
