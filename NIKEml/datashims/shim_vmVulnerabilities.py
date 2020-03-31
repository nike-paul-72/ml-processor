from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import pandas as pd
import ssl
import json
from NIKEml.datashims.apiShimBaseClass import apiShim
import os
from NIKEutil.logger import logger

class dataShim(apiShim):

	@property
	def dataSet(self):
		return self.__dataSet

	def __init__(self):
		pass

	def loadData(self):
		# vmurl - "https://nifi.vulnmanagment-prod.nikecloud.com:5000/data/getinventorylist"
		# vmurl = "https://nifi.ops-playground-test.nikecloud.com/nifi"
		baseurl = "https://nifi-vm.nike.com:5000/data/"
		vmurl = "{0}{1}".format(baseurl,"getVulnTableResults")
		logger.log("Using url {}".format(vmurl))
		req = Request(vmurl)
		try:
			if("https" in vmurl):
				ctx = ssl.create_default_context()
				ctx.check_hostname = False
				ctx.verify_mode = ssl.CERT_NONE
				response = urlopen(req, context=ctx)
			else:
				response = urlopen(req)
			parquet_data = response.read()
			fname = "tempfile.parquet.gzip"
			with open(fname, 'wb') as outfile:
				outfile.write(parquet_data)


			self.__dataSet = pd.read_parquet(fname, engine="pyarrow");
			os.remove(fname)
		except HTTPError as e:
		    logger.log('The server couldn\'t fulfill the request.')
		    logger.log('Error code: ', e.code)
		except URLError as e:
		    logger.log('We failed to reach a server.')
		    logger.log('Reason: ', e.reason)


