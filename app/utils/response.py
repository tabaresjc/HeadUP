# -*- coding: utf8 -*-
from flask import render_template, jsonify, request
from flask.json import JSONEncoder
from flask.ext.wtf import Form
import datetime


def resp(template, status=True, **context):
  """Renders a template from the template folder with the given
  arguments.
          :param template: the name of the template to be
          rendered, or an iterable with template names
          the first one existing will be rendered
          :param context: the variables that should be available in the
          context of the template.
  """
  # detect the request type
  contentType = request.headers.get('Content-Type')
  acceptContent = request.headers.get('Accept')
  # if request.is_xhr or contentType == 'application/json' or acceptContent == 'application/json':
  json_data = {
      'status': status,
      'time': datetime.datetime.utcnow(),
      'data': {}
  }

  for key, obj in context.iteritems():
    if isinstance(obj, (datetime.date, str, int, long, float, list, tuple, dict)):
      json_data['data'][key] = obj
    elif not isinstance(obj, Form):
      json_data['data'][key] = obj
  return jsonify(**json_data)


  # return render_template(template,  **context)


class CustomJSONEncoder(JSONEncoder):

  def default(self, obj):
    if hasattr(obj, 'isoformat'):
      return obj.isoformat()

    if hasattr(obj, '__json_meta__'):
      data = {}
      for field in obj.__json_meta__:
        data[field] = getattr(obj, field)
      return data

    try:

      iterable = iter(obj)
    except TypeError:
      pass
    else:
      return list(iterable)
    return super(CustomJSONEncoder, self).default(obj)
