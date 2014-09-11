#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of easyNav-pi-nav.
# https://github.com/easyNav/easyNav-pi-nav

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Joel Tong me@joeltong.org

import logging

logging.getLogger('').handlers = []

logging.basicConfig(
    # filename = "a.log",
    # filemode="w",
    level = logging.DEBUG)


from easyNav_pi_nav.version import __version__
from easyNav_pi_nav.nav import Nav
from easyNav_pi_nav.point import Point