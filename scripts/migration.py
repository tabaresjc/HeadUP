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
@click.option('--msg', help='autogenerate migration')
@click.option('--autogenerate', default='0', help='enable autogenerate (0 is disabled, 1 is enabled)')
def revision(msg, autogenerate='0'):
    """Generate a revision migration."""
    try:
        os.environ['DATABASE_URL'] = config.SQLALCHEMY_DATABASE_URI
        os.environ['PYTHONPATH'] = config.BASE_DIR
        if autogenerate == '1':
            click.echo('autogenerate enabled...')
            os.system('alembic revision --autogenerate -m "%s"' % msg)
        else:
            os.system('alembic revision -m "%s"' % msg)
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
@click.option('--point', default='head', help='head or revision number')
def upgrade(point='head'):
    """Upgrade to head or to the given revision number."""
    try:
        os.environ['DATABASE_URL'] = config.SQLALCHEMY_DATABASE_URI
        os.environ['PYTHONPATH'] = config.BASE_DIR
        os.system('alembic upgrade %s' % point)
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
@click.option('--point', default='base', help='head or revision number')
def downgrade(point='base'):
    """Downgrade to base or to the given revision number."""
    try:
        os.environ['DATABASE_URL'] = config.SQLALCHEMY_DATABASE_URI
        os.environ['PYTHONPATH'] = config.BASE_DIR
        os.system('alembic downgrade %s' % point)
    except Exception as e:
        click.echo('Error: %s' % e)
