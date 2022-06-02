#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

Common Functions File:
"""
#===========================================================================================================================
import numpy as np
import math
import os
#===========================================================================================================================



#===========================================================================================================================
#---------------------------------------- Calculation Functions ------------------------------------------------------------

#-----------------------------------------------------------------------------------------------
#These functions change the parameters from normal scale to dB and dBm scale and vice versa
def db_to_normal(x_db):
	exp_x=x_db/10.0
	x_normal=10.0**exp_x
	return x_normal

def dbm_to_normal(x_dbm):
	x_db=x_dbm-30.0
	exp_x=x_db/10.0
	x_normal=10.0**exp_x
	return x_normal
	
def normal_to_db(x_normal):
	x_db=10.0*np.log10(x_normal)
	return x_db
	
def normal_to_dbm(x_normal):
	x_db=10.0*np.log10(x_normal)
	x_dbm=x_db+30.0
	return x_dbm
	
#-----------------------------------------------------------------------------------------------
# This function returns the truncated number as a string
def num_trunc(x_,pts):
    if x_==0:
       return '0'

    units = {-12: "T",-9: "G",-6: "M",-3: "K",0: "",3: "m",6: "µ",9: "n",12: "p",15: "f",18:"o",21:"b"}
    k = -12
    while abs(x_ * 10.0**k) < 1: 
        k += 3

    if k in units:
        string=f"{round(x_*10.0**k,pts)}{units[k]}"
    else:
        string=str(x_)
    return string

#===========================================================================================================================
#--------------------------------------- Output Printing Functions ---------------------------------------------------------

trunc_val=3

#-----------------------------------------------------------------------------------------------
#Assigning MOSFET Parameters
def update_MOS_parameters(mos,un,cox,vt,Lmin,vdd):
	mos['un']=un
	mos['cox']=cox
	mos['vt']=vt
	mos['un']=Lmin
	mos['un']=vdd
	return mos
	
#-----------------------------------------------------------------------------------------------
# Printing the MOSFET Parameters
def print_change_opt_gm(W1,Io1,Rb1,W2,Io2,Rb2):
	print ('\n____________________________________________________________________')
	print('------------------------Changes in parameters------------------------\n')
	print('Previous Values:')
	print('W   = ',num_trunc(W1 ,3))
	print('Io  = ',num_trunc(Io1,3))
	print('Rb  = ',num_trunc(Rb1,3))
	print('\nUpdated Values:')
	print('W   = ',num_trunc(W2 ,3))
	print('Io  = ',num_trunc(Io2,3))
	print('Rb  = ',num_trunc(Rb2,3))
	
#-----------------------------------------------------------------------------------------------
# Printing the MOSFET Parameters
def print_MOS_parameters(mos_parameters):
	print ('\n____________________________________________________________________')
	print ('-------------------------MOSFET Parameters--------------------------\n')
	print ('uncox = ', num_trunc(mos_parameters['un']*mos_parameters['cox'],trunc_val))
	print ('un    = ', num_trunc(mos_parameters['un'],trunc_val))
	print ('cox   = ', num_trunc(mos_parameters['cox'],trunc_val))
	print ('vt    = ', num_trunc(mos_parameters['vt'],trunc_val))
	print ('Lmin  = ', num_trunc(mos_parameters['Lmin'],trunc_val))
	print ('vdd   = ', num_trunc(mos_parameters['vdd'],trunc_val))
	
#-----------------------------------------------------------------------------------------------
# Printing the circuit parameters
def print_circuit_parameters(circuit_parameters):
	print ('\n____________________________________________________________________')
	print ('-------------------------Extracted Outputs--------------------------\n')
	for i in circuit_parameters:
		print(str(i)+'\t\t\t  =  ',num_trunc(circuit_parameters[i],2))
	
#-----------------------------------------------------------------------------------------------
# Printing the DC outputs
def print_DC_outputs(dc_outputs,mos_parameters):
	print ('\n____________________________________________________________________')
	print ('-------------------Hand Calculation DC Outputs----------------------\n')
	print ('vg     = ',num_trunc(dc_outputs['vg'],trunc_val))
	print ('vs     = ',num_trunc(dc_outputs['vs'],trunc_val))
	print ('vd     = ',num_trunc(dc_outputs['vd'],trunc_val))
	print ('vgs-vt = ',num_trunc(dc_outputs['vg']-dc_outputs['vs']-mos_parameters['vt'],trunc_val))
		
#-----------------------------------------------------------------------------------------------
# Printing the extracted parameters
def print_extracted_outputs(extracted_parameters):
	print ('\n____________________________________________________________________')
	print ('-------------------------Extracted Outputs--------------------------\n')
	for i in extracted_parameters:
		print(str(i)+'\t\t\t  =  ',num_trunc(extracted_parameters[i],2))
		
#-----------------------------------------------------------------------------------------------
# Printing the extracted parameters for main optimization
def print_extracted_outputs_optimization(extracted_parameters):
	print ('\n____________________________________________________________________')
	print ('-------------------------Extracted Outputs--------------------------\n')
	for i in extracted_parameters:
		print(str(i)+'\t\t\t  =  ',num_trunc(extracted_parameters[i],2))
	
#-----------------------------------------------------------------------------------------------
# Printing the sensitivity of the parameters
def print_sensitivity(circuit_parameters_sensitivity):
	print ('\n____________________________________________________________________')
	print ('-------------------------Sensitivity --------------------------\n')
	for param_name in circuit_parameters_sensitivity:
		print('\n----------- ',param_name,' -----------\n')
		for categ in circuit_parameters_sensitivity[param_name]:
			print(categ,'\t: ',num_trunc(circuit_parameters_sensitivity[param_name][categ],trunc_val))	
#===========================================================================================================================


