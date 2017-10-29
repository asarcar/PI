#!/bin/bash
#
# Usage:
# Start with a MINIMAL Centos *7* installation.
# Then run this script as root, followed by yum update.
#

set -e
set -x

# Install EPEL repo
yum -y localinstall http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-8.noarch.rpm

# Install Nux Dextop repo
rpm --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro
yum -y localinstall http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-1.el7.nux.noarch.rpm

PACKAGES=(
  # From CentOS/EPEL
  wget
  git
  autofs
  ffmpeg
  nfs-utils
  leveldb-devel
  libaio-devel
  libarchive-devel
  libcurl-devel
  libgcrypt-devel
  libicu-devel
  libidn-devel
  libnet-devel
  libnl-devel
  libtasn1-devel
  libudev-devel
  libunwind-devel
  libuuid-devel
  ncurses-devel
  openssl-devel
  python-bson
  python-devel
  python-flask
  python-jinja2
  python-pbr
  python-setuptools
  pywbem
  readline-devel
  snappy-devel
  xz-devel
  zlib-devel
  zlib-static
  fuse
  bison
  bc
  xz
  libtool
  dsniff
  pigz
  pxz
  zip
  # Install pylint to lint python
  pylint
  python
  python34
  tree
)

yum clean expire-cache
yum -y --setopt=exclude= install "${PACKAGES[@]}"

PYTHON_PACKAGES=(
  apiai
  autobahn
  beautifulsoup4
  bson
  google-api-python-client
  pattern
  pymessenger
  python-gflags
  service_identity
  twisted
)

pip install "${PYTHON_PACKAGES[@]}"

exit 0
