# -*- coding: utf8 -*-


class OpenTag:

    def __init__(self, tag, rest=''):
        self.tag = tag
        self.rest = rest

    def as_string(self):
        return '<' + self.tag + self.rest + '>'


class CloseTag(OpenTag):

    def as_string(self):
        return '</' + self.tag + '>'


class SelfClosingTag(OpenTag):
    pass
