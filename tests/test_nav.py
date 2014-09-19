#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of easyNav-pi-nav.
# https://github.com/easyNav/easyNav-pi-nav

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Joel Tong me@joeltong.org

from preggy import expect

from easyNav_pi_nav import Nav
from tests.base import TestCase


class NavTestCase(TestCase):

	def test_can_init(self):
		bla = Nav(None)
		pass

	# def test_can_add(self):
	# 	bla = Nav(None)
	# 	expect(bla.area()).to_equal(5)

