from NIKEutil.logger import logger
from NIKEml.tasks import *
from NIKEml.taskDefinitions import taskDefinitions


class nikeTaskRunner:
	# DATA_PATH=""

	# def __init__(self):
	# 	# self.DATA_PATH = os.getenv("data_path")
	# 	# logger.log("Initiating TaskRunner with data path: {0}".format(self.DATA_PATH))


	def taskFactory(self, taskDefinition):
		# dynamic instantiate the class from definition 
		mod = __import__(taskDefinition["task_module"], fromlist=[taskDefinition["task_class"]])
		classDef = getattr(mod, taskDefinition["task_class"])
		taskInstance = classDef()
		task_call = getattr(taskInstance, taskDefinition["task_method"])
		task = mlTask(taskDefinition["thread_name"], taskDefinition["dependency_files"], taskDefinition["output_files"], task_call)
		return task



	def runTask(self, taskname, start=False, force=False):
		taskDefinition = taskDefinitions[taskname]
		if taskDefinition is None or len(taskDefinition) <=0:
			logger.log("Task definition was not found")
			return taskResult("Not found", f"A task named {taskname} was not found in task definitions.", False, False)

		task_name = taskDefinition["cname"]
		task = self.taskFactory(taskDefinition)
		if task.isRunning():
			return taskResult("Running", f"{task_name} is running, check back later", False, False )

		result = task.isRunnable()
		# logger.log(f"Result of checking {task_name} Task:  State: {result.state} Status {result.status} Runnable: {result.runnable} Forcible: {result.forcible}")

		if (result.runnable and start) or (result.forcible and force):
			result = task.run(force)
			# logger.log(f"Result of calling {task_name} Task:  State: {result.state} Status {result.status} Runnable: {result.runnable} Forcible: {result.forcible}")

		task = None
		# logger.log("Result of calling runPrediction Task:  State: {0} Status {1} Runnable: {2} Forcible: {3}".format(result.state, result.status, result.runnable, result.forcible))
		return result
