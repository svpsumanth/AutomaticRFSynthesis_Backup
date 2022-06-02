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

	s11_dB=output_dict['s11_dB']				#in dB
	iip3_dBm=output_dict['iip3_dBm']			#in dBm
	NF_dB=output_dict['NF_dB']				#in dB
	gain_dB=output_dict['gain_dB']				#in dB
	Io=hand_out_dict['Io']					#in A

	out_check=np.array([0,0,0,0])		# if outputs are with in range then=0 else 1
						# [gain,iip3,s11,nf]



	As=1/abs(s11_max_dB)				# Coefficients of the Parameters in Cost Function
	Ai=1/abs(iip3_min_dBm)
	An=1/abs(NF_max_dB)
	Ag=1/abs(gain_min_dB)
	Ac=600

	if s11_dB > s11_max_dB:
		s11_dB=s11_dB-s11_max_dB
		out_check[2]=1
	else:
		s11_dB=0
		out_check[2]=0

	if NF_dB > NF_max_dB :
		NF_dB=NF_dB-NF_max_dB
		out_check[3]=1
	else:
		NF_dB=0
		out_check[2]=0

	if gain_dB < gain_min_dB :
		gain_dB=gain_min_dB-gain_dB
		out_check[0]=1
	else:
		gain_dB=0
		out_check[0]=0

	if iip3_dBm < iip3_min_dBm :
		iip3_dBm=iip3_min_dBm-iip3_dBm
		out_check[1]=1
	else:
		iip3_dBm=0
		out_check[1]=0

	CF=As*(s11_dB)+Ai*(iip3_dBm)+An*(NF_dB)+Ag*(gain_dB)+Ac*Io
	#CF=Ac*Io
	CF_wo_Io=As*(s11_dB)+Ai*(iip3_dBm)+An*(NF_dB)+Ag*(gain_dB)
	return CF,CF_wo_Io,out_check

def Gradient(CF_old,CF_wo_Io_old,out_check_old,hand_out_dict,sys_req_dict,extract_param1,cir_filename,chi_filename):
	in_change=1.001 		#change + original  #1.1
	
			
			#Finding the Gradient of Io	
	hand_out_dict['Io']=in_change*hand_out_dict['Io']	
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new1,CF_wo_Io1,out_check=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['Io']=hand_out_dict['Io']/in_change
	dum1=hand_out_dict['Io']
	slope_Io=(CF_new1-CF_old)/(((in_change-1)*dum1))
	slope_Io_2=(CF_wo_Io1-CF_wo_Io_old)/(((in_change-1)*dum1))
	d_Io=slope_Io

	gain=(extract_param2['gain_dB']-extract_param1['gain_dB'])/extract_param1['gain_dB']
	s11=(extract_param2['s11_dB']-extract_param1['s11_dB'])/abs(extract_param1['s11_dB'])
	iip3=(extract_param2['iip3_dBm']-extract_param1['iip3_dBm'])/abs(extract_param1['iip3_dBm'])
	nf=(extract_param2['NF_dB']-extract_param1['NF_dB'])/extract_param1['NF_dB']

	Sense_Io=np.array([gain,iip3,s11,nf])

	

	'''if CF_wo_Io_old==0:
		d_Io=slope_Io
	else:
		d_Io=slope_Io_2'''
	
			#Finding the Gradient of W	
	hand_out_dict['W']=in_change*hand_out_dict['W']
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new2,CF_wo_Io2,out_check=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['W']=hand_out_dict['W']/in_change
	dum2=hand_out_dict['W']
	slope_W=(CF_new2-CF_old)/(((in_change-1)*dum2))
	slope_W_2=(CF_wo_Io2-CF_wo_Io_old)/(((in_change-1)*dum2))
	d_W=slope_W

	gain=(extract_param2['gain_dB']-extract_param1['gain_dB'])/extract_param1['gain_dB']
	s11=(extract_param2['s11_dB']-extract_param1['s11_dB'])/extract_param1['s11_dB']
	iip3=(extract_param2['iip3_dBm']-extract_param1['iip3_dBm'])/extract_param1['iip3_dBm']
	nf=(extract_param2['NF_dB']-extract_param1['NF_dB'])/extract_param1['NF_dB']

	Sense_W=np.array([gain,iip3,s11,nf])

	

	'''if CF_wo_Io_old==0:
		d_W=slope_W
	else:
		d_W=slope_W_2'''

			#Finding the Gradient of Rb	
	hand_out_dict['Rb']=in_change*hand_out_dict['Rb']
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new3,CF_wo_Io3,out_check=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['Rb']=hand_out_dict['Rb']/in_change
	dum3=hand_out_dict['Rb']
	slope_Rb=(CF_new3-CF_old)/(((in_change-1)*dum3))
	slope_Rb_2=(CF_wo_Io3-CF_wo_Io_old)/(((in_change-1)*dum3))
	d_Rb=slope_Rb

	gain=(extract_param2['gain_dB']-extract_param1['gain_dB'])/extract_param1['gain_dB']
	s11=(extract_param2['s11_dB']-extract_param1['s11_dB'])/extract_param1['s11_dB']
	iip3=(extract_param2['iip3_dBm']-extract_param1['iip3_dBm'])/extract_param1['iip3_dBm']
	nf=(extract_param2['NF_dB']-extract_param1['NF_dB'])/extract_param1['NF_dB']

	Sense_Rb=np.array([gain,iip3,s11,nf])

		

	'''if CF_wo_Io_old==0:
		d_Rb=slope_Rb
	else:
		d_Rb=slope_Rb_2'''

			#Finding the Gradient of Rd	
	hand_out_dict['Rd']=in_change*hand_out_dict['Rd']
	output_dict,extract_param2=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF_new4,CF_wo_Io4,out_check=cost_function(sys_req_dict,output_dict,hand_out_dict)
	hand_out_dict['Rd']=hand_out_dict['Rd']/in_change
	dum4=hand_out_dict['Rd']		
	slope_Rd=(CF_new4-CF_old)/(((in_change-1)*dum4))
	slope_Rd_2=(CF_wo_Io4-CF_wo_Io_old)/(((in_change-1)*dum4))
	d_Rd=slope_Rd

	gain=(extract_param2['gain_dB']-extract_param1['gain_dB'])/extract_param1['gain_dB']
	s11=(extract_param2['s11_dB']-extract_param1['s11_dB'])/extract_param1['s11_dB']
	iip3=(extract_param2['iip3_dBm']-extract_param1['iip3_dBm'])/extract_param1['iip3_dBm']
	nf=(extract_param2['NF_dB']-extract_param1['NF_dB'])/extract_param1['NF_dB']

	Sense_Rd=np.array([gain,iip3,s11,nf])

	'''if CF_wo_Io_old==0:
		d_Rd=slope_Rd
	else:
		d_Rd=slope_Rd_2'''
	
	coeff_grad={'Io':d_Io,'W':d_W,'Rb':d_Rb,'Rd':d_Rd}

	print('\n',Sense_Io)
	print(Sense_W)
	print(Sense_Rb)
	print(Sense_Rd,'\n')

	Out_Dir_Sense=np.array([1,1,-1,-1])	#[gain iip3 s11 nf]   1 - increasing, -1 - decreasing
	Io_Sign= Sense_Io/abs(Sense_Io)

	'''Sense_Io=Sense_Io*out_check_old
	Sense_W=Sense_W*out_check_old
	Sense_Rb=Sense_Rb*out_check_old
	Sense_Rd=Sense_Rd*out_check_old'''

	print('\n',Sense_Io)
	print(Sense_W)
	print(Sense_Rb)
	print(Sense_Rd,'\n')
	
	Io_Coeff_sign=-1*Io_Sign*Out_Dir_Sense

	eps=1e-12  		#makes sure that 0/0 doesnt happen
	gain_sum=(abs(Sense_Io[0])+abs(Sense_W[0])+abs(Sense_Rd[0])+abs(Sense_Rb[0])+eps)
	iip3_sum=(abs(Sense_Io[1])+abs(Sense_W[1])+abs(Sense_Rd[1])+abs(Sense_Rb[1])+eps)
	s11_sum=(abs(Sense_Io[2])+abs(Sense_W[2])+abs(Sense_Rd[2])+abs(Sense_Rb[2])+eps)
	nf_sum=(abs(Sense_Io[3])+abs(Sense_W[3])+abs(Sense_Rd[3])+abs(Sense_Rb[3])+eps)

	Sense_Io=np.array([abs(Sense_Io[0])/gain_sum,abs(Sense_Io[1])/iip3_sum,abs(Sense_Io[2])/s11_sum,abs(Sense_Io[3])/nf_sum])*Io_Coeff_sign
	Sense_W=np.array([abs(Sense_W[0])/gain_sum,abs(Sense_W[1])/iip3_sum,abs(Sense_W[2])/s11_sum,abs(Sense_W[3])/nf_sum])
	Sense_Rb=np.array([abs(Sense_Rb[0])/gain_sum,abs(Sense_Rb[1])/iip3_sum,abs(Sense_Rb[2])/s11_sum,abs(Sense_Rb[3])/nf_sum])
	Sense_Rd=np.array([abs(Sense_Rd[0])/gain_sum,abs(Sense_Rd[1])/iip3_sum,abs(Sense_Rd[2])/s11_sum,abs(Sense_Rd[3])/nf_sum])

	print('\n',Sense_Io)
	print(Sense_W)
	print(Sense_Rb)
	print(Sense_Rd,'\n')
	
	
	coeff_Io=4**(sum(Sense_Io))
	coeff_W=4**(sum(abs(Sense_W)))
	coeff_Rb=4**(sum(abs(Sense_Rb)))
	coeff_Rd=4**(sum(abs(Sense_Rd)))

	#print('\n',Sense_Io,'\n')

	coeff_lf={'Io':coeff_Io,'W':coeff_W,'Rb':coeff_Rb,'Rd':coeff_Rd}

	return coeff_grad,coeff_lf























