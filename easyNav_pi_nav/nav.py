
#!/usr/bin/python

import threading
import json
import requests
import logging
import time
import smokesignal

from easyNav_pi_dispatcher import DispatcherClient
from easyNav_pi_nav import __version__

from path import Path 
from point import Point


class Nav(object):
	""" This is the Nav class, which handles navigation on the Raspberry Pi. 
	It retrieves remote location information and navigates to the point.  In addition,
	this class implements the REST API endpoints from the server. 
	"""

	HOST_ADDR = "http://localhost:1337"
	# HOST_ADDR = "http://192.249.57.162:1337"
	THRESHOLD_DIST = 100
	THRESHOLD_ANGLE = 20 * 0.0174532925

	## Run Levels here
	RUNLVL_NORMAL = 0
	RUNLVL_WARNING_OBSTACLE = 1


	def __init__(self):
		super(Nav, self).__init__()

		self.runLevel = Nav.RUNLVL_NORMAL
		## Sets the run interval, in terms of number of seconds
		self.RUN_INTERVAL = 3

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

		## For collision detection: lock navigation until ready
		self.collisionLocked = False
		self.obstacle = None

		## For pausing nav
		self.toPause = False

		logging.info('Nav Daemon running.')


	def start(self):
		""" Start the daemon and run persistently.  Auto-retrieves new map in starting. 
		"""
		## Disable pausing 
		self.toPause = False

		## Start inter-process comms
		self._dispatcherClient.start()

		# self.resetMap()
		# self.updateMap()

		def runThread():
			refTime = time.time()
			while(self._active):
				if ( (time.time() - refTime) > self.RUN_INTERVAL):
					refTime = time.time()
					self.tick()
					time.sleep(0.01)


		self._threadListen = threading.Thread(target=runThread)
		self._threadListen.start()

		self._dispatcherClient.send(9002, 'say', {'text': 'Started Navigation Daemon.'})
		logging.info('Nav: Started Daemon v%s.' % __version__)


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
			nodeFrom = json.loads(args.get('payload')).get('from')
			nodeTo = json.loads(args.get('payload')).get('to')
			if ((nodeTo == None) or (nodeFrom == None)):
				logging.error('Received no start / end nodes')
				return

			# DEPRECATED ------
			## reset current location
			# self.setPosBySUID(str(nodeFrom))
			# /DEPRECATED ------

			## Get new path
			self.getPathTo(nodeFrom, nodeTo)


		# @smokesignal.on('obstacle')
		# def onObstacle(args):
		# 	response = int(json.loads(args.get('payload')).get('status'))
		# 	if (response == 0):
		# 		self.obstacle = None
		# 		return # Do not set collision locked
		# 	elif (response == 1):
		# 		self.obstacle = 'FRONT'
		# 	elif (response == 2):
		# 		self.obstacle = 'LEFT'
		# 	elif (response == 3):
		# 		self.obstacle = 'RIGHT'

		# 	# If collision, set to true
		# 	self.collisionLocked = True


		@smokesignal.on('point')
		def onPoint(args):
			"""Update location based on interprocess posting
			by cruncher
			"""
			locInfo = json.loads(args.get('payload'))
			x = locInfo.get('x')
			y = locInfo.get('y')
			z = locInfo.get('z')
			angle = locInfo.get('ang')
			self.__model['currLoc'] = Point.fromParam(
				x=x, 
				y=y,
				z=z, 
				orientation=angle)
			# logging.info(
			# 	'[ NAV ] Internal pos is currently: (x=%s y=%s z=%s ang=%s)' % 
			# 	(x,y,z,angle) )


		@smokesignal.on('reset')
		def onReset(args):
			"""If navigation needs to be reset during routing, 
			use this 
			"""
			self._dispatcherClient.send(9002, 'say', {'text': 'Nav reset.'})
			self._resetNavParams() # Reset all navigation params and await new path
			logging.debug('Nav has been RESET.')


		@smokesignal.on('pause')
		def onPause(args):
			""" Pause navigation.  Useful for stairs / etc. 
			"""
			self.toPause = True
			self._dispatcherClient.send(9002, 'say', {'text': 'Nav paused.'})
			logging.debug('Nav is PAUSED.')


		@smokesignal.on('unpause')
		def onPause(args):
			""" Unpause navigation.  Useful for stairs / etc. 
			"""
			self.toPause = False
			self._dispatcherClient.send(9002, 'say', {'text': 'Nav resumed.'})
			logging.debug('Nav is RESUMED.')


	def setPosByXYZ(self, x=0, y=0, z=0, orientation=0):
		""" Set position by XYZ 
		"""
		_x = str(x)
		_y = str(y)
		_z = str(z)
		_orientation = str(orientation)
		try:
			r = requests.post(Nav.HOST_ADDR 
				+ '/heartbeat/location/?x=' + _x
				+ '&y=' + _y
				+ '&z=' + _z
				+ '&orientation=' + _orientation)
		except requests.exceptions.RequestException as e:
			logging.error('Oops!  Failed to set position by XYZ. Error: %s' % e)


	def setPosBySUID(self, suid=0):
		"""Set position on server, by SUID
		"""
		## Get the current old values (orientation workaround)
		# self.getPos()
		orientation = 0
		# orientation = (self.__model['currLoc'])['orientation']
		### TODO: Fix orientation bug

		## Get the SUID coordinates
		try:
			r = requests.get(Nav.HOST_ADDR + '/node/?SUID=' + str(suid))
		except requests.exceptions.RequestException as e:
			logging.error('Oops!  Failed to set position by SUID. Error: %s' % e)

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
		try:
			r = requests.delete(Nav.HOST_ADDR + '/map')
			logging.info('Map deleted.')
		except requests.exceptions.RequestException as e:
			logging.error('Oops!  Failed to delete map.  Is server connected?')


	def updateMap(self):
		"""Updates the map on server. 
		"""
		try:
			r = requests.get(Nav.HOST_ADDR + '/map/update')
			# self._dispatcherClient.send(9002, 'say', {'text': 'Map updated.'})
			logging.info('Map updated.')
		except requests.exceptions.RequestException as e:
			logging.error('Oops!  Failed to update map.  Is server connected?')


	def updateMapCustom(self, building, floor):
		"""Updates the map on server, with floor and building name.
		"""
		try:
			r = requests.get(Nav.HOST_ADDR + '/map/update?floor=' + floor + '&building=' + building)
			# self._dispatcherClient.send(9002, 'say', {'text': 'Map updated.'})
			logging.info('Map updated with building ' + building + ' at floor ' + floor)
		except requests.exceptions.RequestException as e:
			logging.error('Oops!  Failed to update map building=%s floor=%s.  Is server connected?' % (building, floor))


	def getPathTo(self, nodeFrom, nodeTo):
		"""Gets shortest path from point from current location, and updates internal
		path accordingly.
		"""
		try:
			self._resetNavParams()
			r = requests.get(Nav.HOST_ADDR + '/map/shortest/' + str(nodeFrom) + '/' + str(nodeTo) )
			self.__model['path'] = Path.fromString(r.text)
			self._dispatcherClient.send(9002, 'say', {'text': 'Retrieved new path.'})
			logging.info('Retrieved new path.')
		except requests.exceptions.RequestException as e:
			logging.info('Oops!  Failed to retrieve shortest path.  Is server connected?')


	def _resetNavParams(self):
		"""Reset nav flags and relevant info. 
		"""
		self._hasPassedStart = False 	# Variable to test if start pt has passed
		self.achievedNode = -1 			# Variable to test if previous point was the SAME point!!
		self.__model['path'] = None 	# Reset path


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
		logging.debug('>>>>>> Current target: %s' % path.get())
		feedback = path.isOnPath(pt, self.THRESHOLD_DIST, self.THRESHOLD_ANGLE)

		status = feedback['status']

		## Collision detection first
		if (self.collisionLocked):
			if (self.obstacle == None):
				# Unlock collisionLocked
				self._dispatcherClient.send(9002, 'say', {'text': 'Obstacle cleared.  Move forward!'})
				logging.debug('Obstacle cleared.  Move forward!')
				self.collisionLocked = False
				time.sleep(5)
				logging.debug('Time to clear obstacle has passed.')

			elif (self.obstacle == 'FRONT'):
				self._dispatcherClient.send(9002, 'say', {'text': 'Obstacle ahead.  Turn left or right!'})
				logging.debug('Obstacle ahead.  Turn left or right!')

			elif (self.obstacle == 'LEFT'):
				self._dispatcherClient.send(9002, 'say', {'text': 'Obstacle on the left!'})
				logging.debug('Obstacle on the left!')

			elif (self.obstacle == 'RIGHT'):
				self._dispatcherClient.send(9002, 'say', {'text': 'Obstacle on the right!'})
				logging.debug('Obstacle on the right!')

			# Do not execute below
			return 


		if (status is Point.REACHED):
			##TODO: Implement print to voice
			checkpointName = '' ## initialize it first

			if (path.isAtDest() is False): 


				if ((self._hasPassedStart == False) and (self.__model['path'].ref == 0)):
					self.__model['path'].next()
					self._hasPassedStart = True # So this does not trigger again at start
					self.achievedNode = 0

				# elif ( (self.__model['path'].ref != 0) and (self.achievedNode == int(self.__model['path'].ref - 1)) ):
				else:
					if (self.achievedNode == (self.__model['path'].ref - 1)):
						self.achievedNode = self.__model['path'].ref # Update to current node before incrementing
						##TODO: Fix this tomorrow
						try:
							currNode = self.__model['path'].get() ## Get current node
							checkpointName = currNode.name()
						except:
							logging.error('Oops.  Invalid name?')
						self.__model['path'].next()

				## Store the last value, i.e. 'delay'

				self._dispatcherClient.send(9002, 'say', {'text': 'Checkpoint ' + checkpointName + ' reached!'})
				logging.debug('checkpoint reached!')
			else:
				self._dispatcherClient.send(9002, 'say', {'text': 'Destination ' + checkpointName + ' reached!'})
				self._resetNavParams() # Reset all navigation params and await new path
				logging.debug('Reached destination, done!')
			pass

		elif (status is Point.MOVE_FORWARD):
			self._dispatcherClient.send(9002, 'say', {'text': 'Move forward!'})
			logging.debug('move forward!')
			pass

		elif (status is Point.OUT_OF_PATH):
			self._dispatcherClient.send(9002, 'say', {'text': 'Out of path!'})
			logging.debug('Out of path!')
			## DEPRECATED --------------------------------
			# self.getPathTo( self.path().dest().name() )
			## /DEPRECATED --------------------------------
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

		# print ('--------------curr node--------', self.__model['path'].ref)

		# print 'VAL ACHIEVED--------------------', self.achievedNode
		# print 'VAL TARGETED--------------------', self.__model['path'].ref


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
		if (self.toPause == False):
			self.feedbackCorrection()
			# self.getPos() if (debug is False) else True




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
























