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


optimization_input_parameters['filename']['mos_file']='TSMC065 Package'
optimization_input_parameters['MOS_Type']='NMOS'
optimization_input_parameters['Lmin']=60*1e-9
optimization_input_parameters['Vdd']=1
optimization_input_parameters['Vgs_req']=0.48

"""
optimization_input_parameters['filename']['mos_file']='/home/ee18b028/cadence_project/tsmc018.scs'
optimization_input_parameters['MOS_Type']='NMOS'
optimization_input_parameters['Lmin']=0.18*1e-6
optimization_input_parameters['Vdd']=1.8
optimization_input_parameters['Vgs_req']=0.55
"""

'''
optimization_input_parameters['filename']['mos_file']='/home/ee18b028/cadence_project/ibm013.scs'
optimization_input_parameters['MOS_Type']='NMOS'
optimization_input_parameters['Lmin']=0.13*1e-6
optimization_input_parameters['Vdd']=1.3
optimization_input_parameters['Vgs_req']=0.55
'''

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# File Names ( continuation )

optimization_input_parameters['filename']['directory']='/home/ee18b064/cadence_project/Double_Balanced_Mixer/'+optimization_input_parameters['circuit_type']+'/'   ## Single ended CGA location


optimization_input_parameters['iip3_method']='hb_single_pin' # Options : 'basic_hb', 'basic_pss', 'advanced_hb', 'advanced_pss', 'hb_sweep' , 'hb_manual_sweep' , 'hb_single_pin' , 'hb_single_pin_diff' , 'hb_manual_sweep_diff'


optimization_input_parameters['filename']['working_directory']='/home/ee18b064/Optimization/Mixer_optimization/'
optimization_input_parameters['filename']['multiple_files']=1

optimization_input_parameters['filename']['library_yaml']='/home/ee18b064/Optimization/Mixer_optimization/library.yml'

optimization_input_parameters['filename']['mos_param_yaml']='/home/ee18b064/Optimization/Mixer_optimization/mos_param.yml'


optimization_input_parameters['filename']['tcsh']='/home/ee18b064/Optimization/Mixer_optimization/spectre_run.tcsh'
optimization_input_parameters['filename']['tcsh_iip3']='/home/ee18b064/Optimization/Mixer_optimization/spectre_run_iip3.tcsh'

optimization_input_parameters['filename']['tcsh_run']='tcsh /home/ee18b064/Optimization/Mixer_optimization/spectre_run.tcsh'
optimization_input_parameters['filename']['tcsh_iip3_run']='tcsh /home/ee18b064/Optimization/Mixer_optimization/spectre_run_iip3.tcsh'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Output Conditions

optimization_input_parameters['output_conditions']={
	'iip3_dbm':-10.0,
	'iip2_dbm':40,
	'conv_gain_db':16.0,
	'nf_db':15.0,
	'flo':1e9,
	'frf':1.01e9,
	'bb_BW':1e6,
	'region':2
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Simulation Conditions
optimization_input_parameters['simulation_conditions']={
	'hb_sweep_time_save':0,
	'iip3_errpreset':'moderate',  # Available methods : ['conservative'-Accurate  ,  'moderate'  ,   'liberal'-Not very Accurate]
	'pin_iip3':-65,
	'f_delta_iip3':1e6,
	'mismatch':0.001
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parameters List
optimization_input_parameters['circuit_parameters_list']=['Rd','Ibias','C1','C2','Cload','W1','W2','Rbias1','Rbias2','Rbias3','flo','mismatch','frf','Alo','Temp']
optimization_input_parameters['output_parameters_list']=['Io','conv_gain_db','iip3_dbm','iip2_dbm','nf_db','p_src','gm1','vdsat1','vg1','vd1','bb_BW','gm2','gds1','region']
optimization_input_parameters['output_specs_params_list']=['conv_gain_db','iip3_dbm','iip2_dbm','nf_db','bb_BW','region']
optimization_input_parameters['cir_writing_dict']={'wid1':'W1','wid2':'W2','cur0':'Ibias','Resd':'Rd','cap1':'C1','cap2':'C2','cap3':'Cload','mismatch':'mismatch','Resbias1':'Rbias1','Resbias2':'Rbias2','Resbias3':'Rbias3','f_lo':'flo','f_rf':'frf','cir_temp':'Temp','ampl_lo':'Alo'}


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Manual Hand Calculations
optimization_input_parameters['manual_circuit_parameters']={
	'Rd':228.20462153614875,
	'Ibias':0.004147335185231752,
	'C1':8.924088e-12,
	'C2':9.072181999999999e-12,
	'Cload':6.97562922955008e-11,
	'W1':0.0008993817044672005,
	'W2':0.000316174483274684,
	'Rbias1':3531.5463401108104,
	'Rbias2':1522.411749283791,
	'Rbias3':861.8322182441458,
	'mismatch':0,
	'flo':1e9,
	'frf':1.01e9,
	'Alo':0.2916661346480465,
	'Temp':27
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parameters for steps pre optimization
optimization_input_parameters['pre_optimization']={}

optimization_input_parameters['pre_optimization']['type']=1				#Available Methods : ['manual' , 1]
optimization_input_parameters['pre_optimization']['ampl_threshold']=2
optimization_input_parameters['pre_optimization']['sat_threshold']=75e-3
optimization_input_parameters['pre_optimization']['body_threshold']=100e-3
optimization_input_parameters['pre_optimization']['C_threshold']=200
optimization_input_parameters['pre_optimization']['Rbias_threshold']=200

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assigning values to the loss weights
loss_weights={}
loss_weights['conv_gain_db']=3/abs(optimization_input_parameters['output_conditions']['conv_gain_db'])	
loss_weights['iip3_dbm']=1/abs(optimization_input_parameters['output_conditions']['iip3_dbm'])
loss_weights['iip2_dbm']=1/abs(optimization_input_parameters['output_conditions']['iip2_dbm'])	
loss_weights['nf_db']=1/abs(optimization_input_parameters['output_conditions']['nf_db'])
loss_weights['bb_BW']=1/abs(optimization_input_parameters['output_conditions']['bb_BW'])
loss_weights['region']=1/abs(optimization_input_parameters['output_conditions']['region'])	
loss_weights['Io']=200	
optimization_input_parameters['loss_weights']=loss_weights


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assigning Values of Alpha
alpha_parameters={}
alpha_parameters['alpha']=100e-3   # may change during iterations
alpha_parameters['fixed_alpha']=60e-3 # Will not change during iterations
alpha_parameters['Rd']=1
alpha_parameters['W2']=1
alpha_parameters['W1']=1
alpha_parameters['Ibias']=1
alpha_parameters['Alo']=1
alpha_parameters['Rbias2']=1
alpha_parameters['Rbias3']=1
optimization_input_parameters['alpha']=alpha_parameters

optimization_input_parameters['alpha_type']='Normal'
optimization_input_parameters['alpha_start']=0.8
optimization_input_parameters['alpha_end']=0.1


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parameters for Optimization
optimization_input_parameters['max_iteration']	=10
optimization_input_parameters['alpha_min']	=-1
optimization_input_parameters['consec_iter']	=-1

optimization_input_parameters['delta_threshold']=0.01
optimization_input_parameters['alpha_mult']	=1
optimization_input_parameters['loss_type']	=0
optimization_input_parameters['update_check']	=0

optimization_input_parameters['optimizing_parameters']=['Rd','Ibias','W1','W2','Alo','Rbias2','Rbias3']

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
f_directory='/home/ee18b064/Optimization/Mixer_optimization/Simulation_Results/LOSS/'

file_choose='S' # 'S' to run a single time; 'M' to run multiple times


if file_choose=='S':

	# ------- Set Any Additional Parameters Here --------
	filename=f_directory+'latest_result'						# SET THE FILENAME HERE
	optimization_input_parameters['max_iteration']=400
	optimization_input_parameters['iip3_method']='hb_single_pin_diff'	
	# ------- Set Any Additional Parameters Here --------
	

	# ------- DON'T CHANGE THESE LINES -------------
	optimization_input_parameters['filename']['output']=filename
	co.complete_optimization(optimization_input_parameters)
	#co.single_run(optimization_input_parameters)			
	dp.plot_complete(optimization_input_parameters)			
	# ------- DON'T CHANGE THESE LINES -------------		


if file_choose=='M':
	for i in range(0,5):	# SET NUMBER OF ITERATIONS HERE

		# ------- Set Any Additional Parameters Here --------
		filename=f_directory+'tsmc_opt_method'+str(i)			# SET THE FILENAME HERE
		fo=1e9
		wo=2*np.pi*fo
		optimization_input_parameters['output_conditions']['wo']=wo
		iip_mtd=['basic_hb','basic_pss','advanced_hb','advanced_pss','hb_sweep']
		optimization_input_parameters['iip3_method']=iip_mtd[i]
		# ------- Set Any Additional Parameters Here --------


		# ------- DON'T CHANGE THESE LINES -------------
		optimization_input_parameters['filename']['output']=filename
		co.complete_optimization(optimization_input_parameters)
		dp.plot_complete(optimization_input_parameters)
		# ------- DON'T CHANGE THESE LINES -------------

#===========================================================================================================================


