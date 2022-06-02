#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

Main Code:
"""
#===========================================================================================================================
import numpy as np
import math
import complete_optimization as co
import data_plot as dp
import spectre as sp
import temp_var as tv


#===========================================================================================================================
#------------------------------------Main Program Code----------------------------------------------------------------------

# Creating a dictionary with the optimization parameters
optimization_input_parameters={}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# File Names
optimization_input_parameters['filename']={}

#----------------------------------------------------
optimization_input_parameters['model_type']='pkg'		# Options : 'lib' , 'pkg'
optimization_input_parameters['model_name']='tsmc065_tt'
optimization_input_parameters['model_process_corners']=['tsmc065_tt','tsmc065_ff','tsmc065_ss']		# This is valid for only package type
optimization_input_parameters['circuit_type']='non_ideal'	# options : 'ideal' , 'non_ideal'       # if non ideal, then no ideal components

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MOSFET Parameters

#'''
optimization_input_parameters['filename']['mos_file']='TSMC065 Package'
optimization_input_parameters['MOS_Type']='NMOS'
optimization_input_parameters['Lmin']=60*1e-9
optimization_input_parameters['Vdd']=1
#'''

"""
optimization_input_parameters['filename']['mos_file']='/home/ee18b028/cadence_project/tsmc018.scs'
optimization_input_parameters['MOS_Type']='NMOS'
optimization_input_parameters['Lmin']=0.18*1e-6
optimization_input_parameters['Vdd']=1.8
"""

"""
optimization_input_parameters['filename']['mos_file']='/home/ee18b028/cadence_project/ibm013.scs'
optimization_input_parameters['MOS_Type']='NMOS'
optimization_input_parameters['Lmin']=0.13*1e-6
optimization_input_parameters['Vdd']=1.3
"""


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# File Names ( continuation )

#optimization_input_parameters['filename']['directory']='/home/ee18b064/cadence_project/CGA_LNA_autogen/'+optimization_input_parameters['circuit_type']+'/'   ## Single ended CGA location
optimization_input_parameters['filename']['directory']='/home/ee18b064/cadence_project/CGA_LNA_differential/'+optimization_input_parameters['circuit_type']+'/'   ## Differential ended CGA location


optimization_input_parameters['iip3_method']='basic_pss' # Options : 'basic_hb', 'basic_pss', 'advanced_hb', 'advanced_pss', 'hb_sweep' , 'hb_manual_sweep' , 'hb_single_pin' , 'hb_single_pin_diff' , 'hb_manual_sweep_diff'


optimization_input_parameters['filename']['working_directory']='/home/ee18b064/Optimization/Cadence_Current_Optimisation/'

optimization_input_parameters['filename']['library_yaml']='/home/ee18b064/Optimization/Cadence_Current_Optimisation/library.yml'

optimization_input_parameters['filename']['mos_param_yaml']='/home/ee18b064/Optimization/Cadence_Current_Optimisation/mos_param.yml'


optimization_input_parameters['filename']['tcsh']='/home/ee18b064/Optimization/Cadence_Current_Optimisation/spectre_run.tcsh'

optimization_input_parameters['filename']['spectre_run']='tcsh /home/ee18b064/Optimization/Cadence_Current_Optimisation/spectre_run.tcsh'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Output Conditions
fo=1e9
optimization_input_parameters['output_conditions']={
	's11_db':-15.0,
	'iip3_dbm':-5.0,
	'gain_db':10.0,
	'nf_db':4.0,
	'fo':fo,
	'f_lower':50e6,
	'f_upper':2*fo,
	'wo':2.0*np.pi*fo,
	'delta_v':0.1,
	'Rs':50
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Simulation Conditions
optimization_input_parameters['simulation_conditions']={
	'hb_sweep_time_save':0,
	'iip3_errpreset':'conservative',  # Available methods : ['conservative'-Accurate  ,  'moderate'  ,   'liberal'-Not very Accurate]
	'pin_iip3':-65,
	'f_delta_iip3':1e6
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parameters List
optimization_input_parameters['circuit_parameters_list']=['Rb','Rd','Io','C1','C2','W','Rbias','fo','Temp']
optimization_input_parameters['output_parameters_list']=['Io','gain_db','gain_fo','gain_lower','gain_upper','f_lower','f_upper','iip3_dbm','s11_db','s12_db','s21_db','s22_db','Kf','nf_db','p_source','gm1','vdsat','vg','vd','vs']
optimization_input_parameters['output_specs_params_list']=['gain_db','iip3_dbm','s11_db','nf_db']
optimization_input_parameters['cir_writing_dict']={'wid':'W','cur0':'Io','Resb':'Rb','Resd':'Rd','cap1':'C1','cap2':'C2','Resbias':'Rbias','fund_1':'fo','f_lower':'f_lower','f_upper':'f_upper','cir_temp':'Temp'}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Manual Hand Calculations
optimization_input_parameters['manual_circuit_parameters']={
	'Rb':348.415939694684,
	'Rd':253.848816243181,
	'Io':0.001006211176245,
	'C1':3.92222900057188E-11,
	'C2':1.09379321898551E-11,
	'W':0.000159141948323,
	'Rbias':1000,
	'fo':fo,
	'f_lower':50000000,
	'f_upper':2000000000,
	'Temp':27
}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parameters for steps pre optimization
optimization_input_parameters['pre_optimization']={}

optimization_input_parameters['pre_optimization']['Step1b_Limit']=5
optimization_input_parameters['pre_optimization']['Step2_Limit']=5
optimization_input_parameters['pre_optimization']['vdsat_reqd']=0.09

optimization_input_parameters['pre_optimization']['type']='manual'				#Available Methods : ['manual' , 1]
optimization_input_parameters['pre_optimization']['gmrs_threshold']=0.2
optimization_input_parameters['pre_optimization']['vdsat_threshold']=0.02
optimization_input_parameters['pre_optimization']['vosw_threshold']=0.1


optimization_input_parameters['pre_optimization']['C1_threshold']=1e2
optimization_input_parameters['pre_optimization']['C2_threshold']=20
optimization_input_parameters['pre_optimization']['Rbias_threshold']=10



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assigning values to the loss weights
loss_weights={}
loss_weights['gain_db']=1/abs(optimization_input_parameters['output_conditions']['gain_db'])	
loss_weights['iip3_dbm']=1/abs(optimization_input_parameters['output_conditions']['iip3_dbm'])
loss_weights['s11_db']=1/abs(optimization_input_parameters['output_conditions']['s11_db'])	
loss_weights['nf_db']=1/abs(optimization_input_parameters['output_conditions']['nf_db'])	
loss_weights['Io']=500	
optimization_input_parameters['loss_weights']=loss_weights


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assigning Values of Alpha
alpha_parameters={}
alpha_parameters['alpha']=0.04
alpha_parameters['Rb']=1
alpha_parameters['Rd']=1
alpha_parameters['W']=1
alpha_parameters['Io']=1
alpha_parameters['C1']=1
alpha_parameters['C2']=1
optimization_input_parameters['alpha']=alpha_parameters

optimization_input_parameters['alpha_type']='Normal'
optimization_input_parameters['alpha_start']=0.8
optimization_input_parameters['alpha_end']=0.05


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parameters for Optimization
optimization_input_parameters['max_iteration']	=10
optimization_input_parameters['alpha_min']	=-1
optimization_input_parameters['consec_iter']	=-1

optimization_input_parameters['delta_threshold']=0.01
optimization_input_parameters['alpha_mult']	=1
optimization_input_parameters['loss_type']	=0
optimization_input_parameters['update_check']	=0

optimization_input_parameters['optimizing_parameters']=['Rb','Rd','Io','W','C1','C2']

optimization_input_parameters['optimization_name']='loss1'
optimization_input_parameters['optimization_type']=0


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# list of Temperatures at which we solve the circuit
optimization_input_parameters['temp_var']={}
optimization_input_parameters['temp_var']['run_temp_cur_var']=0
optimization_input_parameters['temp_var']['run_temp_var']=0
optimization_input_parameters['temp_var']['run_temp_process_var']=0

temp_list=np.linspace(-40,120,21)
optimization_input_parameters['temp_list']=temp_list


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Creating the location for the files
f_directory='/home/ee18b064/Optimization/Cadence_Current_Optimisation/Simulation_Results/LOSS/'

file_choose='S' # 'S' to run a single time; 'M' to run multiple times


if file_choose=='S':

	# ------- Set Any Additional Parameters Here --------
	filename=f_directory+'wideband_final'						# SET THE FILENAME HERE
	optimization_input_parameters['max_iteration']=1
	optimization_input_parameters['iip3_method']='hb_single_pin_diff'
	#tv.temperature_variation(optimization_input_parameters)	
	# ------- Set Any Additional Parameters Here --------
	

	# ------- DON'T CHANGE THESE LINES -------------
	optimization_input_parameters['filename']['output']=filename
	co.complete_optimization(optimization_input_parameters)			
	dp.plot_complete(optimization_input_parameters)			
	# ------- DON'T CHANGE THESE LINES -------------		


#===========================================================================================================================


