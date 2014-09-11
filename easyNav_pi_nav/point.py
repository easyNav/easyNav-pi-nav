#!/usr/bin/python 

import json
import logging

from numpy import linalg

class Point(object):


	# Private variables

	__model = {
		"location" : 0,
		"orientation" : 0,
		"name" : "",
		"SUID" : "",
		"key" : ""
	}

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
		super(Point, self).__init__()
		data = json.loads(jsonPt)[0]
		self.__model["name"] = data.get("name")
		self.__model["orientation"] = data.get("orientation")
		self.__model["loc"] = json.loads(data.get("loc"))
		self.__model["SUID"] = data.get("SUID")
		self.__model["id"] = data.get("id")

		# convert strings to numeric
		for key in self.__model["loc"]:
			self.__model["loc"][key] = float(self.__model["loc"][key])
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
		loc_a = self.__model.loc
		loc_b = targetPt.loc
		a = (loc_a['x'], loc_a['y'], loc_a['z'])
		a = (loc_b['x'], loc_b['y'], loc_b['z'])
		dist = numpy.linalg.norm(a - b)
		return dist


	def angle(self, targetPt):
		pass 

	def near(self, targetPt, threshold):
		pass

	def feedback(self, targetPt, threshold):
		pass

	def nearPath(self, pt1, pt2, threshold):
		pass



