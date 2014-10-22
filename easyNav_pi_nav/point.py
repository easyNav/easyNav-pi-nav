#!/usr/bin/python 

import json
import logging

from numpy import linalg
from math import fmod
import numpy

class Point(object):


	# proximity enumeration constants
	REACHED, FAR, OUT_OF_PATH, MOVE_FORWARD, ALIGNED, TURN_LEFT, TURN_RIGHT = range(7)



	# "x" : 0, "y": 0, "z": 0 


	def __init__(self, inputDict):
		"""Creates a point, from a dictionary. 
			To instantiate, do something like:
			
				pt = Point.fromJson(jsonStringHere)

		Args: 
			jsonPt: A JSON-style string to parse.  Must be of the ODM format specified 
			by easyNav doc.

		Returns:
			None

		Raises:
			None

		"""
		self.__model = {
			"loc" : inputDict["loc"],
			"orientation" : inputDict["orientation"],
			"name" : inputDict["name"],
			"SUID" : inputDict["SUID"],
			"id" : inputDict["id"]
		}

		# super(Point, self).__init__()
		return


	@classmethod
	def fromParam(cls, x=0, y=0, z=0, orientation=0, name="", suid="", id=""):
		""" Easy method to create points for testing.
		"""
		result = {}
		result["name"] = name
		result["orientation"] = orientation
		result["loc"] = {
			"x" : x,
			"y" : y, 
			"z" : z
		}
		result["SUID"] = suid
		result["id"] = id
		return cls(result)



	@classmethod
	def fromJson(cls, jsonPt):
		""" Creates a point, from a JSON.
		"""
		# Ensure all data is a single JSON element
		tmpData = json.loads(jsonPt)
		if type(tmpData) is list:
			data = tmpData[0]
		else:
			data = tmpData

		result = {}
		result["name"] = data.get("name")
		result["orientation"] = data.get("orientation", 0)

		tempLoc = data.get('loc')
		if type(tempLoc) is dict:
			result["loc"] = tempLoc
		else:
			result["loc"] = json.loads(str(data.get("loc")))
		result["SUID"] = data.get("SUID")
		result["id"] = data.get("id")

		# convert strings to numeric
		for key in result["loc"]:
			result["loc"][key] = float(result["loc"][key])

		if (type(result["orientation"]) is unicode):
			result["orientation"] = float(result["orientation"])
		elif (type(result["orientation"]) is str):
			result["orientation"] = float(result["orientation"])

		return cls(result)



	def __str__(self):
		""" String literal of a point. 
		Args: 
			None 

		Returns: 
			None 

		Raises:
			None
		"""
		return str(self.__model)


	def toJSON(self):
		return json.dumps(self.__model, ensure_ascii=True)


	def name(self):
		return self.__model["name"]


	def suid(self):
		return self.__model["SUID"]


	def loc(self):
		""" Returns the location of the point, as a dictionary
		"""
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
		theta = 0.0 				## init as float

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
				theta = 1.5 * numpy.pi
				return theta

		## Fix faulty case where difference in X coords is 0.
		if (cX == 0):
			if (cY >= 0): 
				theta = numpy.pi
				return theta
			else:
				theta = 0
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

		# logging.debug('[angleTo, deg]:: {}'.format(numpy.rad2deg(theta)) )
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

		Result normalized to -pi < theta <= pi.

		"""
		result = fmod(self.angleTo(targetPt) - self.angle(), 2 * numpy.pi)
		if (result > numpy.pi):
			return result - 2 * numpy.pi 
		else:
			return result


	def angleNear(self, targetPt, threshold):
		""" Determines if point orientation is aligned to target 
		"""
		angleCorrection = self.angleDiff(targetPt)
		logging.debug(angleCorrection)
		if (angleCorrection < (-threshold) ):
			return Point.TURN_RIGHT
		elif (threshold < angleCorrection):
			return Point.TURN_LEFT
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

		If return value is -1, then identitcal points are used and
		hence result is invalid.

		The vector formula imeplented from 
		http://en.wikipedia.org/wiki/Distance_from_a_point_to_a_line 
		"""
		## TODO: Test and fix this function.
		if point1.isEqualXYZ( point2 ):
			return -1 

		pt = self.loc()
		ptA = point1.loc()
		ptB = point2.loc()

		vecAB = numpy.array([
			ptB['x'] - ptA['x'],
			ptB['y'] - ptA['y']
		 ])
		vecUnitAB = numpy.multiply( 1 / numpy.linalg.norm(vecAB), vecAB )

		vecA = numpy.array([
			ptA['x'],
			ptA['y']
		])

		vecP = numpy.array([
			pt['x'],
			pt['y']
		])

		part1 = numpy.vdot ( (vecA - vecP), vecUnitAB )
		vecResult = (vecA - vecP) - (part1 * vecUnitAB)
		result = numpy.linalg.norm(vecResult)
		return result


	def isEqual(self, point):
		""" Determines if another point is equal, in value,
		to the current point. 
		"""
		model = self.__model.pop("id", None)
		model2 = point.__model.pop("id", None)

		return cmp(model, model2) == 0


	def isEqualXYZ(self, point):
		""" Determines if another point is equal, in terms of coordinates,
		to the current point. 
		"""
		x = self.loc()['x'] == point.loc()['x']
		y = self.loc()['y'] == point.loc()['y']
		z = self.loc()['z'] == point.loc()['z']

		return x & y & z


	def nearPath(self, point1, point2, threshold):
		""" Determines if near a path. 
		"""
		return self.distToPath(point1, point2) <= threshold


	def feedbackPath(self, point1, point2, thresholdDist, thresholdAngle):
		""" Gives feedback on path.  The destination point is point2.
		"""
		## Check for valid line first
		if point1.isEqualXYZ(point2):
			return -1
		## Check distance from path.  If too far, then is off track.
		if (self.nearPath(point1, point2, thresholdDist) == False):
			return {
				"status": Point.OUT_OF_PATH,
				"distance": self.distTo(point2),
				"angleCorrection": self.angleDiff(point2)
			}

		## Else do normal feedback correction on point2.
		return self.feedback(point2, thresholdDist, thresholdAngle)


