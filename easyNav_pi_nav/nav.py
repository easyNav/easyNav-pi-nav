
#!/usr/bin/python

import multiprocessing
import json
import requests
import logging

from path import Path 
from point import Point


class Nav(object):
	""" This is the Nav class, which handles navigation on the Raspberry Pi. 
	It retrieves remote location information and navigates to the point.  In addition,
	this class implements the REST API endpoints from the server. 
	"""

	HOST_ADDR = "http://localhost:1337"
	THRESHOLD_DIST = 50
	THRESHOLD_ANGLE = 5 * 0.0174532925

	"""docstring for Nav"""
	def __init__(self, arg):
		super(Nav, self).__init__()
		self.arg = arg

		self.__model = {
			'path': None,
			'currLoc': Point.fromParam()
		}


	def area(self):
		return 2 + 3;
		

	def run(self):
		pass

	def stop(self):
		pass


	def resetMap(self):
		"""Resets the map.
		"""
		r = requests.delete(Nav.HOST_ADDR + '/map')
		pass


	def updateMap(self):
		"""Updates the map on server. 
		"""
		r = requests.get(Nav.HOST_ADDR + '/map/update')
		pass


	def getPos(self):
		"""Gets the position from server, and updates internal 
		coordinates in Nav module.
		"""
		r = requests.get(Nav.HOST_ADDR + '/heartbeat/location')
		self.__model['currLoc'] = Point.fromJson(r.text)
		pass


	def getPathTo(self, pointId):
		"""Gets shortest path from point from current location, and updates internal
		path accordingly.
		"""
		r = requests.get(Nav.HOST_ADDR + '/map/goto/' + pointId)
		self.__model['path'] = Path.fromString(r.text)
		logging.debug('Retrieved new path.')
		pass


	def path(self):
		"""Returns the current path of nav, as a Path instance.
		"""
		return self.__model['path']


	def loc(self):
		""" Returns the current location of user, as a Point instance. 
		"""
		return self.__model['currLoc']


	def feedbackCorrection(self):
		"""Feedback correction control. 
		"""
		path = self.path()
		pt = self.loc()
		logging.debug(pt)
		logging.debug(path.get())
		feedback = path.isOnPath(pt, self.THRESHOLD_DIST, self.THRESHOLD_ANGLE)

		status = feedback['status']
		if (status is Point.REACHED):
			##TODO: Implement print to voice

			if (path.isAtDest() is False): 
				self.__model['path'].next()
				logging.debug('checkpoint reached!')
			else:
				logging.debug('Reached destination, done!')


			pass

		elif (status is Point.MOVE_FORWARD):
			##TODO: Implement print to voice
			logging.debug('move forward!')
			pass

		elif (status is Point.OUT_OF_PATH):
			##TODO: Implement print to voice
			logging.debug('Out of path!')
			self.getPathTo( self.path().dest().name() )
			pass

		elif (status is Point.ALIGNED):
			##TODO: Implement print to voice
			logging.debug('Point aligned!')
			pass

		elif (status is Point.TURN_LEFT):
			##TODO: Implement print to voice
			logging.debug('Turn left!')
			pass

		elif (status is Point.TURN_RIGHT):
			##TODO: Implement print to voice
			logging.debug('Turn right!')
			pass

		else:
			## Oops uncaught feedback 
			logging.warn('Oops, did we account for all feedback flags?')
			pass

		pass 


	def tick(self, debug=False):
		"""Tick function executed every run cycle, called by #run
		Param:
			debug: If False, do not not update position from server 
			Instead do dependency injection manually.
		"""
		self.getPos() if (debug is False) else True
		self.feedbackCorrection()
		pass


	def run(self):
		"""Main function for daemon
		"""
		while(True):
			tick()
			time.sleep(3)
		pass























