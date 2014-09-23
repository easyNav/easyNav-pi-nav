#!/usr/bin/python
# -*- coding: utf-8 -*-

# This file is part of easyNav-pi-nav.
# https://github.com/easyNav/easyNav-pi-nav

# Licensed under the MIT license:
# http://www.opensource.org/licenses/MIT-license
# Copyright (c) 2014 Joel Tong me@joeltong.org

from preggy import expect
import time
import requests
import smokesignal
import logging
from numpy import pi
from tests.base import TestCase

from easyNav_pi_dispatcher import DispatcherClient

from easyNav_pi_nav import Nav, Point, Path



class NavTestCase(TestCase):

	def test_can_init(self):
		bla = Nav()
		pass


	def test_can_update_map(self):
		nav = Nav()
		nav.resetMap()
		nav.updateMap()


	def test_can_get_position(self):
		nav = Nav()
		nav.getPos()
		expect(type(nav.loc()) is Point).to_equal(True)


	def test_can_get_path_to_location(self):
		nav = Nav()
		nav.resetMap()
		nav.updateMap()
		time.sleep(5)
		nav.getPathTo('5')
		expect(type(nav.path()) is Path).to_equal(True)

		print '------RESPONSE---------'
		print nav.path()


	def test_feedback_works(self):
		nav = Nav()
		injection = nav.__dict__['_Nav__model']

		## Direct dependency injection, to override server stuff.
		## This is used to reduce dependency on server for testing.
		pointList = [Point.fromParam(100,0,0)
					, Point.fromParam(100,100,0)
					, Point.fromParam(100,200,0)
					, Point.fromParam(100,300,0)
					, Point.fromParam(100,400,0)
		]
		path = Path.fromPoints(pointList)
		injection['path'] = path

		nav.resetMap()
		nav.updateMap()

		## Do direct dependency injection
		injection['currLoc'] = Point.fromParam(0,0,0, 0)
		nav.tick(debug=True)

		## reached
		injection['currLoc'] = Point.fromParam(100,0,0, 0)
		nav.tick(debug=True)

		injection['currLoc'] = Point.fromParam(100,50,0 , 0)
		nav.tick(debug=True)

		injection['currLoc'] = Point.fromParam(50,50,0 , pi - (pi / 4) )
		nav.tick(debug=True)

		## reached
		injection['currLoc'] = Point.fromParam(100,100,0, 0)
		nav.tick(debug=True)

		injection['currLoc'] = Point.fromParam(102, 150,0, 0)
		nav.tick(debug=True)

		injection['currLoc'] = Point.fromParam(102, 150,0, pi)
		nav.tick(debug=True)

		injection['currLoc'] = Point.fromParam(100, 150,0, pi)
		nav.tick(debug=True)

		## reached
		injection['currLoc'] = Point.fromParam(100,200,0)
		nav.tick(debug=True)

		## Reached
		injection['currLoc'] = Point.fromParam(100,300,0)
		nav.tick(debug=True)

		## Reached
		injection['currLoc'] = Point.fromParam(100,400,0)
		nav.tick(debug=True)

		injection['currLoc'] = Point.fromParam(100,400,0)
		nav.tick(debug=True)


	def test_can_run_as_daemon(self):
		nav = Nav()

		nav.start()
		running = True
		# Run Nav for 5 seconds
		time.sleep(5)

		nav.stop()
		running = False 
		expect(running).to_equal(False)


	def test_daemon_can_receive_event_get_new_path(self):
		""" NOTE: As this test is async, and NoseTest does not 
		support async tests, please check this manually.
		"""
		logging.info('')
		logging.info('---started event test---')

		## Setup Nav daemon
		nav = Nav()
		nav.start()

		## Setup client and send info
		client = DispatcherClient(port=9002)
		client.start()
		client.send(9001, 'newPath', {"to" : "5"})
		logging.info('Requested for new Path from 9002.')

		## Keep daemons alive for 5 seconds.
		time.sleep(5)

		client.stop()
		nav.stop()
		logging.info('---finished event test---')
		


	# def test_can_add(self):
	# 	bla = Nav(None)
	# 	expect(bla.area()).to_equal(5)

