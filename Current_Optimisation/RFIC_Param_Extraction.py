import numpy as np
import math

#===========================================================================================================================
# Basic Functions:

#---------------------------------------------------------------------------------------------------------------------------
# Extracting the files as an array of lines
# Inputs: file name
# Output: array of lines
def extract_file(file_name):
	f=open(file_name)
	lines=f.readlines()
	f.close()
	return lines

#---------------------------------------------------------------------------------------------------------------------------
# Extracting the parameters from the lib file
# Inputs: 
# 1) lines of the lib file
# 2) Parameter Name: un, vt, etc
# 3) MOSFET Type: NMOS or PMOS
# Output: The value of the extracted parameter
def extract_lib_param(lines,param_name,mos_type):
	# Finding the required MOS Type
	while 1:
		if len(lines[0].split())<3:
			lines=lines[1:]
		elif lines[0].split()[2] == mos_type:
			break
		else:
			lines=lines[1:]
			
	# Searching for the required parameter
	while 1:
		f=0
		for word in lines[0].split():
			if word==param_name:
				f=1
				break
		if f==1:
			line=lines[0].split()
			i=0
			while 1:
				if line[i]==param_name:
					value=float(line[i+2])
					break
				i+=1
			break
		else:
			lines=lines[1:]
	return value

#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the DC & SST Parameters from the .chi file
# Inputs: 
# 1) lines of chi file
# 2) Parameter name
# Output: Value of the parameter
def extract_chi_param(lines,param_name):
	while 1:
		if len(lines[0].split())<2:
			lines=lines[1:]
		elif lines[0].split()[1] == param_name:
			break
		else:
			lines=lines[1:]
	value_name=lines[0].split()[3]
	val=valueName_to_value(value_name)
	return val
	
#---------------------------------------------------------------------------------------------------------------------------
# Extracting the Noise Factor from the .chi file
# Inputs: 
# 1) lines of chi file
# 2) Parameter name
# Output: Value of the parameter
def extract_chi_noise(lines,param_name):
	while 1:
		if len(lines[0].split())<5:
			lines=lines[1:]
		elif lines[0].split()[0] == 'Contribution' and lines[0].split()[1] == 'due' and lines[0].split()[2] == 'to' and lines[0].split()[4] == param_name:
			break
		else:
			lines=lines[1:]
	value_name=lines[2].split()[3]
	val=valueE_to_value(value_name[:-1])
	
	nf,f=contrib_to_noise(val)
	
	return val,nf,f

#---------------------------------------------------------------------------------------------------------------------------
# Changing the values extracted as a string to a floating point value 
# Input: Value of the number in string format 	
# Output: Valvue of the number in float
def valueName_to_value(value_name):

	# Checking if the last character of array is a string
	if value_name[-1].isalpha()==0:
		val=float(value_name)
		return val
		
	# Extracting the numerical part of the number 
	val=float(value_name[:-1])
	
	# Extracting the character that denotes the units ( i.e, millt, micro, nano, etc)
	mult_name=value_name[-1]
	mult=1.0
	
	# Calculating the value of the unit
	if mult_name=='M' or mult_name=='m':
		mult=1e-3
	elif mult_name=='U' or mult_name=='u':
		mult=1e-6
	elif mult_name=='N' or mult_name=='n':
		mult=1e-9
	elif mult_name=='P' or mult_name=='p':
		mult=1e-12
	elif mult_name=='F' or mult_name=='f':
		mult=1e-15
	else:
		mult=1.0
		
	val=val*mult
	return val
	
#---------------------------------------------------------------------------------------------------------------------------
# Changing the values extracted as 10e1, 1.5e-2 to a floating point value 
def valueE_to_value(value_name):

	# Extracting the number before and after e
	num1=float(value_name.split('e')[0])
	num2=float(value_name.split('e')[1])
		
	# Calculating the final number
	num=num1*(10**num2)
		
	return num
	
#---------------------------------------------------------------------------------------------------------------------------
# Calculating the noise factor from contribution
def contrib_to_noise(val):
	f=100/val
	nf=10*np.log10(f)
		
	return nf,f
	

#===========================================================================================================================
#--------------------------------------------Output Functions---------------------------------------------------------------



#---------------------------------------------------------------------------------------------------------------------------
# Extracting Vth, un and cox from lib file
# Inputs:
# 1) lines of the lib file
# 2) MOSFET Type: NMOS or PMOS
# 3) MOSFET File
# Outputs: mosfet dictionary containing mosfet parameters
def extract_mosfet_param(file_name,mos_type,mos_dict):
	param_name_vt='VTH0'
	param_name_un='+U0'
	param_name_tox='TOX'
	lines=extract_file(file_name)
	vt=extract_lib_param(lines,param_name_vt,mos_type)
	un=1e-4*extract_lib_param(lines,param_name_un,mos_type)
	tox=extract_lib_param(lines,param_name_tox,mos_type)
	eo=8.85*1e-12
	er=3.9
	cox=eo*er/tox
	
	mos_dict['mew_n']=un
	mos_dict['Vth']=vt
	mos_dict['Cox']=cox
	
	return mos_dict

def extract_sys_req(filename,sys_req_dict):
    f=open(filename,'r')
    for line in f:
        if line[:8]=='gain_dB=':
            sys_req_dict['gain_dB']=float(line[8:-1])
        elif line[0:11]=='s11_dB_max=':
            sys_req_dict['s11_dB_max']=float(line[11:-1])
        elif line[0:13]=='iip3_dBm_min=':
            sys_req_dict['iip3_dBm_min']=float(line[13:-1])
        elif line[0:10]=='NF_max_dB=':
            sys_req_dict['NF_max_dB']=float(line[10:-1])
        elif line[0:2]=='f=':
            sys_req_dict['f']=float(line[2:-1])
        elif line[0:3]=='Rs=':
            sys_req_dict['Rs']=float(line[3:-1])
    f.close()
    return sys_req_dict
  

def Output_dict(extract_param):
	output_dict={}
	output_dict['s11_dB']=extract_param['s11_dB']
	output_dict['NF_dB']=extract_param['NF_dB']
	output_dict['gain_dB']=extract_param['gain_dB']
	output_dict['iip3_dBm']=extract_param['iip3_dBm'] 
	output_dict['pwr_dc']=extract_param['pwr_dc']
	output_dict['Io']=extract_param['Io']
	
	return output_dict     
        
	
#---------------------------------------------------------------------------------------------------------------------------
# Extracting all the output parameters from chi file
# Inputs: .chi file name 
# Outputs: output parameters dictionary 
def extract_output_param(file_name):
	lines=extract_file(file_name)
	
	param_name_gm1='gm1'
	param_name_gds1='gds1'
	param_name_vth1='vth1'
	param_name_cdd1='cdd1'
	param_name_cgg1='cgg1'
	param_name_css1='css1'
	param_name_csg1='csg1'
	param_name_iip3='iip3'
	param_name_s11='s_11'
	param_name_zinr='zin_r'
	param_name_zini='zin_i'
	param_name_gain_db='gain'
	param_name_io='io'
	param_name_Vg='vg'
	param_name_Vs='vs'
	param_name_Vd='vd'
	param_name_pwr='pwr_dc'
	
	param_name_noise='V3'
	
	gm1=extract_chi_param(lines,param_name_gm1)
	gds1=extract_chi_param(lines,param_name_gds1)
	vth1=extract_chi_param(lines,param_name_vth1)
	cdd1=extract_chi_param(lines,param_name_cdd1)
	cgg1=extract_chi_param(lines,param_name_cgg1)
	css1=extract_chi_param(lines,param_name_css1)
	csg1=extract_chi_param(lines,param_name_csg1)
	Io=extract_chi_param(lines,param_name_io)
	Vg=extract_chi_param(lines,param_name_Vg)
	Vs=extract_chi_param(lines,param_name_Vs)
	Vd=extract_chi_param(lines,param_name_Vd)
	iip3=extract_chi_param(lines,param_name_iip3)
	s11=extract_chi_param(lines,param_name_s11)
	zinr=extract_chi_param(lines,param_name_zinr)
	zini=extract_chi_param(lines,param_name_zini)
	gain_db=extract_chi_param(lines,param_name_gain_db)
	pwr_dc=extract_chi_param(lines,param_name_pwr)
	val,nf,F=extract_chi_noise(lines,param_name_noise)
	
	extracted_param={'Io':Io,'gm1':gm1,'gds1':gds1,'Vth':vth1,'Vg':Vg,'Vs':Vs,'Vd':Vd,'cdd1':cdd1,'cgg1':cgg1,'css1':css1,'csg1':abs(csg1),'iip3_dBm':iip3,'s11_dB':s11,'gain_dB':gain_db,'NF_dB':nf,'pwr_dc':pwr_dc,'F':F,'contrib':val,'zin_i':zini,'zin_r':zinr}
	return extracted_param
