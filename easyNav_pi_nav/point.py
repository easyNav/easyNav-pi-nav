#!/usr/bin/python 

import json
import logging

from numpy import linalg
import numpy

class Point(object):


	# proximity enumeration constants
	REACHED, FAR, MOVE_FORWARD, ALIGNED, TURN_LEFT, TURN_RIGHT = range(6)



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
		The assumption is (0,0) starts from the top-left corner of screen, and
		increases downwards, rightwards.
		"""
		loc_a = self.loc() 
		loc_b = targetPt.loc() 

		cX = loc_b['x'] - loc_a['x']
		cY = loc_b['y'] - loc_a['y']

		# This means point is very near; do not bother!!
		if (cX == cY == 0):
			return 0


		# Watch for dividing by 0 case
		if (cY == 0):
			if (cX >= 0): 
				theta = numpy.pi / 2
				return theta
			else:
				theta = 3 / 2 * numpy.pi
				return theta

		# Do actual calculation
		theta = numpy.arctan(abs(cX / cY))

		if ( (cX > 0) and (cY < 0) ):
			theta = theta

		elif ( (cX > 0) and (cY > 0) ):
			theta = numpy.pi - theta

		elif ( (cX < 0) and (cY > 0) ):
			theta = numpy.pi + theta

		else:
			theta = 2 * numpy.pi - theta

		logging.debug('[angleTo, deg]:: {}'.format(numpy.rad2deg(theta)) )
		return theta


	def near(self, targetPt, threshold):
		""" Determines if point is near target
		"""
		distance = self.distTo(targetPt)
		if (distance < threshold):
			return Point.REACHED
		else:
			return Point.FAR
		pass


	def angleDiff(self, targetPt):
		""" Determines if point orientation is towards target
		positive: needs to move clockwise for correction to target
		negative: needs to move counter-clockwise for correction to target

		"""
		return self.angleTo(targetPt) - self.angle()


	def angleNear(self, targetPt, threshold):
		""" Determines if point orientation is aligned to target 
		"""
		angleCorrection = self.angleDiff(targetPt)
		if (angleCorrection < (-threshold) ):
			return Point.TURN_LEFT
		elif (threshold < angleCorrection):
			return Point.TURN_RIGHT
		else:
			return Point.ALIGNED
		pass



	def feedback(self, targetPt, thresholdDist, thresholdAngle):
		""" Returns feedback for route.
		Orientation takes precedence over distance to target, hence 
		this will be corrected first.
		"""
		response = {
			"status": Point.FAR,
			"distance": self.distTo(targetPt),
			"angleCorrection": self.angleDiff(targetPt)
		}

		turningCorrection = self.angleNear(targetPt, thresholdAngle)

		if (turningCorrection is Point.TURN_LEFT):
			response["status"] = Point.TURN_LEFT

		elif (turningCorrection is Point.TURN_RIGHT):
			response["status"] = Point.TURN_RIGHT

		elif ( self.near(targetPt, thresholdDist) is Point.FAR):
			response["status"] = Point.MOVE_FORWARD

		else:
			response["status"] = Point.REACHED

		return response


	def distToPath(self, point1, point2):
		""" Determines distance from line of path, given
		by two points.
		"""
		ptA = self.loc()
		ptB = point1.loc()
		ptC = point2.loc()
		
		vecAB = numpy.array([ ptB['x'] - ptA['x'], ptB['y'] - ptA['y'] ])
		vecV = numpy.array([ -(ptB['x'] - ptC['x']), ptB['x'] - ptC['y'] ])
		vecVUnit = numpy.multiply(1 / numpy.linalg.norm(vecV), vecV)
		result = numpy.linalg.norm( numpy.vdot(vecVUnit, vecAB) )
		return result



