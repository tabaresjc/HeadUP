# -*- coding: utf8 -*-

from flask import Blueprint
mod = Blueprint('stamp', __name__, url_prefix='/stamp')

from . import show  # noqa
from . import ranking  # noqa
from . import category  # noqa
from . import widgets  # noqa
from . import comment  # noqa
