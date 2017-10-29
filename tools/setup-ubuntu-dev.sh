#!/bin/bash
#
# Usage:
# Start with a MINIMAL Ubuntu *16.04LTS* or later installation.
# Then run this script followed by sudo apt-get update -y.
#

# stops execution if a command or pipeline has an error
set -e
# turn on debug tracing of last command executed
set -x

# Local Install repos

PACKAGES=(
  ffmpeg # encode/decode & convert audio/video files
  libffi-dev # Foreign Function Interface needed for openssl
  libssl-dev # SSL Toolkit
  python
  python-flask # webserver
  python-ipdb  # debugger
  python-numpy # matrix operations
  python-setuptools # setup python libs
  tree # display directory
)

sudo -H apt-get autoclean -y
sudo -H apt-get autoremove -y
sudo -H apt-get install -y "${PACKAGES[@]}"

# Link al the appropriate pip/pip3/pip3.5 scripts in /usr/local/bin
# sudo -H easy_install pip

PYTHON_PACKAGES=(
  google-api-python-client
  pip
  python-gflags
  service_identity
  twisted
)
sudo -H pip install --upgrade "${PYTHON_PACKAGES[@]}"

# For now installing apiai and pymessenger in user $HOME directory
# Fixes to these packages are just written over 
PYTHON_USER_PACKAGES=(
  apiai # language: parsing, entities, modeling, ...     
  autobahn # open-source implementation of websocket
  pymessenger # FB Messenger
  twisted # Async Networking Framework
)
pip install --user --install-option="--prefix=" --upgrade "${PYTHON_USER_PACKAGES[@]}"

exit 0
