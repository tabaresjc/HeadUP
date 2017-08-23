# -*- coding: utf8 -*-
from flask_paginate import Pagination


class PaginationHelper(object):

    @classmethod
    def pag(cls, name, page, limit, total, record_name,
            alignment='right', bs_version=3, kind=None, **kwargs):

        name = u'%s.%s.%s.%s.%s.%s.%s' % (
            name, page, limit, total, record_name, alignment, bs_version)

        pagination = cls.get_pagination_by_name(name)

        if not pagination:
            pagination = Pagination(page=page, per_page=limit, total=total,
                                    record_name=record_name,
                                    alignment=alignment,
                                    bs_version=bs_version,
                                    **kwargs)

            cls.set_pagination_by_name(name, pagination)

        if kind == 'links':
            return pagination.links
        elif kind == 'info':
            return pagination.info
        else:
            return pagination

    @classmethod
    def get_pagination_by_name(cls, name):
        if not name:
            return None

        try:
            pages_obj = cls.pages_obj
        except AttributeError:
            pages_obj = dict()
            cls.pages_obj = pages_obj

        return pages_obj.get(name, None)

    @classmethod
    def set_pagination_by_name(cls, name, pagination):
        if not name:
            return None

        try:
            pages_obj = cls.pages_obj
        except AttributeError:
            pages_obj = dict()
            cls.pages_obj = pages_obj

        cls.pages_obj[name] = pagination
