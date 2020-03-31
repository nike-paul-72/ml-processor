#!/usr/bin/env python
# coding: utf-8
# Authors: Matt Harlos, Paul Vilevac
# Last Updated: 2019-01-12

import os, settings, re, time, threading, psutil
import pandas as pd
import numpy as np
from dataConfig import catList
from dataConfig import importantPorts
from progress.bar import Bar
from NIKEutil.logger import logger
from os import path
from datetime import datetime


class nikeVMengineer:
	def __init__(self):
		self.DATA_PATH = os.getenv("data_path")
		logger.log("Initiating model with data path: {0}".format(self.DATA_PATH))

	def engineerFeatures(self):
		startTime = datetime.now()
		logger.log("Starting feature engineering")
		self.loadDataForFeatureEngineering()  # Instrumented
		self.dropFeatures() # Instrumented
		self.createVulnCategoryFeatures() # Tuned
		self.sortVulnsIntoFeaturesTuned() # Tuned
		self.locOStoFeatures() # Optimal, cuts time from 18+ mins ~ 30 seconds
		self.runOneHotEncoding()
		self.locExploitToFeatures() # Optimal, cuts time from 18+ mins ~ 30 seconds
		self.locMalwareData()
		self.createImportantPortFeatures()
		self.locPortData()
		self.saveEncodedMappedData()
		logger.log("Completed feature engineering. Processing took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

			# Updated to reg path from parent
	def loadDataForFeatureEngineering(self):
		startTime = datetime.now()
		self.df = pd.read_parquet(os.path.join(self.DATA_PATH,"vmtopamapped.parquet"))
		self.finaldf = self.df
		logger.log("Loading our data took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def loadDataForReporting(self):
		startTime = datetime.now()
		self.df = pd.read_parquet(os.path.join(self.DATA_PATH,"encoded_mapped_data.parquet"))
		logger.log("Loading our data took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def dropFeatures(self):
		startTime = datetime.now()
		self.df = self.df.drop(['ip_address', 'asset_id', 'host_name', 'lastscandate',
					  "vuln_title", "subnet", "zone", "location"], axis=1)
		logger.log("Dropping features took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def createVulnCategoryFeatures(self):
		logger.log("Creating Features for Vuln Categories")
		startTime = datetime.now()
		bar = Bar("Creating Features for Vuln Categories ", max=len(catList))
		for each in catList:
			bar.next()
			catName = "CAT-{0}".format(each)
			self.df[catName] = 0
		bar.finish()
		logger.log("Creating Features for Vuln Categories Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def sortVulnsIntoFeaturesTuned(self):
		logger.log("Sorting Vulns into Categories - Tuned")
		startTime = datetime.now()
		df = self.df
		bar = Bar("Sorting Vulns into Categories", max=len(self.df))
		bar.next()
		for index in df.index:
			bar.next()
			cat = df["vuln_category"][index]
			parts = cat.split(",")
			for part in parts:
				try:
					thisPart = "CAT-{0}".format(part)
					if part in catList:
						df.at[index, thisPart] = 1 
				except Exception as e:
					logger.log("Missing Cat From Master List - {0}".format(part))
		bar.finish()
		logger.log("Setting vuln category features Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		self.df = df.drop(["vuln_category"], axis = 1)

	def locOStoFeatures(self):

		logger.log("DF loc to asssign OS features")
		df = self.df
		startTime = datetime.now()

		# And and initialize the columns 
		df["is_microsoft"] = 0 
		df["is_linux"] = 0
		df["is_network"] = 0 
		df["is_apple"] = 0 
		df["is_other"] = 0 
		
		# Use loc to sef based upon os description
		df.loc[df['os_description'].str.contains('microsoft',case=False,na=False),'is_microsoft'] = 1
		df.loc[df['os_description'].str.contains('linux|freebsd',regex=True,na=False, flags=re.IGNORECASE) ,'is_linux'] = 1
		df.loc[df['os_description'].str.contains('juniper|cisco|palo alto',regex=True,na=False, flags=re.IGNORECASE) ,'is_network'] = 1
		df.loc[ df['os_description'].str.contains('apple',case=False, na=False),'is_apple'] = 1
		df.loc[ ((df['is_microsoft'] == 0) & (df['is_linux'] == 0) & (df['is_network'] == 0 )  & (df['is_apple'] == 0)) ,'is_other'] = 1
		logger.log("Setting OS Features Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

		# Log results


		self.df = df
		self.df = self.df.drop("os_description", axis=1)

	def runOneHotEncoding(self):
		logger.log("Running one hot encoders")
		startTime = datetime.now()
		encodeFeatures = ["access", "cvss_access_vector", "cvss_authentication", "cvss_v3_attack_vector",
						  "cvss_v3_privileges_required", "cvss_v3_user_interaction", "credentialstatus"]
		bar = Bar("One Hot Encoding", max=len(encodeFeatures))
		for feature in encodeFeatures:
			bar.next()
			if "cvss_" in feature:
				dummies = pd.get_dummies(self.df[feature], prefix=feature)
			else:
				dummies = pd.get_dummies(self.df[feature])
			self.df = pd.concat([self.df, dummies], axis=1)
			self.df = self.df.drop(feature, axis = 1)
		bar.finish()
		logger.log("One Hot Encodding Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def locExploitToFeatures(self):
		logger.log("DF loc to asssign exploit features")
		df = self.df 
		startTime = datetime.now()
		df["exploit_count"] = 0
		df["has_windows_exploit"] = 0
		df["has_web_exploit"] = 0 
		df["has_remote_exploit"] = 0 
		df["has_metasploit_exploit"] = 0
		df["exploit_info"] = df["exploit_info"].fillna(value="NONE")

		# Use loc to create filter maps and populate flags
		df.loc[df['exploit_info'].str.contains('java|ssl|http',regex=True,na=False, flags=re.IGNORECASE) ,'has_web_exploit'] = 1
		df.loc[df['exploit_info'].str.contains('microsoft',case=False,na=False),'has_windows_exploit'] = 1
		df.loc[df['exploit_info'].str.contains('remote',case=False,na=False),'has_remote_exploit'] = 1
		df.loc[df['exploit_info'].str.contains('metasploit',case=False,na=False),'has_metasploit_exploit'] = 1
		df.loc[ (df['exploit_info'].str.count('NONE')==0) ,'exploit_count'] = 1 + df['exploit_info'].str.count("|")
		logger.log("Sorting Exploit Data Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		df = df.drop(["exploit_info"], axis=1)

		# Print Results

		self.df = df

	def locMalwareData(self):
		logger.log("Sorting Malware Data")
		startTime = datetime.now()
		# bar = Bar("Sorting Malware Data", max=len(self.df))
		self.df["malwarekit"] = 0
		self.df["malwarekit_info"] = self.df["malwarekit_info"].fillna(value="NONE")
		self.df.loc[(self.df['malwarekit_info'].str.count('NONE') == 0),'malwarekit'] = 1
		self.df = self.df.drop(["malwarekit_info"], axis=1)
		logger.log("Sorting Malware Data Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def createImportantPortFeatures(self):
		logger.log("Create Port Features")
		startTime = datetime.now()
		bar = Bar("Create Port Features", max=len(importantPorts))
		for port in importantPorts:
			bar.next()
			self.df[port] = 0
		bar.finish()
		logger.log("Creating Port Features Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def locPortData(self):
		logger.log("Setting important ports features (optimized)")
		startTime = datetime.now()
		bar = Bar("Setting Import Port Features", max=len(importantPorts))
		self.df["port"] = self.df["port"].fillna(0)
		for port_name in importantPorts:
			port = int(port_name.replace("port_",""))
			self.df.loc[(self.df['port'] == port),'port_name'] = 1
			bar.next
		bar.finish()
		logger.log("Setting important ports features (optimized) took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		self.df = self.df.drop(["port"],axis=1)

	def saveEncodedMappedData(self):
		startTime = datetime.now()
		encodedDataFile = os.path.join(self.DATA_PATH,"encoded_mapped_data.parquet")
		self.df.to_parquet(encodedDataFile)
		logger.log("Saving Encoded Data to: {0}".format(encodedDataFile))


	def generateEngineeringReport(self):
		self.loadDataForReporting()
		df = self.df
		logger.log("Total Vuln Records: {0}".format(df.shape[0]))
		logger.log("Total Web Vulns with exploits: {0}".format(df.loc[df["has_web_exploit"]>0].shape[0]))
		logger.log("Total Windows Vulns with exploits: {0}".format(df.loc[df["has_windows_exploit"]>0].shape[0]))
		logger.log("Total Vulns with Remote exploits: {0}".format(df.loc[df["has_remote_exploit"]>0].shape[0]))
		logger.log("Total Vulns with Metasploit exploits: {0}".format(df.loc[df["has_metasploit_exploit"]>0].shape[0]))
		logger.log("Total Vulns without exploits: {0}".format(df.loc[df["exploit_count"]>0].shape[0]))
		logger.log("Sum Vulns from Exploit_Count: {0}".format(df["exploit_count"].sum()))	

		logger.log("Total Microsoft Vulns: {0}".format(df.loc[df["is_microsoft"]>0].shape[0]))
		logger.log("Total Linux Vulns: {0}".format(df.loc[df["is_linux"]>0].shape[0]))
		logger.log("Total Network Devices Vulns: {0}".format(df.loc[df["is_network"]>0].shape[0]))
		logger.log("Total Apple Vulns: {0}".format(df.loc[df["is_apple"]>0].shape[0]))
		logger.log("Total Other OS Vulns: {0}".format(df.loc[df["is_other"] > 0].shape[0]))