
#!/usr/bin/python

import threading
import json
import requests
import logging
import time
import smokesignal

from easyNav_pi_dispatcher import DispatcherClient

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

		## For interprocess comms 
		self.DISPATCHER_PORT = 9001
		self._dispatcherClient = DispatcherClient(port=self.DISPATCHER_PORT)

		## Attach event listeners upon instantiation (to prevent duplicates)
		self.attachEvents()

		logging.info('Nav Daemon running.')


	def start(self):
		""" Start the daemon and run persistently.  Auto-retrieves new map in starting. 
		"""
		## Start inter-process comms
		self._dispatcherClient.start()

		self.resetMap()
		self.updateMap()

		def runThread():
			while(self._active):
				self.tick()
				time.sleep(5)


		self._threadListen = threading.Thread(target=runThread)
		self._threadListen.start()

		self._dispatcherClient.send(9002, 'say', {'text': 'Started Navigation Daemon.'})
		logging.info('Nav: Started Daemon.')


	def stop(self):
		""" Stops the Nav daemon. 
		"""
		self._active = False
		self._threadListen.join()

		self._dispatcherClient.send(9002, 'say', {'text': 'Stopping Navigation Daemon.'})

		## Stop inter-process comms
		self._dispatcherClient.stop()

		logging.info('Nav: Stopped Daemon.')



	def attachEvents(self):
		"""Configure event callbacks to attach to daemon on start.

		All events must be a series of event functions.

		Do not call this externally!
		"""
		## clear all signals
		smokesignal.clear()

		@smokesignal.on('newPath')
		def onNewPath(args):
			logging.debug('Event triggered: Request for new path.')
			nodeFrom = args.get('from')
			nodeTo = args.get('to')
			if ((nodeTo == None) or (nodeFrom == None)):
				logging.error('Received no start / end nodes')
				return

			## reset current location
			self.setPosBySUID(str(nodeFrom))
			## Get new path
			self.getPathTo(nodeTo)


		@smokesignal.on('obstacle')
		def onObstacle(args):
			##TODO: Implement obstacle detection
			pass


	def setPosByXYZ(self, x=0, y=0, z=0, orientation=0):
		""" Set position by XYZ 
		"""
		_x = str(x)
		_y = str(y)
		_z = str(z)
		_orientation = str(orientation)
		r = requests.post(Nav.HOST_ADDR 
			+ '/heartbeat/location/?x=' + _x
			+ '&y=' + _y
			+ '&z=' + _z
			+ '&orientation=' + _orientation)


	def setPosBySUID(self, suid=0):
		"""Set position on server, by SUID
		"""
		## Get the current old values (orientation workaround)
		self.getPos()
		orientation = 0
		# orientation = (self.__model['currLoc'])['orientation']
		### TODO: Fix orientation bug

		## Get the SUID coordinates
		r = requests.get(Nav.HOST_ADDR + '/node/?SUID=' + str(suid))
		response = json.loads(r.text)


		## Invalid point exception
		if (response == []):
			logging.error('Oops.  No such SUID on server.')
			return

		response = response[0]
		loc = json.loads(response.get('loc'))
		
		## Set coordinates
		x,y,z = loc.get('x'), loc.get('y'), loc.get('z')
		self.setPosByXYZ(x,y,z, orientation)


	def resetMap(self):
		"""Resets the map.
		"""
		r = requests.delete(Nav.HOST_ADDR + '/map')
		logging.info('Map deleted.')


	def updateMap(self):
		"""Updates the map on server. 
		"""
		r = requests.get(Nav.HOST_ADDR + '/map/update')
		# self._dispatcherClient.send(9002, 'say', {'text': 'Map updated.'})
		logging.info('Map updated.')

	def updateMapCustom(self, building, floor):
		"""Updates the map on server, with floor and building name.
		"""
		r = requests.get(Nav.HOST_ADDR + '/map/update?floor=' + floor + '&building=' + building)
		# self._dispatcherClient.send(9002, 'say', {'text': 'Map updated.'})
		logging.info('Map updated with building ' + building + ' at floor ' + floor)


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
		r = requests.get(Nav.HOST_ADDR + '/map/goto/' + str(pointId))
		self.__model['path'] = Path.fromString(r.text)
		self._dispatcherClient.send(9002, 'say', {'text': 'Retrieved new path.'})
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
		## Return if no path set!
		if path == None:
			return
		logging.debug('Point: %s' % pt)
		logging.debug('Current target: %s' % path.get())
		feedback = path.isOnPath(pt, self.THRESHOLD_DIST, self.THRESHOLD_ANGLE)

		status = feedback['status']
		if (status is Point.REACHED):
			##TODO: Implement print to voice

			if (path.isAtDest() is False): 
				self.__model['path'].next()
				self._dispatcherClient.send(9002, 'say', {'text': 'Checkpoint reached!'})
				logging.debug('checkpoint reached!')
			else:
				self._dispatcherClient.send(9002, 'say', {'text': 'You have reached your destination!'})
				logging.debug('Reached destination, done!')
			pass

		elif (status is Point.MOVE_FORWARD):
			self._dispatcherClient.send(9002, 'say', {'text': 'Move forward!'})
			logging.debug('move forward!')
			pass

		elif (status is Point.OUT_OF_PATH):
			self._dispatcherClient.send(9002, 'say', {'text': 'Out of path!'})
			logging.debug('Out of path!')
			self.getPathTo( self.path().dest().name() )
			pass

		elif (status is Point.ALIGNED):
			##TODO: Implement print to voice
			# self._dispatcherClient.send(9002, 'say', {'text': 'Out of path!'})
			logging.debug('Point aligned!')
			pass

		elif (status is Point.TURN_LEFT):
			self._dispatcherClient.send(9002, 'say', {'text': 'Turn left!'})
			logging.debug('Turn left!')
			pass

		elif (status is Point.TURN_RIGHT):
			self._dispatcherClient.send(9002, 'say', {'text': 'Turn right!'})
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
		# TODO: Code warn obstacle stuff
		self._dispatcherClient.send(9002, 'say', {'text': 'Near obstacle!'})
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
























