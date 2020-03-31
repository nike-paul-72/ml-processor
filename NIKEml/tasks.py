import os, settings, threading
from NIKEutil.checkfiles import fileChecker
from NIKEutil.logger import logger


class taskResult:

	def __init__(self, state="",status="", runnable=False, forcible=False):
		self.state = state
		self.status = status
		self.runnable = runnable
		self.forcible = forcible

class mlTask:	


	def __init__(self, thread_name, dependency_files, output_files, method_call):
		self.DATA_PATH = os.getenv("data_path")
		self.thread_name = thread_name
		self.dependency_files = dependency_files
		self.output_files = output_files
		self.method_call = method_call
		self.runnable = False
		self.forcible = False
		self.checked = False
		logger.log("Initialized task {0} with data path {1}".format(thread_name, self.DATA_PATH ))

	def needsRefresh(self, file_path, file_list):
		# Check to see if files need refreshed
		checker = fileChecker()
		files = checker.getDataFileDetails(file_path, file_list)
		needsRefresh = True
		for file in file_list:
			inFiles = file in files.keys()
			needsRefresh = files[file]["needs_refreshed"] if inFiles else True
			# logger.log(f"file: {file} => needs refresh: {needsRefresh})")
		return needsRefresh

	# make this a propery getter
	def isRunnable(self):
		self.checked = True
		
		if self.isRunning():  
			return taskResult("Running", "Task is currently running")

		needs_refresh = self.needsRefresh(self.DATA_PATH,self.dependency_files)
		if(len(self.dependency_files) > 0 and needs_refresh):
			return taskResult("Cannot Run", "Depedendency files {0} are missing".format(",".join(self.dependency_files)))

		needs_refresh = self.needsRefresh(self.DATA_PATH,self.output_files)
		if not needs_refresh :
			self.forcible = True
			return taskResult("Current", "Existing output file {0} are present and current.".format(",".join(self.output_files)), forcible=True)
		else:
			self.forcible = True
			self.runnable = True
			return taskResult("Needs Refreshed", "Existing output file {0} are missing or out of date, dependency files are present, task is not currently running.".format(",".join(self.output_files)), runnable=True, forcible=True)

	def isRunning(self):
		id2name = dict([(th.name,th) for th in threading.enumerate()])
		return self.thread_name in id2name.keys()


	def run(self, force=False):
		if not self.checked:
			return taskResult("Check first", "Please call task.isRunnable() first.", false)

		if self.runnable or (self.forcible and force):
			try:	
				thread = threading.Thread(target=self.method_call)
				thread.daemon = True  
				thread.name =  self.thread_name              
				thread.start() 
				return taskResult("Started", "Requested process was started on a background thread {0}".format(self.thread_name), runnable=False, forcible=False)         
			except Exception as inst:
				return taskResult("Failed", "An exception occured starting process {0}, exception args {1}, exception details {2}".format(self.thread_name,inst.args,inst))         
		







