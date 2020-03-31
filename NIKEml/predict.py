#!/usr/bin/env python
# coding: utf-8
# Authors: Matt Harlos, Paul Vilevac
# Last Updated: 2019-01-12
import pickle, os, settings, re, time, threading, psutil, gc
import pandas as pd
import numpy as np
from progress.bar import Bar
from sklearn.tree import export_graphviz
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from NIKEutil.logger import logger
from os import path
from datetime import datetime




class nikeVMpredict:
	def __init__(self):
		self.DATA_PATH = os.getenv("data_path")
		# #self.SHOW_BAR =  "True" in os.getenv("show_bar")  #Do this so as to not risk casting blank to bool, works if empty, False, or 
		# logger.log("Initiating model with data path: {0}".format(self.DATA_PATH))

	def loadDataForPredicting(self):
		startTime = datetime.now()
		self.df = pd.read_parquet(os.path.join(self.DATA_PATH,"encoded_mapped_data.parquet"))
		logger.log("Loading our data took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def loadDataFromMapping(self):
		startTime = datetime.now()
		self.finaldf = pd.read_parquet(os.path.join(self.DATA_PATH,"vmtopamapped.parquet"))
		logger.log("Loading our data took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def saveDataFromPredicting(self):
		startTime = datetime.now()
		outputFile = os.path.join(self.DATA_PATH,"predict_results.parquet")
		self.df.to_parquet(outputFile)
		logger.log("Saving our data to {0} took: {1}".format(outputFile, logger.getElapsedTime(startTime,datetime.now())))

	def saveMergedResults(self):
		startTime = datetime.now()
		outputFile = os.path.join(self.DATA_PATH,"final_results.csv")
		self.finaldf.to_csv(outputFile)
		logger.log("Saving our data to {0} took: {1}".format(outputFile, logger.getElapsedTime(startTime,datetime.now())))


	def runPredictions(self):
		self.loadDataForPredicting()
		logger.log("Running predictions")
		startTime = datetime.now()
		model = pickle.load(open("classifierModel3.p", "rb" ))
		feature_list = pickle.load(open("feature_list.p", "rb"))
		df_features = list(self.df.columns)
		for feature in df_features:
			if feature in feature_list:
				continue
			else:
				logger.log("Feature {0} is not in the model feature list. It will be dropped".format(feature))
				self.df = self.df.drop([feature], axis=1)
		predictions = model.predict(self.df)
		logger.log("Made {0} predictions on {1} rows with {2} features".format(len(predictions), len(self.df), len(self.df.columns)))
		logger.log("Creating predictions from our data took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		logger.log("Adding predictions back to original un-encoded data")
		self.saveDataFromPredicting()
		self.df = None 
		gc.collect()
		logger.log("Load pa to vm mapped, attach preductions, save to merged result")
		startTime = datetime.now()
		self.loadDataFromMapping()
		self.finaldf["predictions"] = predictions #
		self.saveMergedResults()
		logger.log("Saving merged results took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))



