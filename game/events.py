

class Decision:
	def __init__(self, name):
		self.name = name

		self.text = "text"
		self.options = ["choice 1", "choice 2", "choice 3"]
		self.outcomes = ["this happened", "that happened", "something else"]
		self.impacts = [[1,1,1], [0,0,0], [0,0,0]] # [food, population, territory]

