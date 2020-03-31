#!/usr/bin/env python
# coding: utf-8

import pickle
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from dataConfig import catList
from dataConfig import importantPorts
import dataLoader
import VMtoPAMapper
from progress.bar import Bar

bar = Bar("Getting Data From Data Shims", max=1)
data = dataLoader.main()
mapper = VMtoPAMapper.main()
bar.next()
bar.finish()


bar = Bar("Loading Data", max=1) 
df = pd.read_parquet("shared_data/mappedData.parquet")
finaldf = df
bar.next()
bar.finish()


bar = Bar("Dropping Features", max=1)
df = df.drop(['ip_address', 'asset_id', 'host_name', 'lastscandate',
			  "vuln_title", "subnet", "zone", "location"], axis=1)
bar.next()
bar.finish()

bar = Bar("Creating Features for Vuln Categories ", max=len(catList))
for each in catList:
	bar.next()
	catName = "CAT-{0}".format(each)
	df[catName] = 0
bar.finish()


bar = Bar("Sorting Vulns into Categories", max=len(df))
for index, each in df.iterrows():
	bar.next()
	cat = each["vuln_category"]
	parts = cat.split(",")
	for part in parts:
		try:
			thisPart = "CAT-{0}".format(part)
			if part in catList:
				df.at[index, thisPart] = 1 
		except Exception as e:
			print("Missing Cat From Master List - {0}".format(part))
df = df.drop(["vuln_category"], axis = 1)
bar.finish()

bar = Bar("Sorting OS Descriptions into OS Features", max=len(df))
df["is_microsoft"] = 0 
df["is_linux"] = 0
df["is_network"] = 0 
df["is_apple"] = 0 
df["is_other"] = 0 
for index, row in df.iterrows():
	bar.next()
	os = str(row.os_description).lower()
	if "microsoft" in os:
		df.at[index, "is_microsoft"] = 1
	elif "linux" in os or "freebsd" in os:
		df.at[index, "is_linux"] = 1
	elif "juniper" in os or "palo alto" in os or "cisco" in os:
		df.at[index, "is_network"] = 1
	elif "apple" in os:
		df.at[index, "is_apple"] = 1
	else:
		df.at[index, "is_other"] = 1
df = df.drop("os_description", axis=1)
bar.finish()


encodeFeatures = ["access", "cvss_access_vector", "cvss_authentication", "cvss_v3_attack_vector",
				  "cvss_v3_privileges_required", "cvss_v3_user_interaction", "credentialstatus"]
bar = Bar("One Hot Encoding", max=len(encodeFeatures))
for feature in encodeFeatures:
	bar.next()
	if "cvss_" in feature:
		dummies = pd.get_dummies(df[feature], prefix=feature)
	else:
		dummies = pd.get_dummies(df[feature])
	df = pd.concat([df, dummies], axis=1)
	df = df.drop(feature, axis = 1)
bar.finish()

bar = Bar("Sorting Exploit Data", max=len(df))
df["exploit_count"] = 0
df["has_windows_exploit"] = 0
df["has_web_exploit"] = 0 
df["has_remote_exploit"] = 0 
df["has_metasploit_exploit"] = 0
df["exploit_info"] = df["exploit_info"].fillna(value="NONE")
for index, row in df.iterrows():
	bar.next()
	rawexploits = str(row["exploit_info"])
	if rawexploits == "NONE":
		df.at[index, "exploit_count"] = 0
		continue
	exploits = rawexploits.split("|")
	df.at[index, "exploit_count"] = len(exploits)
	for exploit in exploits:
		exploit = str(exploit).lower()
		if "microsoft" in exploit:
			df.at[index, "has_windows_exploit"] = 1
		if "java" in exploit or "ssl" in exploit or "http" in exploit:
			df.at[index, "has_web_exploit"] = 1
		if "remote" in exploit:
			df.at[index, "has_remote_exploit"] = 1
		if "metasploit" in exploit:
			df.at[index, "has_metasploit_exploit"] = 1
df = df.drop(["exploit_info"], axis=1)
bar.finish()

bar = Bar("Sorting Malware Data", max=len(df))
df["malwarekit"] = 0
df["malwarekit_info"] = df["malwarekit_info"].fillna(value="NONE")
for index, row in df.iterrows():
	bar.next()
	if not "NONE" in str(row["malwarekit_info"]):
		df.at[index, "malwarekit"] = 1
df = df.drop(["malwarekit_info"], axis=1)
bar.finish()

bar = Bar("Create Port Features", max=len(importantPorts))
for port in importantPorts:
	bar.next()
	df[port] = 0
bar.finish()

bar = Bar("Sorting Ports Into Important Ports", max=len(df))
df["port"] = df["port"].fillna(0)
for index, row in df.iterrows():
	bar.next()
	port = "port_{0}".format(int(row["port"]))
	if port in importantPorts:
		df.at[index, port] = 1
df = df.drop(["port"],axis=1)
df = df.drop(["Unknown"], axis=1)
bar.finish()

print("Saving Encoded Data")
df.to_parquet("shared_data/encoded_mapped_data.parquet")
print("Running Predictions")
model = pickle.load(open("classifierModel3.p", "rb" ))
predictions = model.predict(df)
print("Made {0} predictions on {1} rows with {2} features".format(len(predictions), len(df), len(df.columns)))
print("Adding predictions back to original un-encoded data")
finaldf["predictions"] = predictions
print("Predictions Counts")
print(finaldf.predictions.value_counts())
print("Saving Final Output")
finaldf.to_csv("shared_data/final_results.csv")
