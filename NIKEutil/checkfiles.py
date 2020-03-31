from os import listdir, path
from os.path import isfile, join
from datetime import datetime
from datetime import date


class fileChecker:
	datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
	# onlyfiles = [f for f in listdir(mypath) if (isfile(join(mypath, f)) & (f.split[-1] == "parquet"))]
	def getFileAge(self,firstDateTime, secondDateTime):
		# diff = datetime.strptime(str(secondDateTime), self.datetimeFormat) - datetime.strptime(str(firstDateTime), self.datetimeFormat)
		diff = secondDateTime - firstDateTime
		return int(diff.days)

	def getFileDetails(self, file_path, file):
		file_details = {}
		full_file = path.join(file_path,file)
		if path.exists(full_file):
			file_date ="{}".format(datetime.fromtimestamp(path.getmtime(full_file)))
			datetimeFormat = self.datetimeFormat if "." in file_date else '%Y-%m-%d %H:%M:%S'

			file_age = self.getFileAge(datetime.strptime(str(file_date), datetimeFormat), datetime.now())
			file_details["file_name"] = file
			file_details["full_name"] = full_file
			file_details["file_size"] = path.getsize(full_file)
			file_details["file_date"] = file_date
			file_details["file_age"] = file_age
			file_details["needs_refreshed"] = file_age > 14
		else:
			file_details["file_name"] = file
			file_details["full_name"] = "[File not found]"
			file_details["file_size"] = 0
			file_details["file_date"] = date.min.strftime("%m/%d/%Y, %H:%M:%S")
			file_details["file_age"] = -1
			file_details["needs_refreshed"] = True
		return file_details

	def getDataFileDetails(self, data_path, file_list):
		files = {}
		for file in file_list:
			files[file] = self.getFileDetails(data_path,file)

		return files








