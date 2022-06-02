#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

Resistor Data Extraction Driver File:
"""
#===========================================================================================================================


import res_param_extraction as rpe
import numpy as np
import pylab as py
import yaml
import fileinput
from yaml.loader import SafeLoader

np.set_printoptions(formatter={'float': "{00:0.2e}".format})




file_dir = "/home/ee18b064/cadence_project/Res_mod"
results_dir="/home/ee18b064/Optimization/Details_TSMC65/Resistor_Characteristics/"
param_list=['wid','len','fund_1','cir_temp','i_sin','i_cur','v_dc']
param={
	'wid'      : 2e-6,
	'len'      : 10e-6,
	'fund_1'   : 1e9,
	'cir_temp' : 27,
	'i_sin'	   : 1e-3,
	'i_cur'    : 0,
	'v_dc'	   : 0
}

stream = open("res_model_param.yml", 'r')
model = yaml.load(stream, Loader=SafeLoader)
stream.close()

#rpe.save_THD_plots(file_dir,results_dir,model,param,param_list)  # For THD charecterisation used v_dc as 0 (No DC Current)
#rpe.dc_resist_driver(file_dir,results_dir,model,param,param_list)
#rpe.current_driver(file_dir,results_dir,model,param,param_list)	
rpe.ac_resist_driver(file_dir,results_dir,model,param,param_list)	


		
extracted_param={}
for i in extracted_param:
	print('Resistor Model : ',str(i),'\n')
	for j in extracted_param[i]:
		print(str(j),'\t\t : \t', (extracted_param[i][j]))
	print('\n\n')










