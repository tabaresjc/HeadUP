# -*- coding: utf8 -*-
import pytz


def get_timezones():
    return [(c, c) for c in pytz.all_timezones]
