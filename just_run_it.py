#!/usr/bin/python
import os, sys, getopt
from NIKEutil.logger import logger
from NIKEml.taskDefinitions import taskDefinitions


def help():
	print('usage: python3 just_run_it.py [-h] or -c <command> [-d]')
	print('		-h           	# print help details')
	tasksNames = "|".join(getTaskList())
	print('		-c <command>	# the command to run from the list of [{0}]'.format(tasksNames))
	print('		-d              # optional flag, displays task definition and status')
	print('\nNOTE:')
	print('\nThis script runs the commands without protection from multiple executions in the foreground thread. Useful for testing, and debugging. Use cli-predictor.py for scheduled jobs')
	print("\n\n")

def processArgs(argv):
	command = ""
	commands = getTaskList()
	details = False
	try:
		opts, args = getopt.getopt(argv,"hc:d")
	except getopt.GetoptError:
		help()
		sys.exit()
	for opt, arg in opts:
		if opt == '-h':
			help()
			sys.exit()
		elif opt == '-c':
			if arg in commands:
				command = arg
			else:
				print("Invalid command provided: {0}. Select from list [{1}]".format(arg,"|".join(commands)))
		elif opt == '-d':
			details = True

	return command,details

def getTargetMethod(task_name):
	taskDefinition = getTaskDetails(task_name)
	mod = __import__(taskDefinition["task_module"], fromlist=[taskDefinition["task_class"]])
	classDef = getattr(mod, taskDefinition["task_class"])
	taskInstance = classDef()
	task_call = getattr(taskInstance, taskDefinition["task_method"])
	return task_call;

def getTaskList():
	return taskDefinitions.keys()

def getTaskDetails(task_name):
	return taskDefinitions[task_name]

def printTaskDetails(task_name):
	details = getTaskDetails(task_name)
	print("Task Details: " + task_name)
	print("\nDetails:")
	print("\n\tInternal Name:\t" + details["name"] )
	print("\tDisplay Name:\t" + details["cname"] )
	print("\tDescription:\t" + details["description"] )
	print("\tThread Name:\t" + details["thread_name"] )
	print("\tModule Name:\t" + details["task_module"])
	print("\tClass and Method:\t {0}.{1}()".format(details["task_class"],details["task_method"]))
	print("\tFiles Required to Run:\t" + ",".join(details["dependency_files"]))
	print("\tOutput Files:")
	for file in details["output_files"]:
		print("\t\t" + file)

def main(argv): 
	command,details = processArgs(argv)

	if details:
		printTaskDetails(command)
	else:
		target = getTargetMethod(command)
		target()


if __name__ == "__main__":
	main(sys.argv[1:])
