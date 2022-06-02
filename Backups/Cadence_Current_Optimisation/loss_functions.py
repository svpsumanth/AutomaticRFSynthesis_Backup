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

#===========================================================================================================================
#------------------------------------Defining the functions -----------------------------------------

#-----------------------------------------------------------------------------------------------
# This is the ramp function
def ramp_func(x):
	if x>0:
		return x
	else:
		return 0		
		

#===========================================================================================================================
#--------------------------------------------Output Functions---------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
# This function calculates the loss for Io Optimization
def calc_loss_1(extracted_parameters,output_conditions,loss_weights):
	
	# Extracted Values
	gain=extracted_parameters['gain_db']
	iip3=extracted_parameters['iip3_dbm']
	s11=extracted_parameters['s11_db']
	nf=extracted_parameters['nf_db']
	Io=extracted_parameters['Io']
	
	# Reference Values
	gain_ref=output_conditions['gain_db']
	iip3_ref=output_conditions['iip3_dbm']
	s11_ref=output_conditions['s11_db']
	nf_ref=output_conditions['nf_db']
	
	#Defining the weights to calculate Loss
	A1=loss_weights['gain_db']	# Weight for gain
	A2=loss_weights['iip3_dbm']	# Weight for iip3
	A3=loss_weights['s11_db']	# Weight for s11
	A4=loss_weights['nf_db']	# Weight for nf
	A5=loss_weights['Io']	# Weight for Io
	
	# Calculating Loss
	loss_gain=A1*ramp_func(gain_ref-gain)
	loss_iip3=A2*ramp_func(iip3_ref-iip3)
	loss_s11=A3*ramp_func(s11-s11_ref)
	loss_nf=A4*ramp_func(nf-nf_ref)
	loss_Io=A5*Io
	loss=loss_gain+loss_iip3+loss_s11+loss_nf+loss_Io
	loss_dict={'loss':loss,'loss_gain':loss_gain,'loss_iip3':loss_iip3,'loss_s11':loss_s11,'loss_nf':loss_nf,'loss_Io':loss_Io}
	
	return loss_dict
		
#-----------------------------------------------------------------------------------------------
# This function calculates the loss for FoM
def calc_fom_1(extracted_parameters,output_conditions,loss_weights):
	
	# Extracted Values
	gain_db=extracted_parameters['gain_db']
	iip3_dbm=extracted_parameters['iip3_dbm']
	s11_db=extracted_parameters['s11_db']
	nf_db=extracted_parameters['nf_db']
	P=extracted_parameters['p_source']
	freq=extracted_parameters['freq']/1e9
	
	nf=cf.db_to_normal(nf_db)
	
	# Calculating FoM
	fom_gain=gain_db
	fom_iip3=iip3_dbm
	fom_freq=cf.normal_to_db(freq)
	fom_nf=-1*cf.normal_to_db(nf-1)
	fom_P=-1*cf.normal_to_dbm(P)
	fom_s11=-1*loss_weights['s11_db']*ramp_func(s11_db-output_conditions['s11_db'])
	fom=fom_gain+fom_iip3+fom_freq+fom_nf+fom_P+fom_s11
	
	fom_dict={'loss':fom,'loss_gain':fom_gain,'loss_freq':fom_freq,'loss_nf':fom_nf,'loss_iip3':fom_iip3,'loss_P':fom_P,'loss_s11':fom_s11}
	
	return fom_dict
	



	
	


