#!/usr/bin/env python
# coding: utf-8
# Authors: Matt Harlos, Paul Vilevac
# Last Updated: 2019-01-12
import pickle, os, settings, re, time, threading, psutil
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


class nikeVMlearn:
	# Some utility functions
	def __init__(self):
		self.DATA_PATH = os.getenv("data_path")
		self.SHOW_BAR =  "True" in os.getenv("show_bar")  #Do this so as to not risk casting blank to bool, works if empty, False, or 
		logger.log("Initiating nikeVMPredict with data path: {0}".format(self.DATA_PATH))


	def loadDataForLearning(self):
		self.df = pd.read_excel(os.path.join(DATA_PATH,"ML_Label_Results.xlsx"))
		self.df = self.df.drop(['Unnamed: 0'], axis=1)
		self.df = self.df.dropna(subset=['Feature'])
		logger.log("Feature Counts:\n {0}".format(self.df.Feature.value_counts(dropna=False)))

	def runLearning(self):
		self.loadDataForLearning()
		startTime = datetime.now()
		features = self.df
		features = features.dropna(subset=['Feature'])
		logger.log("Converting Labeled Data to Numpy Array")
		labels = np.array(features['Feature'])
		features= features.drop('Feature', axis = 1)
		feature_list = list(features.columns)
		features = features.fillna(0)
		features = np.array(features)
		logger.log("Splitting data for training")
		train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size = 0.25, random_state = 42)
		logger.log("Training the model against training data")
		rf = RandomForestClassifier(n_estimators = 1000, random_state = 42)
		rf.fit(train_features, train_labels)
		logger.log("Making predictions against testing data")
		predictions = rf.predict(test_features)
		errors = abs(predictions - test_labels)
		logger.log('Mean Absolute Error:', round(np.mean(errors), 2))
		logger.log("Accuracy Score : {0}".format(accuracy_score(test_labels,predictions)))
		self.score = accuracy_score(test_labels,predictions)
		logger.log("Persisting Model")
		pickle.dump(rf, open("classifierModel3.p", "wb" ))
		pickle.dump(feature_list, open("feature_list.p", "wb"))
		logger.log("Done")
		logger.log("Loading our data took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))