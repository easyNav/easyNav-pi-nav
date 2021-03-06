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
		## TODO: Remove below server dependency legacy code 
		# r = requests.get('http://localhost:1337/edge/deleteAll') 
		# r = requests.get('http://localhost:1337/node/deleteAll') 
		# logging.info('Cleared server map redundant fixtures.')

		# r = requests.get('http://localhost:1337/map/update') 
		# expect(r.status_code).to_equal(200)
		# logging.info('Populated server map fixtures.')

		# r = requests.get('http://localhost:1337/node/?SUID=1') 
		# testStr = r.text
		# cls.pt = Point.fromJson(testStr)
		# logging.info('Generated new point.')

		# r2 = requests.get('http://localhost:1337/node/?SUID=3') 
		# testStr2 = r2.text
		# cls.pt2 = Point.fromJson(testStr2)
		cls.pt = Point.fromParam(x=0, y=2436, z=0, orientation=0)
		cls.pt2 = Point.fromParam(x=2152, y=731, z=0, orientation=0)
		logging.info('Generated mock points.')
		pass

	@classmethod
	def teardown_class(cls):
		# r = requests.get('http://localhost:1337/edge/deleteAll') 
		# r = requests.get('http://localhost:1337/node/deleteAll') 
		# expect(r.status_code).to_equal(200)
		# logging.info('Cleared server map fixtures.')
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
		distance = self.pt.distTo(self.pt2)
		expect(distance).to_be_numeric()
		expect(distance).to_be_greater_than(0)
		pass

	def test_can_determine_if_target_pt_is_near(self):
		ptA = Point.fromParam(0,0,0)
		ptB = Point.fromParam(10, 10, 10)
		ptC = Point.fromParam(4000, 4000, 4000)
		expect( ptA.near(ptA, 20) ).to_equal(Point.REACHED)
		expect( ptA.near(ptC, 20) ).to_equal(Point.FAR)
		expect( ptA.near(ptC, 20000) ).to_equal(Point.REACHED)
		expect( ptA.near(ptB, 20) ).to_equal(Point.REACHED)

	def test_can_retrieve_internal_orientation(self):
		expect(self.pt.angle()).to_be_numeric()

	def test_can_retrieve_orientation_from_another_pt(self):
		## TODO: Write more tests for this test orientation
		angleTo = self.pt.angleTo(self.pt2)
		expect(angleTo).to_be_numeric()

		# if point is very near / exactly the same point, give a zero.
		angleTo = self.pt.angleTo(self.pt)
		expect(angleTo).to_equal(0)

	def test_target_point_angle_is_near_or_aligned(self):
		result = self.pt.angleNear(self.pt2, 0.17453)
		expect(result).Not.to_equal(Point.ALIGNED)

		result = self.pt.angleNear(self.pt, 0.17453)
		expect(result).to_equal(Point.ALIGNED)

	def test_feedback_correction_is_working(self):
		thresholdDist, thresholdAngle  = 10, 0.17453
		feedback = self.pt.feedback(self.pt2, thresholdDist, thresholdAngle)
		expect(feedback['status']).to_equal(Point.TURN_RIGHT)

	def test_distance_to_line_path_works(self):
		"""Determines distance of point from pathway between 2 lines
		"""
		ptA = Point.fromParam(0,0,0)
		ptB = Point.fromParam(0, 20, 0)

		pt = Point.fromParam(0,10,0)
		distance = pt.distToPath(ptA, ptB)
		expect(distance).to_equal(0)

		pt = Point.fromParam(5,10,0)
		distance = pt.distToPath(ptA, ptB)
		expect(distance).to_equal(5)

		pt = Point.fromParam(20,10,0)
		distance = pt.distToPath(ptA, ptB)
		expect(distance).to_equal(20)

		pt = Point.fromParam(20,20,0)
		distance = pt.distToPath(ptA, ptB)
		expect(distance).to_equal(20)

		# Test for invalid point, which should return -1
		ptA = Point.fromParam(0,20,0)
		ptB = Point.fromParam(0, 20, 0)
		pt = Point.fromParam(20,20,0)
		distance = pt.distToPath(ptA, ptB)
		expect(distance).to_equal(-1)

		# logging.info('----------------------------------------------{}'.format(distance))
		pass

