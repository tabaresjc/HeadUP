# -*- coding: utf8 -*-

import click
from flask import Flask
from app import app


@click.group()
def cli():
    pass


@cli.command()
def attr_json():
    """Migrate the pickled longblob column to a longtext with json."""

    from app.models import Category, Post, Picture, User
    categories = Category.query.all()
    copy_attributes(categories)

    posts = Post.query.all()
    copy_attributes(posts)

    pictures = Picture.query.all()
    copy_attributes(pictures)

    users = User.query.all()
    copy_attributes(users)


def copy_attributes(items):
    for item in items:
        item.attr = {}
        if item.attributes:
            for key, value in item.attributes.iteritems():
                item.attr[key] = value
        item.save()
