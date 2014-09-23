#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of easyNav-pi-nav.
# https://github.com/easyNav/easyNav-pi-nav

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Joel Tong me@joeltong.org

from preggy import expect

from easyNav_pi_nav import __version__
from tests.base import TestCase


class VersionTestCase(TestCase):
    def test_has_proper_version(self):
        expect(type(__version__) is str).to_equal(True)
