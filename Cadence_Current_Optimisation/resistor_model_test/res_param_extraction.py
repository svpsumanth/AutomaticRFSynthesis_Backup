#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

Resistor Data Extraction File:
"""
#===========================================================================================================================


import numpy as np
import matplotlib.pyplot as plt
import fileinput
import math
import cmath
import os
import yaml
from yaml.loader import SafeLoader


#-------------------------------------------------------------------------------------------------------------------------
# For a given fundamental frequency and current(signal) this function evaluates THD
def extract_THD(file_dir,param):
	
	freq=param['fund_1']
	harmonics=np.arange(1,15)*freq
	
	harmonic_Vol=[]

	for i in harmonics:
		harmonic_Vol.append(extract_hb_magnitude(file_dir,i))	
	
	harmonic_Vol=np.array(harmonic_Vol)
	
	THD=20*np.log(sum(harmonic_Vol[1:]**2)/harmonic_Vol[0]**2)/np.log(10)
	return THD


#-------------------------------------------------------------------------------------------------------------------------
# For a given fundamental frequency and current(signal) this function evaluates THD

def extract_ac_resistance(file_dir,param_list,param):

	freqRange=np.logspace(7,10,30)

	acResist=[]
	for freq in freqRange:
		param['fund_1']=freq
		run_param(file_dir,param_list,param)
		acResist.append(extract_hb_magnitude(file_dir,freq)/param['i_sin'])
	
	acResist_dic={}
	acResist_dic['acResist']=acResist
	acResist_dic['freq']=freqRange	
	return acResist_dic
		
		



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

#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the DC from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_dc_param(file_dir):

	file_name=file_dir+'/dc.out'
	lines=extract_file(file_name)

	lines=lines[7:]
	lines=lines[0].split()

	Res_dc=valueE_to_value(lines[3])
	
	return Res_dc

#---------------------------------------------------------------------------------------------------------------------------	
# Extracting the DC from the file
# Inputs: Optimization_input_parameters
# Output: Dictionary with all the parameters

def extract_dc_Cur(file_dir):

	file_name=file_dir+'/dc.out'
	lines=extract_file(file_name)

	lines=lines[7:]
	lines=lines[0].split()

	I_dc=valueE_to_value(lines[2])
	
	return I_dc
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
# Extracts Vout_magnitude from hb,pss file line
# Inputs: Line
# Output: Vout_Magnitude

def extract_complex_vout(lines):
	# Extracting Vout Magnitude
	lines=lines.split()
	char_r=lines[1].split('(')[1]
	char_i=lines[2].split(')')[0]

	vout_r=valueE_to_value(char_r)
	vout_i=valueE_to_value(char_i)
	
	#vout_mag=np.sqrt(vout_r*vout_r+vout_i*vout_i)
	vout=complex(vout_r,vout_i)

	return vout

#---------------------------------------------------------------------------------------------------------------------------	
# Extracting Vout magnitude of fundamental and im3 from file ( for hb_sweep )
# Inputs: Filename, Optimization Input Parameters
# Output: Magnitude of Vout at fundamental and im3

def extract_hb_magnitude(file_dir,freq):
	
	file_name=file_dir+'/circ.raw/hb_test.fi.pss_hb'
	
	lines=extract_file(file_name)

	fund_1=freq
	f_error=freq/100

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
					if 'V2' in lines[0].split()[0]:
						flag_test=0
						v2=extract_complex_vout(lines[0])

						if 'V3' in lines[1].split()[0]:
							v3=extract_complex_vout(lines[1])
						vout=abs(v2-v3)

					else:
						lines=lines[1:]
				flag_fun=1
			lines=lines[1:]
			
			if flag_fun==1 :
				break
		else:
			lines=lines[1:]

		
	return vout

#---------------------------------------------------------------------------------------------------------------------------
# Function That runs the netlist after writing the parameters

def run_param(file_dir,param_list,param):
	write_param(file_dir,param_list,param)
	run_file()

#-----------------------------------------------------------------
# Function that modifies temperature in .scs file
def write_temp(file_dir,temperature):
	
	file_name=file_dir+'/circ.scs'
	
	f=open(file_name,'r+')
	s=''

	new_line="parameters cir_temp="+str(temperature)+"\n"			# Change this line according to the line you ewant to replace

	for line in fileinput.input(file_name):
		if "parameters cir_temp=" in line:					# Change this line too
			line=line.replace(line,new_line)
		s=s+line
	f.truncate(0)
	f.write(s)
	f.close()

#-----------------------------------------------------------------
# Function that modifies Resistor model in .scs file
def write_res(file_dir,res,res_name):
	
	file_name=file_dir+'/circ.scs'
	
	f=open(file_name,'r+')
	s=''
	
	if res['type']=='n':
		char='0'
	elif res['type']=='p':
		char='V4'
	new_line="Resistance (V2 V3 " +char+ ") " +res_name+" wr=wid lr=len" +"\n"			# Change this line according to the line you ewant to replace

	for line in fileinput.input(file_name):
		if 'Resistance' in line:					
			line=line.replace(line,new_line)
		s=s+line
	f.truncate(0)
	f.write(s)
	f.close()



#-----------------------------------------------------------------
# Function that modifies the .scs file
def write_param(file_dir,param_list,param):
	
	filename=file_dir+'/circ.scs'
	f=open(filename,'r+')
	s=''

	for line in fileinput.input(filename):
		
		for param_name in param_list:
			
			if "parameters "+param_name+'=' in line:
				line=line.replace(line,"parameters "+param_name+'='+str(param[param_name])+'\n')

		s=s+line
	f.truncate(0)
	f.write(s)
	f.close()


def run_file():
	os.system('cd /home/ee18b064/cadence_project')
	os.system('tcsh /home/ee18b064/Optimization/Cadence_Current_Optimisation/res_mod.tcsh')


#-----------------------------------------------------------------------------------------------
#Function that computes THD for different currents for all the models and saves it in the mentioned Directory

def save_THD_plots(file_dir,results_dir,model,param,param_list):
	
	for i in model['all_models'] :

		write_res(file_dir,model[i],str(i))
		param['wid']=model[i]['wmin']	#minimum width
		param['len']=model[i]['lmin']	#minimum length
		param['i_cur']=0
		param['v_dc']=0
		param['i_sin']=1e-6

		THD_list=[]
		sig_cur=np.logspace(-6,-3,10)

		for cur in sig_cur:
			param['i_sin']=cur
			run_param(file_dir,param_list,param)
			THD=extract_THD(file_dir,param)
			THD_list.append(THD)
		
		thd_dic={}
		thd_dic['THD_list']=THD_list
		thd_dic['sig_cur']=sig_cur
		thd_dic['model_name']=i
		
		plot_thd_cur_plots(thd_dic,results_dir)


#-----------------------------------------------------------------------------------------------
# This Function is driver to find AC Resistance for different freq and at corner dimensions

def ac_resist_driver(file_dir,results_dir,model,param,param_list):
	
	for i in model['all_models']:
		write_res(file_dir,model[i],str(i))
		
		# W-min L-min
		param['wid']=model[i]['wmin']
		param['len']=model[i]['lmin']

		param['i_cur']=0
		param['v_dc']=1
		param['i_sin']=0
		run_param(file_dir,param_list,param)	
		dcResist=extract_dc_param(file_dir)

		param['v_dc']=1
		param['i_cur']=0
		param['i_sin']=1e-6
		run_param(file_dir,param_list,param)
		acResist_dic= extract_ac_resistance(file_dir,param_list,param)
		acResist_dic['model_name']=i
		acResist_dic['dcResist']=len(acResist_dic['acResist'])*[dcResist]
		
		save_path=results_dir+'AC_Resist/SS/'
		save_acresist(acResist_dic,save_path)

		
		# W-min  L-max
		param['wid']=model[i]['wmin']
		param['len']=model[i]['lmax']

		param['i_cur']=0
		param['v_dc']=1
		param['i_sin']=0
		run_param(file_dir,param_list,param)	
		dcResist=extract_dc_param(file_dir)

		param['v_dc']=1
		param['i_cur']=0
		param['i_sin']=1e-6
		run_param(file_dir,param_list,param)
		acResist_dic= extract_ac_resistance(file_dir,param_list,param)
		acResist_dic['model_name']=i
		acResist_dic['dcResist']=len(acResist_dic['acResist'])*[dcResist]
		
		save_path=results_dir+'AC_Resist/SL/'
		save_acresist(acResist_dic,save_path)

		# W-max  L-max
		param['wid']=model[i]['wmax']
		param['len']=model[i]['lmax']

		param['i_cur']=0
		param['v_dc']=1
		param['i_sin']=0
		run_param(file_dir,param_list,param)	
		dcResist=extract_dc_param(file_dir)

		param['v_dc']=1
		param['i_cur']=0
		param['i_sin']=1e-6
		run_param(file_dir,param_list,param)
		acResist_dic= extract_ac_resistance(file_dir,param_list,param)
		acResist_dic['model_name']=i
		acResist_dic['dcResist']=len(acResist_dic['acResist'])*[dcResist]
		
		save_path=results_dir+'AC_Resist/LL/'
		save_acresist(acResist_dic,save_path)


		# W-max  L-min
		param['wid']=model[i]['wmax']
		param['len']=model[i]['lmin']

		param['i_cur']=0
		param['v_dc']=1
		param['i_sin']=0
		run_param(file_dir,param_list,param)	
		dcResist=extract_dc_param(file_dir)

		param['v_dc']=1
		param['i_cur']=0
		param['i_sin']=1e-6
		run_param(file_dir,param_list,param)
		acResist_dic= extract_ac_resistance(file_dir,param_list,param)
		acResist_dic['model_name']=i
		acResist_dic['dcResist']=len(acResist_dic['acResist'])*[dcResist]
		
		save_path=results_dir+'AC_Resist/LS/'
		save_acresist(acResist_dic,save_path)

	
#-----------------------------------------------------------------------------------------------
# This Function is driver to find AC Resistance for different freq and at corner dimensions

def dc_resist_driver(file_dir,results_dir,model,param,param_list):

	for i in model['all_models']:
		write_res(file_dir,model[i],str(i))

		vRange=np.linspace(0.1,1,15)

		#SS
		dcResist=[]
		param['i_cur']=0
		param['i_sin']=1e-6
		param['wid']=model[i]['wmin']
		param['len']=model[i]['lmin']
		
		for v in vRange:
			param['v_dc']=v
			run_param(file_dir,param_list,param)
			dcResist.append(extract_dc_param(file_dir))
		
		dcResist_dic={}
		dcResist_dic['dcResist']=dcResist
		dcResist_dic['vol']=vRange
		dcResist_dic['model_name']=i
	
		save_path=results_dir+'DC_Resist/SS/'
		#print(dcResist)
		save_dcresist(dcResist_dic,save_path)

		#LS
		dcResist=[]
		param['i_cur']=0
		param['i_sin']=1e-6
		param['wid']=model[i]['wmax']
		param['len']=model[i]['lmin']
		
		for v in vRange:
			param['v_dc']=v
			run_param(file_dir,param_list,param)
			dcResist.append(extract_dc_param(file_dir))
		
		dcResist_dic={}
		dcResist_dic['dcResist']=dcResist
		dcResist_dic['vol']=vRange
		dcResist_dic['model_name']=i
	
		save_path=results_dir+'DC_Resist/LS/'
		save_dcresist(dcResist_dic,save_path)

		#SL
		dcResist=[]
		param['i_cur']=0
		param['i_sin']=1e-6
		param['wid']=model[i]['wmin']
		param['len']=model[i]['lmax']
		
		for v in vRange:
			param['v_dc']=v
			run_param(file_dir,param_list,param)
			dcResist.append(extract_dc_param(file_dir))
		
		dcResist_dic={}
		dcResist_dic['dcResist']=dcResist
		dcResist_dic['vol']=vRange
		dcResist_dic['model_name']=i
	
		save_path=results_dir+'DC_Resist/SL/'
		save_dcresist(dcResist_dic,save_path)


		# LL		
		dcResist=[]
		param['i_cur']=0
		param['i_sin']=1e-6
		param['wid']=model[i]['wmax']
		param['len']=model[i]['lmax']
		
		for v in vRange:
			param['v_dc']=v
			run_param(file_dir,param_list,param)
			dcResist.append(extract_dc_param(file_dir))
		
		dcResist_dic={}
		dcResist_dic['dcResist']=dcResist
		dcResist_dic['vol']=vRange
		dcResist_dic['model_name']=i
	
		save_path=results_dir+'DC_Resist/LL/'
		save_dcresist(dcResist_dic,save_path)


#-----------------------------------------------------------------------------------------------
# This Function is driver to find Current vs Voltage

def current_driver(file_dir,results_dir,model,param,param_list):

	for i in model['all_models']:
		write_res(file_dir,model[i],str(i))

		vRange=np.linspace(0.01,1,40)

		#SS
		current=[]
		param['i_cur']=0
		param['i_sin']=1e-6
		param['wid']=model[i]['wmin']
		param['len']=model[i]['lmin']
		
		for v in vRange:
			param['v_dc']=v
			run_param(file_dir,param_list,param)
			current.append(extract_dc_Cur(file_dir))
		
		current_dic={}
		current_dic['current']=current
		current_dic['vol']=vRange
		current_dic['model_name']=i
	
		save_path=results_dir+'Current/SS/'
		save_current(current_dic,save_path)

		#LS
		current=[]
		param['i_cur']=0
		param['i_sin']=1e-6
		param['wid']=model[i]['wmax']
		param['len']=model[i]['lmin']
		
		for v in vRange:
			param['v_dc']=v
			run_param(file_dir,param_list,param)
			current.append(extract_dc_Cur(file_dir))
		
		current_dic={}
		current_dic['current']=current
		current_dic['vol']=vRange
		current_dic['model_name']=i
	
		save_path=results_dir+'Current/LS/'
		save_current(current_dic,save_path)

		#SL
		current=[]
		param['i_cur']=0
		param['i_sin']=1e-6
		param['wid']=model[i]['wmin']
		param['len']=model[i]['lmax']
		
		for v in vRange:
			param['v_dc']=v
			run_param(file_dir,param_list,param)
			current.append(extract_dc_Cur(file_dir))
		
		current_dic={}
		current_dic['current']=current
		current_dic['vol']=vRange
		current_dic['model_name']=i
	
		save_path=results_dir+'Current/SL/'
		save_current(current_dic,save_path)


		# LL		
		current=[]
		param['i_cur']=0
		param['i_sin']=1e-6
		param['wid']=model[i]['wmax']
		param['len']=model[i]['lmax']
		
		for v in vRange:
			param['v_dc']=v
			run_param(file_dir,param_list,param)
			current.append(extract_dc_Cur(file_dir))
		
		current_dic={}
		current_dic['current']=current
		current_dic['vol']=vRange
		current_dic['model_name']=i
	
		save_path=results_dir+'Current/LL/'
		save_current(current_dic,save_path)


#-----------------------------------------------------------------------------------------------
# Plotting acResistance vs Frequency

def save_acresist(acResist_dic,results_dir):
	
	print("\n\nSaving the Plot for AC Resistance vs Freq of "+acResist_dic['model_name']+'\n\n')
	
	fig=plt.semilogx(acResist_dic['freq'],acResist_dic['acResist'],label='AC')
	fig=plt.semilogx(acResist_dic['freq'],acResist_dic['dcResist'],label='DC')
	plt.legend()	
	
	filepath=results_dir+'png/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	plt.savefig(filepath+acResist_dic['model_name']+'.png')	

	filepath=results_dir+'pdf/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	plt.savefig(filepath+acResist_dic['model_name']+'.pdf')	
	plt.clf()

#-----------------------------------------------------------------------------------------------
# Plotting dcResistance vs Bias Voltage

def save_dcresist(dcResist_dic,results_dir):
	
	print("\n\nSaving the Plot for DC Resistance vs Bias of "+dcResist_dic['model_name']+'\n\n')
	
	fig=plt.plot(dcResist_dic['vol'],dcResist_dic['dcResist'])	
	
	filepath=results_dir+'png/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	plt.savefig(filepath+dcResist_dic['model_name']+'.png')	

	filepath=results_dir+'pdf/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	plt.savefig(filepath+dcResist_dic['model_name']+'.pdf')	
	plt.clf()


# Plotting dcResistance vs Bias Voltage

def save_current(current_dic,results_dir):
	
	print("\n\nSaving the Plot for Current vs Bias of "+current_dic['model_name']+'\n\n')
	
	fig=plt.plot(current_dic['vol'],current_dic['current'])	
	plt.ylabel('DC Current(A)')
	plt.xlabel('Bias Voltage')
	filepath=results_dir+'png/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	plt.savefig(filepath+current_dic['model_name']+'.png')	

	filepath=results_dir+'pdf/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	plt.savefig(filepath+current_dic['model_name']+'.pdf')	
	plt.clf()



#-----------------------------------------------------------------------------------------------
# Plotting THD vs Current

def plot_thd_cur_plots(thd_dic,results_dir):
	
	print("\n\nSaving the Plot for THD vs Current of "+thd_dic['model_name']+'\n\n')
	
	fig=plt.semilogx(thd_dic['sig_cur'],thd_dic['THD_list'])

	filepath=results_dir+'THDvsCUR/'+'png/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	plt.savefig(filepath+thd_dic['model_name']+'.png')	

	filepath=results_dir+'THDvsCUR/'+'pdf/'
	if not os.path.exists(filepath):
		os.makedirs(filepath)
	plt.savefig(filepath+thd_dic['model_name']+'.pdf')	
	plt.clf()





















