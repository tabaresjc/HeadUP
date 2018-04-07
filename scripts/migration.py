# -*- coding: utf8 -*-

import os
import sys
import click
from app import app
import config


@click.group()
def cli():
    pass


@cli.command()
@click.option('--point', default='head', help='head or revision number')
def upgrade(point='head'):
    """Upgrade to head or to the given revision number."""
    try:
        os.environ['DATABASE_URL'] = config.SQLALCHEMY_DATABASE_URI
        os.system('alembic upgrade %s' % point)
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
@click.option('--point', default='base', help='head or revision number')
def downgrade(point='base'):
    """Downgrade to base or to the given revision number."""
    try:
        os.environ['DATABASE_URL'] = config.SQLALCHEMY_DATABASE_URI
        os.system('alembic upgrade %s' % point)
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
def downgrade_one():
    """Undo last migration."""
    try:
        os.environ['DATABASE_URL'] = config.SQLALCHEMY_DATABASE_URI
        os.system('alembic upgrade -1')
    except Exception as e:
        click.echo('Error: %s' % e)
