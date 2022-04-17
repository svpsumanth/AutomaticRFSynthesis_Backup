#This function takes in the file which contain all the noise details and returns the total integrated noise figure i.e..  integ(out_noise^2)/integ(out_noise_of_input^2*Gain^2)

import numpy as np
from matplotlib import pylab
from pylab import *
import cmath

def extract_integrated_nf(filename):
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

	loglog(freq_list,out_frm_input_list)
	loglog(freq_list,out_list)	
	show()

	loglog(freq_list,f_list)	
	show()
	return integ_nf



def extract_complex_vout(lines):
	# Extracting Vout Magnitude
	words=lines.split()
	char_r=words[1].split('(')[1]
	char_i=words[2].split(')')[0]

	vol_r=float(char_r)
	vol_i=float(char_i)
	vol=complex(vol_r,vol_i)

	return vol

def extract_conv_gain(filename_fund,filename_ac,Vinp='Vinp',Vinn='Vinn',Voutp='Voutp',Voutn='Voutn'):
	f=open(filename_fund)
	lines=f.readlines()
	f.close()

	freq_in_list=[]
	Vinp_list=[]
	Vinn_list=[]		
	Voutp_list=[]
	Voutn_list=[]		
	freq_out_list=[]

	freq_flag=0
	for line in lines:
		line=line.strip()
		if "\"freq\"" in line:
			words=line.split(' ')
			if len(words)==2:
				freq_in_list.append(float(words[1]))
				freq_flag=1
		if freq_flag==1:
			
			if "\""+Vinp+"\"" in line:
				#words=line.split(' ')
				Vinp_list.append(extract_complex_vout(line))
				freq_flag=0

			if "\""+Vinn+"\"" in line:
				#words=line.split(' ')
				Vinn_list.append(extract_complex_vout(line))

	Vinn_list=np.array(Vinn_list)
	Vinp_list=np.array(Vinp_list)
	Vin_list=Vinp_list-Vinn_list
	
	f=open(filename_ac)
	lines=f.readlines()
	f.close()

	freq_flag=0
	for line in lines:
		line=line.strip()
		if "\"freq\"" in line:
			words=line.split(' ')
			if len(words)==2:
				freq_out_list.append(float(words[1]))
				freq_flag=1
		if freq_flag==1:
			
			if "\""+Voutp+"\"" in line:
				#words=line.split(' ')
				Voutp_list.append(extract_complex_vout(line))
				freq_flag=0

			if "\""+Voutn+"\"" in line:
				#words=line.split(' ')
				Voutn_list.append(extract_complex_vout(line))
	
	Voutn_list=np.array(Voutn_list)
	Voutp_list=np.array(Voutp_list)
	Vout_list=Voutp_list-Voutn_list

	gain=Vout_list/Vin_list
	
	loglog(freq_out_list,abs(gain))
	show()

	return abs(gain[-1])


filename="/home/ee18b064/cadence_project/Double_Balanced_Mixer/ideal/hb_single_pin_diff/circ.raw/hbnoise.pnoise_hbnoise"
filename_fund="/home/ee18b064/cadence_project/Double_Balanced_Mixer/ideal/hb_single_pin_diff/circ.raw/hb_conv_gain.0.pac_hbac"
filename_ac="/home/ee18b064/cadence_project/Double_Balanced_Mixer/ideal/hb_single_pin_diff/circ.raw/hb_conv_gain.-1.pac_hbac"

print(extract_integrated_nf(filename))
print(20*np.log10(extract_conv_gain(filename_fund,filename_ac)))
