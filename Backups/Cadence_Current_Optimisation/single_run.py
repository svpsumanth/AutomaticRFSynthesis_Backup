#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

Main Code:
"""
#===========================================================================================================================
import numpy as np
import math
import cmath
import complete_optimization as co
import data_plot as dp
import spectre as sp
import temp_var as tv
from matplotlib import pylab
from pylab import *

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
optimization_input_parameters['filename']['directory']='/home/ee18b064/cadence_project/CGA_LNA_differential_2/'+optimization_input_parameters['circuit_type']+'/'   ## Differential ended CGA location

optimization_input_parameters['iip3_method']='basic_pss' # Options : 'basic_hb', 'basic_pss', 'advanced_hb', 'advanced_pss', 'hb_sweep' , 'hb_manual_sweep' , 'hb_single_pin' , 'hb_single_pin_diff'


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
optimization_input_parameters['output_parameters_list']=['Io','gain_db','iip3_dbm','s11_db','s12_db','s21_db','s22_db','nf_db','p_source','gm1','vdsat','vg','vd','vs']
optimization_input_parameters['output_specs_params_list']=['gain_db','iip3_dbm','s11_db','nf_db']
optimization_input_parameters['cir_writing_dict']={'wid':'W','cur0':'Io','Resb':'Rb','Resd':'Rd','cap1':'C1','cap2':'C2','Resbias':'Rbias','fund_1':'fo','cir_temp':'Temp'}

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Manual Hand Calculations
optimization_input_parameters['manual_circuit_parameters']={
	'Rb':347.482,
	'Rd':265.326,
	'Io':992.479e-6,
	'C1':31.831e-12,
	'C2':10.852e-12,
	'W':142.717e-6,
	'Rbias':500,
	'fo':fo,
	'Temp':27
}


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
	filename=f_directory+'spectre_test_tsmc_pinv'						# SET THE FILENAME HERE
	optimization_input_parameters['max_iteration']=1
	optimization_input_parameters['iip3_method']='hb_single_pin_diff'	
	# ------- Set Any Additional Parameters Here --------

	Kf_list=[]
	freq_list=np.logspace(6,11,20)
	for i in freq_list:
		optimization_input_parameters['manual_circuit_parameters']['fo']=i
		optimization_input_parameters['output_conditions']['wo']=2*np.pi*i
		co.single_run(optimization_input_parameters)
		extracted_parameters=(optimization_input_parameters['extracted_parameters'])
		Kf_list.append(extracted_parameters['Kf'])

	semilogx(freq_list,Kf_list)	
	show()
	
	'''
	# ------- DON'T CHANGE THESE LINES -------------
	optimization_input_parameters['filename']['output']=filename
	co.single_run(optimization_input_parameters)					
	# ------- DON'T CHANGE THESE LINES -------------	
	'''
	extracted_parameters=(optimization_input_parameters['extracted_parameters'])	

	'''s12_db=extracted_parameters['s12_db']
	s22_db=extracted_parameters['s22_db']
	s12_rad=extracted_parameters['s12_rad']
	s22_rad=extracted_parameters['s22_rad']

	#feedback_gain=cmath.rect(10**(s12_db/20),s12_rad)/(1+cmath.rect(10**(s22_db/20),s22_rad))
	#print("Feedback Gain (dB)= ",20*np.log10(abs(feedback_gain)))

	
	s21_db=extracted_parameters['s21_db']
	s11_db=extracted_parameters['s11_db']
	s21_rad=extracted_parameters['s21_rad']
	s11_rad=extracted_parameters['s11_rad']
	
	print("S11 : ",cmath.rect(10**(s11_db/20),s11_rad),"\tMag : ",10**(s11_db/20),"\tPhase : ",s11_rad*180/np.pi)
	print("S12 : ",cmath.rect(10**(s12_db/20),s12_rad),"\tMag : ",10**(s12_db/20),"\tPhase : ",s12_rad*180/np.pi)
	print("S21 : ",cmath.rect(10**(s21_db/20),s21_rad),"\tMag : ",10**(s21_db/20),"\tPhase : ",s21_rad*180/np.pi)
	print("S22 : ",cmath.rect(10**(s22_db/20),s22_rad),"\tMag : ",10**(s22_db/20),"\tPhase : ",s22_rad*180/np.pi)'''

	


	

	

	

	#forward_gain=cmath.rect(10**(s21_db/20),s21_rad)/(1+cmath.rect(10**(s11_db/20),s11_rad))
	#print("Forward Gain (dB)= ",20*math.log(abs(forward_gain/np.sqrt(1)),10))

#===========================================================================================================================
