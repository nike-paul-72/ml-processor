
# Note 1: Runs all tasks in the task definitions one after another, when they are runnable, else will skip
# Note 2: Can force runnable tasks to run by setting always_force to True in code.  
# Note 3: This is primarly used for cron jobs or scripted runs (via YAML CF script)

import time, os
from NIKEutil.logger import logger
from NIKEml.taskRunner import nikeTaskRunner
from NIKEml.taskDefinitions import taskDefinitions
from NIKEml.status import nikeMLStatus


always_force = False


logger.log("### CLI PREDICTOR - CHECK STATUS")
statusCheck = nikeMLStatus()
status = statusCheck.getStatus()
logger.log("State: {0} Status: {1}".format(status.state, status.result_text))
for key in status.files.keys():
	file_details = status.files[key]
	logger.log("File: {0}  Last Updated: {1}  Size: {2} bytes".format(file_details["file_name"],file_details["file_date"], file_details["file_size"]))

logger.log("### CLI PREDICTOR - RUNNING TASKS")

taskRunner = nikeTaskRunner()
for task_name in taskDefinitions.keys(): 
	done = False
	loopCount = 0
	loopMax = 4*40 # Max we wait is 4x 15sec slices x
	force_run = always_force
	while not done: 
		task = taskDefinitions[task_name]
		logger.log("Running task {0}.  Force: {1}".format(task["cname"],force_run))
		result = taskRunner.runTask(task_name, force=force_run)
		logger.log("State: {0} Status: {1} Runnable: {2} Forcible: {3}".format(result.state, result.status, result.runnable, result.forcible))
		# First time through, we will force it to run
		force_run = False
		if result.state == "Current":
			done = True
		if result.state in ["Running", "Started"]:
			force_run = False
			time.sleep(15)  # Wait before polling the command -> problem is, if it never get's current, will run indefinitely
			++loopCount
			if loopCount >= loopMax:
				logger.log("Failed to complete Data Loading in {0} minutes. Exitting script.".format(loopMax*15))
				exit()

logger.log("### CLI PREDICTOR - CHECK STATUS")
statusCheck = nikeMLStatus()
status = statusCheck.getStatus()
logger.log("State: {0} Status: {1}".format(status.state, status.result_text))
for key in status.files.keys():
	file_details = status.files[key]
	logger.log("File: {0}  Last Updated: {1}  Size: {2} bytes".format(file_details["file_name"],file_details["file_date"], file_details["file_size"]))
