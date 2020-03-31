#!/usr/bin/env python
# coding: utf-8
# Authors: Paul Vilevac
# Last Updated: 2019-01-12

import os, settings, re, time, threading, psutil
from NIKEutil.logger import logger
from os import path
from datetime import datetime
from NIKEutil.checkfiles import fileChecker
from NIKEml.tasks import *
from NIKEml.taskDefinitions import taskDefinitions

class statusResult:
	state = "";
	files = {};
	result_text = "";

	def __init__(self, state="", files=[], result_text=""):
		self.state = state
		self.files = files
		self.result_text = result_text


class nikeMLStatus():
	def __init__(self):
		self.DATA_PATH = os.getenv("data_path")

	def getStatus(self):
		# Get file details
		checker = fileChecker()
		logger.log("Getting ml system status")
		ml_files = []
		for task_id in taskDefinitions.keys():
			files = taskDefinitions[task_id]["output_files"]
			# print("\n".join(files))
			ml_files.extend(files)
		# ml_files = ["paloalto.parquet","vmVulnerabilities.parquet","vmtopamapped.parquet","encoded_mapped_data.parquet","final_results.csv","ML_Label_Results.xlsx"]
		files = checker.getDataFileDetails(self.DATA_PATH, ml_files)
		results = list()
		for key in files.keys():
			file_details = files[key]
			if(file_details["needs_refreshed"]):
				results.append("{0} is missing or needs refreshed.".format(key))

		## Recode to use task definitions, check for thread name, if so, add user readable name to is runnning list

		id2name = dict([(th.name,th) for th in threading.enumerate()])
		for task_id in taskDefinitions.keys():
			thread = taskDefinitions[task_id]["thread_name"]
			if thread in id2name.keys():
				results.append("{0} process is currently running".format(taskDefinitions[task_id]["cname"]))

		if len(results) == 0:
			results.append("Files are current, no threads running.")

		return statusResult("Status", files, ",".join(results))