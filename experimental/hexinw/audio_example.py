#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
  import apiai
except ImportError:
  sys.path.append(
      os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
  )
  import apiai

import pyaudio
import time
import wave

CLIENT_ACCESS_TOKEN = 'bbcf65728aee49b39dba2da7b59f63dd'
CHUNK = 1024

def main():
  if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

  wf = wave.open(sys.argv[1], 'rb')

  ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)
  request = ai.voice_request()
  request.lang = 'en'  # optional, default value equal 'en'

  # instantiate PyAudio (1)
  p = pyaudio.PyAudio()

  """
  # define callback (2)
  def callback(in_data, frame_count, time_info, status):
    data = wf.readframes(frame_count)
    request.send(data)
    return (data, pyaudio.paContinue)

  # open stream using callback (3)
  stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                  channels=wf.getnchannels(),
                  rate=wf.getframerate(),
                  output=False,
                  stream_callback=callback)


  stream.start_stream()
  # wait for stream to finish (5)
  while stream.is_active():
    time.sleep(0.1)
  """

  stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                  channels=wf.getnchannels(),
                  rate=wf.getframerate(),
                  output=True)

  # read data
  data = wf.readframes(CHUNK)

  # play stream (3)
  while len(data) > 0:
    stream.write(data)
    request.send(data)
    data = wf.readframes(CHUNK)

  # stop stream (6)
  stream.stop_stream()
  stream.close()
  wf.close()
  p.terminate()

  print ("Wait for response...")
  response = request.getresponse()

  print (response.read())

if __name__ == '__main__':
  main()
