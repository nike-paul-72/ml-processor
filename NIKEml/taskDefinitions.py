

taskDefinitions = { "load": \
					{ "name" : "dataLoader", \
					  "cname" : "Data Loader", \
					  "description" : "Iteratively loads data from datashims and stores to S3", \
					  "thread_name" : "dataloader", \
					  "task_module" : "NIKEml.dataLoader", \
					  "task_class" : "nikeDataLoader", \
					  "task_method" : "getData", \
					  "dependency_files" : [], \
					  "output_files" : ["paloalto.parquet","vmVulnerabilities.parquet"]
					},
					"map": \
					{ "name" : "dataMapper", \
					  "cname" : "Data Mapper", \
					  "description" : "Maps vm vmVulnerability data to palo alto zones and stores to s3", \
					  "thread_name" : "datamapper", \
					  "task_module" : "NIKEml.ec2ThreadedMapper", \
					  "task_class" : "nikeThreadedMapper", \
					  "task_method" : "runMapper", \
					  "dependency_files" : ["paloalto.parquet","vmVulnerabilities.parquet"], \
					  "output_files" : ["vmtopamapped.parquet"]
					},
					"engineer": \
					{ "name" : "featureengineer", \
					  "cname" : "Feature Engineer", \
					  "description" : "Runs multiple feature engineering steps prior to ML processing", \
					  "thread_name" : "featureengineer", \
					  "task_module" : "NIKEml.engineer", \
					  "task_class" : "nikeVMengineer", \
					  "task_method" : "engineerFeatures", \
					  "dependency_files" : ["vmtopamapped.parquet"], \
					  "output_files" : ["encoded_mapped_data.parquet"]
					},
					"learn": \
					{ "name" : "learner", \
					  "cname" : "ML Learning", \
					  "description" : "Emits pickled ML algorithms taught by provided data", \
					  "thread_name" : "learner", \
					  "task_module" : "NIKEml.learn", \
					  "task_class" : "nikeVMlearn", \
					  "task_method" : "runLearning", \
					  "dependency_files" : ["ML_Label_Results.xlsx"], \
					  "output_files" : ["classifierModel3.p","feature_list.p"]
					},
					"predict": \
					{ "name" : "predictor", \
					  "cname" : "ML Predictor", \
					  "description" : "Emits confidence scores via ML processing using learning", \
					  "thread_name" : "predictor", \
					  "task_module" : "NIKEml.predict", \
					  "task_class" : "nikeVMpredict", \
					  "task_method" : "runPredictions", \
					  "dependency_files" : ["vmtopamapped.parquet","encoded_mapped_data.parquet"], \
					  "output_files" : ["final_results.csv"]
					},
					"split": \
					{ "name" : "predictor", \
					  "cname" : "ML Predictor", \
					  "description" : "Emits confidence scores via ML processing using learning", \
					  "thread_name" : "splitter", \
					  "task_module" : "NIKEml.predict", \
					  "task_class" : "nikeVMpredict", \
					  "task_method" : "runPredictions", \
					  "dependency_files" : ["final_results.csv"], \
					  "output_files" : ["final_results_sev_10_conf_2.csv","final_results_sev_10_conf_1.csv","final_results_sev_10_conf_0.csv","final_results_sev_09_conf_2.csv","final_results_sev_09_conf_1.csv","final_results_sev_09_conf_0.csv","final_results_sev_08_conf_2.csv","final_results_sev_08_conf_1.csv","final_results_sev_08_conf_0.csv","final_results_sev_07_conf_2.csv","final_results_sev_07_conf_1.csv","final_results_sev_07_conf_0.csv","final_results_sev_06_conf_2.csv","final_results_sev_06_conf_1.csv","final_results_sev_06_conf_0.csv","final_results_sev_05_conf_2.csv","final_results_sev_05_conf_1.csv","final_results_sev_05_conf_0.csv","final_results_sev_04_conf_2.csv","final_results_sev_04_conf_1.csv","final_results_sev_04_conf_0.csv","final_results_sev_03_conf_2.csv","final_results_sev_03_conf_1.csv","final_results_sev_03_conf_0.csv","final_results_sev_02_conf_2.csv","final_results_sev_02_conf_1.csv","final_results_sev_02_conf_0.csv","final_results_sev_01_conf_2.csv","final_results_sev_01_conf_1.csv","final_results_sev_01_conf_0.csv","final_results_sev_00_conf_2.csv","final_results_sev_00_conf_1.csv","final_results_sev_00_conf_0.csv"]
					}
				}
