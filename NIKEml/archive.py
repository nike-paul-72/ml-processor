### Code Archive
	### This has been replaced above
	def sortOsIntoOsFeatures(self):
		logger.log("Sorting OS Descriptions into OS Features")
		startTime = datetime.now()
		bar = Bar("Sorting OS Descriptions into OS Features", max=len(self.df))
		self.df["is_microsoft"] = 0 
		self.df["is_linux"] = 0
		self.df["is_network"] = 0 
		self.df["is_apple"] = 0 
		self.df["is_other"] = 0 
		# Can split and MF this
		for index, row in self.df.iterrows():
			bar.next()
			os = str(row.os_description).lower()
			if "microsoft" in os:
				self.df.at[index, "is_microsoft"] = 1
			elif "linux" in os or "freebsd" in os:
				self.df.at[index, "is_linux"] = 1
			elif "juniper" in os or "palo alto" in os or "cisco" in os:
				self.df.at[index, "is_network"] = 1
			elif "apple" in os:
				self.df.at[index, "is_apple"] = 1
			else:
				self.df.at[index, "is_other"] = 1
		self.df = self.df.drop("os_description", axis=1)
		bar.finish()
		df = self.df
		print("Total Vulns: {0}".format(df.shape[0]))
		print("Total Linux Vulns: {0}".format(df.loc[df["is_linux"]>0].shape[0]))
		print("Total Network Devices Vulns: {0}".format(df.loc[df["is_network"]>0].shape[0]))
		print("Total Apple Vulns: {0}".format(df.loc[df["is_apple"]>0].shape[0]))
		print("Total Other OS Vulns: {0}".format(df.loc[df["is_other"] > 0].shape[0]))
		logger.log("Sorting OS Features Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def sortExploitData(self):
		logger.log("DF Lpc to populate exploit feature")
		startTime = datetime.now()
		self.df["exploit_count"] = 0
		self.df["has_windows_exploit"] = 0
		self.df["has_web_exploit"] = 0 
		self.df["has_remote_exploit"] = 0 
		self.df["has_metasploit_exploit"] = 0
		self.df["exploit_info"] = self.df["exploit_info"].fillna(value="NONE")
		bar = Bar("Sorting Vulsn into Exploits", max=len(self.df))

		for index, row in self.df.iterrows():
			bar.next()
			rawexploits = str(row["exploit_info"])
			if rawexploits == "NONE":
				self.df.at[index, "exploit_count"] = 0
				continue
			exploits = rawexploits.split("|")
			self.df.at[index, "exploit_count"] = len(exploits)
			for exploit in exploits:
				exploit = str(exploit).lower()
				if "microsoft" in exploit:
					self.df.at[index, "has_windows_exploit"] = 1
				if "java" in exploit or "ssl" in exploit or "http" in exploit:
					self.df.at[index, "has_web_exploit"] = 1
				if "remote" in exploit:
					self.df.at[index, "has_remote_exploit"] = 1
				if "metasploit" in exploit:
					self.df.at[index, "has_metasploit_exploit"] = 1

		logger.log("Sorting Exploit Data Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

		df = self.df
		logger.log("Total Vulns Records: {0}".format(df.shape[0]))
		logger.log("Total Web Vulns with exploits: {0}".format(df.loc[df["has_web_exploit"]>0].shape[0]))
		logger.log("Total Windows Vulns with exploits: {0}".format(df.loc[df["has_windows_exploit"]>0].shape[0]))
		logger.log("Total Vulns with Remote exploits: {0}".format(df.loc[df["has_remote_exploit"]>0].shape[0]))
		logger.log("Total Vulns with Metasploit exploits: {0}".format(df.loc[df["has_metasploit_exploit"]>0].shape[0]))
		logger.log("Total Vulns without exploits: {0}".format(df.loc[df["exploit_count"]>0].shape[0]))
		logger.log("Sum Vulns from Exploit_Count: {0}".format(df["exploit_count"].sum()))

		self.df = self.df.drop(["exploit_info"], axis=1)

	# not ideal
	def createVulnCategoryFeatures_old(self):
		logger.log("Creating Features for Vuln Categories")
		startTime = datetime.now()
		bar = Bar("Creating Features for Vuln Categories ", max=len(catList))
		for each in catList:
			bar.next()
			catName = "CAT_{0}".format(each) #self.formatColumnName(each))
			self.df[catName] = 0
		bar.finish()
		logger.log("Creating Features for Vuln Categories Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	# Won't work, need to see if there is another option. 
	def parallelize_sortVulnsIntoFeatures(self):
		logger.log("Sorting Vulns into Categories in parallel")
		startTime = datetime.now()
		num_cores = psutil.cpu_count(logical=False) #number of cores on your machine
		threads_per_core = 1 #number of partitions to split dataframe
		workers =num_cores * threads_per_core # How many parititions and threads to parallelize the work
		logger.log("Threads per Core count: {0} Core Count: {1} Total Workers: {2}".format(threads_per_core, num_cores, workers))
		ssTime = datetime.now() 
		df_split = np.array_split(self.df, workers * 6) ### otherwizse each slice is too big
		logger.log("Splitting data for parallel processing : {0}".format(logger.getElapsedTime(ssTime,datetime.now())))
		pool = Pool(workers)
		df = pd.concat(pool.map(self.sortVulnsIntoFeatures, df_split))
		pool.close()
		pool.join()
		self.df = df
		logger.log("Setting Vuln Category Features Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		self.df = self.df.drop(["vuln_category"], axis = 1)


	# Less code, but poorer performance
	def locVulnCategoriesToFeature(self):
		logger.log("Loc Vulns Categories into features")
		startTime = datetime.now()
		df = self.df
		catalizer = lambda x: "CAT_" + x
		bar = Bar("Sorting Vulns into Categories", max=len(self.df))
		bar.next()

		for index in df.index:
			cat_names = list(map(catalizer, df["vuln_category"][index].split(","))); 
			values = [1]*len(cat_names)
			df.loc[index, cat_names] = values
			bar.next()
		bar.finish()
		logger.log("Setting Vuln Category Features Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		df = self.df
		self.df = self.df.drop(["vuln_category"], axis = 1)
		catalizer = lambda x: "CAT_" + x
		cat_names = list(map(catalizer, catList)); 
		for cat_name in cat_names:
			logger.log("{0} Count: {1}".format(cat_name, df[cat_name].sum))

	# Poorer performance
	def createVulnCategoryFeatures2(self):
		logger.log("Creating Features for Vuln Categories - new")
		startTime = datetime.now()
		defaultValues = [0] * len(catList)
		catalizer = lambda x: "CAT_" + x
		cat_names = list(map(catalizer, catList)); 
		self.df = pd.concat(
		    [
		        self.df,
		        pd.DataFrame(
		            [defaultValues], 
		            index=self.df.index, 
		            columns=cat_names
		        )
		    ], axis=1
		)
		# for col in self.df.columns: 
		# 	print(col)
		logger.log("Creating Features for Vuln Categories Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))



	def sortVulnsIntoFeatures(self):
		logger.log("Sorting Vulns into Categories")
		startTime = datetime.now()
		bar = Bar("Sorting Vulns into Categories", max=len(self.df))
		for index, each in self.df.iterrows():
			bar.next()
			cat = each["vuln_category"]
			parts = cat.split(",")
			for part in parts:
				try:
					thisPart = "CAT-{0}".format(part)
					if part in catList:
						self.df.at[index, thisPart] = 1 
				except Exception as e:
					print("Missing Cat From Master List - {0}".format(part))
		bar.finish()
		logger.log("Setting vuln category features Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))
		self.df = self.df.drop(["vuln_category"], axis = 1)


	def sortMalwareData(self):
		logger.log("Sorting Malware Data")
		startTime = datetime.now()
		bar = Bar("Sorting Malware Data", max=len(self.df))
		self.df["malwarekit"] = 0
		self.df["malwarekit_info"] = self.df["malwarekit_info"].fillna(value="NONE")
		for index, row in self.df.iterrows():
			bar.next()
			if not "NONE" in str(row["malwarekit_info"]):
				self.df.at[index, "malwarekit"] = 1
		self.df = self.df.drop(["malwarekit_info"], axis=1)
		bar.finish
		logger.log("Sorting Malware Data Took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))

	def sortPortData(self):
		logger.log("Setting important ports features (legacy)")
		startTime = datetime.now()
		bar = Bar("Sorting Ports Into Important Ports", max=len(self.df))
		self.df["port"] = self.df["port"].fillna(0)
		for index, row in self.df.iterrows():
			bar.next()
			port = "port_{0}".format(int(row["port"]))
			if port in importantPorts:
				self.df.at[index, port] = 1
		self.df = self.df.drop(["port"],axis=1)
		try:
			self.df = self.df.drop(["Unknown"], axis=1)
		except:
			logger.log("Nothing to see here")
		bar.finish()
		logger.log("Setting important ports features (legacy) took: {0}".format(logger.getElapsedTime(startTime,datetime.now())))