#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064
Pre Optimization File:
"""
#===========================================================================================================================
import numpy as np
import math
import common_functions as cf
import spectre as sp
import hand_calculation_mixer as hc1
#import hand_calculation_2 as hc2


#===========================================================================================================================
#------------------------------------Defining the functions for simple calculations-----------------------------------------

#---------------------------------------------------------------------------------------------------------------------------
# Function to manually choose the Initial Circuit Parameters	
def manual_initial_parameters(optimization_input_parameters):

	# Getting Circuit Parameters
	circuit_parameters=optimization_input_parameters['manual_circuit_parameters'].copy()
		
	# Running Eldo
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)	
	
	return circuit_parameters,extracted_parameters


#===========================================================================================================================
#------------------------------------------- Output Functions --------------------------------------------------------------
def pre_optimization(mos_parameters,optimization_input_parameters,optimization_results):
	
	#======================================================== Manual Initial Points =============================================================================================================

	if optimization_input_parameters['pre_optimization']['type']=='manual':
		
		print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Manual Operating Point Selection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		#--------------------Initial Point Calculations-------------------------

		# Calculating the Values of Circuit Parameters
		circuit_parameters,extracted_parameters=manual_initial_parameters(optimization_input_parameters)

		# Storing the Circuit and Extracted Parameters
		optimization_results['manual_hc']={}
		optimization_results['manual_hc']['circuit_parameters']=circuit_parameters.copy()
		optimization_results['manual_hc']['extracted_parameters']=extracted_parameters.copy()

		# Printing the values
		#cf.print_circuit_parameters(circuit_parameters)
		#cf.print_extracted_outputs(extracted_parameters)

		#cf.wait_key()

	
	#======================================================== Automatic Initial Points =============================================================================================================

	if optimization_input_parameters['pre_optimization']['type']==1:
		circuit_parameters,extracted_parameters=hc1.automatic_initial_parameters(mos_parameters,optimization_input_parameters,optimization_results)

	if optimization_input_parameters['pre_optimization']['type']==2:
		circuit_parameters,extracted_parameters=hc2.automatic_initial_parameters(mos_parameters,optimization_input_parameters,optimization_results)

	return circuit_parameters,extracted_parameters
	

#===========================================================================================================================

