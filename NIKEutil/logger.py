from datetime import datetime

class logger:
	def log(event):
		print("[+] {0} - {1}".format(datetime.now(), event))

	def getElapsedTime(firstDateTime, secondDateTime):
		datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
		diff = datetime.strptime(str(secondDateTime), datetimeFormat) - datetime.strptime(str(firstDateTime), datetimeFormat)
		return "{}".format(diff)