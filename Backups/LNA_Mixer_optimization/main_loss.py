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

optimization_input_parameters['filename']['directory']='/home/ee18b064/cadence_project/LNA_Mixer/'+optimization_input_parameters['circuit_type']+'/'   ## Single ended CGA location


optimization_input_parameters['iip3_method']='hb_single_pin' # Options : 'basic_hb', 'basic_pss', 'advanced_hb', 'advanced_pss', 'hb_sweep' , 'hb_manual_sweep' , 'hb_single_pin' , 'hb_single_pin_diff' , 'hb_manual_sweep_diff'


optimization_input_parameters['filename']['working_directory']='/home/ee18b064/Optimization/LNA_Mixer_optimization/'
optimization_input_parameters['filename']['multiple_files']=1

optimization_input_parameters['filename']['library_yaml']='/home/ee18b064/Optimization/LNA_Mixer_optimization/library.yml'

optimization_input_parameters['filename']['mos_param_yaml']='/home/ee18b064/Optimization/LNA_Mixer_optimization/mos_param.yml'


optimization_input_parameters['filename']['tcsh']='/home/ee18b064/Optimization/LNA_Mixer_optimization/spectre_run.tcsh'
optimization_input_parameters['filename']['tcsh_iip3']='/home/ee18b064/Optimization/LNA_Mixer_optimization/spectre_run_iip3.tcsh'

optimization_input_parameters['filename']['tcsh_run']='tcsh /home/ee18b064/Optimization/LNA_Mixer_optimization/spectre_run.tcsh'
optimization_input_parameters['filename']['tcsh_iip3_run']='tcsh /home/ee18b064/Optimization/LNA_Mixer_optimization/spectre_run_iip3.tcsh'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Output Conditions

optimization_input_parameters['output_conditions']={
	'iip3_dbm':-20.5,
	'iip2_dbm':40,
	'conv_gain_db':24.0,
	's11_db':-15,
	'nf_db':7.5,
	'flo':1e9,
	'frf':1.01e9,
	'f_lower':50e6,
	'f_upper':2e9,
	'bb_BW':1e7,
	'region':2
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Simulation Conditions
optimization_input_parameters['simulation_conditions']={
	'hb_sweep_time_save':0,
	'iip3_errpreset':'moderate',  # Available methods : ['conservative'-Accurate  ,  'moderate'  ,   'liberal'-Not very Accurate]
	'pin_iip3':-60,
	'f_delta_iip3':1e6,
	'mismatch':0.001
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parameters List
optimization_input_parameters['circuit_parameters_list']=['Rb','Rd1','Rd2','Rbias1','Rbias2','Rbias3','Rbias4','C1','C2','C3','C4','Cload','len1','len2','W1','W2','W3','Ibias1','Ibias2','frf','flo','Alo','Temp']
optimization_input_parameters['output_parameters_list']=['Io1','Io2','conv_gain_db','lna_gain_db','bb_BW','s11_db','nf_db','iip3_dbm','gm1','gds1','region1','gm2','gds2','region2']
optimization_input_parameters['output_specs_params_list']=['conv_gain_db','s11_db','iip3_dbm','nf_db','bb_BW']
optimization_input_parameters['cir_writing_dict']={'Resb':'Rb','Resd1':'Rd1','Resd2':'Rd2','Resbias1':'Rbias1','Resbias2':'Rbias2','Resbias3':'Rbias3','Resbias4':'Rbias4','cap1':'C1','cap2':'C2','cap3':'C3','cap4':'C4','cload':'Cload','len':'len1','len_m':'len2','wid1':'W1','wid2':'W2','wid3':'W3','cur1':'Ibias1','cur2':'Ibias2','f_lo':'flo','frf_fund1':'frf','frf_fund2':'frf_fund2','f_lower':'f_lower','f_upper':'f_upper','cir_temp':'Temp','ampl_lo':'Alo'}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Manual Hand Calculations
optimization_input_parameters['manual_circuit_parameters']={
	'Rb':348.415939694684,
	'Rd1':253.848816243181,
	'Rd2':312.905928035364,
	'Rbias1':1000,
	'Rbias2':10542.6257806746,
	'Rbias3':18822.0142235087,
	'Rbias4':16952.3497955799,
	'C1':3.92222900057188E-11,
	'C2':1.09379321898551E-11,
	'C3':2.989372E-12,
	'C4':2.993296E-12,
	'Cload':1.2614747845379E-11,
	'len1':6.000000000000001e-08,
	'len2':6.29828476248202E-08,
	'W1':0.000159141948323,
	'W2':6.89151884046593E-05,
	'W3':3.77519707772386E-05,
	'Ibias1':0.001006211176245,
	'Ibias2':0.00113123671996,
	'frf':1010000000.0,
	'frf_fund2':1011000000.0,
	'flo':1000000000.0,
	'f_lower':50000000.0,
	'f_upper':2000000000.0,
	'Alo':0.4889605,
	'Temp':27
}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Parameters for steps pre optimization
optimization_input_parameters['pre_optimization']={}

optimization_input_parameters['pre_optimization']['type']='manual'				#Available Methods : ['manual' , 1]
optimization_input_parameters['pre_optimization']['ampl_threshold']=2
optimization_input_parameters['pre_optimization']['sat_threshold']=75e-3
optimization_input_parameters['pre_optimization']['body_threshold']=100e-3
optimization_input_parameters['pre_optimization']['C_threshold']=200
optimization_input_parameters['pre_optimization']['Rbias_threshold']=200

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assigning values to the loss weights
loss_weights={}
loss_weights['conv_gain_db']=1/abs(optimization_input_parameters['output_conditions']['conv_gain_db'])	
loss_weights['s11_db']=1/abs(optimization_input_parameters['output_conditions']['s11_db'])	
loss_weights['iip3_dbm']=1/abs(optimization_input_parameters['output_conditions']['iip3_dbm'])
loss_weights['iip2_dbm']=1/abs(optimization_input_parameters['output_conditions']['iip2_dbm'])	
loss_weights['nf_db']=3/abs(optimization_input_parameters['output_conditions']['nf_db'])
loss_weights['bb_BW']=1/abs(optimization_input_parameters['output_conditions']['bb_BW'])
loss_weights['region']=1/abs(optimization_input_parameters['output_conditions']['region'])	
loss_weights['Io']=200	
optimization_input_parameters['loss_weights']=loss_weights


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Assigning Values of Alpha
alpha_parameters={}
alpha_parameters['alpha']=40e-3   # may change during iterations
alpha_parameters['fixed_alpha']=40e-3 # Will not change during iterations
alpha_parameters['Rb']=1
alpha_parameters['Rd1']=1
alpha_parameters['Rd2']=1
alpha_parameters['Rbias3']=1
alpha_parameters['Rbias4']=1
alpha_parameters['Cload']=1
alpha_parameters['len2']=1
alpha_parameters['Ibias1']=1
alpha_parameters['Ibias2']=1
alpha_parameters['W1']=1
alpha_parameters['W2']=1
alpha_parameters['W3']=1
alpha_parameters['Alo']=1
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

optimization_input_parameters['optimizing_parameters']=['Rb','Rd1','Rd2','Rbias3','Rbias4','Cload','len2','Ibias1','Ibias2','W1','W2','W3','Alo']

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
f_directory='/home/ee18b064/Optimization/LNA_Mixer_optimization/Simulation_Results/LOSS/'

# ------- Set Any Additional Parameters Here --------
filename=f_directory+'optimize_3'						# SET THE FILENAME HERE
optimization_input_parameters['max_iteration']=80
optimization_input_parameters['iip3_method']='hb_manual_sweep_diff'	
# ------- Set Any Additional Parameters Here --------
	

# ------- DON'T CHANGE THESE LINES -------------
optimization_input_parameters['filename']['output']=filename
#co.complete_optimization(optimization_input_parameters)
co.single_run(optimization_input_parameters)			
#dp.plot_complete(optimization_input_parameters)			
# ------- DON'T CHANGE THESE LINES -------------		

#===========================================================================================================================


