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

	# def test_proximity_pt(self):
	# 	a = Point.fromParam(0,99,0,0)
	# 	b = Point.fromParam(0,100,0,0)
	# 	logging.info('*********')
	# 	logging.info(a.feedback(b, 800, 0))
	# 	while(True):
	# 		time.sleep(1)

	def test_gt_pos(self):
		nav = Nav()
		nav.start()
		nav.getPathTo(2)
		while(True):
			nav.getPos()
			time.sleep(1)

	"""
	def test_prakash_path(self):
		nav = Nav()
		injection = nav.__dict__['_Nav__model']

		## Direct dependency injection, to override server stuff.
		## This is used to reduce dependency on server for testing.
		pointList = [Point.fromParam(0, 2558,0, 0)
					, Point.fromParam(2152,2558,0, 0)
		]
		path = Path.fromPoints(list(pointList))
		injection['path'] = path

		nav.resetMap()
		nav.updateMap()

		print '-----------------PING--------------'
		injection['currLoc'] = Point.fromParam(0,2558,0, 0)
		nav.tick(debug=True)
		print '-----------------PING--------------'

		## Do direct dependency injection
		print '-----------------PING--------------'
		injection['currLoc'] = Point.fromParam(5,2558,0, 0)
		nav.tick(debug=True)
		print '-----------------PING--------------'

		while (True):
			pass
			time.sleep(1)

		print '-----------------PING--------------'
		injection['currLoc'] = Point.fromParam(0,2558,0, 0)
		nav.tick(debug=True)
		print '-----------------PING--------------'





		print path.get()

		# while(True):
		# 	time.sleep(1)

		# injection['currLoc'] = Point.fromParam(50,1260,0, 4.712385)
		# nav.tick(debug=True)

		## Do direct dependency injection
		# for i in range(0, 360, 5):
		# 	print i
		# 	rad = (float(i) / 180) * 3.14159
		# 	print ('------ORIENTATION: %s' % rad)
		# 	injection['currLoc'] = Point.fromParam(2,1260,0, rad)
		# 	nav.tick(debug=True)

		# while (True):
		# 	time.sleep(1)

		## reached
		# injection['currLoc'] = Point.fromParam(100,0,0, 0)
		# nav.tick(debug=True)

		# injection['currLoc'] = Point.fromParam(100,50,0 , 0)
		# nav.tick(debug=True)

		# injection['currLoc'] = Point.fromParam(50,50,0 , pi - (pi / 4) )
		# nav.tick(debug=True)

		## reached
		# injection['currLoc'] = Point.fromParam(100,100,0, 0)
		# nav.tick(debug=True)

		# injection['currLoc'] = Point.fromParam(102, 150,0, 0)
		# nav.tick(debug=True)

		# injection['currLoc'] = Point.fromParam(102, 150,0, pi)
		# nav.tick(debug=True)

		# injection['currLoc'] = Point.fromParam(100, 150,0, pi)
		# nav.tick(debug=True)

		# ## reached
		# injection['currLoc'] = Point.fromParam(100,200,0)
		# nav.tick(debug=True)

		# ## Reached
		# injection['currLoc'] = Point.fromParam(100,300,0)
		# nav.tick(debug=True)

		# ## Reached
		# injection['currLoc'] = Point.fromParam(100,400,0)
		# nav.tick(debug=True)

		# injection['currLoc'] = Point.fromParam(100,400,0)
		# nav.tick(debug=True)


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

"""