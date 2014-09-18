
#!/usr/bin/python

from point import Point
import json
import logging


class Path(object):

	"""docstring for Nav"""
	def __init__(self, args):
		super(Path, self).__init__()
		self.nodes = args['nodes']
		self.ref = 0
		return

	@classmethod
	def fromPoints(cls, pointList):
		args = {
			'nodes': pointList
		}
		return cls(args)


	@classmethod
	def fromString(cls, inputString):
		data = json.loads(inputString)
		args = {
			'nodes': []
		}
		for node in data:
			args['nodes'].append(Point.fromJson(json.dumps(node)))
		return cls(args)


	def next(self):
		if ( (len(self.nodes) - 2) != self.ref ):
			self.ref += 1
		return self


	def prev(self):
		if (self.ref > 0 ):
			self.ref -= 1
		return self


	def length(self):
		return len(self.nodes)


	def get(self):
		return self.nodes[self.ref]


	def isNear(self):
		## TODO: implement this
		pass


