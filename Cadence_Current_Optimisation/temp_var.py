#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

File Data Extraction File:
"""
#===========================================================================================================================

import spectre as sp
import numpy as np
import file_write as fw

#------------------------------------Defining the functions -----------------------------------------

def temperature_variation(optimization_input_parameters):
	
	temp_list=optimization_input_parameters['temp_list']
	circuit_parameters=optimization_input_parameters['manual_circuit_parameters'].copy()
	
	opt_param_temp_var_dict = {}

	# Writing the name of the netlist directory to tcsh file
	sp.write_tcsh_initial(optimization_input_parameters)

	for i in range(len(temp_list)):
		circuit_parameters['Temp']=temp_list[i]
		#sp.write_temp(temp_list[i],optimization_input_parameters)
		extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
		#print(circuit_parameters['Temp'])
		opt_param_temp_var_dict[i] = extracted_parameters
	
	fw.save_output_temp_var(opt_param_temp_var_dict,optimization_input_parameters)\


#-----------------------------------------------------------------------------------------------------
# This function will be used to analyze the temperature variaition for the best optimized result
def temperature_variation_final(optimization_results,optimization_input_parameters):
	
	print("-------------------------------------------------------------Temperature Variation of Best Result -----------------------------------------------------------------------")
	iter_number=optimization_results['optimized_results']['iter_number']-1
	circuit_parameters=optimization_results['circuit_parameters_iter'][iter_number].copy()
	print("Best Result : ", circuit_parameters)

	temp_list=optimization_input_parameters['temp_list']
	opt_param_temp_var_dict = {}

	# Writing the name of the netlist directory to tcsh file
	sp.write_tcsh_initial(optimization_input_parameters)

	for i in range(len(temp_list)):
		circuit_parameters['Temp']=temp_list[i]
		extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
		opt_param_temp_var_dict[i] = extracted_parameters
	
	fw.save_output_temp_var(opt_param_temp_var_dict,optimization_input_parameters)


#-----------------------------------------------------------------------------------------------------
# This function will be used to analyze the temperature variaition for the best optimized result
def temperature_variation_with_current(optimization_results,optimization_input_parameters):
	
	print("-------------------------------------------------------------Temperature and Current Variation of Best Result -----------------------------------------------------------------------")
	iter_number=optimization_results['optimized_results']['iter_number']-1
	circuit_parameters=optimization_results['circuit_parameters_iter'][iter_number].copy()
	print("Best Result : ", circuit_parameters)

	Io=circuit_parameters['Io']
	
	Io_points_singleside=7
	a=np.logspace(np.log10(0.1*Io),np.log10(Io),Io_points_singleside+1)
	b=np.logspace(np.log10(Io),np.log10(10*Io),Io_points_singleside+1)

	Io_list=np.concatenate((a,b[1:]))
	
	#Io_list=np.linspace(Io/2,1.5*Io,Io_points)

	temp_list=optimization_input_parameters['temp_list']
	opt_param_temp_var_dict = {}

	# Writing the name of the netlist directory to tcsh file
	sp.write_tcsh_initial(optimization_input_parameters)

	for i in range(len(Io_list)):
		circuit_parameters['Io']=Io_list[i]
		opt_param_Io_var_dict={}
		for j in range(len(temp_list)):
			circuit_parameters['Temp']=temp_list[j]
			#sp.write_temp(temp_list[i],optimization_input_parameters)
			extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
			opt_param_Io_var_dict[j]=extracted_parameters
		opt_param_temp_var_dict[i] = opt_param_Io_var_dict
	
	fw.save_output_temp_var_with_current(Io_list,opt_param_temp_var_dict,optimization_input_parameters)


#-----------------------------------------------------------------------------------------------------
# This function will be used to analyze the temperature variaition for the best optimized result
def temperature_process_variation_final(optimization_results,optimization_input_parameters):
	
	print("-------------------------------------------------------------Temperature , Process Variation of Best Result -----------------------------------------------------------------------")
	iter_number=optimization_results['optimized_results']['iter_number']-1
	circuit_parameters=optimization_results['circuit_parameters_iter'][iter_number].copy()
	print("Best Result : ", circuit_parameters)

	temp_list=optimization_input_parameters['temp_list']
	opt_param_temp_var_dict = {}

	# Writing the name of the netlist directory to tcsh file
	sp.write_tcsh_initial(optimization_input_parameters)

	for model in optimization_input_parameters['model_process_corners']:

		optimization_input_parameters['model_name']=model		#  Defining which model to use (tt,ff,ss)
		sp.write_library(optimization_input_parameters)			# Writes the include commands to the netlist file
	
		dum=len(opt_param_temp_var_dict)+1
		for i in np.array(range(len(temp_list)))+len(opt_param_temp_var_dict)+1:
			circuit_parameters['Temp']=temp_list[i-dum]
			extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
			opt_param_temp_var_dict[i-1] = [extracted_parameters,model,temp_list[i-dum]]
	
	fw.save_output_temp_process_var(opt_param_temp_var_dict,optimization_input_parameters)


#-----------------------------------------------------------------------------------------------------

#===========================================================================================================================3
