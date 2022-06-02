#===========================================================================================================================
"""
Name: Pyneni Roopesh
Roll Number: EE18B028

Netlist Writing File:
"""
#===========================================================================================================================
import numpy as np
import math
import fileinput
import sys
import os
import csv
import common_functions as cf
import data_plot as dp
import pandas as pd
import spectre as sp

#===========================================================================================================================
#-------------------------------------------- Simulation Output Results ----------------------------------------------------
	
#-----------------------------------------------------------------
# Function that stores the data of parameters vs iterations in a csv file
def save_info_single_array_iter(filename_root,filename_name,values_iter,niter):
	
	filename=filename_root+filename_name
	f=open(filename,'w')
	
	#f.truncate(0)
	
	f.write('Iteration No,') # CHANGE
	for param in values_iter[1]:
		f.write(str(param)+',')
	f.write('\n')
	
	i=0
	while i<niter:
		f.write(str(i+1)+',') # CHANGE
		for param in values_iter[i]:
			f.write(str(values_iter[i][param])+',')
		f.write('\n')
		i+=1
	f.close()
	
#-----------------------------------------------------------------
# Function that stores the data of loss slopes vs iterations in a csv file
def save_info_double_array_iter(filename_root,filename_name,values_iter,niter):
	
	filename=filename_root+filename_name
	f=open(filename,'w')
	
	#f.truncate(0)
	
	f.write('Iteration No,') # CHANGE
	for param in values_iter[1]:
		f.write(str(param)+',')
		for categ in values_iter[1][param]:
			f.write(str(categ)+',')
	f.write('\n')
	
	i=0
	while i<niter:
		f.write(str(i+1)+',') # CHANGE
		for param in values_iter[i]:
			f.write(str(param)+',')
			for categ in values_iter[i][param]:
				f.write(str(values_iter[i][param][categ])+',')
		f.write('\n')
		i+=1
	f.close()


	
#-----------------------------------------------------------------
# Function that stores the all the simulation data in different csv files
def save_info(optimization_input_parameters,optimization_results):
	filename=optimization_input_parameters['filename']['output']
	newpath =filename+'/results/'
	if not os.path.exists(newpath):
		os.makedirs(newpath)
		
	loss_slope_iter=optimization_results['loss_slope_iter']
	sensitivity_iter=optimization_results['sensitivity_iter']
	
	#dict_sensitivity=optimization_results['sensitivity']
	
	loss_iter=optimization_results['loss_iter']
	alpha_parameters_iter=optimization_results['alpha_parameters_iter']
	output_parameters_iter=optimization_results['output_parameters_iter']
	circuit_parameters_iter=optimization_results['circuit_parameters_iter']
	average_parameters_iter=optimization_results['average_parameters_iter']
	
	niter=optimization_results['n_iter']
	
	save_info_double_array_iter(newpath,'loss_slope.csv',loss_slope_iter,niter)
	save_info_double_array_iter(newpath,'sensitivity.csv',sensitivity_iter,niter)
	
	save_info_single_array_iter(newpath,'loss.csv',loss_iter,niter)
	save_info_single_array_iter(newpath,'alpha_parameters.csv',alpha_parameters_iter,niter)
	save_info_single_array_iter(newpath,'output_parameters.csv',output_parameters_iter,niter)
	save_info_single_array_iter(newpath,'circuit_parameters.csv',circuit_parameters_iter,niter)
	save_info_single_array_iter(newpath,'average_parameters.csv',average_parameters_iter,niter)
	
	
#===========================================================================================================================
#-------------------------------------------- Simulation Input Results -----------------------------------------------------

#-----------------------------------------------------------------
# Function that prints the filenames
def print_input_results_filenames(f,optimization_input_parameters):
	f.write('\n\n---------------------- Filenames -----------------------')
	f.write('\nMOSFET File   :'+str(optimization_input_parameters['filename']['mos_file']))
	f.write('\nDirectory     :'+str(optimization_input_parameters['filename']['directory']))
	f.write('\nIIP3 Method   :'+str(optimization_input_parameters['iip3_method']))

	f.write('\nTCSH          :'+str(optimization_input_parameters['filename']['tcsh']))
	f.write('\nSpectre Run   :'+str(optimization_input_parameters['filename']['spectre_run']))

#-----------------------------------------------------------------
# Function that prints the output conditions
def print_input_results_output_conditions(f,optimization_input_parameters):
	f.write('\n\n---------------------- Output Conditions -----------------------')
	for name in optimization_input_parameters['output_conditions']:
		f.write('\n'+str(name)+': '+cf.num_trunc(optimization_input_parameters['output_conditions'][name],3))
	
#-----------------------------------------------------------------
# Function that prints the simulation conditions
def print_input_results_simulation_conditions(f,optimization_input_parameters):
	f.write('\n\n---------------------- Simulation Conditions -----------------------')
	for name in optimization_input_parameters['simulation_conditions']:
		f.write('\n'+str(name)+': '+str(optimization_input_parameters['simulation_conditions'][name]))

#-----------------------------------------------------------------
# Function that prints a list
def print_input_results_list(f,optimization_input_parameters,list_name):
	f.write('\n\n---------------------- '+list_name+' -----------------------\n')
	for name in optimization_input_parameters[list_name]:
		f.write(str(name)+', ')

#-----------------------------------------------------------------
# Function that prints the MOS Parameters
def print_input_results_mos_parameters(f,optimization_input_parameters):
	f.write('\n\n---------------------- MOS Parameters -----------------------')
	f.write('\nMOS Type :'+str(optimization_input_parameters['MOS_Type']))
	f.write('\nVdd      :'+str(optimization_input_parameters['Vdd']))
	f.write('\nLmin     :'+str(optimization_input_parameters['Lmin']))

#-----------------------------------------------------------------
# Function that prints the manual circuit parameters
def print_input_results_manual_parameters(f,optimization_input_parameters):
	f.write('\n\n---------------------- Manual Circuit Parameters -----------------------')
	for name in optimization_input_parameters['manual_circuit_parameters']:
		f.write('\n'+str(name)+': '+cf.num_trunc(optimization_input_parameters['manual_circuit_parameters'][name],3))

#-----------------------------------------------------------------
# Function that prints the pre optimization parameters
def print_input_results_pre_optimization(f,optimization_input_parameters):
	f.write('\n\n---------------------- Pre Optimization -----------------------')
	f.write('\nPre_Opt_Type	   :'+str(optimization_input_parameters['pre_optimization']['type']))
	f.write('\nC1_threshold    :'+str(optimization_input_parameters['pre_optimization']['C_threshold']))
	f.write('\nRbias_threshold :'+str(optimization_input_parameters['pre_optimization']['Rbias_threshold']))
	

#-----------------------------------------------------------------
# Function that prints the loss weights
def print_input_results_loss_weights(f,optimization_input_parameters):
	f.write('\n\n---------------------- Loss Weights -----------------------')
	for name in optimization_input_parameters['loss_weights']:
		f.write('\n'+str(name)+': '+cf.num_trunc(optimization_input_parameters['loss_weights'][name],3))

#-----------------------------------------------------------------
# Function that prints the alpha parameters
def print_input_results_alpha_parameters(f,optimization_input_parameters):
    f.write('\n\n---------------------- Alpha Parameters -----------------------')
    for name in optimization_input_parameters['alpha']:
        f.write('\n'+str(name)+': '+cf.num_trunc(optimization_input_parameters['alpha'][name],3))
    f.write('\nAlpha Type  :'+str(optimization_input_parameters['alpha_type']))
    f.write('\nAlpha Start :'+str(optimization_input_parameters['alpha_start']))
    f.write('\nAlpha End   :'+str(optimization_input_parameters['alpha_end']))

#-----------------------------------------------------------------
# Function that prints the optimization parameters
def print_input_results_optimization(f,optimization_input_parameters):
	f.write('\n\n---------------------- Optimization Parameters -----------------------')
	
	f.write('\nMax Iterations :'+str(optimization_input_parameters['max_iteration']))
	f.write('\nAlpha Min      :'+str(optimization_input_parameters['alpha_min']))
	f.write('\nConsec Iter    :'+str(optimization_input_parameters['consec_iter']))
	
	f.write('\nAlpha Mult      :'+str(optimization_input_parameters['alpha_mult']))
	f.write('\nDelta Threshold :'+str(optimization_input_parameters['delta_threshold']))
	f.write('\nLoss Type       :'+str(optimization_input_parameters['loss_type']))
	f.write('\nUpdate Check    :'+str(optimization_input_parameters['update_check']))

	f.write('\nOptimization Name :'+str(optimization_input_parameters['optimization_name']))
	f.write('\nOptimization Type :'+str(optimization_input_parameters['optimization_type']))

	f.write('\nOptimization Parameters : ')
	for name in optimization_input_parameters['optimizing_parameters']:
		f.write(str(name)+' ,')

#-----------------------------------------------------------------
# Function that prints the acceptable solution
def print_input_acceptable_solution(f,optimization_input_parameters):
	if 'acceptable_solution' not in optimization_input_parameters:
		return

	f.write('\n\n---------------------- Acceptable Solution Parameters -----------------------')
	for name in optimization_input_parameters['acceptable_solution']:
		f.write('\n'+str(name)+': '+cf.num_trunc(optimization_input_parameters['acceptable_solution'][name],3))

#-----------------------------------------------------------------
# Function that prints additional information
def print_input_extra_notes(f):
	f.write('\n\n------------- Note ------------------')
	f.write('\nLoss Type is 1 for normal gradient descent')
	f.write('\nLoss Type is 0 for gradient descent with slope of Io is only considered when other losses are 0 and Io slope is ignored otherwise')
	f.write('\n\nUpdate Check is 1 if we want to perform next iteration with the a previous result having the smaller loss')
	f.write('\nUpdate Check is 0 fif we will perform next iteration with present circuit parameters')


#-----------------------------------------------------------------
# Function that stores input and output data of the simulation
def save_input_results(optimization_input_parameters):
	filename=optimization_input_parameters['filename']['output']
	newpath =filename+'/'
	if not os.path.exists(newpath):
		os.makedirs(newpath)
		
	filename=filename+str('/input_data.txt')
	f=open(filename,'w')

	#print_input_results_filenames(f,optimization_input_parameters)
	print_input_results_output_conditions(f,optimization_input_parameters)
	print_input_results_simulation_conditions(f,optimization_input_parameters)
	print_input_results_list(f,optimization_input_parameters,'circuit_parameters_list')
	print_input_results_list(f,optimization_input_parameters,'output_parameters_list')
	print_input_results_mos_parameters(f,optimization_input_parameters)
	print_input_results_manual_parameters(f,optimization_input_parameters)
	print_input_results_pre_optimization(f,optimization_input_parameters)
	print_input_results_loss_weights(f,optimization_input_parameters)
	print_input_results_alpha_parameters(f,optimization_input_parameters)
	print_input_results_optimization(f,optimization_input_parameters)
	print_input_acceptable_solution(f,optimization_input_parameters)
	print_input_extra_notes(f)
	
	f.close()
	
#===========================================================================================================================
#-------------------------------------------- Simulation Output Results ----------------------------------------------------

#-----------------------------------------------------------------
# Function that prints parameters
def print_output_parameters(f,parameters):
	for param_name in parameters:
		f.write('\n'+str(param_name)+': '+cf.num_trunc(parameters[param_name],3))

#-----------------------------------------------------------------
# Function that prints parameters
def print_output_mos_parameters(f,optimization_results):
	f.write('\n\n---------------- MOS Parameters ----------------------------------')
	for param_name in optimization_results['mos_parameters']:
		f.write('\n'+str(param_name)+': '+cf.num_trunc(optimization_results['mos_parameters'][param_name],3))

#-----------------------------------------------------------------
# Function that stores input and output data of the simulation
def save_output_results(optimization_results,optimization_input_parameters):
	filename=optimization_input_parameters['filename']['output']
	newpath =filename+'/'
	if not os.path.exists(newpath):
		os.makedirs(newpath)
		
	filename=filename+str('/output_data.txt')
	f=open(filename,'w')

	print_dict=optimization_results['optimized_results']
	iter_number=print_dict['iter_number']-1
	
	f.write('\n-------------------------------------------------------------------')
	if optimization_input_parameters['optimization_name']=='loss1':
		f.write('\nMaximum Loss of gain+Io+s11+iip3='+cf.num_trunc(print_dict['loss_max'],3))
		f.write('\nOptimized Point occured at iteration='+str(print_dict['iter_number']))
		f.write('\nOptimized Io Loss='+cf.num_trunc(print_dict['Io_loss'],3))
	
	elif optimization_input_parameters['optimization_name']=='fom1':
		f.write('\nMaximum Loss of s11='+cf.num_trunc(print_dict['loss_max'],3))
		f.write('\nOptimized Point occured at iteration='+str(print_dict['iter_number']))
		f.write('\nOptimized FOM in dB='+cf.num_trunc(print_dict['FOM'],3))
	
	"""
	f.write('\n\n------------------------- Output Parameter Values ----------------------------------------')
	for name in optimization_results['output_parameters_iter'][iter_number]:
		f.write('\n'+str(name)+': '+cf.num_trunc(optimization_results['output_parameters_iter'][iter_number][name],3))
		
	f.write('\n\n------------------------- Circuit Parameter Values ----------------------------------------')
	for name in optimization_results['circuit_parameters_iter'][iter_number]:
		f.write('\n'+str(name)+': '+cf.num_trunc(optimization_results['circuit_parameters_iter'][iter_number][name],3))
	"""
	
	f.write('\n\n------------------------- Circuit Parameter Values ----------------------------------------')
	print_output_parameters(f,optimization_results['circuit_parameters_iter'][iter_number])
	
	f.write('\n\n------------------------- Output Parameter Values ----------------------------------------')
	print_output_parameters(f,optimization_results['output_parameters_iter'][iter_number])

	if 'acceptable_solution' in optimization_results:
		f.write('Acceptable Solutions:\n')
		for i in optimization_results['acceptable_solution']:
			f.write(str(i)+' ; ')
		
	f.write('\n\nTime Taken to Run (hh/mm/ss.) = '+str(optimization_results['time']))

	print_output_mos_parameters(f,optimization_results)

	if 'manual_hc' in optimization_results:
		f.write('\n\n--------------------- Manual Hand Calculations ---------------------------------')
		f.write('\n\n---------------- Circuit Parameters ------------------------')
		print_output_parameters(f,optimization_results['manual_hc']['circuit_parameters'])
		f.write('\n\n---------------- Extracted Parameters ------------------------')
		print_output_parameters(f,optimization_results['manual_hc']['extracted_parameters'])

	if 'auto_hc' in optimization_results:
		f.write('\n\n--------------------- Automatic Hand Calculations ---------------------------------')
		f.write('\n\n---------------- Circuit Parameters ------------------------')
		print_output_parameters(f,optimization_results['auto_hc']['circuit_parameters'])
		f.write('\n\n---------------- Extracted Parameters ------------------------')
		print_output_parameters(f,optimization_results['auto_hc']['extracted_parameters'])

	if 'hc_update' in optimization_results:
		f.write('\n\n--------------------- Hand Calculations Update ---------------------------------')
		f.write('\n\n---------------- Circuit Parameters ------------------------')
		print_output_parameters(f,optimization_results['hc_update']['circuit_parameters'])
		f.write('\n\n---------------- Extracted Parameters ------------------------')
		print_output_parameters(f,optimization_results['hc_update']['extracted_parameters'])

	if 'gm_update' in optimization_results:
		f.write('\n\n--------------------- gm Update ---------------------------------')
		f.write('\n\n---------------- Circuit Parameters ------------------------')
		print_output_parameters(f,optimization_results['gm_update']['circuit_parameters'])
		f.write('\n\n---------------- Extracted Parameters ------------------------')
		print_output_parameters(f,optimization_results['gm_update']['extracted_parameters'])

	if 'gmvd_update' in optimization_results:
		f.write('\n\n--------------------- gmvd Update ---------------------------------')
		f.write('\n\n---------------- Circuit Parameters ------------------------')
		print_output_parameters(f,optimization_results['gmvd_update']['circuit_parameters'])
		f.write('\n\n---------------- Extracted Parameters ------------------------')
		print_output_parameters(f,optimization_results['gmvd_update']['extracted_parameters'])

	if 'optimization_start' in optimization_results:
		f.write('\n\n--------------------- Optimization Start ---------------------------------')
		f.write('\n\n---------------- Circuit Parameters ------------------------')
		print_output_parameters(f,optimization_results['optimization_start']['circuit_parameters'])
		f.write('\n\n---------------- Extracted Parameters ------------------------')
		print_output_parameters(f,optimization_results['optimization_start']['extracted_parameters'])
		
	f.close()


#------------------------------------------------------------------------------------------------------------------------------------
#Writes all the Mosfet DC Parameters to a file
def extract_dc_mos(optimization_input_parameters):
	file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/all_mos_dc.out'
	save_path=optimization_input_parameters['filename']['output']
	lines=sp.extract_file(file_name)

	lines=lines[7:]
	lines=lines[0].split()

	all_dc={}
	mosfet_count=7
	param_list=['gm','gds','vth','vdsat','cgs','cgd','region']

	count=1
	for i in range(mosfet_count):
		mos_name='M'+str(i)
		for j in range(len(param_list)):
			all_dc[mos_name+'_'+param_list[j]]=cf.num_trunc(float(lines[count]),3)
			count=count+1
			

	if not os.path.exists(save_path):
			os.makedirs(save_path)

	f=open(save_path+'/All_mos_dc.txt','w')
	for i in range(mosfet_count):
		mos_name='M'+str(i)
		for j in range(len(param_list)):
			f.write(mos_name+'_'+param_list[j]+'    \t\t:\t   '+str(all_dc[mos_name+'_'+param_list[j]])+'\n')
		f.write('---------------------------------------------------------\n')
	f.close()


#===========================================================================================================================

#-------------------------------------------- Temperature Variation Results ----------------------------------------------------

def save_output_temp_var(opt_param_temp_var_dict,optimization_input_parameters):
	
	filepath=optimization_input_parameters['filename']['output']+'/Temp_variation/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)

	filename=filepath+'temp_var.csv'
	f=open(filename,'w')
	writer=csv.writer(f)
	
	extracted_parameters=opt_param_temp_var_dict[0]
	temp_list=optimization_input_parameters['temp_list']	

	header = ['Temperature']
	for param_name in extracted_parameters:
		header.append(param_name)

	writer.writerow(header)

	for i in range(len(opt_param_temp_var_dict)):
		row=[]
		row.append(temp_list[i])
		extracted_parameters=opt_param_temp_var_dict[i]
		for param_name in extracted_parameters:
			row.append(extracted_parameters[param_name])
		writer.writerow(row)

	f.close()
	dp.plot_temp_var_plots(filename,filepath,optimization_input_parameters)


#-------------------------------------------- Temperature and Current Variation Results ----------------------------------------------------

def save_output_temp_var_with_current(Io_list,opt_param_temp_var_dict,optimization_input_parameters):
	
	filepath=optimization_input_parameters['filename']['output']+'/Temperature_current_variation/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)

	filename=filepath+'temp_cur_var.csv'
	f=open(filename,'w')
	writer=csv.writer(f)
	
	extracted_parameters=opt_param_temp_var_dict[0][0]
	temp_list=optimization_input_parameters['temp_list']	

	header = ['Input_Current','Temperature']
	for param_name in extracted_parameters:
		header.append(param_name)

	writer.writerow(header)

	for j in range(len(Io_list)):
		row=[]
		row.append(Io_list[j])
		for i in range(len(opt_param_temp_var_dict[j])):
			row.append(temp_list[i])
			extracted_parameters=opt_param_temp_var_dict[j][i]
			for param_name in extracted_parameters:
				row.append(extracted_parameters[param_name])

			writer.writerow(row)
			row=row[:1]

	f.close()
	dp.plot_temp_with_current_var_plots(filename,filepath,optimization_input_parameters,Io_list)
	


#-------------------------------------------- Temperature Variation Results ----------------------------------------------------

def save_output_temp_process_var(opt_param_temp_var_dict,optimization_input_parameters):
	
	filepath=optimization_input_parameters['filename']['output']+'/Temp_Process_variation/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)

	filename=filepath+'temp_process_var.csv'
	f=open(filename,'w')
	writer=csv.writer(f)
	
	extracted_parameters=opt_param_temp_var_dict[0][0]
	temp_list=optimization_input_parameters['temp_list']	

	header = ['Corner','Temperature']
	for param_name in extracted_parameters:
		header.append(param_name)

	writer.writerow(header)

	for i in range(len(opt_param_temp_var_dict)):
		row=[]
		
		extracted_parameters=opt_param_temp_var_dict[i][0]
		model_name=opt_param_temp_var_dict[i][1]
		Temperature=opt_param_temp_var_dict[i][2]

		row.append(model_name)
		row.append(Temperature)

		for param_name in extracted_parameters:
			row.append(extracted_parameters[param_name])
		writer.writerow(row)

	f.close()
	dp.plot_temp_process_var_plots(filename,filepath,optimization_input_parameters)


	
#===========================================================================================================================






















