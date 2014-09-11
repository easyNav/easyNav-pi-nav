#!/usr/bin/python 

import json
import logging

from numpy import linalg
import numpy

class Point(object):


	# Private variables


	# "x" : 0, "y": 0, "z": 0 


	def __init__(self, jsonPt):
		"""Creates a point, from a JSON-style string. 

		Args: 
			jsonPt: A JSON-style string to parse.  Must be of the ODM format specified 
			by easyNav doc.

		Returns:
			None

		Raises:
			None

		"""

		# internal variables --------------
		self.__model = {
			"location" : 0,
			"orientation" : 0,
			"name" : "",
			"SUID" : "",
			"key" : ""
		}
		#----------------------------------

		super(Point, self).__init__()
		data = json.loads(jsonPt)[0]
		self.__model["name"] = data.get("name")
		self.__model["orientation"] = data.get("orientation", 0)
		self.__model["loc"] = json.loads(data.get("loc"))
		self.__model["SUID"] = data.get("SUID")
		self.__model["id"] = data.get("id")

		# convert strings to numeric
		for key in self.__model["loc"]:
			self.__model["loc"][key] = float(self.__model["loc"][key])

		if type(self.__model["orientation"]) is str:
			self.__model["orientation"] = float(self.__model["orientation"])
		return


	def __str__(self):
		""" String literal of a point. 
		Args: 
			None 

		Returns: 
			None 

		Raises:
			None
		"""
		pass


	def toJSON(self):
		return json.dumps(self.__model, ensure_ascii=True)


	def loc(self):
		""" Returns the location of the point, as a dictionary
		"""
		logging.info(self.__model["loc"]["y"])
		return self.__model["loc"]

	def distTo(self, targetPt):
		""" Returns the distance to a point. 
		Args:
			None 

		Returns:
			None

		Raises:
			None
		"""
		loc_a = self.loc()
		loc_b = targetPt.loc()

		a = numpy.array((loc_a['x'], loc_a['y'], loc_a['z']))
		b = numpy.array((loc_b['x'], loc_b['y'], loc_b['z']))
		dist = linalg.norm(a - b)
		return dist


	def angle(self):
		"""Returns the orientation of the point, with respect to North
		"""
		return self.__model['orientation']


	def angleTo(self, targetPt):
		"""Returns the orientation of the point, with respect to another point.  
		Measurement given from north.
		"""
		loc_a = self.loc() 
		loc_b = targetPt.loc() 

		cX = loc_b['x'] - loc_a['x']
		cY = loc_b['y'] - loc_a['y']

		theta = numpy.arctan(abs(cX / cY))

		if ( (cX > 0) and (cY > 0) ):
			theta = theta

		elif ( (cX > 0) and (cY < 0) ):
			theta = numpy.pi - theta

		elif ( (cX < 0) and (cY < 0) ):
			theta = numpy.pi + theta

		else:
			theta = 2 * numpy.pi - theta

		return theta


	def near(self, targetPt, threshold):
		""" Determines if point is near target
		"""
		distance = self.distTo(targetPt)
		return (distance < threshold)


	def feedback(self, targetPt, threshold):
		pass

	def nearPath(self, pt1, pt2, threshold):
		pass



