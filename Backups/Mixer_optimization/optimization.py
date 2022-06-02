#===========================================================================================================================
"""
Name: Pyneni Roopesh
Roll Number: EE18B028

Optimization Algorithm:
"""
#===========================================================================================================================
import numpy as np
import math
import common_functions as cf
import spectre as sp
import optimization_functions_loss as ofl
import file_write as fw
#import optimization_functions_fom as off

#===========================================================================================================================
#------------------------------------Defining the functions -----------------------------------------

	
#-----------------------------------------------------------------------------------------------
# This function updates the values of circuit parameters by trying to minimize loss
def calc_loss_slope(output_conditions,circuit_parameters,loss_dict,extracted_parameters,optimization_input_parameters):

	loss_weights=optimization_input_parameters['loss_weights']
	delta_threshold=optimization_input_parameters['delta_threshold']
	
	# Getting the sensitivity dictionary
	circuit_parameters_sensitivity={}
	for param_name in optimization_input_parameters['optimizing_parameters']:
		circuit_parameters_sensitivity[param_name]=0
	
	# Creating new dictionaries
	circuit_parameters1=circuit_parameters.copy() # This dictionary will store the values of parameters after increment to calculate the slope
	extracted_parameters1=extracted_parameters.copy() # This dictionary will store the values of parameters after increment to calculate the slope
	circuit_parameters_slope={} # This dictionary will store the values of slope of different losses with change of all circuit parameters
	
	# Calculating the value to update each parameter with
	for param_name in optimization_input_parameters['optimizing_parameters']:
		
		# Calculating the increment value
		increment_factor=delta_threshold # The value by which parameter increases = increment_factor*parameter
		increment=circuit_parameters[param_name]*increment_factor
	
	
		# Incrementing the circuit parameter
		circuit_parameters1=circuit_parameters.copy()
		circuit_parameters1[param_name]=circuit_parameters1[param_name]+increment
		
		
		# Extracting Loss
		extracted_parameters1=sp.write_extract(circuit_parameters1,optimization_input_parameters)
		#print('\n\n',circuit_parameters,'\n\n',extracted_parameters,'\n\n',circuit_parameters1,'\n\n',extracted_parameters1,'\n\n',param_name,'\n\n')

		if optimization_input_parameters['optimization_name']=='loss1':
			loss_dict1=ofl.calc_loss_1(extracted_parameters1,output_conditions,loss_weights)
		elif optimization_input_parameters['optimization_name']=='fom1':
			loss_dict1=off.calc_fom_1(extracted_parameters1,output_conditions,loss_weights)
			
		
		# Calculating Slope	
		circuit_parameters_slope[param_name]={}
		for param in loss_dict:
			circuit_parameters_slope[param_name][param]=(loss_dict1[param]-loss_dict[param])/increment
			
		circuit_parameters_sensitivity[param_name]={}
		
		# Calculating Sensitivity
		for categ_name in optimization_input_parameters['output_parameters_list']:
			initial_param=extracted_parameters[categ_name]
			final_param=extracted_parameters1[categ_name]
			sensitivity=(final_param-initial_param)/(initial_param)
			circuit_parameters_sensitivity[param_name][categ_name]=sensitivity
		
	return circuit_parameters_slope,circuit_parameters_sensitivity
	
#-----------------------------------------------------------------------------------------------
# Updating alpha
def update_alpha(loss_iter,alpha,i,alpha_mult,optimization_type,optimization_input_parameters):

	n_iter=optimization_input_parameters['max_iteration']-1
	alpha_start=optimization_input_parameters['alpha_start']
	alpha_end=optimization_input_parameters['alpha_end']

	if optimization_input_parameters['alpha_type']=='Linear':
		alpha=alpha_start+((alpha_end-alpha_start)*(i+1)/n_iter)
		print(alpha)

	elif optimization_input_parameters['alpha_type']=='Log':
		alpha_start_log=np.log(alpha_start)
		alpha_end_log=np.log(alpha_end)
		alpha_log=alpha_start_log+((alpha_end_log-alpha_start_log)*(i+1)/n_iter)
		alpha=np.exp(alpha_log)
		
	else:
		# Checking criteria for reducing threshold
		if i>0:
			if loss_iter[i]['loss']>=loss_iter[i-1]['loss'] and optimization_type==0:
				alpha*=alpha_mult
			elif loss_iter[i]['loss']<=loss_iter[i-1]['loss'] and optimization_type==1:
				alpha*=alpha_mult
		
	return alpha


#-----------------------------------------------------------------------------------------------
# Updating alpha for each parameters
def update_alpha_param (optimization_input_parameters,circuit_parameters_sensitivity,alpha_parameters):
	sum_output={}
	
	norm_sensitivity={}
	for i in optimization_input_parameters['optimizing_parameters']:
		norm_sensitivity[i]={}
		for j in optimization_input_parameters['output_specs_params_list']:
			norm_sensitivity[i][j]=circuit_parameters_sensitivity[i][j]
		
	for param in optimization_input_parameters['optimizing_parameters']:
		for out_spec in norm_sensitivity[param]:
			sum_output[out_spec]=1e-12
		break

	
	for param in optimization_input_parameters['optimizing_parameters']:
		for out_spec in norm_sensitivity[param]:
			sum_output[out_spec]=sum_output[out_spec]+abs(norm_sensitivity[param][out_spec])

	for param in optimization_input_parameters['optimizing_parameters']:
		for out_spec in norm_sensitivity[param]:
			norm_sensitivity[param][out_spec]=abs(norm_sensitivity[param][out_spec])/sum_output[out_spec]+1e-12

	out_dir_sense=np.array([1,1,1,-1,1,0])			#'conv_gain_db','iip3_dbm','iip2_dbm','nf_db','bb_BW','region'
	sense_Io=np.array(list(norm_sensitivity['Ibias'].values()))
	sign_Io=sense_Io/abs(sense_Io)
	Io_coeff_sign=-1*sign_Io*out_dir_sense

	base=2
	lf_coeff={}
	for param in norm_sensitivity:
		if param == 'Ibias' :
			lf_coeff[param]=sum(np.array(list(norm_sensitivity[param].values()))*Io_coeff_sign)
		else:
			lf_coeff[param]=sum(abs(np.array(list(norm_sensitivity[param].values()))))
			
	for param in lf_coeff:
		alpha_parameters[param]=base**lf_coeff[param]
	print(alpha_parameters)
	return alpha_parameters
	


#-----------------------------------------------------------------------------------------------
# Updating circuit parameters
def check_circuit_parameters(old_circuit_parameters,circuit_parameters,loss_iter,update_check,i,optimization_type):

	# Checking criteria for reducing threshold
	if update_check==1:
		if i>0:
			if loss_iter[i]['loss']>=loss_iter[i-1]['loss'] and optimization_type==0:
				circuit_parameters=old_circuit_parameters.copy()
			elif loss_iter[i]['loss']<=loss_iter[i-1]['loss'] and optimization_type==1:
				circuit_parameters=old_circuit_parameters.copy()
	old_circuit_parameters=circuit_parameters.copy()
	return circuit_parameters, old_circuit_parameters

def update_Cload(circuit_parameters,extracted_parameters,optimization_input_parameters):
	flo=optimization_input_parameters['output_conditions']['flo']
	frf=optimization_input_parameters['output_conditions']['frf']
	circuit_parameters['Cload']=1/(2*np.pi*(frf-flo)*circuit_parameters['Rd'])
	
	return circuit_parameters

def update_Alo(circuit_parameters,extracted_parameters,optimization_input_parameters):
	vdd=optimization_input_parameters['Vdd']
	vcmlo=extracted_parameters['Vcmlo']
	Alo=circuit_parameters['Alo']

	circuit_parameters['Alo']=min(vdd-vcmlo,vcmlo,Alo)
	
	return circuit_parameters


def update_L(circuit_parameters):
	circuit_parameters['L']=max(60e-9,circuit_parameters['L'])
	
	return circuit_parameters
	
#-----------------------------------------------------------------------------------------------
# Updating C2 and Rbias
def update_C2_Rbias(circuit_parameters,extracted_parameters,optimization_input_parameters):

	threshold2=optimization_input_parameters['pre_optimization']['C2_threshold']
	threshold3=optimization_input_parameters['pre_optimization']['Rbias_threshold']

	# Assigning the values
	cgs=extracted_parameters['cgs1']
	cgd=extracted_parameters['cgd1']
	
	gain_db=extracted_parameters['gain_db']
	gain=np.sqrt(cf.db_to_normal(gain_db))
	wo=optimization_input_parameters['output_conditions']['wo']
	
	# Calculating C2
	#C2a=threshold2*cgs
	#C2b=threshold2*cgd*gain
	#C2=np.maximum(C2a,C2b)
	
	C2=circuit_parameters['C2']
	# Calculating Rbias
	Rbias=max(threshold3/(wo*C2),1000)

	#circuit_parameters['C2']=C2
	circuit_parameters['Rbias']=Rbias

	return circuit_parameters

#-----------------------------------------------------------------------------------------------
# Checking stopping condition 
def check_stop_alpha(loss_iter,alpha,i,alpha_min):

	if alpha_min<0:
		return 0
	if i>1:
		if alpha<=alpha_min:
			return 1
	return 0
	
#-----------------------------------------------------------------------------------------------
# Checking stopping condition 
def check_stop_loss(loss_iter,i,n_iter,optimization_type):

	flag=0
	if n_iter<1:
		return 0
	if i>n_iter:
		flag=1
		for j in range(n_iter):
			if loss_iter[i-j]['loss']<loss_iter[i-j-1]['loss'] and optimization_type==0:
				flag=0
			elif loss_iter[i-j]['loss']>loss_iter[i-j-1]['loss'] and optimization_type==1:
				flag=0
	return flag
	
#-----------------------------------------------------------------------------------------------
# Checking stopping condition 
def moving_avg(loss_iter,circuit_parameters_iter,average_parameters,i,n_points):

	average_parameters[i]={}
	#average_parameters[i]['loss_Io']=0
	average_parameters[i]['Ibias']=0
		
	if i<n_points:
		for j in range(i+1):
			#average_parameters[i]['loss_Io']+=loss_iter[i-j]['loss_Io']
			average_parameters[i]['Ibias']+=circuit_parameters_iter[i-j]['Ibias']
		#average_parameters[i]['loss_Io']/=(i+1)
		average_parameters[i]['Ibias']/=(i+1)
	else:
		for j in range(n_points):
			#average_parameters[i]['loss_Io']+=loss_iter[i-j]['loss_Io']
			average_parameters[i]['Ibias']+=circuit_parameters_iter[i-j]['Ibias']
		#average_parameters[i]['loss_Io']/=n_points
		average_parameters[i]['Ibias']/=n_points
		
	return average_parameters


		
#===========================================================================================================================
#--------------------------------------------Output Functions---------------------------------------------------------------
	
#---------------------------------------------------------------------------------------------------------------------------
# Function to do main optimization
def main_opt_single(circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results):

	# Defining some values
	i=0
	spec_met_flag=0  # Tells if outspecs are met and is used to lower alpha
	 
	output_conditions=optimization_input_parameters['output_conditions']
	
	loss_weights=optimization_input_parameters['loss_weights']
	alpha_min=optimization_input_parameters['alpha_min']
	consec_iter=optimization_input_parameters['consec_iter']
	alpha_mult=optimization_input_parameters['alpha_mult']
	max_iteration=optimization_input_parameters['max_iteration']
	delta_threshold=optimization_input_parameters['delta_threshold']
	loss_type=optimization_input_parameters['loss_type']
	optimization_type=optimization_input_parameters['optimization_type']
	
	alpha_parameters=optimization_input_parameters['alpha']
	
	alpha_parameters_initial=optimization_input_parameters['alpha'].copy()
	
	# Creating old circuit parameters
	old_circuit_parameters=circuit_parameters.copy() # This dictionary will store the value of parameters for previous iterations
	
	# Creating the dictionaries
	loss_iter=optimization_results['loss_iter'].copy() # This dictionary will store the value of all loss values for different iterations
	loss_slope_iter=optimization_results['loss_slope_iter'].copy() # This dictionary will store the value of slope of losses for all parameters for different iterations
	alpha_parameters_iter=optimization_results['alpha_parameters_iter'].copy() # This dictionary will store the value of threshold for different iterations
	output_parameters_iter=optimization_results['output_parameters_iter'].copy() # This dictionary will store the value of output parameters for different iterations
	circuit_parameters_iter=optimization_results['circuit_parameters_iter'].copy() # This dictionary will store the value of circuit parameters for different iterations
	average_parameters_iter=optimization_results['average_parameters_iter'].copy()
	sensitivity_iter=optimization_results['sensitivity_iter'].copy()
	check_loss=1

	offset=len(optimization_results['circuit_parameters_iter'])
	i=i+offset
	max_iteration=max_iteration+offset
	
	# Running Eldo
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)

	# Calculating loss
	if optimization_input_parameters['optimization_name']=='loss1':
		loss_iter[i-1]=ofl.calc_loss_1(extracted_parameters,output_conditions,loss_weights)
	elif optimization_input_parameters['optimization_name']=='fom1':
		loss_iter[i-1]=off.calc_fom_1(extracted_parameters,output_conditions,loss_weights)
	
	# Printing the values of loss before optimization
	print('-----------------------------Before Iteration---------------------------------')
	print('Loss = ',cf.num_trunc(loss_iter[i-1]['loss'],3))	
	

	

	# Performing the iterations
	while i<max_iteration:
		cf.print_circuit_parameters(circuit_parameters)
		cf.print_extracted_outputs(extracted_parameters)
		print("\n\nStage 1 \n\n" )
	
		# Checking if there is extra loss from output conditions
		if optimization_input_parameters['optimization_name']=='loss1':
			check_loss=ofl.calc_check_loss(loss_iter,i,loss_type)
		elif optimization_input_parameters['optimization_name']=='fom1':
			check_loss=off.calc_check_loss(loss_iter,i,loss_type)
		
		
		# Updating the circuit parameters
		circuit_parameters_slope,circuit_parameters_sensitivity=calc_loss_slope(output_conditions,circuit_parameters,loss_iter[i-1],extracted_parameters,optimization_input_parameters)
		
		alpha_parameters=update_alpha_param(optimization_input_parameters,circuit_parameters_sensitivity,alpha_parameters)

		if loss_iter[i-1]['loss']==loss_iter[i-1]['loss_Io']:
			spec_met_flag=1
			alpha_parameters['alpha']=alpha_parameters['fixed_alpha']

		# Updating the value of alpha	
		#alpha_parameters['alpha']=update_alpha(loss_iter,alpha_parameters['alpha'],i,alpha_mult,optimization_type,optimization_input_parameters)
		if (i+1)%500==0 and spec_met_flag==0:		
			alpha_parameters['alpha']=1.03*alpha_parameters['alpha']
		
		if optimization_input_parameters['optimization_name']=='loss1':
			circuit_parameters=ofl.update_circuit_parameters(circuit_parameters,circuit_parameters_slope,check_loss,optimization_input_parameters)
		elif optimization_input_parameters['optimization_name']=='fom1':
			circuit_parameters=off.update_circuit_parameters(circuit_parameters,circuit_parameters_slope,check_loss,optimization_input_parameters)
		
		circuit_parameters=update_L(circuit_parameters)
	
		print("\n\nStage 2 \n\n" )
	
		# Extracting output parameters for new circuit parameters
		extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
		fw.extract_dc_mos(optimization_input_parameters)

		# Updating different dictionaries
		if optimization_input_parameters['optimization_name']=='loss1':
			loss_iter[i]=ofl.calc_loss_1(extracted_parameters,output_conditions,loss_weights)
		elif optimization_input_parameters['optimization_name']=='fom1':
			loss_iter[i]=off.calc_fom_1(extracted_parameters,output_conditions,loss_weights)
			

		# Storing some parameters
		alpha_parameters_iter[i]=alpha_parameters.copy()
		loss_slope_iter[i]=circuit_parameters_slope.copy()
		sensitivity_iter[i-1]=circuit_parameters_sensitivity.copy()
		circuit_parameters_iter[i]={}
		circuit_parameters_iter[i]=circuit_parameters.copy()

		print("\n\nStage 3 \n\n" )
	
		# Storing output parameters list
		output_parameters_iter[i]={}
		for output_param_name in optimization_input_parameters['output_parameters_list']:
			output_parameters_iter[i][output_param_name]=extracted_parameters[output_param_name]
		

		# Storing average parameters ( using a moving average filter )
		n_points=4
		average_parameters_iter=moving_avg(loss_iter,circuit_parameters_iter,average_parameters_iter,i,n_points)
		

		# Printing the values of loss for given iteration
		print('\n--------------------------------------------------------Iteration Number ',i+1,'---------------------------------------------------------')
		print('Loss = ',cf.num_trunc(loss_iter[i]['loss'],3))	
		

		# Updating the value of circuit_parameters
		old_circuit_parameters,circuit_parameters=check_circuit_parameters(old_circuit_parameters,circuit_parameters,
		loss_iter,optimization_input_parameters['update_check'],i,optimization_type)
		#circuit_parameters=update_C2_Rbias(circuit_parameters,extracted_parameters,optimization_input_parameters)
		#circuit_parameters=update_Cload(circuit_parameters,extracted_parameters,optimization_input_parameters)
		circuit_parameters=update_Alo(circuit_parameters,extracted_parameters,optimization_input_parameters)
		
		

		# Checking for stopping condition
		flag_alpha=check_stop_alpha(loss_iter,alpha_parameters['alpha'],i,alpha_min)
		flag_loss=check_stop_loss(loss_iter,i,consec_iter,optimization_type)
		
		print("\n\nStage 5 \n\n" )
	
		
	
		# Incrementing i
		i+=1
		if flag_loss==1 or flag_alpha==1:
			break
	
	# Calculating slope and sensitivity
	circuit_parameters_slope,circuit_parameters_sensitivity=calc_loss_slope(output_conditions,circuit_parameters,loss_iter[i-1],extracted_parameters,optimization_input_parameters)
	sensitivity_iter[i-1]=circuit_parameters_sensitivity.copy()
	
	# Storing the final results
	optimization_results['loss_iter']=loss_iter
	optimization_results['loss_slope_iter']=loss_slope_iter
	optimization_results['alpha_parameters_iter']=alpha_parameters_iter
	optimization_results['output_parameters_iter']=output_parameters_iter
	optimization_results['circuit_parameters_iter']=circuit_parameters_iter
	optimization_results['average_parameters_iter']=average_parameters_iter
	optimization_results['sensitivity_iter']=sensitivity_iter
	optimization_results['n_iter']=i
	
	# Resetting the value of alpha
	optimization_input_parameters['alpha']=alpha_parameters_initial.copy()

	# Finding the best optimization results
	if optimization_input_parameters['optimization_name']=='loss1':
		optimization_results['optimized_results']=ofl.check_best_solution(optimization_results,0)
	elif optimization_input_parameters['optimization_name']=='fom1':
		optimization_results['optimized_results']=off.check_best_solution(optimization_results,0)
		optimization_results['acceptable_solution']=off.check_acceptable_solutions(optimization_results,optimization_input_parameters)

	iter_number=optimization_results['optimized_results']['iter_number']-1
	circuit_parameters=optimization_results['circuit_parameters_iter'][iter_number]
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
		
	return circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results
	
#===========================================================================================================================

def main_opt(circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results):

	# Creating the dictionaries
	loss_iter={} # This dictionary will store the value of all loss values for different iterations
	loss_slope_iter={} # This dictionary will store the value of slope of losses for all parameters for different iterations
	alpha_parameters_iter={} # This dictionary will store the value of threshold for different iterations
	output_parameters_iter={} # This dictionary will store the value of output parameters for different iterations
	circuit_parameters_iter={} # This dictionary will store the value of circuit parameters for different iterations
	average_parameters_iter={}
	sensitivity_iter={}

	
	# Storing the results
	optimization_results['loss_iter']=loss_iter
	optimization_results['loss_slope_iter']=loss_slope_iter
	optimization_results['alpha_parameters_iter']=alpha_parameters_iter
	optimization_results['output_parameters_iter']=output_parameters_iter
	optimization_results['circuit_parameters_iter']=circuit_parameters_iter
	optimization_results['average_parameters_iter']=average_parameters_iter
	optimization_results['sensitivity_iter']=sensitivity_iter
	

	if optimization_input_parameters['iip3_method'] == 'hb_manual_sweep':

		if optimization_input_parameters['simulation_conditions']['hb_sweep_time_save']==1:
			optimization_input_parameters['iip3_method']='hb_single_pin'
			# Writing the name of the netlist directory to tcsh file
			sp.write_tcsh_initial(optimization_input_parameters)
			circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results=main_opt_single(circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results)

		optimization_input_parameters['iip3_method'] = 'hb_manual_sweep'
		# Writing the name of the netlist directory to tcsh file
		sp.write_tcsh_initial(optimization_input_parameters)
		circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results=main_opt_single(circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results)

	else:
		circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results=main_opt_single(circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results)
		
	return circuit_parameters,extracted_parameters,optimization_results
		
	



