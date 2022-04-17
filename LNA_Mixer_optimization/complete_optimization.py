#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

Full Optimization Code:
"""
#===========================================================================================================================
import numpy as np
import math
import datetime
import file_write as fw
import optimization as op
import common_functions as cf
import pre_optimization as pr
import spectre as sp
import temp_var as tv
import os
#===========================================================================================================================


#===========================================================================================================================
#------------------------------------Main Program Code----------------------------------------------------------------------

def complete_optimization(optimization_input_parameters):

	# Calculating Starting Time
	time_start=datetime.datetime.now()

	# Saving the optimization input results
	fw.save_input_results(optimization_input_parameters)

	# Creating Optimization Results Dictionary
	optimization_results={}

	# Writing the include command
	sp.write_errpreset(optimization_input_parameters)

	#Writing Pin for the IIP3 calculation
	p_in=optimization_input_parameters['simulation_conditions']['pin_iip3']
	sp.write_single_param('pin',p_in,optimization_input_parameters)
	#sp.write_pin(p_in,optimization_input_parameters)

	#======================================================== MOSFET PARAMETERS ==================================================================================================
	
	print('************************************************************************************************************')
	print('*********************************** MOSFET Parameters ******************************************************')

	# Setting Lmin and Vdd
	Lmin=optimization_input_parameters['Lmin']
	vdd=optimization_input_parameters['Vdd']

	# Extracting From File
	mos_file_parameters = {'un':0,'cox':0,'vt':0,'Lmin':Lmin,'vdd':vdd}
	mos_file_parameters=sp.extract_mosfet_param(optimization_input_parameters,mos_file_parameters)
	mos_parameters=mos_file_parameters.copy()

	optimization_results['mos_parameters']=mos_parameters

	# Printing the MOSFET Parameters
	cf.print_MOS_parameters(mos_parameters)

	# Writing the MOSFET File Location to .cir file
	sp.write_cir_initial(optimization_input_parameters)

	# Writing the name of the netlist directory to tcsh file
	sp.write_tcsh_initial(optimization_input_parameters)

	#cf.wait_key()


	#======================================================== PRE OPTIMIZATION ===================================================================================================

	print('************************************************************************************************************')
	print('*********************************** Pre Optimization *******************************************************')
	
	# Running pre optimization
	circuit_parameters,extracted_parameters=pr.pre_optimization(mos_parameters,optimization_input_parameters,optimization_results)
	# Printing the values
	cf.print_circuit_parameters(circuit_parameters)
	cf.print_extracted_outputs(extracted_parameters)

	#======================================================== OPTIMIZATION =======================================================================================================
	
	print('************************************************************************************************************')
	print('*********************************** Main Optimization ******************************************************')

	# Storing the Circuit and Extracted Parameters
	optimization_results['optimization_start']={}
	optimization_results['optimization_start']['circuit_parameters']=circuit_parameters.copy()
	optimization_results['optimization_start']['extracted_parameters']=extracted_parameters.copy()

	# Running the main optimization
	circuit_parameters,extracted_parameters,optimization_results=op.main_opt(circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results)

	# Printing the values
	cf.print_circuit_parameters(circuit_parameters)
	cf.print_extracted_outputs(extracted_parameters)
	
	#======================================================== AFTER OPTIMIZATION =================================================================================================
	
	# Calculating End Time and Time Difference
	time_end=datetime.datetime.now()
	time_delta=time_end-time_start
	optimization_results['time']=time_delta
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
	fw.extract_dc_mos(optimization_input_parameters)
	if optimization_input_parameters['temp_var']['run_temp_cur_var']==1:
		tv.temperature_variation_with_current(optimization_results,optimization_input_parameters)	
	
	if optimization_input_parameters['temp_var']['run_temp_var']==1:
		tv.temperature_variation_final(optimization_results,optimization_input_parameters)

	if optimization_input_parameters['temp_var']['run_temp_process_var']==1:
		tv.temperature_process_variation_final(optimization_results,optimization_input_parameters)


	fw.save_info(optimization_input_parameters,optimization_results)
	fw.save_output_results(optimization_results,optimization_input_parameters)



#=============================================================================================================================================================================
# Running the manual Parameters
def single_run(optimization_input_parameters):

	# Creating Optimization Results Dictionary
	optimization_results={}

	# Writing the include command
	sp.write_errpreset(optimization_input_parameters)

	# Writing the name of the netlist directory to tcsh file
	sp.write_tcsh_initial(optimization_input_parameters)

	#Writing Pin for the IIP3 calculation
	p_in=optimization_input_parameters['simulation_conditions']['pin_iip3']
	sp.write_single_param('pin',p_in,optimization_input_parameters)
	#sp.write_pin(p_in,optimization_input_parameters)


	print('************************************************************************************************************')
	print('*********************************** MOSFET Parameters ******************************************************')

	# Setting Lmin and Vdd
	Lmin=optimization_input_parameters['Lmin']
	vdd=optimization_input_parameters['Vdd']

	# Extracting From File
	mos_file_parameters = {'un':0,'cox':0,'vt':0,'Lmin':Lmin,'vdd':vdd}
	mos_file_parameters=sp.extract_mosfet_param(optimization_input_parameters,mos_file_parameters)
	mos_parameters=mos_file_parameters.copy()

	optimization_results['mos_parameters']=mos_parameters

	# Printing the MOSFET Parameters
	cf.print_MOS_parameters(mos_parameters)
	# Writing the MOSFET File Location to .cir file
	sp.write_cir_initial(optimization_input_parameters)

	#======================================================== RUN ===================================================================================================

	# Getting Circuit Parameters
	#circuit_parameters=optimization_input_parameters['manual_circuit_parameters'].copy()
	# Running pre optimization
	circuit_parameters,extracted_parameters=pr.pre_optimization(mos_parameters,optimization_input_parameters,optimization_results)

	# Running Eldo
	#extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)	
	optimization_input_parameters['extracted_parameters']=extracted_parameters
	#fw.extract_dc_mos(optimization_input_parameters)

	# Printing the values
	cf.print_circuit_parameters(circuit_parameters)
	cf.print_extracted_outputs(extracted_parameters)

	#======================================================== AFTER RUN =================================================================================================
	
	if optimization_input_parameters['temp_var']['run_temp_cur_var']==1:
		tv.temperature_variation_with_current(optimization_results,optimization_input_parameters)	
	
	if optimization_input_parameters['temp_var']['run_temp_var']==1:
		tv.temperature_variation_final(optimization_results,optimization_input_parameters)

	if optimization_input_parameters['temp_var']['run_temp_process_var']==1:
		tv.temperature_process_variation_single_run(optimization_results,optimization_input_parameters)

	#=============================================================================================================================================================================



