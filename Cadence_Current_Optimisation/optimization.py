#===========================================================================================================================
"""
Name: Pyneni Roopesh
Roll Number: EE18B028

Optimization Algorithm:
"""
#===========================================================================================================================
import numpy as np
import math
import os
import time
import datetime
import common_functions as cf
import spectre as sp
import optimization_functions_loss as ofl
import multiprocessing
import fileinput
#import optimization_functions_fom as off

#===========================================================================================================================
#------------------------------------Defining the functions -----------------------------------------

	
#-----------------------------------------------------------------------------------------------
# This function calculates the gradient 
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
			percent_change=(final_param-initial_param)/(initial_param*increment_factor)
			circuit_parameters_sensitivity[param_name][categ_name]=percent_change
		
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
def update_alpha_param ():
	pass


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
	average_parameters[i]['Io']=0
		
	if i<n_points:
		for j in range(i+1):
			#average_parameters[i]['loss_Io']+=loss_iter[i-j]['loss_Io']
			average_parameters[i]['Io']+=circuit_parameters_iter[i-j]['Io']
		#average_parameters[i]['loss_Io']/=(i+1)
		average_parameters[i]['Io']/=(i+1)
	else:
		for j in range(n_points):
			#average_parameters[i]['loss_Io']+=loss_iter[i-j]['loss_Io']
			average_parameters[i]['Io']+=circuit_parameters_iter[i-j]['Io']
		#average_parameters[i]['loss_Io']/=n_points
		average_parameters[i]['Io']/=n_points
		
	return average_parameters

#----------------------------------------------------------------------------------------------------------------
# Command that returns the string that has to be printed in the .cir file
def print_param(param_var,val):
	return "parameters "+param_var+'='+str(val)+'\n'


def scs_file_generate(circuit_parameters,optimization_input_parameters,main_file_path,out_file_dir):
	
	param_list=optimization_input_parameters['optimizing_parameters']

	cir_dict={}
	for cir_param in optimization_input_parameters['cir_writing_dict']:
		cir_dict[optimization_input_parameters['cir_writing_dict'][cir_param]]=cir_param
	


	'''f=open(main_file_path)
	lines=f.readlines()
	f.close()
	
	s=''
	for line in lines:
		s=s+line'''

	increment_factor=optimization_input_parameters['delta_threshold'] #parameter increases by increment_factor*parameter
	
	for param in param_list:
		s=''
		file_dir=out_file_dir+'slope_'+param+'/'
		out_file_path=file_dir+'circ.scs'

		if not os.path.exists(file_dir):
			os.makedirs(file_dir)
		
				
		write_dict=sp.dict_convert(circuit_parameters,optimization_input_parameters)
		circuit_parameters[param]=circuit_parameters[param]*(1+increment_factor)
		for line in fileinput.input(main_file_path):
			if "parameters "+cir_dict[param]+'=' in line:
				line=line.replace(line,print_param(cir_dict[param],circuit_parameters[param]))
			s=s+line
	
		f_out=open(out_file_path,'w')
		f_out.write(s)
		f_out.close()


#-----------------------------------------------------------------------------------------------
def tcsh_file_generate(param_list,out_file_dir):

	for param in param_list:
		out_file_path=out_file_dir+'tcsh_run_'+param+'.tcsh'

		if not os.path.exists(out_file_dir):
			os.makedirs(out_file_dir)
	
		s=''
	
		s='#tcsh\n'
		s=s+'source ~/.cshrc\n'
		s=s+'cd '+out_file_dir+'slope_'+param+'\n'
		s=s+'spectre circ.scs =log display.log\n'
		s=s+'exit'

		f_out=open(out_file_path,'w')
		f_out.write(s)
		f_out.close()


#-----------------------------------------------------------------------------------------------
def run_specific_file(spectre_run_command):
	#os.system(file_dir)
	os.system(spectre_run_command)

def run_files_parallel(param_list,out_file_dir):
	
	args=[]

	for param in param_list:
		args.append('tcsh '+out_file_dir+'tcsh_run_'+param+'.tcsh')

	
	pool = multiprocessing.Pool()
	
	outputs = pool.map(run_specific_file, args)
	pool.close()
	pool.join()

#-----------------------------------------------------------------------------------------------
# This function updates the values of circuit parameters by trying to minimize loss
def calc_loss_slope_parallel(output_conditions,circuit_parameters,loss_dict,extracted_parameters,optimization_input_parameters):

	loss_weights=optimization_input_parameters['loss_weights']
	delta_threshold=optimization_input_parameters['delta_threshold']
	
	# Getting the sensitivity dictionary
	circuit_parameters_sensitivity={}
	for param_name in optimization_input_parameters['optimizing_parameters']:
		circuit_parameters_sensitivity[param_name]=0
	
	# Creating new dictionaries
	circuit_parameters1=circuit_parameters.copy() #store the values of parameters after increment to calculate the slope
	extracted_parameters1=extracted_parameters.copy() # store the values of parameters after increment to calculate the slope
	circuit_parameters_slope={} # Tstore the values of slope of different losses with change of all circuit parameters


	
	main_file_path=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.scs'
	out_file_dir=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/slope_duplicates/'

	scs_file_generate(circuit_parameters1.copy(),optimization_input_parameters,main_file_path,out_file_dir)
	tcsh_file_generate(optimization_input_parameters['optimizing_parameters'],out_file_dir)
	run_files_parallel(optimization_input_parameters['optimizing_parameters'],out_file_dir)

	# Calculating the value to update each parameter with
	for param_name in optimization_input_parameters['optimizing_parameters']:
		
		# Calculating the increment value
		increment_factor=delta_threshold # The value by which parameter increases = increment_factor*parameter
		increment=circuit_parameters[param_name]*increment_factor
	
	
		# Incrementing the circuit parameter
		circuit_parameters1=circuit_parameters.copy()
		circuit_parameters1[param_name]=circuit_parameters1[param_name]+increment
		
		
		# Extracting Loss
		#extracted_parameters1=sp.write_extract(circuit_parameters1,optimization_input_parameters)
		extracted_parameters1=sp.extract_output_param(optimization_input_parameters,out_file_dir+'slope_'+param_name)
		
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
			percent_change=(final_param-initial_param)/(initial_param*increment_factor)
			circuit_parameters_sensitivity[param_name][categ_name]=percent_change
		
	return circuit_parameters_slope,circuit_parameters_sensitivity


		
#===========================================================================================================================
#--------------------------------------------Output Functions---------------------------------------------------------------
	
#---------------------------------------------------------------------------------------------------------------------------
# Function to do main optimization
def main_opt_single(circuit_parameters,extracted_parameters,optimization_input_parameters,optimization_results):

	# Defining some values
	i=0
	
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
	
	# Running spectre
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
	
		# Checking if there is extra loss from output conditions
		if optimization_input_parameters['optimization_name']=='loss1':
			check_loss=ofl.calc_check_loss(loss_iter,i,loss_type)
		elif optimization_input_parameters['optimization_name']=='fom1':
			check_loss=off.calc_check_loss(loss_iter,i,loss_type)
		
		
		# Updating the circuit parameters
		time_start=datetime.datetime.now()
		#circuit_parameters_slope,circuit_parameters_sensitivity=calc_loss_slope(output_conditions,circuit_parameters,loss_iter[i-1],extracted_parameters,optimization_input_parameters)								 
		circuit_parameters_slope,circuit_parameters_sensitivity=calc_loss_slope_parallel(output_conditions,circuit_parameters,loss_iter[i-1],extracted_parameters,optimization_input_parameters)

		if optimization_input_parameters['optimization_name']=='loss1':
			circuit_parameters=ofl.update_circuit_parameters(circuit_parameters,circuit_parameters_slope,check_loss,optimization_input_parameters)
		elif optimization_input_parameters['optimization_name']=='fom1':
			circuit_parameters=off.update_circuit_parameters(circuit_parameters,circuit_parameters_slope,check_loss,optimization_input_parameters)
		
		time_end=datetime.datetime.now()
		print("\n\nGradient finding time : ",time_end-time_start,'\n\n')
	
		# Extracting output parameters for new circuit parameters
		extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
		

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
		

		# Updating the value of alpha	
		alpha_parameters['alpha']=update_alpha(loss_iter,alpha_parameters['alpha'],i,alpha_mult,optimization_type,optimization_input_parameters)
		

		# Updating the value of circuit_parameters
		old_circuit_parameters,circuit_parameters=check_circuit_parameters(old_circuit_parameters,circuit_parameters,
		loss_iter,optimization_input_parameters['update_check'],i,optimization_type)
		circuit_parameters=update_C2_Rbias(circuit_parameters,extracted_parameters,optimization_input_parameters)
		

		# Checking for stopping condition
		flag_alpha=check_stop_alpha(loss_iter,alpha_parameters['alpha'],i,alpha_min)
		flag_loss=check_stop_loss(loss_iter,i,consec_iter,optimization_type)
		

		# Incrementing i
		i+=1
		if flag_loss==1 or flag_alpha==1:
			break
	
	# Calculating slope and sensitivity
	#circuit_parameters_slope,circuit_parameters_sensitivity=calc_loss_slope(output_conditions,circuit_parameters,loss_iter[i-1],extracted_parameters,optimization_input_parameters)
	circuit_parameters_slope,circuit_parameters_sensitivity=calc_loss_slope_parallel(output_conditions,circuit_parameters,loss_iter[i-1],extracted_parameters,optimization_input_parameters)
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
		
	



