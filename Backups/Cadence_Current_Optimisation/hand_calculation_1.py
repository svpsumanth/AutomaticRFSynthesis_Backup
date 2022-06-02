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
def calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions):
	vs=circuit_parameters['Io']*circuit_parameters['Rb']
	vgs=mos_parameters['vt']+ 2*opt_conditions['Rs']*circuit_parameters['Io']
	vg=vgs+vs
	vd=mos_parameters['vdd']-circuit_parameters['Io']*circuit_parameters['Rd']
	
	dc_outputs={'vg':vg,'vd':vd,'vs':vs}
	
	return dc_outputs
	

def Sat_Vol_check(circuit_parameters,mos_parameters,optimization_input_parameters):		# Checking the Voltage levels
	Io=circuit_parameters['Io']
	Rs=optimization_input_parameters['output_conditions']['Rs']
	Rd=circuit_parameters['Rd']
	Rb=circuit_parameters['Rb']
	Vth=mos_parameters['vt']
	Vdd=optimization_input_parameters['Vdd']
	# We need to check the node voltages in the system we will check Vd,Vs,Vg of M1
	DC_status=False
	Vdsat=2*Io*Rs
	Vd=Vdd-Io*Rd
	Vs=Io*Rb
	Vg=Io*Rb+Vdsat+Vth
	if (Vd<Vdd and Vg<Vdd and Vs<Vdd):
	    if Vd>Vg-Vth:
	            DC_status=True
	    else:
	            DC_status=False

	return DC_status


def DC_correct(circuit_parameters,mos_parameters,optimization_input_parameters):		# Correcting the Bias Values
	DC_status=Sat_Vol_check(circuit_parameters,mos_parameters,optimization_input_parameters)

	opt_conditions=optimization_input_parameters['output_conditions']
	gain_db	=opt_conditions['gain_db']
	Rs=opt_conditions['Rs']
	iip3_dbm=opt_conditions['iip3_dbm']
	Vdd=optimization_input_parameters['Vdd']
	L=optimization_input_parameters['Lmin']
	mew_n=mos_parameters['un']
	Cox=mos_parameters['cox']
	Io=circuit_parameters['Io']
	W =circuit_parameters['W']
	Rd=circuit_parameters['Rd']

	gain=cf.db_to_normal(gain_db/2)
	p1dbm=iip3_dbm-9.6
	pin=(1e-3)*10**(p1dbm/10)
	vosw=gain*np.sqrt(8*Rs*pin)+optimization_input_parameters['pre_optimization']['vosw_threshold']


	while DC_status==False:
		circuit_parameters['Io']=1.01*circuit_parameters['Io']
		circuit_parameters['W']=2*circuit_parameters['Io']*L/(mew_n*Cox*((2*circuit_parameters['Io']*Rs)**2))
		circuit_parameters['Rb']=(Vdd-vosw)/circuit_parameters['Io']-2*Rs-Rd
		if circuit_parameters['Rb']<50:
			circuit_parameters['Rb']=50
		DC_status=Sat_Vol_check(circuit_parameters,mos_parameters,optimization_input_parameters)

	# Calculating dc outputs
	dc_outputs=calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions)
	
	# Running Eldo
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)

	return circuit_parameters,dc_outputs,extracted_parameters




def calculate_initial_parameters(mos_parameters,optimization_input_parameters):
	
	threshold1=optimization_input_parameters['pre_optimization']['C1_threshold']
	threshold2=optimization_input_parameters['pre_optimization']['C2_threshold']
	threshold3=optimization_input_parameters['pre_optimization']['Rbias_threshold']
	opt_conditions=optimization_input_parameters['output_conditions']

	nf_db	=opt_conditions['nf_db']
	gain_db	=opt_conditions['gain_db']
	Rs	=opt_conditions['Rs']
	iip3_dbm=opt_conditions['iip3_dbm']
	fo	=opt_conditions['wo']/(2*np.pi)
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
	C2=threshold2*2*W*L*Cox/3   
	Rbias= max(threshold3/(2*np.pi*Rs*fo),1000)     

	# Forming a dictionry for Circuit parameters 
	circuit_parameters={}
	circuit_parameters['fo']=fo
	circuit_parameters['f_lower']=f_lower
	circuit_parameters['f_upper']=2*fo
	circuit_parameters['Io']=Io
	circuit_parameters['W']=W
	circuit_parameters['Rb']=Rb
	circuit_parameters['Rd']=Rd
	circuit_parameters['Rbias']=Rbias
	circuit_parameters['C1']=C1
	circuit_parameters['C2']=C2
	circuit_parameters['Temp']=optimization_input_parameters['manual_circuit_parameters']['Temp']
	#circuit_parameters['pin']=optimization_input_parameters['simulation_conditions']['pin_iip3']

	# Calculating dc outputs
	dc_outputs=calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions)
	
	# Running spectre and extracting the values
	extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)


	return circuit_parameters,dc_outputs,extracted_parameters
	
	

def update_initial_parameters(circuit_parameters,mos_parameters,extracted_parameters,optimization_input_parameters):

	threshold2=optimization_input_parameters['pre_optimization']['C2_threshold']
	threshold3=optimization_input_parameters['pre_optimization']['Rbias_threshold']
	opt_conditions=optimization_input_parameters['output_conditions']
	# Assigning the values
	cgs=extracted_parameters['cgs1']
	cgd=extracted_parameters['cgd1']
	gain=circuit_parameters['Rd']/(2*opt_conditions['Rs'])
	wo=opt_conditions['wo']
	
	# Calculating C2
	C2a=threshold2*cgs
	C2b=threshold2*cgd*gain
	C2=np.maximum(C2a,C2b)
	
	# Calculating Rbias
	Rbias=max(threshold3/(wo*C2),1000)

	circuit_parameters['C2']=C2
	circuit_parameters['Rbias']= Rbias
	mos_parameters['vt']=extracted_parameters['vt']

	DC_status=Sat_Vol_check(circuit_parameters,mos_parameters,optimization_input_parameters)
	if DC_status==False:
		circuit_parameters,dc_initial_outputs,extracted_parameters= DC_correct(circuit_parameters,mos_parameters,optimization_input_parameters)

	# Calculating dc outputs
	dc_initial_outputs=calc_dc_opt(circuit_parameters,mos_parameters,opt_conditions)

	return circuit_parameters,dc_initial_outputs,mos_parameters,extracted_parameters



def dc_optimize_gm(mos_parameters,circuit_parameters,extracted_parameters,optimization_input_parameters):
	count=50
	flag=0
	
	opt_conditions=optimization_input_parameters['output_conditions']
	gain_db	=opt_conditions['gain_db']
	Rs=opt_conditions['Rs']
	iip3_dbm=opt_conditions['iip3_dbm']

	gain=cf.db_to_normal(gain_db/2)
	p1dbm=iip3_dbm-9.6
	pin=(1e-3)*10**(p1dbm/10)
	vosw=gain*np.sqrt(8*Rs*pin)+optimization_input_parameters['pre_optimization']['vosw_threshold']


	if abs(extracted_parameters['Io']-circuit_parameters['Io'])<0.2*circuit_parameters['Io']:
		print("DC current is ok")
		while extracted_parameters['gm1']<0.8*20e-3:
			gm_prev=extracted_parameters['gm1']
			if flag==0:
				circuit_parameters['Io']=1.1*circuit_parameters['Io']
				#circuit_parameters['W']=2*circuit_parameters['Io']*optimization_input_parameters['Lmin']/(mos_parameters['un']*mos_parameters['cox']*((2*circuit_parameters['Io']*optimization_input_parameters['output_conditions']['Rs'])**2))
			
				circuit_parameters['W']=2*circuit_parameters['Io']*optimization_input_parameters['Lmin']/(mos_parameters['un']*mos_parameters['cox']*extracted_parameters['vdsat']**2)
				circuit_parameters['Rb']=(optimization_input_parameters['Vdd']-vosw)/circuit_parameters['Io']-2*optimization_input_parameters['output_conditions']['Rs']-circuit_parameters['Rd']
				if circuit_parameters['Rb']<50:
					circuit_parameters['Rb']=50
					
			extracted_parameters=sp.write_extract(circuit_parameters,optimization_input_parameters)
			gm_current=extracted_parameters['gm1']

			print('\n\ngm=',gm_current,'Io=',extracted_parameters['Io'],'W=',circuit_parameters['W'],circuit_parameters['Rb'],'\n\n')
			count=count-1
			print(count,Sat_Vol_check(circuit_parameters,mos_parameters,optimization_input_parameters))
			if count==0:
				break
		print('gm=',cf.num_trunc(extracted_parameters['gm1'],3),'Io=',cf.num_trunc(extracted_parameters['Io'],3),'W=',cf.num_trunc(circuit_parameters['W'],3))


		return circuit_parameters , extracted_parameters




def automatic_initial_parameters(mos_parameters,optimization_input_parameters,optimization_results):

	#======================================================== Step 1 =============================================================================================================

	print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Automatic Operating Point Selection 1 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

	print('\n\n--------------------------------- Operating Point Calculations ------------------------------------')

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#--------------------Initial Point Calculations-------------------------

	# Calculating the Values of Circuit Parameters
	circuit_parameters,dc_initial_outputs,extracted_parameters=calculate_initial_parameters(mos_parameters,optimization_input_parameters)

	# Check whether all node voltages are in limit
	DC_status=Sat_Vol_check(circuit_parameters,mos_parameters,optimization_input_parameters)
	
	if DC_status == False :
		circuit_parameters,dc_initial_outputs,extracted_parameters= DC_correct(circuit_parameters,mos_parameters,optimization_input_parameters)

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

	# Printing the values
	cf.print_circuit_parameters(circuit_parameters)
	cf.print_DC_outputs(dc_initial_outputs,mos_parameters)
	cf.print_extracted_outputs(extracted_parameters)

	#cf.wait_key()

	#======================================================== Step 2 =============================================================================================================

	print('\n\n--------------------------------- gm Updation ------------------------------------')
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	#--------------------gm updating------------------------------
	circuit_parameters,extracted_parameters=dc_optimize_gm(mos_parameters,circuit_parameters,extracted_parameters,optimization_input_parameters)

	# Storing the Circuit and Extracted Parameters
	optimization_results['gm_update']={}
	optimization_results['gm_update']['circuit_parameters']=circuit_parameters.copy()
	optimization_results['gm_update']['extracted_parameters']=extracted_parameters.copy()

	# Printing the values
	cf.print_circuit_parameters(circuit_parameters)
	cf.print_extracted_outputs(extracted_parameters)

	#cf.wait_key()

	return circuit_parameters,extracted_parameters

#===========================================================================================================================




	



