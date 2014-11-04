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
		# nav.getPos()
		expect(type(nav.loc()) is Point).to_equal(True)


	def test_can_set_position_by_suid(self):
		nav = Nav()
		nav.setPosBySUID(3)
		# nav.getPos()
		logging.debug(nav.loc())
		## TODO write assertions for this


	def test_can_get_path_to_location(self):
		nav = Nav()
		nav.resetMap()
		nav.updateMap()
		time.sleep(5)
		nav.getPathTo('5')
		expect(type(nav.path()) is Path).to_equal(True)

		print '------RESPONSE---------'
		print nav.path()


	## DEPRECATED, AND VALUES OUTDATED.  USE GUI TO CHECK FOR 
	## ACCURACY. 
	"""
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

		## Dependency injection to reset path
		nav._resetNavParams()

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
	"""


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


	def test_can_avoid_collision(self):
		logging.info('')
		logging.info('---started event test---')

		## Setup Nav daemon
		nav = Nav()
		nav.start()

		pointList = [Point.fromParam(100,0,0)
					, Point.fromParam(100,200,0)
		]
		path = Path.fromPoints(pointList)
		injection['path'] = path

		## Setup collision info
		client = DispatcherClient(port=9002)
		client.start()
		client.send(9001, 'obstacle', {"status" : "0"})

		time.sleep(5)

		## Keep daemons alive for 5 seconds.
		time.sleep(10)

		client.stop()
		nav.stop()
		logging.info('---finished event test---')


	def test_daemon_update_pos_from_cruncher_event(self):
		logging.info('')
		logging.info('---started event test---')

		## Setup Nav daemon
		nav = Nav()
		nav.start()
		loc = nav.loc() # get current location as a point
		x,y,z,angle = loc.getLocTuple()

		expect(x).to_equal(0)
		expect(y).to_equal(0)
		expect(z).to_equal(0)
		expect(angle).to_equal(0)

		# Wait for 2 seconds to set-up
		time.sleep(2)

		## Setup mock cruncher
		client = DispatcherClient(port=9004)
		client.start()
		client.send(9001, 'point', {
			"x": 10, 
			"y": 123, 
			"z": 456, 
			"ang": 1, 
		})

		# Wait for 5 seconds to propagate
		startTime = time.time()
		while(time.time() - startTime < 5):
			time.sleep(0.01)
			
		loc = nav.loc() # get current location as a point
		x,y,z,angle = loc.getLocTuple()
		expect(x).to_equal(10)
		expect(y).to_equal(123)
		expect(z).to_equal(456)
		expect(angle).to_equal(1)

		client.stop()
		nav.stop()
		logging.info('---finished event test---')

		
	def test_can_avoid_collision(self):
		logging.info('')
		logging.info('---started event test---')

		## Setup Nav daemon
		nav = Nav()
		nav.start()

		pointList = [Point.fromParam(100,0,0)
					, Point.fromParam(100,200,0)
		]
		path = Path.fromPoints(pointList)
		injection = nav.__dict__['_Nav__model']
		injection['path'] = path

		## Setup collision info
		client = DispatcherClient(port=9002)
		client.start()
		client.send(9001, 'obstacle', {"status" : "0"})
		client.send(9001, 'obstacle', {"status" : "1"})
		time.sleep(10)
		client.send(9001, 'obstacle', {"status" : "0"})

		## Keep daemons alive for 5 seconds.
		time.sleep(15)

		print('--------------------------')

		client.stop()
		nav.stop()
		logging.info('---finished event test---')



	# #TODO: remove this -------------------------------------------------------
	# def test_feedback_works_TEMP(self):

	# 	nav = Nav()
	# 	injection = nav.__dict__['_Nav__model']

	# 	## Direct dependency injection, to override server stuff.
	# 	## This is used to reduce dependency on server for testing.

	# 	nav.resetMap()
	# 	nav.updateMapCustom('nocobot', '2')

	# 	pointList = [
	# 		#Point.fromParam(25, 250, 0, name="DOT 11"),
	# 		#Point.fromParam(125, 250, 0, name="DOT 14"),
	# 		Point.fromParam(225, 175, 0, name="DOT 17"),
	# 		Point.fromParam(450, 175, 0, name="DOT 9"),
	# 		Point.fromParam(450, 75, 0, name="DOT 6")
	# 	]

	# 	path = Path.fromPoints(pointList)
	# 	injection['path'] = path


	# 	## Do direct dependency injection
	# 	# injection['path'].next();
	# 	# injection['path'].next();
	# 	nav.tick(debug=True)
	# 	nav.tick(debug=True)
	# 	# print('showed point 1--------------------------------------')
	# 	# injection['currLoc'] = Point.fromParam(350,180,0, pi / 2)
	# 	# nav.tick(debug=True)
	# 	# nav.tick(debug=True)
	# 	# nav.tick(debug=True)
	# 	# nav.tick(debug=True)
	# 	injection['path'].next();

	# 	print('showed point 2--------------------------------------')
	# 	injection['currLoc'] = Point.fromParam(200,325,0, 3 * pi / 2)
	# 	nav.tick(debug=True)
	# 	nav.tick(debug=True)
	# 	nav.tick(debug=True)
	# 	nav.tick(debug=True)

	# 	injection['path'].next();

	# 	print('showed point 3--------------------------------------')
	# 	injection['currLoc'] = Point.fromParam(450,125,0, pi)
	# 	nav.tick(debug=True)
	# 	nav.tick(debug=True)
	# 	nav.tick(debug=True)
	# 	nav.tick(debug=True)


	# 	while(True):
	# 		time.sleep(1)
	# 		pass
		

	# 	## reached
	# 	injection['currLoc'] = Point.fromParam(100,0,0, 0)
	# 	nav.tick(debug=True)

	# 	injection['currLoc'] = Point.fromParam(100,50,0 , 0)
	# 	nav.tick(debug=True)

	# 	injection['currLoc'] = Point.fromParam(50,50,0 , pi - (pi / 4) )
	# 	nav.tick(debug=True)

	# 	## reached
	# 	injection['currLoc'] = Point.fromParam(100,100,0, 0)
	# 	nav.tick(debug=True)

	# 	injection['currLoc'] = Point.fromParam(102, 150,0, 0)
	# 	nav.tick(debug=True)

	# 	injection['currLoc'] = Point.fromParam(102, 150,0, pi)
	# 	nav.tick(debug=True)

	# 	injection['currLoc'] = Point.fromParam(100, 150,0, pi)
	# 	nav.tick(debug=True)

	# 	## reached
	# 	injection['currLoc'] = Point.fromParam(100,200,0)
	# 	nav.tick(debug=True)

	# 	## Reached
	# 	injection['currLoc'] = Point.fromParam(100,300,0)
	# 	nav.tick(debug=True)

	# 	## Reached
	# 	injection['currLoc'] = Point.fromParam(100,400,0)
	# 	nav.tick(debug=True)

	# 	injection['currLoc'] = Point.fromParam(100,400,0)
	# 	nav.tick(debug=True)



	# def test_can_add(self):
	# 	bla = Nav(None)
	# 	expect(bla.area()).to_equal(5)

