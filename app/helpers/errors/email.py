# -*- coding: utf8 -*-

from logging.handlers import SMTPHandler
from threading import Thread
import logging


class ThreadedSMTPHandler(SMTPHandler):

    enabled = False

    def __init__(self, app, **kwargs):

        config = app.config

        self.enabled = config.get('LOG_EMAIL_ENABLED') == True

        if not self.enabled:
            return

        if (not config.get('LOG_EMAIL_DEFAULT_SENDER') or
            not config.get('LOG_EMAIL_DEFAULT_RECIPIENTS') or
            not config.get('LOG_EMAIL_HOST')):
            raise NotImplementedError()

        mailhost = config.get('LOG_EMAIL_HOST')
        sender = config.get('LOG_EMAIL_DEFAULT_SENDER')
        recipients = config.get('LOG_EMAIL_DEFAULT_RECIPIENTS').split(',')
        subject = u'[%s] Application error' % (config.get('SITE_NAME'))

        if config.get('LOG_EMAIL_PORT'):
            mailhost = (mailhost, config.get('LOG_EMAIL_PORT'))

        credentials, secure = (None, None)

        if config.get('LOG_EMAIL_USERNAME'):
            credentials = (config.get('LOG_EMAIL_USERNAME'),
                           config.get('LOG_EMAIL_PASSWORD'))

            if config.get('LOG_EMAIL_USE_TLS'):
                secure = ()

        super(ThreadedSMTPHandler, self).__init__(mailhost=mailhost,
                                                  fromaddr=sender,
                                                  toaddrs=recipients,
                                                  subject=subject,
                                                  credentials=credentials,
                                                  secure=secure)

    def emit(self, record):
        if not self.enabled:
            return

        thread = Thread(target=SMTPHandler.emit, args=(self, record))
        thread.start()
