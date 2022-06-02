#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

File Data Extraction File:
"""
#===========================================================================================================================
import numpy as np
import fileinput
import math
import cmath
import os
import yaml
from matplotlib import pylab
from pylab import *
from yaml.loader import SafeLoader


"""
====================================================================================================================================================================================
------------------------------------------------------------ EXTRACTION FUNCTION ---------------------------------------------------------------------------------------------------
"""

#===========================================================================================================================
# Character to Real Number Functions:

#---------------------------------------------------------------------------------------------------------------------------
# Changing the values extracted as a string to a floating point value 
# Input: Value of the number in string format 	
# Output: Value of the number in float

def valueName_to_value(value_name):

	# Checking if the last character of array is a string
	if value_name[-1].isalpha()==0:
		val=float(value_name)
		return val
	
	# Checking if the last character of array is a string
	if (value_name[-1]=='G' and value_name[-2]=='E') or (value_name[-1]=='g' and value_name[-2]=='e'):
		val=float(value_name[:-3])*1e6
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
	elif mult_name=='G' or mult_name=='g':
		mult=1e9
	else:
		mult=1.0
		
	val=val*mult
	return val
	
#---------------------------------------------------------------------------------------------------------------------------
# Changing the values extracted as 10e1, 1.5e-2 to a floating point value 
# Input: Value of the number in string format 	
# Output: Value of the number in float

def valueE_to_value(value_name):
    
    # Extracting the number before and after e
    if 'e' in value_name:
        num1=float(value_name.split('e')[0])
        num2=float(value_name.split('e')[1])
        
        # Calculating the final number
        num=num1*(10**num2)
    
    else:
        num=float(value_name)
    
    return num





#===========================================================================================================================
# Basic File Extraction Functions:


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

	if mos_type=='NMOS':
		m_type='type=n'
	else:
		m_type='type=p'

	# Finding the required MOS Type
	while 1:
		if len(lines[0].split())<3:
			lines=lines[1:]
		elif 'model' in lines[0].split() and lines[0].split()[3] == m_type:
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
# Extracting the DC from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_dc_param(optimization_input_parameters):

	file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/dc.out'
	lines=extract_file(file_name)
	extracted_parameters={}

	lines=lines[7:]
	lines=lines[0].split()

	extracted_parameters['vd']=valueE_to_value(lines[1])
	extracted_parameters['vg']=valueE_to_value(lines[2])
	extracted_parameters['vs']=valueE_to_value(lines[3])

	extracted_parameters['i_source']=np.absolute(valueE_to_value(lines[4]))
	extracted_parameters['v_source']=np.absolute(valueE_to_value(lines[5]))
	extracted_parameters['p_source']=extracted_parameters['i_source']*extracted_parameters['v_source']

	extracted_parameters['Io']=valueE_to_value(lines[6])
	extracted_parameters['gm1']=valueE_to_value(lines[7])
	extracted_parameters['gds1']=valueE_to_value(lines[8])
	extracted_parameters['vt']=valueE_to_value(lines[9])
	extracted_parameters['vdsat']=valueE_to_value(lines[10])

	extracted_parameters['cgd1']=np.absolute(valueE_to_value(lines[11]))
	extracted_parameters['cgs1']=np.absolute(valueE_to_value(lines[12]))

	return extracted_parameters

#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the AC from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_ac_param_single(optimization_input_parameters):

	file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/ac.out'
	lines=extract_file(file_name)
	extracted_parameters={}

	lines=lines[7:]
	lines=lines[0].split()

	extracted_parameters['gain_db']=valueE_to_value(lines[4])
	extracted_parameters['freq']=valueE_to_value(lines[0])

	return extracted_parameters

#---------------------------------------------------------------------------------------------------------------------------	
# Doing an AC analysis to get gain at different frequencies and extracting them.
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_ac_param(optimization_input_parameters):

	file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/ac.out'
	lines=extract_file(file_name)
	extracted_parameters={}

	check_title=0
	for line in lines:
		if check_title==1:
			if len(line.split())==0:
				break
			
			freq=float(line.split()[0])
			gain=float(line.split()[4])
			
			if freq==optimization_input_parameters['output_conditions']['fo']:
				gain_fo=gain
			
			if freq==optimization_input_parameters['output_conditions']['f_lower']:
				gain_lower=gain

			if freq==optimization_input_parameters['output_conditions']['f_upper']:
				gain_upper=gain

		if 'freq' in line:
			check_title=1
	
	extracted_parameters['gain_lower']=gain_lower
	extracted_parameters['gain_fo']=gain_fo
	extracted_parameters['gain_upper']=gain_upper	
	extracted_parameters['gain_db']=min(gain_fo,gain_lower+3,gain_upper+3)
	extracted_parameters['freq']=optimization_input_parameters['output_conditions']['fo']
	extracted_parameters['f_lower'] = optimization_input_parameters['output_conditions']['f_lower']
	extracted_parameters['f_upper'] = optimization_input_parameters['output_conditions']['f_upper']
	return extracted_parameters

#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the SP from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_sp_param(optimization_input_parameters):

	file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/sp.out'
	lines=extract_file(file_name)
	extracted_parameters={}
	
	lines=lines[16:]
	line1=lines[0].split()
	line2=lines[1].split()

	s11_db=valueE_to_value(line1[1].split(',')[0])
	s12_db=valueE_to_value(line1[3].split(',')[0])
	s21_db=valueE_to_value(line2[0].split(',')[0])
	s22_db=valueE_to_value(line2[2].split(',')[0])

	s11_rad=valueE_to_value(line1[2])
	s12_rad=valueE_to_value(line1[4])
	s21_rad=valueE_to_value(line2[1])
	s22_rad=valueE_to_value(line2[3])
	
	D=cmath.rect(10**(s11_db/20),s11_rad)*cmath.rect(10**(s22_db/20),s22_rad)-cmath.rect(10**(s12_db/20),s12_rad)*cmath.rect(10**(s21_db/20),s21_rad)
	
	Kf=(1-10**(s11_db/10)-10**(s22_db/10)+abs(D)**2)/(2*10**(s12_db/20)*10**(s21_db/20))
	#Kf=0
	
	extracted_parameters['s11_db']=valueE_to_value(line1[1].split(',')[0])
	extracted_parameters['s12_db']=valueE_to_value(line1[3].split(',')[0])
	extracted_parameters['s21_db']=valueE_to_value(line2[0].split(',')[0])
	extracted_parameters['s22_db']=valueE_to_value(line2[2].split(',')[0])

	extracted_parameters['s11_rad']=valueE_to_value(line1[2])
	extracted_parameters['s12_rad']=valueE_to_value(line1[4])
	extracted_parameters['s21_rad']=valueE_to_value(line2[1])
	extracted_parameters['s22_rad']=valueE_to_value(line2[3])

	extracted_parameters['Kf']=Kf
	return extracted_parameters

#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the Noise from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_noise_param(optimization_input_parameters):

	file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/noise.out'
	lines=extract_file(file_name)
	extracted_parameters={}

	lines=lines[7:]
	lines=lines[0].split()

	extracted_parameters['nf_db']=valueE_to_value(lines[1])

	return extracted_parameters


#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the Integrated Noise figure from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_integ_noise_param(optimization_input_parameters):
	#print("\n\n Finding Noise Figure \n\n")
	filename=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+"/circ.raw/noise_test.noise"
	f=open(filename)
	lines=f.readlines()
	f.close()

	freq_list=[]
	out_list=[]
	f_list=[]		#noise factor

	freq_flag=0
	for line in lines:
		line=line.strip()
		if "\"freq\"" in line:
			words=line.split(' ')
			if len(words)==2:
				freq_list.append(float(words[1]))
				freq_flag=1
		if freq_flag==1:
			if "\"out\"" in line:
				words=line.split(' ')
				out_list.append(float(words[1]))
				freq_flag=0

			if "\"F\"" in line:
				words=line.split(' ')
				f_list.append(float(words[1]))
	
	out_list=np.array(out_list)**2
	freq_list=np.array(freq_list)
	f_list=np.array(f_list)
	out_frm_input_list=out_list/f_list

	integ_out=np.trapz(out_list,freq_list)
	integ_in=np.trapz(out_frm_input_list,freq_list)
	integ_f=integ_out/integ_in	

	integ_nf=10*np.log10(integ_f)

	extracted_parameters={}
	extracted_parameters['nf_integ_db']=integ_nf
	semilogx(freq_list,10*np.log10(f_list))
	show()

	ind=0
	for i in range(len(freq_list)):
		if freq_list[i]<=1e9+1e7:
			ind=i

	nf_spot=10*np.log10(f_list[ind])
	extracted_parameters['nf_spot_db']=nf_spot
	extracted_parameters['nf_spot_freq']=freq_list[ind]
	
	extracted_parameters['nf_db']=10*np.log10(f_list[0])
	return extracted_parameters
#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the IIP3 from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_iip3_param(optimization_input_parameters):

	if optimization_input_parameters['iip3_method']=='basic_hb':
		file_name_1=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/hbac_test.0.pac_hbac'
		file_name_2=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/hbac_test.-2.pac_hbac'
		pin=optimization_input_parameters['simulation_conditions']['pin_iip3']
		extracted_parameters=extract_iip3_basic(file_name_1,file_name_2,pin)
	
	elif optimization_input_parameters['iip3_method']=='basic_pss':
		file_name_1=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/pac_test.0.pac'
		file_name_2=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/pac_test.-2.pac'
		pin=optimization_input_parameters['simulation_conditions']['pin_iip3']
		extracted_parameters=extract_iip3_basic(file_name_1,file_name_2,pin)

	elif optimization_input_parameters['iip3_method']=='hb_manual_sweep':
		file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/hb_test.fd.qpss_hb'
		extracted_parameters=extract_iip3_manual_sweep(file_name,optimization_input_parameters)
	
	elif optimization_input_parameters['iip3_method']=='hb_single_pin':
		file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/hb_test.fd.qpss_hb'
		extracted_parameters=extract_iip3_hb_single_pin(file_name,optimization_input_parameters)

	elif optimization_input_parameters['iip3_method']=='hb_single_pin_diff':
		file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/hb_test.fd.qpss_hb'
		extracted_parameters=extract_iip3_hb_single_pin_diff(file_name,optimization_input_parameters)

	elif optimization_input_parameters['iip3_method']=='hb_manual_sweep_diff':
		file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/hb_test.fd.qpss_hb'
		extracted_parameters=extract_iip3_manual_sweep_diff(file_name,optimization_input_parameters)
	
	else:
		extracted_parameters=extract_iip3_advanced_sweep(optimization_input_parameters)

	return extracted_parameters


#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the IIP3 from Basic Analysis
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_iip3_basic(file_name_1,file_name_2,pin):

	# Extracting the magnitude of fundamental and im3
	vout_mag_fun=extract_magnitude_single(file_name_1)
	vout_mag_im3=extract_magnitude_single(file_name_2)

	# Calculating the iip3
	iip3=pin+10*(np.log10(vout_mag_fun)-np.log10(vout_mag_im3))

	extracted_parameters={}
	extracted_parameters={'iip3_dbm':iip3}
	
	return extracted_parameters

#---------------------------------------------------------------------------------------------------------------------------	
# Extracts the magnitude from a analysis file that has only single frequency output
# Inputs: Filename
# Output: Magnitude of Vout

def extract_magnitude_single(file_name):
	
	lines=extract_file(file_name)
	
	# Finding the required line in the analysis
	flag=0
	while 1:
		if len(lines[0].split())<2:
			lines=lines[1:]
		elif 'Vout' in lines[0].split()[0] and flag==0:
			flag=1
			lines=lines[1:]
		elif 'Vout' in lines[0].split()[0] and flag==1:
			break
		else:
			lines=lines[1:]
	
	# Extracting Vout_r and Vout_i
	lines=lines[0].split()
	char_r=lines[1].split('(')[1]
	char_i=lines[2].split(')')[0]
	vout_r=valueE_to_value(char_r)
	vout_i=valueE_to_value(char_i)
	
	# Calculating Vout magnitude
	vout_mag=np.sqrt(vout_r*vout_r+vout_i*vout_i)

	return vout_mag


#---------------------------------------------------------------------------------------------------------------------------	
# Checks if the frequency is within range ( within (target-error,target+error) )
# Inputs: Test Frequency, Target Frequency, Error
# Output: 1 if Yes and 0 if No

def check_freq(f_test,f_target,f_error):
	if f_test<f_target+f_error and f_test>f_target-f_error:
		return 1
	else:
		return 0


#---------------------------------------------------------------------------------------------------------------------------	
# Extracts Vout_magnitude from hb,pss file line
# Inputs: Line
# Output: Vout_Magnitude

def extract_vout(lines):
	# Extracting Vout Magnitude
	lines=lines.split()
	char_r=lines[1].split('(')[1]
	char_i=lines[2].split(')')[0]

	vout_r=valueE_to_value(char_r)
	vout_i=valueE_to_value(char_i)
	
	vout_mag=np.sqrt(vout_r*vout_r+vout_i*vout_i)

	return vout_mag


#---------------------------------------------------------------------------------------------------------------------------	
# Extracts Voul complex voltage from hb,pss file line
# Inputs: Line
# Output: Complex voltage

def extract_complex_vout(lines):
	# Extracting Vout Magnitude
	lines=lines.split()
	char_r=lines[1].split('(')[1]
	char_i=lines[2].split(')')[0]

	vol_r=valueE_to_value(char_r)
	vol_i=valueE_to_value(char_i)
	
	#vout_mag=np.sqrt(vout_r*vout_r+vout_i*vout_i)
	vol=complex(vol_r,vol_i)

	return vol



#---------------------------------------------------------------------------------------------------------------------------	
# Outputs the filename needed
# Inputs: Optimization Input Parameters, i
# Output: Filename

def get_iip3_advanced_filename(optimization_input_parameters,i):
	
	# Finding the number part of the string
	num_str=str(i)
	if len(num_str)==1:
		num_str='00'+num_str
	elif len(num_str)==2:
		num_str='0'+num_str
	
	# Getting the full filename
	file_name=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.raw/'

	if optimization_input_parameters['iip3_method']=='advanced_hb':
		file_name_1=file_name+'sweep_hb-'+num_str+'_hbac_test.0.pac_hbac'
		file_name_2=file_name+'sweep_hb-'+num_str+'_hbac_test.-2.pac_hbac'
	
	elif optimization_input_parameters['iip3_method']=='advanced_pss':
		file_name_1=file_name+'sweep_hb-'+num_str+'_pac_test.0.pac'
		file_name_2=file_name+'sweep_hb-'+num_str+'_pac_test.-2.pac'
	
	else:
		file_name_1=file_name+'sweep_hb-'+num_str+'_hb_test.fd.qpss_hb'
		file_name_2='dummy'

	return file_name_1,file_name_2


#---------------------------------------------------------------------------------------------------------------------------	
# Extracting Vout magnitude of fundamental and im3 from file ( for hb_sweep )
# Inputs: Filename, Optimization Input Parameters
# Output: Magnitude of Vout at fundamental and im3

def extract_magnitude_multiple(file_name,optimization_input_parameters):

	lines=extract_file(file_name)

	fund_1=optimization_input_parameters['output_conditions']['wo']/(2*np.pi)
	fund_2=fund_1+optimization_input_parameters['simulation_conditions']['f_delta_iip3']

	f_im3=2*fund_2-fund_1
	f_error=optimization_input_parameters['simulation_conditions']['f_delta_iip3']/10000

	flag=0
	flag_fun=0
	flag_im3=0
	flag_test=0

	while 1:
		if len(lines[0].split())<2:
			lines=lines[1:]
		
		elif 'freq' in lines[0].split()[0] and flag==0:
			flag=1
			lines=lines[1:]
		
		elif 'freq' in lines[0].split()[0] and flag==1:
			if flag_fun==0 and check_freq(float(lines[0].split()[1]),fund_2,f_error)==1 :
				
				#Extracting Vout for fundamental
				flag_test=1
				while flag_test==1:
					if 'Vout' in lines[0].split()[0]:
						flag_test=0
						vout_fund=extract_vout(lines[0])
					else:
						lines=lines[1:]
				flag_fun=1
			
			elif flag_im3==0 and check_freq(float(lines[0].split()[1]),f_im3,f_error)==1 :
				
				#Extracting Vout for im3
				flag_test=1
				while flag_test==1:
					if 'Vout' in lines[0].split()[0]:
						flag_test=0
						vout_im3=extract_vout(lines[0])
					else:
						lines=lines[1:]
				flag_im3=1
			lines=lines[1:]
			
			if flag_fun==1 and flag_im3==1:
				break
		
		else:
			lines=lines[1:]

	return vout_fund,vout_im3



#---------------------------------------------------------------------------------------------------------------------------	
#Extract hb complex voltage at a particular node and particular freq
def extract_hb_magnitude(file_name,freq,node="Vout"):

	#file_name=file_dir+'/circ.raw/hb_test.fi.pss_hb'
	lines=extract_file(file_name)
	fund_1=freq
	f_error=freq/100000

	flag=0
	flag_fun=0
	flag_test=0

	while 1:
		if len(lines[0].split())<2:
			lines=lines[1:]
		
		elif '\"freq\"' in lines[0].split()[0] and flag==0:
			flag=1
			lines=lines[1:]
		
		elif '\"freq\"' in lines[0].split()[0] and flag==1:
			if flag_fun==0 and check_freq(float(lines[0].split()[1]),fund_1,f_error)==1 :
				
				#Extracting Vout for fundamental
				flag_test=1
				while flag_test==1:
					if node in lines[0].split()[0]:
						flag_test=0
						vol=extract_complex_vout(lines[0])

					else:
						lines=lines[1:]
				flag_fun=1
			lines=lines[1:]
			
			if flag_fun==1 :
				break
		else:
			lines=lines[1:]

		
	return vol




#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the IIP3 from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_iip3_advanced(optimization_input_parameters):

	pin_start=-65
	pin_stop=-55
	n_points=10


	p_in=np.linspace(pin_start,pin_stop,n_points)
	vout_fund=np.zeros(n_points,dtype=float)
	vout_im3=np.zeros(n_points,dtype=float)

	# Extracting the magnitudes of fundamental and im3 for all pin
	for i in range(n_points):
		file_name_1,file_name_2=get_iip3_advanced_filename(optimization_input_parameters,i)
		if optimization_input_parameters['iip3_method']=='hb_sweep':
			vout_fund[i],vout_im3[i]=extract_magnitude_multiple(file_name_1,optimization_input_parameters)
		else:
			vout_fund[i]=extract_magnitude_single(file_name_1)
			vout_im3[i]=extract_magnitude_single(file_name_2)

	# Calculating the 20*log of Vout of fundamental and im3
	vout_fund_log=20*np.log10(vout_fund)
	vout_im3_log=20*np.log10(vout_im3)

	""""
	print('Vout_Fund:',vout_fund)
	print('Vout_IM3 :',vout_im3)
	print('Vout_Fund_Log:',vout_fund_log)
	print('Vout_IM3_Log :',vout_im3_log)
	"""
	
	# y_power is the difference between 20log(fund) and 20log(im3)
	# We want to find the value of pin when y_power vs pin graph touches x-axis ( i.e y_power=0 )
	y_power=vout_fund_log-vout_im3_log
	
	# We are excluding the first point ( pin=-80dbm ) because this is giving an error in iip3 calculation
	y_power=y_power[1:]
	p_in=p_in[1:]
	
	"""
	print('y_Power  :',y_power)
	print('Power_in :',p_in)
	"""
	
	# We are finding m and c where y_power=m*pin + c
	A = np.vstack([p_in, np.ones(len(p_in))]).T
	m, c = np.linalg.lstsq(A, y_power, rcond=None)[0]

	# Calculating iip3
	iip3=-1.0*c/m
	#print("\n\ndifference in slope : ",m,"\n\n")
	extracted_parameters={}
	extracted_parameters={'iip3_dbm':iip3}
	
	return extracted_parameters


#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the IIP3 from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_iip3_advanced_sweep(optimization_input_parameters):

	pin_start=-70
	pin_stop=-40
	n_points=61
	slope_points=5


	p_in=np.linspace(pin_start,pin_stop,n_points)
	vout_fund=np.zeros(n_points,dtype=float)
	vout_im3=np.zeros(n_points,dtype=float)

	# Extracting the magnitudes of fundamental and im3 for all pin
	for i in range(n_points):
		file_name_1,file_name_2=get_iip3_advanced_filename(optimization_input_parameters,i)
		if optimization_input_parameters['iip3_method']=='hb_sweep':
			vout_fund[i],vout_im3[i]=extract_magnitude_multiple(file_name_1,optimization_input_parameters)
		else:
			vout_fund[i]=extract_magnitude_single(file_name_1)
			vout_im3[i]=extract_magnitude_single(file_name_2)

	# Calculating the 20*log of Vout of fundamental and im3
	vout_fund_log=20*np.log10(vout_fund)
	vout_im3_log=20*np.log10(vout_im3)

	print("Pin : ",p_in)
	print("Fund : ",vout_fund_log,"\nIM3 : ",vout_im3_log)
	
	total_sweep_out={}
	
	min_ind=0
	min_lst_sq=1000
	for i in range(int(n_points-(slope_points-1))):
		sweep_out={}
		vout_fund_log_r=vout_fund_log[i:i+5]
		vout_im3_log_r=vout_im3_log[i:i+5]
		p_in_r=p_in[i:i+5]

		y_fund=vout_fund_log_r
		y_im3=vout_im3_log_r

		A = np.vstack([p_in_r, np.ones(len(p_in_r))]).T
		m_fund, c_fund = np.linalg.lstsq(A, y_fund, rcond=None)[0]
		m_im3, c_im3 = np.linalg.lstsq(A, y_im3, rcond=None)[0]

		sweep_out['lst_sq']=(m_fund-1)**2+(m_im3-3)**2
		sweep_out['iip3']=(c_im3-c_fund)/(m_fund-m_im3)
		sweep_out['m_fund']=m_fund
		sweep_out['c_fund']=c_fund
		sweep_out['m_im3']=m_im3
		sweep_out['c_im3']=c_im3
		
		total_sweep_out[i]=sweep_out
		
		if total_sweep_out[i]['lst_sq'] < min_lst_sq:
			min_ind=i
			min_lst_sq=total_sweep_out[i]['lst_sq']

	#print(total_sweep_out[min_ind])
	iip3=total_sweep_out[min_ind]['iip3']

	extracted_parameters={}
	extracted_parameters={'iip3_dbm':iip3}
	
	return extracted_parameters



#---------------------------------------------------------------------------------------------------------------------------
# This function sweeps pin manually from python and extracts iip3
def extract_iip3_manual_sweep(file_name,optimization_input_parameters):

	pin_start=-70
	pin_stop=-40
	n_points=16
	slope_points=5

	p_in=np.linspace(pin_start,pin_stop,n_points)
	vout_fund=np.zeros(n_points,dtype=float)
	vout_im3=np.zeros(n_points,dtype=float)
		
	for i in range(n_points):
		write_pin(p_in[i],optimization_input_parameters)
		run_file(optimization_input_parameters)
		vout_fund[i],vout_im3[i]=extract_magnitude_multiple(file_name,optimization_input_parameters)

	# Calculating the 20*log of Vout of fundamental and im3
	vout_fund_log=20*np.log10(vout_fund)
	vout_im3_log=20*np.log10(vout_im3)

	#print("Pin : ",p_in)
	#print("Fund : ",vout_fund_log,"\nIM3 : ",vout_im3_log)
	
	total_sweep_out={}
	
	min_ind=0
	min_lst_sq=1000
	for i in range(int(n_points-(slope_points-1))):
		sweep_out={}
		vout_fund_log_r=vout_fund_log[i:i+5]
		vout_im3_log_r=vout_im3_log[i:i+5]
		p_in_r=p_in[i:i+5]

		y_fund=vout_fund_log_r
		y_im3=vout_im3_log_r

		A = np.vstack([p_in_r, np.ones(len(p_in_r))]).T
		m_fund, c_fund = np.linalg.lstsq(A, y_fund, rcond=None)[0]
		m_im3, c_im3 = np.linalg.lstsq(A, y_im3, rcond=None)[0]

		sweep_out['lst_sq']=(m_fund-1)**2+(m_im3-3)**2
		sweep_out['iip3']=(c_im3-c_fund)/(m_fund-m_im3)
		sweep_out['m_fund']=m_fund
		sweep_out['c_fund']=c_fund
		sweep_out['m_im3']=m_im3
		sweep_out['c_im3']=c_im3
		
		total_sweep_out[i]=sweep_out
		
		if total_sweep_out[i]['lst_sq'] < min_lst_sq:
			min_ind=i
			min_lst_sq=total_sweep_out[i]['lst_sq']

	#print(total_sweep_out[min_ind])
	iip3=total_sweep_out[min_ind]['iip3']
	#print(total_sweep_out[min_ind])
	extracted_parameters={}
	extracted_parameters={'iip3_dbm':iip3}
	
	return extracted_parameters



# This function sweeps pin manually from python and extracts iip3 for differential case
def extract_iip3_manual_sweep_diff(file_name,optimization_input_parameters):

	pin_start=-70
	pin_stop=-40
	n_points=16
	slope_points=5

	p_in=np.linspace(pin_start,pin_stop,n_points)
	vout_fund=np.zeros(n_points,dtype=float)
	vout_im3=np.zeros(n_points,dtype=float)

	fund_1=optimization_input_parameters['output_conditions']['wo']/(2*np.pi)
	fund_2=fund_1+optimization_input_parameters['simulation_conditions']['f_delta_iip3']
	f_im3=2*fund_2-fund_1

		
	for i in range(n_points):
		write_pin(p_in[i],optimization_input_parameters)
		run_file(optimization_input_parameters)

		voutp_fund=extract_hb_magnitude(file_name,fund_1,node="Voutp")
		voutp_im3=extract_hb_magnitude(file_name,f_im3,node="Voutp")

		voutn_fund=extract_hb_magnitude(file_name,fund_1,node="Voutn")
		voutn_im3=extract_hb_magnitude(file_name,f_im3,node="Voutn")
	
		vout_fund[i]=abs(voutp_fund-voutn_fund)
		vout_im3[i]=abs(voutp_im3-voutn_im3)

		#vout_fund[i],vout_im3[i]=extract_magnitude_multiple(file_name,optimization_input_parameters)

	# Calculating the 20*log of Vout of fundamental and im3
	vout_fund_log=20*np.log10(vout_fund)
	vout_im3_log=20*np.log10(vout_im3)

	#print("Pin : ",p_in)
	#print("Fund : ",vout_fund_log,"\nIM3 : ",vout_im3_log)
	
	total_sweep_out={}
	
	min_ind=0
	min_lst_sq=1000
	for i in range(int(n_points-(slope_points-1))):
		sweep_out={}
		vout_fund_log_r=vout_fund_log[i:i+5]
		vout_im3_log_r=vout_im3_log[i:i+5]
		p_in_r=p_in[i:i+5]

		y_fund=vout_fund_log_r
		y_im3=vout_im3_log_r

		A = np.vstack([p_in_r, np.ones(len(p_in_r))]).T
		m_fund, c_fund = np.linalg.lstsq(A, y_fund, rcond=None)[0]
		m_im3, c_im3 = np.linalg.lstsq(A, y_im3, rcond=None)[0]

		sweep_out['lst_sq']=(m_fund-1)**2+(m_im3-3)**2
		sweep_out['iip3']=(c_im3-c_fund)/(m_fund-m_im3)
		sweep_out['m_fund']=m_fund
		sweep_out['c_fund']=c_fund
		sweep_out['m_im3']=m_im3
		sweep_out['c_im3']=c_im3
		
		total_sweep_out[i]=sweep_out
		
		if total_sweep_out[i]['lst_sq'] < min_lst_sq:
			min_ind=i
			min_lst_sq=total_sweep_out[i]['lst_sq']

	#print(total_sweep_out[min_ind])
	iip3=total_sweep_out[min_ind]['iip3']
	#print(total_sweep_out[min_ind])
	extracted_parameters={}
	extracted_parameters={'iip3_dbm':iip3}
	
	return extracted_parameters
#---------------------------------------------------------------------------------------------------------------------------
# This Function finds IIP3 by only using single Pin
def extract_iip3_hb_single_pin(file_name,optimization_input_parameters):
	

	p_in=optimization_input_parameters['simulation_conditions']['pin_iip3']
	vout_fund=1
	vout_im3=1

	write_pin(p_in,optimization_input_parameters)
	run_file(optimization_input_parameters)
	vout_fund,vout_im3=extract_magnitude_multiple(file_name,optimization_input_parameters)

	# Calculating the iip3
	iip3=p_in+10*(np.log10(vout_fund)-np.log10(vout_im3))

	extracted_parameters={}
	extracted_parameters={'iip3_dbm':iip3}
	
	return extracted_parameters
	

# This Function finds IIP3 by only using single Pin
def extract_iip3_hb_single_pin_diff(file_name,optimization_input_parameters):
	
	p_in=optimization_input_parameters['simulation_conditions']['pin_iip3']

	fund_1=optimization_input_parameters['output_conditions']['wo']/(2*np.pi)
	fund_2=fund_1+optimization_input_parameters['simulation_conditions']['f_delta_iip3']
	f_im3=2*fund_2-fund_1

	write_pin(p_in,optimization_input_parameters)
	run_file(optimization_input_parameters)

	voutp_fund=extract_hb_magnitude(file_name,fund_1,node="Voutp")
	voutp_im3=extract_hb_magnitude(file_name,f_im3,node="Voutp")

	voutn_fund=extract_hb_magnitude(file_name,fund_1,node="Voutn")
	voutn_im3=extract_hb_magnitude(file_name,f_im3,node="Voutn")

	vout_fund=abs(voutp_fund-voutn_fund)
	vout_im3=abs(voutp_im3-voutn_im3)
	
	#print(voutp_fund,voutp_im3,voutn_fund,voutn_im3,vout_fund,vout_im3)
	# Calculating the iip3
	iip3=p_in+10*(np.log10(vout_fund)-np.log10(vout_im3))

	extracted_parameters={}
	extracted_parameters={'iip3_dbm':iip3}
	
	return extracted_parameters
	
#---------------------------------------------------------------------------------------------------------------------------

#===========================================================================================================================

#--------------------------------------------Output Functions---------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------
# Extracting Vth, un and cox from lib file
# Inputs:
# 1) lines of the lib file
# 2) MOSFET Dictionary File
# Outputs: mosfet dictionary containing mosfet parameters

def extract_mosfet_param(optimization_input_parameters,mos_dict):

	if optimization_input_parameters['model_type']=='lib':		# model files like tsmc018 or ibm013 etc..
		mos_dict=extract_mosfet_param_lib(optimization_input_parameters,mos_dict)
		return mos_dict
	
	elif optimization_input_parameters['model_type']=='pkg':	# For packages like tsmc065
		mos_dict=extract_mosfet_param_pkg(optimization_input_parameters,mos_dict)
		return mos_dict

#---------------------------------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------------------------------
# Extracting Vth, un and cox from lib file
# Inputs:
# 1) lines of the lib file
# 2) MOSFET Dictionary File
# Outputs: mosfet dictionary containing mosfet parameters

def extract_mosfet_param_lib(optimization_input_parameters,mos_dict):
	file_name=optimization_input_parameters['filename']['mos_file']
	mos_type=optimization_input_parameters['MOS_Type']
	
	param_name_vt='vth0'
	param_name_un='+u0'
	param_name_tox='tox'
	lines=extract_file(file_name)
	vt=extract_lib_param(lines,param_name_vt,mos_type)
	un=1e-4*extract_lib_param(lines,param_name_un,mos_type)
	tox=extract_lib_param(lines,param_name_tox,mos_type)
	eo=8.85*1e-12
	er=3.9
	cox=eo*er/tox
	
	mos_dict['un']=un
	mos_dict['vt']=vt
	mos_dict['cox']=cox
	
	return mos_dict

#---------------------------------------------------------------------------------------------------------------------------
# Extracting Vth, un and cox from lib file
# Inputs:
# 1) lines of the lib file
# 2) MOSFET Dictionary File
# Outputs: mosfet dictionary containing mosfet parameters

def extract_mosfet_param_pkg(optimization_input_parameters,mos_dict):

	stream = open(optimization_input_parameters['filename']['mos_param_yaml'], 'r')
	mos_param = yaml.load(stream, Loader=SafeLoader)
	stream.close()
	
	vdd=float(mos_param['vdd'])
	lmin=float(mos_param['lmin'])
	vt=float(mos_param['vt'])
	un=float(mos_param['un'])
	tox=float(mos_param['tox'])
	eo=8.85*1e-12
	er=3.9
	cox=eo*er/tox
	
	mos_dict['un']=un
	mos_dict['vt']=vt
	mos_dict['cox']=cox
	mos_dict['Lmin']=lmin
	mos_dict['vdd']=vdd
	
	return mos_dict
	

#---------------------------------------------------------------------------------------------------------------------------
# Extracting all the output parameters from chi file
# Inputs: optimization_input parameters
# Outputs: output parameters dictionary 

def extract_output_param(optimization_input_parameters):
	
	extracted_parameters_dc=extract_dc_param(optimization_input_parameters)
	extracted_parameters_ac=extract_ac_param(optimization_input_parameters)
	extracted_parameters_sp=extract_sp_param(optimization_input_parameters)
	extracted_parameters_noise=extract_noise_param(optimization_input_parameters)
	extracted_parameters_iip3=extract_iip3_param(optimization_input_parameters)

	extracted_parameters={}
	
	for param_name in extracted_parameters_dc:
		extracted_parameters[param_name]=extracted_parameters_dc[param_name]
	for param_name in extracted_parameters_ac:
		extracted_parameters[param_name]=extracted_parameters_ac[param_name]
	for param_name in extracted_parameters_sp:
		extracted_parameters[param_name]=extracted_parameters_sp[param_name]
	for param_name in extracted_parameters_noise:
		extracted_parameters[param_name]=extracted_parameters_noise[param_name]
	for param_name in extracted_parameters_iip3:
		extracted_parameters[param_name]=extracted_parameters_iip3[param_name]

	return extracted_parameters

#===========================================================================================================================


"""
====================================================================================================================================================================================
------------------------------------------------------------ FILE WRITE FUNCTIONS --------------------------------------------------------------------------------------------------
"""


#-----------------------------------------------------------------
#Function to write the include library commands in the netlist
def write_library(optimization_input_parameters):
	
	stream = open(optimization_input_parameters['filename']['library_yaml'], 'r')
	library = yaml.load(stream, Loader=SafeLoader)
	stream.close()

	filename=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.scs'
	f=open(filename,'r+')
	s=''

	flag=0
	for line in fileinput.input(filename):
		if "include" in line and flag==0:					# Change this line too
			line=library[optimization_input_parameters['model_name']]
			flag=1
		elif "include" in line and flag==1:
			line=''
		s=s+line
	
	f.truncate(0)
	f.write(s)
	f.close()

#-----------------------------------------------------------------
#Function to write the errpreset method for iip3 in the netlist
def write_errpreset(optimization_input_parameters):
	
	filename=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.scs'
	f=open(filename,'r+')
	s=''

	for line in fileinput.input(filename):
		if "errpreset" in line: 			# Change this line too
			words=line.split(' ')
			for i in range(len(words)):
				if "errpreset=" in  words[i] :
					if  len(words[i])!=len("errpreset=") :
						words[i]="errpreset="+optimization_input_parameters['simulation_conditions']['iip3_errpreset'].strip()
					else:
						print("\n\nIIP3 ERRPRESET didnt change\n\n")
			line=' '.join(words)
		s=s+line
	
	f.truncate(0)
	f.write(s)
	f.close()


#-----------------------------------------------------------------
# Command that returns the string that has to be printed in the .cir file
def print_param(param_var,val):
	return "parameters "+param_var+'='+str(val)+'\n'

#-----------------------------------------------------------------      
# Function that converts input parameter dictionary to writing dictionary
def dict_convert(circuit_parameters,optimization_input_parameters):
	write_dict={}
	simulation_conditions=optimization_input_parameters['simulation_conditions']
	
	write_dict['pin']=simulation_conditions['pin_iip3']
	write_dict['fund_2']=circuit_parameters['fo']+simulation_conditions['f_delta_iip3']
	
	for param_name in optimization_input_parameters['cir_writing_dict']:
		write_dict[param_name]=circuit_parameters[optimization_input_parameters['cir_writing_dict'][param_name]]
	
	return write_dict
            
#-----------------------------------------------------------------
# Function that modifies the .scs file
def write_param(circuit_parameters,optimization_input_parameters):
	
	write_dict=dict_convert(circuit_parameters,optimization_input_parameters)
	
	filename=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.scs'

	f=open(filename,'r+')
	s=''
	
	for line in fileinput.input(filename):
		for param_name in write_dict:
			if "parameters "+param_name+'=' in line:
				line=line.replace(line,print_param(param_name,write_dict[param_name]))
		s=s+line
	f.truncate(0)
	f.write(s)
	f.close()


#-----------------------------------------------------------------
# Function that modifies temperature in .scs file
def write_temp(temperature,optimization_input_parameters):
	
	filename=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.scs'
	
	f=open(filename,'r+')
	s=''

	new_line="Temperature options temp="+str(temperature)+"\n"			# Change this line according to the line you ewant to replace

	for line in fileinput.input(filename):
		if "Temperature options temp=" in line:					# Change this line too
			line=line.replace(line,new_line)
		s=s+line
	f.truncate(0)
	f.write(s)
	f.close()


#-----------------------------------------------------------------
# Function that modifies pin of 2 tones in .scs file
def write_pin(pin,optimization_input_parameters):
	
	filename=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.scs'
	
	f=open(filename,'r+')
	s=''

	new_line="parameters pin="+str(pin)+"\n"			# Change this line according to the line you ewant to replace

	for line in fileinput.input(filename):
		if "parameters pin=" in line:					# Change this line too
			line=line.replace(line,new_line)
		s=s+line
	f.truncate(0)
	f.write(s)
	f.close()



#-----------------------------------------------------------------
# Function that adds the MOSFET Location
def write_cir_initial(optimization_input_parameters):
	
	stream = open(optimization_input_parameters['filename']['library_yaml'], 'r')
	library = yaml.load(stream, Loader=SafeLoader)
	stream.close()
	
	filename=optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'/circ.scs'
	f=open(filename,'r+')
	s=''

	write_dict={
		'len':optimization_input_parameters['Lmin'],
		'v_dd':optimization_input_parameters['Vdd']
	}	
	
	
	flag=0
	for line in fileinput.input(filename):

		if "include" in line and flag==0:					# Change this line too
			line=library[optimization_input_parameters['model_name']]
			flag=1
		elif "include" in line and flag==1:
			line=''
		
		for param_name in write_dict:
			if "parameters "+param_name+'=' in line:
				line=line.replace(line,print_param(param_name,write_dict[param_name]))
		s=s+line

	f.truncate(0)
	f.write(s)
	f.close()

#-----------------------------------------------------------------
# Function that modifies tcs file initially
def write_tcsh_initial(optimization_input_parameters):
	
	filename=optimization_input_parameters['filename']['tcsh']
	f=open(filename,'r+')
	s=''
	
	s='#tcsh\n'
	s=s+'source ~/.cshrc\n'
	s=s+'cd '+optimization_input_parameters['filename']['directory']+optimization_input_parameters['iip3_method']+'\n'
	s=s+'spectre circ.scs =log display.log\n'
	s=s+'exit'
	
	f.truncate(0)
	f.write(s)
	f.close()

#===========================================================================================================================


"""
====================================================================================================================================================================================
------------------------------------------------------------ SPECTRE RUNNING FUNCTIONS ---------------------------------------------------------------------------------------------
"""

#-----------------------------------------------------------------------------------------------	
# This function will run the shell commands to run Spectre

def run_file(optimization_input_parameters):
	os.system('cd /home/ee18b064/cadence_project')
	os.system(optimization_input_parameters['filename']['spectre_run'])
	
#-----------------------------------------------------------------------------------------------
# This function will write the circuit parameters, run Eldo and extract the output parameters

def write_extract(circuit_parameters,optimization_input_parameters):
	
	# Writing to netlist file
	write_param(circuit_parameters,optimization_input_parameters)

	# Running netlist file
	run_file(optimization_input_parameters)
	
	# Extracting Parameters from .chi File
	extracted_parameters=extract_output_param(optimization_input_parameters)
	
	return extracted_parameters

#===========================================================================================================================

