# -*- coding: utf8 -*-
import functools
from flask import request
import app


def task_handler(f):
    @app.mq.task(ignore_result=True)
    @functools.wraps(f)
    def _wrapper(*args, **kwds):
        ctx = app.app.test_request_context()
        ctx.push()
        with ctx:
            result = f(*args, **kwds)
        ctx.pop()
        return result
    return _wrapper
