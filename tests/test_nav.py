#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of easyNav-pi-nav.
# https://github.com/easyNav/easyNav-pi-nav

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Joel Tong me@joeltong.org

from preggy import expect
import time

from easyNav_pi_nav import Nav, Point, Path

from tests.base import TestCase


class NavTestCase(TestCase):

	def test_can_init(self):
		bla = Nav(None)
		pass


	def test_can_update_map(self):
		nav = Nav(None)
		nav.resetMap()
		res = nav.updateMap()


	def test_can_get_position(self):
		nav = Nav(None)
		nav.getPos()
		expect(type(nav.loc()) is Point).to_equal(True)


	def test_can_get_path_to_location(self):
		nav = Nav(None)
		nav.resetMap()
		nav.updateMap()
		time.sleep(5)
		nav.getPathTo('5')
		expect(type(nav.path()) is Path).to_equal(True)

		print '------RESPONSE---------'





	# def test_can_add(self):
	# 	bla = Nav(None)
	# 	expect(bla.area()).to_equal(5)

