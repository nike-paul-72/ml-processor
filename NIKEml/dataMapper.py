import pandas as pd
import sys, os, re
from os import path
from netaddr import IPNetwork, IPAddress
import urllib.request
import json
from datetime import datetime

class dataMapper():
	def __init__(self, vmdata, padata):
		self.vmdata = vmdata
		self.padata = padata

	def getPADetail(self, IP):
		results = {
			"subnets":[],
			"zones":[],
			"locations":[],
			"access":"Unknown"
		}
		padata = self.padata
		for i in padata.index:
			subNet = padata["Subnet"][i]
			if IPAddress(IP) in IPNetwork(subNet):
				# print("Match! {0} is in {1}".format(IP, subNet))
				results["subnets"].append(padata["Subnet"][i])
				results["zones"].append(padata["Zone"][i])
				results["locations"].append(padata["Location"][i])
				results["access"] = "External" if ("EXT" in padata["Zone"][i] or "DMZ" in  padata["Zone"][i]) else "Internal"
		return results

	def mapData(self):
		print("[+] {0} - {1}".format(datetime.now(), "Starting parallel mapper"))
		for i in self.vmdata.index:
			ipAddress = self.vmdata["ip_address"][i]
			paDetails = self.getPADetail(ipAddress)
			self.vmdata.at[i,'access'] = paDetails.get("access")
			self.vmdata.at[i,'subnet'] = ", ".join(paDetails.get("subnets"))
			self.vmdata.at[i,'location'] = ", ".join(paDetails.get("locations"))
			self.vmdata.at[i,'zone'] =", ".join(paDetails.get("zones"))
		results = "Processed {0} records".format(i)
		print("[+] {0} - {1}".format(datetime.now(), results))