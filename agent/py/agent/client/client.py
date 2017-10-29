import apiai
import gflags
import json
import os.path
import sys
from util.base import log
from util.db.pinfo_db import *

FLAGS = gflags.FLAGS

sessions = {}

class AgentClient(object):
  def __init__(self):
    self._ai = apiai.ApiAI(FLAGS.client_access_token)

  def process(self, client_id, query_text):

    request = self._ai.text_request()
    request.lang = 'en'  # optional, default value equal 'en'

    #request.session_id = "<SESSION ID, UNIQUE FOR EACH USER>"

    request.query = query_text #"Hello"
    response = request.getresponse()

    data = json.loads(response.read().decode())
    log.INFO("===JSON===> %s" % data)
    if client_id not in sessions:
      sessions[client_id] = {}

    sess = sessions[client_id]

    # Response already present in the intent, just return that
    if ('fulfillment' in data['result'] and
        'speech' in data['result']['fulfillment'] and
        data['result']['fulfillment']['speech']):
      return PInfo(text = data['result']['fulfillment']['speech'])

    # Response not present - we need to build one
    action = data['result']['action']

    pinfo_key = (action,)
    if 'parameters' not in data['result']:
        return pinfo_lookup(pinfo_key);

    # parameters exist
    params = data['result']['parameters']

    if 'product' in params and params['product'] != '':
      prod = params['product']
      log.INFO("[session {%s}]: product name is '{%s}'" % (client_id, prod))
      if 'prod' not in sess or sess['prod'] != prod:
        sess.clear()
      sess['prod'] = prod
    # Add the session attribute to pinfo_key
    pinfo_key += (sess.get('prod'),)

    if 'Model' in params and params['Model'] != '':
      model = params['Model']
      log.INFO("[session {%s}]: model is '{%s}'" % (client_id, model))
      if 'model' not in sess or sess['model'] != model:
        if 'feature' in sess:
          del sess['feature']
      sess['model'] = model
    # Add the session attribute to pinfo_key
    pinfo_key += (sess.get('model'),)

    if 'feature' in params and params['feature'] != '':
      feature = params['feature']
      log.INFO("[session {%s}]: feature is '{%s}'" % (client_id, feature))
      sess['feature'] =  feature
    # Add the session attribute to pinfo_key
    pinfo_key += (sess.get('feature'),)

    log.INFO("===>>>pinfo_key %s" % (pinfo_key,))

    return pinfo_lookup(pinfo_key)
