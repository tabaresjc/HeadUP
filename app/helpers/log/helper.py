# -*- coding: utf8 -*-
from __future__ import absolute_import

from cloghandler import ConcurrentRotatingFileHandler
import logging


class LogHelper(object):
    "Object containing the flask application."
    app = None
    size = 512 * 1024
    copy_total = 20

    def __init__(self, app=None, config=None, *args, **kwargs):
        self.app = app
        self.start()

    @property
    def format(self):
        if not hasattr(self, '_format'):
            self._format = logging.Formatter('[%(asctime)s] %(levelname)s in %(name)s: %(message)s')
        return self._format

    @property
    def level(self):
        if not hasattr(self, '_level'):
            self._level = logging.DEBUG if self.app.config.get('DEBUG') else logging.INFO
        return self._level

    @property
    def file_suffix(self):
        if not hasattr(self, '_file_suffix'):
            self._file_suffix = '%Y-%m-%d'
        return self._file_suffix

    def start(self):
        log_path = self.app.config.get('LOG_PATH')

        if not log_path:
            return

        log_handler = ConcurrentRotatingFileHandler(log_path,
                                                    'a',
                                                    self.size,
                                                    self.copy_total)

        log_handler.setFormatter(self.format)
        log_handler.setLevel(self.level)
        # log_handler.suffix = self.file_suffix

        self.app.logger.addHandler(log_handler)
