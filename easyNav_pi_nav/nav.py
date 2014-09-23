
#!/usr/bin/python

import threading
import json
import requests
import logging
import time

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

	## Run Levels here
	RUNLVL_NORMAL = 0
	RUNLVL_WARNING_OBSTACLE = 1

	"""docstring for Nav"""
	def __init__(self):
		super(Nav, self).__init__()

		self.runLevel = Nav.RUNLVL_NORMAL
		## Sets the run interval, in terms of number of seconds
		self.RUN_INTERVAL = 5

		########## Private vars ##########
		self.__model = {
			'path': None,
			'currLoc': Point.fromParam()
		}

		## For multithreading
		self._threadListen = None
		self._active = True

		logging.info('Nav Daemon running.')


	def start(self):
		""" Start the daemon and run persistently.  Auto-retrieves new map in starting. 
		"""
		self.resetMap()
		self.updateMap()

		def runThread():
			while(self._active):
				self.tick()
				time.sleep(5)


		self._threadListen = threading.Thread(target=runThread)
		self._threadListen.start()
		logging.info('Nav: Started Daemon.')


	def stop(self):
		""" Stops the Nav daemon. 
		"""
		self._active = False
		self._threadListen.join()
		logging.info('Nav: Stopped Daemon.')


	def resetMap(self):
		"""Resets the map.
		"""
		r = requests.delete(Nav.HOST_ADDR + '/map')
		logging.info('Map deleted.')


	def updateMap(self):
		"""Updates the map on server. 
		"""
		r = requests.get(Nav.HOST_ADDR + '/map/update')
		logging.info('Map cleared.')


	def getPos(self):
		"""Gets the position from server, and updates internal 
		coordinates in Nav module.
		"""
		r = requests.get(Nav.HOST_ADDR + '/heartbeat/location')
		self.__model['currLoc'] = Point.fromJson(r.text)


	def getPathTo(self, pointId):
		"""Gets shortest path from point from current location, and updates internal
		path accordingly.
		"""
		r = requests.get(Nav.HOST_ADDR + '/map/goto/' + pointId)
		self.__model['path'] = Path.fromString(r.text)
		logging.info('Retrieved new path.')


	def path(self):
		"""Returns the current path of nav, as a Path instance.
		"""
		return self.__model['path']


	def loc(self):
		""" Returns the current location of user, as a Point instance. 
		"""
		return self.__model['currLoc']


	def exeLevelNorm(self):
		""" Called for run level RUNLVL_NORMAL.  Do not call externally.
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


	def exeLevelWarnObstacle(self):
		""" Called for run level RUNLVL_WARN_OBSTACLE.  Do not call externally.
		"""
		logging.warn('Near obstacle!!')
		pass


	def feedbackCorrection(self):
		"""Feedback correction control, called by Nav daemon automatically.
		"""
		if (self.runLevel == Nav.RUNLVL_NORMAL):
			self.exeLevelNorm()
		elif (self.runLevel == Nav.RUNLVL_WARNING_OBSTACLE):
			self.exeLevelWarnObstacle()

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




###################################
##  Main program defined here    ##
###################################

def runMain():
	""" Main function called when run as standalone daemon
	"""
	nav = Nav()
	nav.start()


if __name__ == '__main__':
	runMain()
























