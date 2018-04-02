# -*- coding: utf8 -*-

from app.helpers import HttpJsonEncoder
import app


app.app.json_encoder = HttpJsonEncoder
