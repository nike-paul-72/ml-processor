import pickle, os, settings, re, time, threading, psutil
import pandas as pd
import numpy as np







def getDataframeFromParquet(file):
	df = pd.read_parquet(file)
	return df

def getDataframeFromCSV(file):
	df = pd.read_csv(file)
	return df


def printColumns()
	DATA_PATH = os.getenv("data_path")
	# mapped_file = os.path.join(DATA_PATH,"vmtopamapped.parquet")
	# df = getDataframeFromParquet(mapped_file)
	# for column in df.columns:
	# 	print(column)


	# predict_file = os.path.join(DATA_PATH,"encoded_mapped_data.parquet")
	# df = getDataframeFromCSV(predict_file)
	# for column in df.columns:
	# 	print(column)

	df = getDataframeFromCSV(os.path.join(DATA_PATH,"final_results.csv"))
	print(df.shape)


if __name__ == "__main__":
	printColumns()