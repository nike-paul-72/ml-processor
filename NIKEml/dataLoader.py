from NIKEml.datashims.apiShimBaseClass import apiShim
import pyarrow
import os, settings
from NIKEutil.logger import logger
from datetime import datetime


class nikeDataLoader:
	def __init__(self):
		self.DATA_PATH = os.getenv("data_path")
		logger.log("Initiating Data Loader with data path: {0}".format(self.DATA_PATH))

	def loadShim(self, shimPackage, shimModule, shimClass):
		module = "{0}.{1}".format(shimPackage, shimModule)
		logger.log(f"Loading module name {module}")
		mod = __import__(module, fromlist=[shimClass])
		classDef = getattr(mod, shimClass)
		logger.log("Creating an instance of {1}.{2} ".format(shimClass, shimPackage, shimModule))
		shimInstance = classDef()

		return shimInstance


	def getShimList(self, directory):
		shims = []
		for file in os.listdir(directory):
			if file.endswith(".py") and file.find("BaseClass") == -1:
				shims.append(file)
		return shims


	def saveJson(self, dataSet, output_file):
		dataSet.to_json(output_file, orient='records');
		logger.log("Saved data to {0}".format(output_file))

	def saveParquet(self, dataSet, output_file):
		dataSet.to_parquet(output_file);
		logger.log("Saved data to {0}".format(output_file))

	def saveCSV(self, dataSet, output_file):
		dataSet.to_csv(output_file, index = None, header=True);
		logger.log("Saved data to {0}".format(output_file))

	def getOutputFileName(self, path, shimName, extension):
		filename = "{0}.{1}".format(shimName.replace('shim_',''), extension)
		return os.path.join(path, filename)


	def getData(self):
		path = self.DATA_PATH
		shimFolder = os.path.join(os.getcwd(),"NIKEml", "datashims")
		logger.log(f"Data Shim Path {shimFolder}")
		shimFiles = self.getShimList(shimFolder)
		logger.log(f"{shimFiles}")
		shims = dict()
		for shimFile in shimFiles:
			shimName = os.path.splitext(shimFile)[0]
			shims[shimName] = self.loadShim("NIKEml.datashims", shimName, "dataShim")
		logger.log("Loaded {0} shims".format(len(shims)))
		for shimName in shims:
			logger.log("Loading data in shim {0}".format(shimName))
			try:
				startTime = datetime.now()
				shims[shimName].loadData()
				logger.log("{0} records loaded".format(len(shims[shimName].dataSet)))
				# Save to JSON
				if(shims[shimName].dataSet.size >0):
					prqName = self.getOutputFileName(path,shimName,"parquet")
					self.saveParquet(shims[shimName].dataSet,prqName)
					logger.log("Completed loading in {0}".format(logger.getElapsedTime(startTime,datetime.now())))
				else:
					print("Data not loaded, nothing to save")
			except Exception as inst:
				logger.log(inst.args)     # arguments stored in .args
				logger.log(inst)          # __str__ allows args to be printed directly,

