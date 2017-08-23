# -*- coding: utf8 -*-

from app import app
from app.helpers import HttpJsonEncoder


app.json_encoder = HttpJsonEncoder
