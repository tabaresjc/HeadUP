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
def translation_init(language='en'):
    """Init the translation folder for the selected language."""
    if language not in ['es', 'ja', 'en', 'fr']:
        click.echo("Selected language code is not supported")
        return
    try:
        os.system('pybabel init -i scripts/translation/messages.pot -d app/translations -l ' + language)
        os.unlink('scripts/translation/messages.pot')
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
def translation_compile():
    """Compile the translatable strings from the app and dump into translations folder."""
    try:
        os.system('pybabel extract -F scripts/translation/babel.cfg -k lazy_gettext -o scripts/translation/messages.pot app')
        os.system('pybabel compile -f -d app/translations')
    except Exception as e:
        click.echo('Error: %s' % e)

@cli.command()
def translation_update():
    """Update the translation file."""
    try:
        os.system('pybabel update -i messages.pot -d translations')
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
def translation_update():
    try:
        os.system('pybabel extract -F scripts/translation/babel.cfg -k lazy_gettext -o scripts/translation/messages.pot app')
        os.system('pybabel update -i scripts/translation/messages.pot -d app/translations')
        os.unlink('scripts/translation/messages.pot')
    except Exception as e:
        click.echo('Error: %s' % e)
