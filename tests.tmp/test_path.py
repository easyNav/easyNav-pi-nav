#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of easyNav-pi-nav.
# https://github.com/easyNav/easyNav-pi-nav

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Joel Tong me@joeltong.org

from preggy import expect
from numpy import pi
import requests
import logging
import json

from easyNav_pi_nav import Path
from easyNav_pi_nav import Point
from tests.base import TestCase


class PathTestCase(TestCase):

	@classmethod
	def setup_class(cls):
		r = requests.get('http://localhost:1337/edge/deleteAll') 
		r = requests.get('http://localhost:1337/node/deleteAll') 
		logging.info('Cleared server map redundant fixtures.')

		r = requests.get('http://localhost:1337/map/update') 
		expect(r.status_code).to_equal(200)
		logging.info('Populated server map fixtures.')

		cls.pathNodes = requests.get('http://localhost:1337/map/shortest/121/125').text
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


	def test_can_instantiate_from_string(self):
		path = Path.fromString(self.pathNodes)
		pass


	def test_can_instantiate_from_points(self):
		pointList = []
		
		pointList.append(Point.fromParam())
		pointList.append(Point.fromParam(8, 8, 8))
		pointList.append(Point.fromParam(21, 32, 63))
		pointList.append(Point.fromParam(88, 3, 20))
		pointList.append(Point.fromParam(400, 2, 31))
		pointList.append(Point.fromParam(200, 0, 0))

		path = Path.fromPoints(pointList)
		expect(path.length()).to_equal(6)


	def test_can_retrieve_length (self):
		path = Path.fromString(self.pathNodes)
		expect(path.length()).to_be_numeric()
		expect(path.length()).Not.to_equal(0)
		pass

	def test_can_retrieve_node (self):
		path = Path.fromString(self.pathNodes)
		node = path.get()
		expect(type(node) is Point).to_be_true()

	def test_can_move_forward_backward(self):
		path = Path.fromString(self.pathNodes)
		node = path.get()
		node2 = path.next().next().get()
		node3 = path.prev().get()
		node4 = path.prev().get()
		nodeN = path.next().next().next().next().next().next().get()
		nodeP = path.prev().prev().prev().prev().prev().prev().get()

		expect(type(node) is Point).to_be_true()
		expect(type(node2) is Point).to_be_true()
		expect(type(node3) is Point).to_be_true()
		expect(type(node4) is Point).to_be_true()
		expect(type(nodeN) is Point).to_be_true()
		expect(type(nodeP) is Point).to_be_true()

		expect(node.isEqual(node2)).to_equal(False)
		expect(node.isEqual(node3)).to_equal(False)
		expect(node.isEqual(node4)).to_equal(True)
		expect(node.isEqual(nodeP)).to_equal(True)

	def test_determine_current_point_is_destination(self):
		path = Path.fromString(self.pathNodes)
		expect(path.isAtDest()).to_equal(False)

		nodeLast = path.next().next().next().next().next().next()
		expect(path.isAtDest()).to_equal(True)

		nodeLast = path.next().next().next().next().next().next().get()
		expect(path.isAtDest()).to_equal(True)

	def test_if_current_point_is_on_path(self):
		pointList = [Point.fromParam(100,0,0)
					, Point.fromParam(100,1000,0)
					, Point.fromParam(100,2000,0)
					, Point.fromParam(100,3000,0)
					, Point.fromParam(100,4000,0)
		]

		thresholdDist = 50
		thresholdAngle = 5 * 0.0174532925			# Radians

		path = Path.fromPoints(pointList)

		pt = Point.fromParam(100,0,0)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.REACHED)

		pt = Point.fromParam(200,0,0, 0)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.TURN_LEFT)

		pt = Point.fromParam(0,0,0)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.TURN_RIGHT)

		pt = Point.fromParam(0,0,0, pi / 2)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.MOVE_FORWARD)


		## TODO: This should be OUT OF RANGE.  however, for the cases of first
		## and last node, we assume that it is still reachable for now.  Hence
		## only turning error is reported.
		pt = Point.fromParam(20000,0,0)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.TURN_LEFT)
		# expect(feedback).to_equal(Point.OUT_OF_PATH)


		path.next()


		## TODO: Remove this, since in new version, reaching a point will advance 
		##       node
		pt = Point.fromParam(110,100,0, 0)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.MOVE_FORWARD)

		pt = Point.fromParam(90,100,0)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.TURN_RIGHT)

		pt = Point.fromParam(500, 500,0, pi - (pi / 4))
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.TURN_LEFT)

		## Checking with respect to different orientation

		pt = Point.fromParam(110,1000,0, pi)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.REACHED)

		path.next()

		pt = Point.fromParam(90,5000, 0, pi / 2)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.TURN_RIGHT)

		pt = Point.fromParam(90,1500, 0, pi / 2)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.TURN_LEFT)

		pt = Point.fromParam(100,1000,0)
		feedback = path.isOnPath(pt, thresholdDist, thresholdAngle)['status']
		expect(feedback).to_equal(Point.MOVE_FORWARD)








