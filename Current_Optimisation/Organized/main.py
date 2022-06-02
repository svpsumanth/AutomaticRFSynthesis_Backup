#===========================================================================================================================
"""
Name: Pyneni Roopesh
Roll Number: EE18B028
Main Code:
"""
#===========================================================================================================================
import numpy as np
import math
import complete_optimization as co
import data_plot as dp

import RFIC_Param_Extraction as pe


#===========================================================================================================================
#------------------------------------Main Program Code----------------------------------------------------------------------

# Creating the location for the files
f_directory='/home/ee18b064/Transfer_files/Organized/Simulation_Results/'
recquirement_file='/home/ee18b064/Transfer_files/Organized/Recquirements.txt'
#f_name_plot='test'
#filename=f_directory+f_name_plot


recquirement_dict={'gain_dB':0,'s11_dB_max':0,'iip3_dBm_min':0,'NF_max_dB':0,'f':0,'Rs':0}
recquirement_dict=pe.extract_sys_req(input_name,sys_req_dict)


# Output Conditions
s11_db=recquirement_dict['s11_dB_max']
iip3_dbm=recquirement_dict['iip3_dBm_min']
gain_db=recquirement_dict['gain_dB']
nf_db=recquirement_dict['NF_max_dB']
freq=recquirement_dict['f']
wo=2.0*np.pi*freq
Rs=recquirement_dict['Rs']
#output_conditions = {'s11_db':s11_db,'iip3_dbm':iip3_dbm,'gain_db':gain_db,'nf_db':nf_db,'wo':wo,'delta_v':delta_v,'Rs':Rs}

# File Names
file_name_lib='/home/ee18b064/Eldo_files/Models_UMC180/tsmc018.lib'
file_name_chi="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics/default/CGA_CurrentMirror_1_With_parasitics_default_default.chi"
file_name_cir="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics/default/CGA_CurrentMirror_1_With_parasitics_default_default.cir"

# Assigning values to the loss weights
loss_weights={}
loss_weights['gain_db']=1/gain_db	# Weight for gain
loss_weights['iip3_dbm']=1/iip3_dbm	# Weight for iip3
loss_weights['s11_db']=1/s11_db	# Weight for s11
loss_weights['nf_db']=1/nf_db	# Weight for nf
loss_weights['Io']=400	# Weight for Io

# Assigning Values of Alpha
aplha=40e-3
'''alpha_parameters={}
alpha_parameters['alpha']=0.15
alpha_parameters['Rb']=2
alpha_parameters['Rd']=2.5
alpha_parameters['W']=2
alpha_parameters['Io']=0.25'''

# Combining into a single dictionary

optimization_input_parameters={}
#optimization_input_parameters['alpha']		=alpha_parameters
#optimization_input_parameters['output_conditions']=output_conditions
#optimization_input_parameters['loss_weights']	=loss_weights
#optimization_input_parameters['alpha_min']	=-1
#optimization_input_parameters['consec_iter']	=-1
#optimization_input_parameters['alpha_mult']	=1
optimization_input_parameters['max_iteration']	=300
#optimization_input_parameters['delta_threshold']=0.001
optimization_input_parameters['loss_type']	=1
#optimization_input_parameters['update_check']	=0

optimization_input_parameters['filename_lib']=file_name_lib
optimization_input_parameters['filename_chi']=file_name_chi
optimization_input_parameters['filename_cir']=file_name_cir
optimization_input_parameters['MOS_Type']='NMOS'
optimization_input_parameters['Lmin']=0.18*1e-6
optimization_input_parameters['Vdd']=1.8

#optimization_input_parameters['Step1b_Limit']=5
#optimization_input_parameters['vdsat_reqd']=0.09

#"""
filename=f_directory+'test'
optimization_input_parameters['max_iteration']=5
optimization_input_parameters['filename_output']=filename
co.complete_optimization(optimization_input_parameters)
dp.plot_complete(filename)
#"""

"""
# Calling the complete optimization function
for i in range(1,2):
	#j=i/4
	filename=f_directory+'run_c_5'
	#loss_weights['Io']=1000-(200*j)
	
	# Running the files
	optimization_input_parameters['filename_output']=filename
	co.complete_optimization(optimization_input_parameters)
	dp.plot_complete(filename)
"""


#===========================================================================================================================


