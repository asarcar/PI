#
# Copyright (c) 2016 Pi Inc. All rights reserved.
#
# Author: asarcar@piekul.com
#
# This bot listens to port 5002 for incoming connections from Facebook. It takes
# in any messages that the bot receives and echos it back.
#
# Usage:
#
#   # Serve forever.
#   server = BotServer()
#   server.run()
#   server.wait()
#

from flask import Flask, request
import gflags
import json
from pymessenger.bot import Bot
from pymessenger import Element, Button
import requests
import sys
import thread
import threading
import traceback

from bot.interfaces import BotInterfaces
from bot.speech import processor as s2t # Speech to Text
from util.base import log
from util.db.pinfo_db import PInfo
from util.misc.decorators import fatal_on_exception

FLAGS= gflags.FLAGS

# Map webhook type to function
webhook_funcs = {}

def webhook_func(webhook_type):
  """
  Decorates webhook funcs and populates the webhook function tables.
  """
  def decorator(func):
    webhook_funcs[webhook_type] = func
    return func
  return decorator

class WebhookType:
  """
  Types of Webhooks.
  """
  (PostBack, Message) = range(2)

# Map message type to function
message_funcs = {}

def message_func(message_type):
  """
  Decorates message funcs and populates the message function tables.
  """
  def decorator(func):
    message_funcs[message_type] = func
    return func
  return decorator

class BotServer(object):
  def __init__(self):
    from bot.interfaces import BotInterfaces
    self._interfaces = BotInterfaces()
    self._agent_client = self._interfaces.agent_client
    self._app = Flask(__name__)
    self._event = threading.Event()
    self._event.set()

  def _get_type_from_payload(self, payload):
    """
    Get type of webhook.
    Current support: message, postback
    Reference: https://developers.facebook.com/docs/messenger-platform/
               webhook-reference/message-received
    """
    data = json.loads(payload)
    if "postback" in data["entry"][0]["messaging"][0]:
      return "postback"
    elif "message" in data["entry"][0]["messaging"][0]:
      return "message"

    return None

  def _iter_messaging_events(self, payload):
    """
    Generate tuples of (sender_id, message_text) from the provided payload.
    This part technically clean up received data to pass only meaningful data
    to processIncoming() function
    """
    data = json.loads(payload)
    messaging_events = data["entry"][0]["messaging"]

    for event in messaging_events:
      sender_id = event["sender"]["id"]

      # Not a message
      if "message" not in event:
        yield sender_id, None

      if ("message" in event and "text" in event["message"] and "quick_reply"
          not in event["message"]):
        data = event["message"]["text"].encode('unicode_escape')
        yield sender_id, {'type':'text', 'data': data, 'message_id': event['message']['mid']}
      elif "attachments" in event["message"]:
        if "location" == event['message']['attachments'][0]["type"]:
          coordinates = event['message']['attachments'][
              0]['payload']['coordinates']
          latitude = coordinates['lat']
          longitude = coordinates['long']

          yield sender_id, {'type':'location','data':[latitude, longitude],
              'message_id': event['message']['mid']}
        elif "audio" == event['message']['attachments'][0]["type"]:
          audio_url = event['message'][
              'attachments'][0]['payload']['url']
          yield sender_id, {'type':'audio','data': audio_url,
              'message_id': event['message']['mid']}
        else:
          yield sender_id, {'type':'text','data':"I don't understand this",
              'message_id': event['message']['mid']}
      elif "quick_reply" in event["message"]:
        data = event["message"]["quick_reply"]["payload"]
        yield sender_id, {'type':'quick_reply','data': data,
            'message_id': event['message']['mid']}
      else:
        yield sender_id, {'type':'text','data':"I don't understand this",
            'message_id': event['message']['mid']}

  @message_func("text")
  def _message_text(self, sender_id, text):
    """
    Handle a text message.

    Args:
      sender_id (int64): Sender ID.
      text (string): Text message.

    Returns:
      response : Response from machine learning.
    """
    log.INFO("MSG---> %s" % text)
    resp = self._agent_client.process(sender_id, text)
    return resp

  @message_func("audio")
  def _message_audio(self, sender_id, audio_url):
    """
    Handle an audio message.

    Args:
      sender_id (int64): Sender ID.
      audio_url (string): Audio url.

    Returns:
      response : Response from machine learning.
    """
    # Get text from audio.
    try:
      text = s2t.transcribe(audio_url)
      if text == "" or text == None:
        return
    except Exception as exc:
      return PInfo(text = "I'm sorry. I could not follow your question")

    text = text.decode('utf-8')
    log.INFO("MSG---> %s" % text)
    resp = self._agent_client.process(sender_id, text)
    return resp

  @message_func("image")
  def _message_image(self, sender_id, message):
    """
    Handle image message.
    """
    return None

  @message_func("location")
  def _message_location(self, sender_id, message):
    """
    Handle location message.
    """
    return None

  @message_func("quick_reply")
  def _message_quick_reply(self, sender_id, message):
    """
    Handle quick reply message.
    """
    return None

  @webhook_func("postback")
  def _webhook_postback(self, payload):
    """
    Developer-defined postbacks
    """
    pass

  @webhook_func("message")
  def _webhook_message(self, payload):
    """
    Handle messages.
    """
    log.INFO("===> Handle message %s" % payload)
    # Process webhook messages.
    for sender_id, msg_info in self._iter_messaging_events(payload):
      if msg_info is None:
        return "ok"

      try:
        handler = message_funcs[msg_info['type']]
      except KeyError:
        log.DEBUG("Unrecognized message type %s" % (msg_info['type'],))
        continue
      resp = handler(self, sender_id, msg_info['data'])
      if resp is None:
        continue
      log.INFO("RSP***> Text:'{%s}', Image:'{%s}', Video:'{%s}', Audio:'{%s}'" %
               (resp.text, resp.image_url, resp.video_url, resp.audio_url))
      self.bot_respond(sender_id, resp)

  #@app.route("/", methods = ['GET', 'POST'])
  def bot_pi(self):
    if request.method == 'GET':
      if (request.args.get("hub.verify_token") != FLAGS.bot_verify_token):
        return None
      return request.args.get("hub.challenge")

    if request.method == 'POST':
      log.INFO("%s" % request.json)
      payload = request.get_data()
      webhook_type = self._get_type_from_payload(payload)

      # Process webhook events.
      try:
        handler = webhook_funcs[webhook_type]
      except KeyError:
        log.DEBUG("Unrecognized webhook type %s" % (webhook_type,))
        return "success"

      handler(self, payload)

    return "success"

  def bot_respond(self, sender_id, resp):
    if (resp.IsTextOnly()):
      self._bot.send_text_message(sender_id, resp.text)
      log.INFO("Sending Text")
      return None

    if (resp.image_url):
      self._bot.send_image_url(sender_id, resp.image_url)
      self._bot.send_text_message(sender_id, resp.text)
      log.INFO("Sending Text N Image")
      return None

    if (resp.video_url):
      self._bot.send_video_url(sender_id, resp.video_url)
      self._bot.send_text_message(sender_id, resp.text)
      log.INFO("Sending Text N Video")
      return None

    # Must be Audio URL
    self._bot.send_audio_url(sender_id, resp.audio_url)
    self._bot.send_text_message(sender_id, resp.text)
    log.INFO("Sending Text N Audio")

  @fatal_on_exception
  def run(self):
    """
    Starts the bot server.
    """
    self._event.clear()
    self._bot = Bot(FLAGS.bot_access_token)
    # TODO: Fix flask app to run in background thread.
    # In fact, we need to switch to WSGI server in production.
    #thread.start_new_thread(self._serve_http, ())
    self._serve_http()

  @fatal_on_exception
  def _serve_http(self):
    """
    Thread that starts the HTTP server.
    """
    self._app.add_url_rule("/", methods=['GET', 'POST'],
        view_func=self.bot_pi)
    self._app.run(port=FLAGS.bot_port, debug=False)

  def stop(self):
    """
    Stops the bot server.
    """
    if not self._event.is_set():
      self._event.set()

  def wait(self):
    """
    Waits for the thread to exit.
    """
    self._event.wait()
