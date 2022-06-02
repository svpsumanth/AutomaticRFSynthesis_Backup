import RFIC_Write as write
import RFIC_Param_Extraction as pe
import numpy as np

def cost_function(ref_dict,output_dict,hand_out_dict):

	# ref_dict = Dictionary which contain Reference Values
	# output_dict = current values of the recquired Quantities
	# hand_out_dict = hand Calculated Output (need only Current)

	s11_max_dB=ref_dict['s11_dB_max']			#in dB
	iip3_min_dBm=ref_dict['iip3_dBm_min']			#in dBm
	NF_max_dB=ref_dict['NF_max_dB']				#in dB
	gain_min_dB=ref_dict['gain_dB']				#in dB
	
	f=hand_out_dict['fo']
	s11_dB=output_dict['s11_dB']				#in dB
	iip3_dBm=output_dict['iip3_dBm']			#in dBm
	NF_dB=output_dict['NF_dB']				#in dB
	gain_dB=output_dict['gain_dB']				#in dB
	Io=hand_out_dict['Io']					#in A
	pwr_dc=output_dict['pwr_dc']

	if s11_dB > s11_max_dB:
		s11_dB=s11_dB-s11_max_dB
	else:
		s11_dB=0

	#CF=-(gain_dB+iip3_dBm+10*np.log(f/1e9)-10*np.log(10**(NF_dB/10)-1)-10*np.log(pwr_dc/1e-3))	
	CF_wo_s11=-(gain_dB+iip3_dBm+10*np.log(f/1e9)/np.log(10)-10*np.log(10**(NF_dB/10)-1)/np.log(10)-10*np.log(pwr_dc/1e-3)/np.log(10))
	#print(NF_dB)

	if NF_dB>12.5:
		correction_nf=4
	else:
		correction_nf=1

	if iip3_dBm< (-15):
		correction_iip3=1.25
	else:
		correction_iip3=1
	
	CF=5*s11_dB-(gain_dB+correction_iip3*iip3_dBm+10*np.log(f/1e9)/np.log(10)-correction_nf*10*np.log(10**(NF_dB/10)-1)/np.log(10)-10*np.log(pwr_dc/1e-3)/np.log(10))	
	return CF,CF_wo_s11

def Gradient(CF_old,CF_wo_s11_old,hand_out_dict,sys_req_dict,extract_param1,cir_filename,chi_filename):
	in_change=1.005 		#change + original  #1.1
	
			
			#Finding the Gradient of Io	
	hand_out_dict['Io']=in_change*hand_out_dict['Io']	
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new1,CF_wo_s11_1=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['Io']=hand_out_dict['Io']/in_change
	dum1=hand_out_dict['Io']
	slope_Io=(CF_new1-CF_old)/(((in_change-1)*dum1))
	slope_Io_2=(CF_wo_s11_1-CF_wo_s11_old)/(((in_change-1)*dum1))
	d_Io=slope_Io


	'''if CF_old!=0:
		d_Io=slope_Io
	else:
		d_Io=slope_Io_2'''


	
			#Finding the Gradient of W	
	hand_out_dict['W']=in_change*hand_out_dict['W']
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new2,CF_wo_s11_2=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['W']=hand_out_dict['W']/in_change
	dum2=hand_out_dict['W']
	slope_W=(CF_new2-CF_old)/(((in_change-1)*dum2))
	slope_W_2=(CF_wo_s11_2-CF_wo_s11_old)/(((in_change-1)*dum2))
	d_W=slope_W

	'''if CF_old!=0:
		d_W=slope_W
	else:
		d_W=slope_W_2'''

			#Finding the Gradient of Rb	
	hand_out_dict['Rb']=in_change*hand_out_dict['Rb']
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new3,CF_wo_s11_3=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['Rb']=hand_out_dict['Rb']/in_change
	dum3=hand_out_dict['Rb']
	slope_Rb=(CF_new3-CF_old)/(((in_change-1)*dum3))
	slope_Rb_2=(CF_wo_s11_3-CF_wo_s11_old)/(((in_change-1)*dum3))
	d_Rb=slope_Rb
		

	'''if CF_old!=0:
		d_Rb=slope_Rb
	else:
		d_Rb=slope_Rb_2'''

			#Finding the Gradient of Rd	
	hand_out_dict['Rd']=in_change*hand_out_dict['Rd']
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new4,CF_wo_s11_4=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['Rd']=hand_out_dict['Rd']/in_change
	dum4=hand_out_dict['Rd']		
	slope_Rd=(CF_new4-CF_old)/(((in_change-1)*dum4))
	slope_Rd_2=(CF_wo_s11_4-CF_wo_s11_old)/(((in_change-1)*dum4))
	d_Rd=slope_Rd

	'''if CF_old!=0:
		d_Rd=slope_Rd
	else:
		d_Rd=slope_Rd_2'''

			#Finding the Gradient of fo	
	hand_out_dict['fo']=in_change*hand_out_dict['fo']	
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new5,CF_wo_s11_5=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['fo']=hand_out_dict['fo']/in_change
	dum5=hand_out_dict['fo']
	slope_fo=(CF_new5-CF_old)/(((in_change-1)*dum5))
	slope_fo_2=(CF_wo_s11_5-CF_wo_s11_old)/(((in_change-1)*dum5))
	d_fo=slope_fo
	

	'''if CF_old!=0:
		d_fo=slope_fo
	else:
		d_fo=slope_fo_2'''
	
	coeff_grad={'Io':d_Io,'W':d_W,'Rb':d_Rb,'Rd':d_Rd,'fo':d_fo}
	coeff_lf={'Io':0,'W':0,'Rb':0,'Rd':0}
	return coeff_grad,coeff_lf























