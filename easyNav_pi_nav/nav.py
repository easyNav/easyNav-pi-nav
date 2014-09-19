
#!/usr/bin/python

import multiprocessing


class Nav(object):

	"""docstring for Nav"""
	def __init__(self, arg):
		super(Nav, self).__init__()
		self.arg = arg
		jobs = []
		for i in range(5):
			p = multiprocessing.Process(target=self.worker)
			jobs.append(p)
			p.start()


	def worker(self):
		print 'Worker--------------------------------------------'
		return


	def area(self):
		return 2 + 3;
		

	def run(self):
		pass

	def stop(self):
		pass