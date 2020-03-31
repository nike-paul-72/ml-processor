from abc import abstractmethod, ABC, ABCMeta

class apiShim(ABC):

	@abstractmethod
	def __init__(self):
		pass

	@abstractmethod
	def loadData(self):
		pass


	@property
	@abstractmethod
	def dataSet(self):
		pass