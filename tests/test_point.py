#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of easyNav-pi-nav.
# https://github.com/easyNav/easyNav-pi-nav

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Joel Tong me@joeltong.org

from preggy import expect
import requests
import logging
import json

from easyNav_pi_nav import Point
from tests.base import TestCase


class NavTestCase(TestCase):

	@classmethod
	def setup_class(cls):

		r = requests.get('http://localhost:1337/edge/deleteAll') 
		r = requests.get('http://localhost:1337/node/deleteAll') 
		logging.info('Cleared server map redundant fixtures.')

		r = requests.get('http://localhost:1337/map/update') 
		expect(r.status_code).to_equal(200)
		logging.info('Populated server map fixtures.')

		r = requests.get('http://localhost:1337/node/?SUID=1') 
		testStr = r.text
		cls.pt = Point(testStr)
		logging.info('Generated new point.')
		pass

	@classmethod
	def teardown_class(cls):
		r = requests.get('http://localhost:1337/edge/deleteAll') 
		r = requests.get('http://localhost:1337/node/deleteAll') 
		expect(r.status_code).to_equal(200)
		logging.info('Cleared server map fixtures.')
		pass

	def setup(self):
		pass

	def teardown(self):
		pass

	def test_can_instantiate(self):
		# Will pass if setup fixture passes
		pass

	def test_can_convert_to_json(self):
		expect( json.loads(self.pt.toJSON()) ).Not.to_be_null()
		pass

	def test_can_return_location(self):
		loc = self.pt.loc()
		expect(loc["x"]).to_be_numeric()
		expect(loc["y"]).to_be_numeric()
		expect(loc["z"]).to_be_numeric()
		pass

	def test_can_return_distance_to_another_point(self):
		pass



		# expect(bla.area()).to_equal(5)

