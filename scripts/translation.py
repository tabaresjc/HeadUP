# -*- coding: utf8 -*-

import os
import sys
import click
from app import app


@click.group()
def cli():
    pass


@cli.command()
@click.option('--language', default='en', help='Language code (es, ja, fr)')
def init(language='en'):
    """Create new message catalogs from a POT file."""
    try:
        os.system('pybabel init -i scripts/translation/messages.pot -d app/translations -l ' + language)
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
def compile():
    """Compile the translatable strings from the app and dump into translations folder."""
    try:
        os.system('pybabel compile -f -d app/translations')
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
def update():
    """Update existing message catalogs from a POT file."""
    try:
        try:
            os.unlink('scripts/translation/messages.pot')
        except:
            pass
        os.system(
            'pybabel extract -F scripts/translation/babel.cfg -k lazy_gettext -o scripts/translation/messages.pot .')
        os.system('pybabel update -i scripts/translation/messages.pot -d app/translations')
    except Exception as e:
        click.echo('Error: %s' % e)
