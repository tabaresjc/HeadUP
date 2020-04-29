# -*- coding: utf8 -*-

import os
import sys
import click
import config
import json
import datetime
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
        po2json()
    except Exception as e:
        click.echo('Error: %s' % e)


@cli.command()
def update():
    """Update existing message catalogs from a POT file."""
    try:
        remove_file('scripts/translation/messages.pot')

        cmd = [
            'pybabel extract',
            '-F scripts/translation/babel.cfg',
            '-k _lg -k _ -k lazy_gettext',
            '-o scripts/translation/messages.pot .'
        ]

        os.system(' '.join(cmd))
        os.system('pybabel update -i scripts/translation/messages.pot -d app/translations')

        po2json()
    except Exception as e:
        click.echo('Error: %s' % e)


def po2json():
    directory = os.path.join(config.APP_STATIC_DATA_PATH, 'languages')

    if not os.path.exists(directory):
        os.makedirs(directory)

    for key, item in config.LANGUAGES:
        file_name = os.path.join(directory, '%s.json' % key)
        cmd = 'pojson -e utf-8 app/translations/%s/LC_MESSAGES/messages.po' % (
            key)
        r = os.popen(cmd).read()

        obj = json.loads(r)

        # remove empty entry
        del  obj['']

        for k, v in obj.iteritems():
            if not isinstance(v, list):
                continue

            c = ''.join([t for t in v if t is not None])
            c = c.replace(u'%(', u'{').replace(u')s', u'}')
            obj[k] = c


        remove_file(file_name)

        data = {
            'status': True,
            'data': obj
        }

        with open(file_name, 'w') as f:
            json.dump(data, f)


def remove_file(file_name):
    try:
        os.unlink(file_name)
    except:
        pass
