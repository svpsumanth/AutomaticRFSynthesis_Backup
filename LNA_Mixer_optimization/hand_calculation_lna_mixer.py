#===========================================================================================================================
"""
Name: Pavan Sumanth
Roll Number: EE18B064

Hand Calculations 1 File:
"""
#===========================================================================================================================
import numpy as np
import math
import common_functions as cf
import spectre as sp

#===========================================================================================================================

	
#-----------------------------------------------------------------------------------------------
# Calculating DC Output Values from Initial Circuit Parameters
def calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions,optimization_input_parameters):
	vs=0
	vgs=mos_parameters['vt']+ np.sqrt(2*circuit_parameters['Ibias']*optimization_input_parameters['Lmin']/(mos_parameters['un']*mos_parameters['cox']*circuit_parameters['W1']))
	vg=vgs+vs
	vd=mos_parameters['vt']+optimization_input_parameters['pre_optimization']['body_threshold']+ np.sqrt(circuit_parameters['Ibias']*optimization_input_parameters['Lmin']/(mos_parameters['un']*mos_parameters['cox']*circuit_parameters['W2']))
	
	dc_outputs={'vg':vg,'vd':vd,'vs':vs}
	return dc_outputs
	

def DC_linear_correct(circuit_parameters,mos_parameters,optimization_input_parameters,extracted_parameters):		# Correcting the Bias Values
	count=10
	while extracted_parameters['region']<=1 and count>0:
		print("DC Correct loop : ",count)
		circuit_parameters['W2']=1.07*circuit_parameters['W2']
		extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
		count=count-1
	opt_conditions=optimization_input_parameters['output_conditions']
	# Calculating dc outputs
	dc_outputs=calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions,optimization_input_parameters)
	
	# Running Eldo
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)

	return circuit_parameters,dc_outputs,extracted_parameters

def DC_subthreshold_correct(circuit_parameters,mos_parameters,optimization_input_parameters,extracted_parameters):		# Correcting the Bias Values
	count=12
	safe_count=0
	Vdd=optimization_input_parameters['Vdd']
	opt_conditions=optimization_input_parameters['output_conditions']
	gain_db	=opt_conditions['conv_gain_db']
	gain=cf.db_to_normal(gain_db/2)
	while count>0:
		print("DC subthreshold correct loop : ",count)
		print("Vgs-Vth : ",extracted_parameters['vg1']-extracted_parameters['vt'])
		print("Vg : ",extracted_parameters['vg1'] , "Vth : ", extracted_parameters['vt'], "Vdsat : ",extracted_parameters['vdsat1'])

		if extracted_parameters['region']==2:
			safe_count=safe_count+1
			print("Safe Count : ",safe_count)
			if extracted_parameters['vg1']-extracted_parameters['vt']>20e-3 or safe_count==20:			
				break

		circuit_parameters['Ibias']=1.07*circuit_parameters['Ibias']
		#circuit_parameters['W1']=1.04*circuit_parameters['W1']
		gm=extracted_parameters['gm1']
		circuit_parameters['Rd']=min((np.pi/2)*(gain/gm),2*Vdd/(3*circuit_parameters['Ibias']))
		circuit_parameters['W2']=circuit_parameters['W2']*1.07
		extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
		
		
		count=count-1
	opt_conditions=optimization_input_parameters['output_conditions']
	# Calculating dc outputs
	dc_outputs=calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions,optimization_input_parameters)
	
	# Running Eldo
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)

	return circuit_parameters,dc_outputs,extracted_parameters


def calculate_initial_parameters(mos_parameters,optimization_input_parameters):
	print("Hello")
	calculate_initial_parameters_lna(mos_parameters,optimization_input_parameters)
	calculate_initial_parameters_mixer(mos_parameters,optimization_input_parameters)

def calculate_initial_parameters_lna(mos_parameters,optimization_input_parameters):
	threshold1=optimization_input_parameters['pre_optimization']['C_threshold']
	threshold2=optimization_input_parameters['pre_optimization']['Rbias_threshold']
	opt_conditions=optimization_input_parameters['output_conditions']
	inter_conditions=optimization_input_parameters['intermediate_specs']

	nf_db	=inter_conditions['lna_nf_db']
	gain_db	=inter_conditions['lna_gain_db']
	Rs	=opt_conditions['Rs']
	iip3_dbm=inter_conditions['lna_iip3_dbm']
	fo	=opt_conditions['fo']
	s11_db	=opt_conditions['s11_db']
	L	=optimization_input_parameters['Lmin']
	Vdd	=optimization_input_parameters['Vdd']
	mew_n	=mos_parameters['un']
	Cox	=mos_parameters['cox']
	
	gamma=2
	k=1.5
	
	f=cf.db_to_normal(nf_db)
	gain=cf.db_to_normal(gain_db/2)
	s11=cf.db_to_normal(s11_db)
	
	
	p1dbm=iip3_dbm-9.6
	pin=(1e-3)*10**(p1dbm/10)
	vosw=gain*np.sqrt(8*Rs*pin)+optimization_input_parameters['pre_optimization']['vosw_threshold']
	vosw=vosw

	Zim_max=0.5*Rs*np.sqrt((1-s11)/s11) 
	Io_min=(k**2)*np.pi*2*fo*(L**2)*Zim_max/(3*mew_n*Rs**2) 
	vdsat=2*Rs*Io_min

	Rd=max(4*Rs/(f-1-gamma),2*gain*Rs)
	Io=Io_min
	W=2*Io*L/(mew_n*Cox*(vdsat**2))                         # Got the Value of W
	Rb=(Vdd-vosw)/Io-2*Rs-Rd                                # Got the value for Rb and with this we know Rb,Rd,W,L,Io
	

	if Rb<0:
		Rb=50	

	F_sim=1+gamma+4*Rs/Rd+Rs/Rb
	#C1=threshold1/(2*np.pi*fo*2*Rs)
	f_lower=optimization_input_parameters['output_conditions']['f_lower']
	C1=1/(2*np.pi*f_lower*2*Rs)
	C2=threshold1*2*W*L*Cox/3   
	Rbias= max(threshold2/(2*np.pi*Rs*fo),1000)     

	# Forming a dictionry for Circuit parameters 
	circuit_parameters={}
	circuit_parameters['flo']=fo
	circuit_parameters['f_lower']=f_lower
	circuit_parameters['f_upper']=optimization_input_parameters['output_conditions']['f_upper']
	circuit_parameters['Ibias1']=Io
	circuit_parameters['len1']=L
	circuit_parameters['W1']=W
	circuit_parameters['Rb']=Rb
	circuit_parameters['Rd1']=Rd
	circuit_parameters['Rbias1']=Rbias
	circuit_parameters['C1']=C1
	circuit_parameters['C2']=C2
	circuit_parameters['Temp']=optimization_input_parameters['manual_circuit_parameters']['Temp']
	#circuit_parameters['pin']=optimization_input_parameters['simulation_conditions']['pin_iip3']

	# Calculating dc outputs
	#dc_outputs=calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions)
	dc_outputs={}
	# Running spectre and extracting the values
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)


	return circuit_parameters,dc_outputs,extracted_parameters




def calculate_initial_parameters_mixer(mos_parameters,optimization_input_parameters):	

	ampl_threshold=optimization_input_parameters['pre_optimization']['ampl_threshold']
	sat_threshold=optimization_input_parameters['pre_optimization']['sat_threshold']
	dvt=optimization_input_parameters['pre_optimization']['body_threshold']
	C_threshold=optimization_input_parameters['pre_optimization']['C_threshold']
	Rbias_threshold=optimization_input_parameters['pre_optimization']['Rbias_threshold']
	opt_conditions=optimization_input_parameters['output_conditions']
	inter_conditions=optimization_input_parameters['intermediate_specs']


	lna_gain=1
	nf_db	=10*np.log10((10**(inter_conditions['mixer_nf_db']/10)-1)*lna_gain**2+1)-5
	gain_db	=inter_conditions['mixer_conv_gain_db']
	bb_BW	=opt_conditions['bb_BW']

	flo	=opt_conditions['flo']
	frf	=opt_conditions['frf']

	L	=optimization_input_parameters['Lmin']
	Vdd	=optimization_input_parameters['Vdd']
	mew_n	=mos_parameters['un']
	Cox	=mos_parameters['cox']
	Vgs_req =optimization_input_parameters['Vgs_req']
	Vth0    =mos_parameters['vt']
	
	Rs=50/4
	gamma=2/3
	
	f=cf.db_to_normal(nf_db)
	gain=cf.db_to_normal(gain_db/2)
	
	Vgs1=Vgs_req
	Io=0.5*(Vgs1-Vth0)*((np.pi**2)/(4*Rs*(f-1)))*(gamma+4/(np.pi*gain))
	gm=((np.pi**2)/(4*Rs*(f-1)))*(gamma+4/(np.pi*gain))
	Rd=(np.pi/2)*(gain/gm)
	W1=2*Io*L/(mew_n*Cox*(Vgs1-Vth0)**2)

	Vth3=Vth0+dvt
	Vgs3=(np.sqrt(2)/(ampl_threshold+np.sqrt(2)))*(Vdd-(Vgs1-Vth0)*(1+np.pi*gain/4))+Vth3-sat_threshold
	W2=2*Io*L/(mew_n*Cox*(max(Vgs3-Vth3,150e-3))**2)	
	Vcm_lo=max(Vgs1-Vth0+Vgs3,Vgs1+sat_threshold)
	Alo=abs((Vgs3-Vth3)*ampl_threshold/np.sqrt(2))	

	C1=C_threshold*W1*L*Cox*2/3
	C2=C_threshold*W2*L*Cox*2/3

	Rbias1=Rbias_threshold/(2*np.pi*frf*C1)
	Rbias2=Rbias_threshold*Vdd/(2*np.pi*frf*C2*Vcm_lo)

	Rbias3=Vcm_lo*Rbias2/(Vdd-Vcm_lo)
	Cload=1/(2*np.pi*(frf-flo)*Rd)

	# Forming a dictionry for Circuit parameters 
	circuit_parameters={}
	circuit_parameters['Rd2']=Rd
	circuit_parameters['Ibias2']=Io
	circuit_parameters['len2']=L
	circuit_parameters['W2']=W1
	circuit_parameters['W3']=W2
	circuit_parameters['Rbias2']=Rbias1
	circuit_parameters['Rbias3']=Rbias2
	circuit_parameters['Rbias4']=Rbias3
	circuit_parameters['C3']=C1
	circuit_parameters['C4']=C2
	circuit_parameters['Cload']=Cload
	circuit_parameters['Alo']=Alo
	circuit_parameters['flo']=flo
	circuit_parameters['frf']=frf
	circuit_parameters['mismatch']=0
	circuit_parameters['Temp']=optimization_input_parameters['manual_circuit_parameters']['Temp']
	#circuit_parameters['pin']=optimization_input_parameters['simulation_conditions']['pin_iip3']

	# Calculating dc outputs
	#dc_outputs=calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions,optimization_input_parameters)
	dc_outputs={}	

	# Running spectre and extracting the values
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)


	return circuit_parameters,dc_outputs,extracted_parameters
	

def update_initial_parameters(circuit_parameters,mos_parameters,extracted_parameters,optimization_input_parameters):

	ampl_threshold=optimization_input_parameters['pre_optimization']['ampl_threshold']
	sat_threshold=optimization_input_parameters['pre_optimization']['sat_threshold']
	dvt=optimization_input_parameters['pre_optimization']['body_threshold']
	C_threshold=optimization_input_parameters['pre_optimization']['C_threshold']
	Rbias_threshold=optimization_input_parameters['pre_optimization']['Rbias_threshold']
	opt_conditions=optimization_input_parameters['output_conditions']
	
	# Assigning the values
	cgs1=extracted_parameters['cgs1']
	cgd1=extracted_parameters['cgd1']
	
	cgs2=extracted_parameters['cgs2']
	cgd2=extracted_parameters['cgd2']
	mos_parameters['vt']=extracted_parameters['vt']


	lna_gain=optimization_input_parameters['lna_gain']
	nf_db	=10*np.log10((10**(opt_conditions['nf_db']/10)-1)*lna_gain**2+1)-5
	gain_db	=opt_conditions['conv_gain_db']
	flo	=opt_conditions['flo']
	frf	=opt_conditions['frf']
	L	=optimization_input_parameters['Lmin']
	Vdd	=optimization_input_parameters['Vdd']
	mew_n	=mos_parameters['un']
	Cox	=mos_parameters['cox']
	Vgs_req =optimization_input_parameters['Vgs_req']
	Vth0    =mos_parameters['vt']
	Vth3	=extracted_parameters['vt2']
	gamma=2/3
	
	Rs=50/4
	f=cf.db_to_normal(nf_db)
	gain=cf.db_to_normal(gain_db/2)
	

	Vgs1=Vgs_req+160e-3
	gm=extracted_parameters['gm1']
	
	crct_fctr=1.5
	Io=0.5*(Vgs1-Vth0)*gm*crct_fctr
	Rd=min((2*np.pi/2)*(gain/(gm*crct_fctr)),2*Vdd/(3*Io))
	W1=2*Io*L/(mew_n*Cox*(Vgs1-Vth0)**2)*crct_fctr  

	#Vgs3=(np.sqrt(2)/(ampl_threshold+np.sqrt(2)))*(Vdd-(Vgs1-Vth0)*(1+np.pi*gain/4))+Vth3-sat_threshold
	Vgs3=max(extracted_parameters['Vcmlo']-extracted_parameters['vd1'],Vth3+150e-3)
	print(Vgs3)
	W2=2*Io*L/(mew_n*Cox*(Vgs3-Vth3)**2)	
	#Vcm_lo=max(Vgs1-Vth0+Vgs3+sat_threshold,Vgs1+sat_threshold)
	Vcm_lo=extracted_parameters['Vcmlo']
	Alo=abs((Vgs3-Vth3))*ampl_threshold/np.sqrt(2)	

	# Calculating C2
	C1=C_threshold*cgs1
	C2=C_threshold*cgs2
	
	# Calculating Rbias
	Rbias1=Rbias_threshold/(2*np.pi*frf*C1)
	Rbias2=Rbias_threshold*Vdd/(2*np.pi*frf*C2*Vcm_lo)
	Rbias3=Vcm_lo*Rbias2/(Vdd-Vcm_lo)
	Cload=1/(2*np.pi*(frf-flo)*Rd)

	# Forming a dictionry for Circuit parameters 
	circuit_parameters['Rd']=Rd
	circuit_parameters['Ibias']=Io
	circuit_parameters['W1']=W1
	circuit_parameters['W2']=W2
	circuit_parameters['Rbias1']=Rbias1
	circuit_parameters['Rbias2']=Rbias2
	circuit_parameters['Rbias3']=Rbias3
	circuit_parameters['C1']=C1
	circuit_parameters['C2']=C2
	circuit_parameters['Cload']=Cload
	circuit_parameters['Alo']=Alo
	
	
	# Calculating dc outputs
	dc_initial_outputs=calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions,optimization_input_parameters)	

	# Running spectre and extracting the values
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
	
	
	# Printing the values
	print("\n\n\t\t\tAfter Initial point Correction\n\n")
	cf.print_circuit_parameters(circuit_parameters)
	cf.print_DC_outputs(dc_initial_outputs,mos_parameters)
	cf.print_extracted_outputs(extracted_parameters)


	if extracted_parameters['region']==1:
		circuit_parameters,dc_initial_outputs,extracted_parameters= DC_linear_correct(circuit_parameters,mos_parameters,optimization_input_parameters,extracted_parameters)
		# Printing the values
		print("After Linear Correction")
		cf.print_circuit_parameters(circuit_parameters)
		cf.print_DC_outputs(dc_initial_outputs,mos_parameters)
		cf.print_extracted_outputs(extracted_parameters)

	

	if extracted_parameters['region']==3:
		circuit_parameters,dc_initial_outputs,extracted_parameters= DC_subthreshold_correct(circuit_parameters,mos_parameters,optimization_input_parameters,extracted_parameters)
		# Printing the values
		print("After Subthreshold Correction")
		cf.print_circuit_parameters(circuit_parameters)
		cf.print_DC_outputs(dc_initial_outputs,mos_parameters)
		cf.print_extracted_outputs(extracted_parameters)

	if extracted_parameters['region']==2:
		count=0
		while count>=0:
			gm=extracted_parameters['gm1']
			circuit_parameters['Ibias']=1.05*circuit_parameters['Ibias']
			circuit_parameters['W1']=1.1*circuit_parameters['W1']
			circuit_parameters['Rd']=min((2*np.pi/2)*(gain/gm),2*Vdd/(3*circuit_parameters['Ibias']))
			extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)

			print("After Sat Count = ",count)
			cf.print_circuit_parameters(circuit_parameters)
			cf.print_DC_outputs(dc_initial_outputs,mos_parameters)
			cf.print_extracted_outputs(extracted_parameters)

			count=count-1
	return circuit_parameters,dc_initial_outputs,mos_parameters,extracted_parameters


def automatic_initial_parameters(mos_parameters,optimization_input_parameters,optimization_results):

	#======================================================== Step 1 =============================================================================================================

	print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Automatic Operating Point Selection 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
	print("Test1\n\n\n\n")
	print('\n\n--------------------------------- Operating Point Calculations ------------------------------------')
	print("Test1\n\n\n\n")
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#--------------------Initial Point Calculations-------------------------
	print("Test1\n\n\n\n")
	# Calculating the Values of Circuit Parameters
	circuit_parameters,dc_initial_outputs,extracted_parameters=calculate_initial_parameters(mos_parameters,optimization_input_parameters)
	print("Test1\n\n\n\n")
	cf.print_DC_outputs(dc_initial_outputs,mos_parameters)
	
	# Storing the Circuit and Extracted Parameters
	optimization_results['auto_hc']={}
	optimization_results['auto_hc']['circuit_parameters']=circuit_parameters.copy()
	optimization_results['auto_hc']['extracted_parameters']=extracted_parameters.copy()

	# Printing the values
	cf.print_circuit_parameters(circuit_parameters)
	cf.print_DC_outputs(dc_initial_outputs,mos_parameters)
	cf.print_extracted_outputs(extracted_parameters)

	#cf.wait_key()
	

	#======================================================== Step 1 b ============================================================================================================
	
	print('\n\n--------------------------------- Operating Point Updations ------------------------------------')


	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#--------------------Initial Point Updating-----------------------------

	# Calculating the Values of Circuit Parameters
	circuit_parameters,dc_initial_outputs,mos_parameters,extracted_parameters=update_initial_parameters(circuit_parameters,
	mos_parameters,extracted_parameters,optimization_input_parameters)

	# Storing the Circuit and Extracted Parameters
	optimization_results['hc_update']={}
	optimization_results['hc_update']['circuit_parameters']=circuit_parameters.copy()
	optimization_results['hc_update']['extracted_parameters']=extracted_parameters.copy()

	return circuit_parameters,extracted_parameters

#===========================================================================================================================




	



