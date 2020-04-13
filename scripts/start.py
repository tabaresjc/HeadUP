# -*- coding: utf8 -*-

import click
from flask import Flask


@click.group()
def cli():
    pass


@cli.command()
def db_init():
    """Initialize the database."""
    from app.models import Category

    categories = [
        (u'Uncategorized', 'uncategorized', 'Uncategorized')
    ]

    for name, slug, description in categories:
        c = Category.create(
            name=name,
            slug=slug,
            description=description)
        c.save()


@cli.command()
@click.option('--nickname', default=None, help='User\'s name')
@click.option('--email', default='', help='User\'s email')
@click.option('--password', default=None, help='User\'s password')
def init_user(nickname, email, password):
    """Create user."""
    from app.models import User, Role

    if nickname and email and password:
        user = User.create(
            email=email,
            password='',
            nickname=nickname,
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
