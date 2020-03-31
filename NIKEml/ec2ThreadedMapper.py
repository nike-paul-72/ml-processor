import pandas as pd
import os, settings
import numpy as np
from multiprocessing import Pool
from NIKEml.dataMapper import dataMapper
import psutil
from datetime import datetime
from datetime import timedelta
from NIKEutil.logger import logger

class nikeThreadedMapper:
	DATA_PATH = "" 

	def __init__(self):
		self.DATA_PATH = os.getenv("data_path")

	def saveParquet(self, dataSet, output_file):
		dataSet.to_parquet(output_file);

	def parallelize_dataframe(self, df, func):
		num_cores = psutil.cpu_count(logical=True) #number of cores on your machine
		threads_per_core = 1 #number of partitions to split dataframe
		workers =num_cores * threads_per_core # How many parititions and threads to parallelize the work
		logger.log("Threads per Core count: {0} Core Count: {1} Total Workers: {2}".format(threads_per_core, num_cores, workers))
		df_split = np.array_split(df, workers)
		pool = Pool(workers)
		df = pd.concat(pool.map(func, df_split))
		pool.close()
		pool.join()
		return df

	# Note, this function will be called by the pool parallizer
	def mapData(self, data):
		pafilepath = os.path.join(self.DATA_PATH,"paloalto.parquet")
		logger.log("Reading PA data from {0}".format(pafilepath))
		paZones = pd.read_parquet(pafilepath, engine='pyarrow') # Load a copy of the PA data 
		mapper = dataMapper(data,paZones) # Init the mapper passing the passed data segment and pa data
		mapper.mapData(); # Call the map data function
		return mapper.vmdata # Return the data

	def runMapper(self):
		logger.log("Starting mapping process")
		startTime = datetime.now()
		vmfilepath = os.path.join(self.DATA_PATH,"vmVulnerabilities.parquet")
		logger.log("Reading VM data from {0}".format(vmfilepath))
		vmVulns = pd.read_parquet(vmfilepath, engine='pyarrow')
		logger.log("Initiating parallel mapper")
		results = self.parallelize_dataframe(vmVulns,self.mapData)
		logger.log("Mapping cmpleted")
		resultsfilepath = os.path.join(self.DATA_PATH,"vmtopamapped.parquet")
		logger.log("Writing Results to: {0}".format(resultsfilepath))
		self.saveParquet(results, resultsfilepath)
		logger.log("Completed Processing")
		logger.log("Data Mapping took: {0}".format(logger.getElapsedTime(startTime, datetime.now())))
