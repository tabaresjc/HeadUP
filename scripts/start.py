# -*- coding: utf8 -*-

import click
from flask import Flask
from app import app


@click.group()
def cli():
    pass


@cli.command()
def db_init():
    """Initialize the database."""
    from app import db
    from app.models import Category
    db.create_all()
    click.echo('Initialize the database.')

    c1 = Category.create(name=u'Uncategorized', slug=u'uncategorized')
    c1.save()
    c2 = Category.create(name=u'News', slug=u'news')
    c2.save()


@cli.command()
def db_update():
    """Update Database."""
    click.echo('Update Database.')
    from app import db
    db.create_all()


@cli.command()
@click.option('--name', default=None, help='User\'s name')
@click.option('--email', default='', help='User\'s email')
@click.option('--password', default=None, help='User\'s password')
def init_user(name, email, password):
    """Create user."""
    from app.models import User, Role
    email_parts = email.split('@')
    if len(email_parts) > 1 and name and password:
        user = User.create(
            name=name,
            email=email,
            password='',
            nickname=email_parts[0],
            role_id=Role.ROLE_ADMIN,
            address=u'',
            phone=u'',
            lang='en'
        )
        user.set_password(unicode(password))
        user.save()
        click.echo("User created")
    else:
        click.echo("Sorry! can not create user :( ")
