
#!/usr/bin/python

import multiprocessing
import unirest
import json
import requests

from path import Path 
from point import Point


class Nav(object):

	HOST_ADDR = "http://localhost:1337"

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
		pass


	def path(self):
		"""Returns the current path of nav, as a Path instance.
		"""
		return self.__model['path']


	def loc(self):
		""" Returns the current location of user, as a Point instance. 
		"""
		return self.__model['currLoc']






















