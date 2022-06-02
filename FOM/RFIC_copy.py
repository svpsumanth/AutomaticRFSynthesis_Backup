import numpy as np
import os
import RFIC_Write as write
import RFIC_Hand_calculations as hc
import RFIC_Param_Extraction as pe
import RFIC_optimize as optimize
import pylab as py

#----------------------Recquired File Names-----------------------------#


lib_name='/home/ee18b064/Eldo_files/Models_UMC180/tsmc018.lib'
input_name='/home/ee18b064/Transfer_files/RFIC_req.txt'
cir_filename="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics/default/CGA_CurrentMirror_1_With_parasitics_default_default.cir"
chi_filename="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics/default/CGA_CurrentMirror_1_With_parasitics_default_default.chi"


#---------------------Defining Some constants---------------------------#


L_min=180*1e-9
Vdd=1.8
sys_req_dict={'gain_dB':0,'s11_dB_max':0,'iip3_dBm_min':0,'NF_max_dB':0,'f':0,'Rs':0}
mos_file_parameters = {'mew_n':0,'Cox':0,'Vth':0,'L_min':L_min,'Vdd':Vdd}



#--------------------Extracting Parmaeters of MOSFET,Recquirements----------------#


mos_param_dict=pe.extract_mosfet_param(lib_name,'NMOS',mos_file_parameters)

sys_req_dict=pe.extract_sys_req(input_name,sys_req_dict)
sys_req_dict['k']=1.5   # Let us define k=1+gds*Rd
sys_req_dict['gamma']=2/3  # Noise multiplication factor for the mosfet


#--------------------------------------Hand Calculations-----------------------------


hand_out_dict=hc.circuit_parameters(mos_param_dict,sys_req_dict)
DC_status=hc.Sat_Vol_check(hand_out_dict)
print('******************************Hand Calculated Values*****************************************')
write.print_dict(hand_out_dict)


#----------------------------------------Node Voltages check------------------


if DC_status==False:
	print("****************After Hand Claculations are corrected For DC Voltages*****************************************")
	hand_out_dict=hc.DC_correct(hand_out_dict)
	

#----------------Running the 1st Iteration with hand calculated value-----------------------


print('**********************************Running the first Iteration*********************************************************')
write.call_write_param(hand_out_dict,cir_filename)
write.Run_Eldo()
extract_param=pe.extract_output_param(chi_filename)


#----------------Updating recquired input parametres from simulation after one Iteration-------


hand_out_dict['Vth']=extract_param['Vth']
hand_out_dict['C2']=100*abs(extract_param['csg1'])

#-----------------Simulating with these new values-------------------------------

 
write.call_write_param(hand_out_dict,cir_filename)
write.Run_Eldo()
extract_param=pe.extract_output_param(chi_filename)
DC_status=hc.Sat_Vol_check(hand_out_dict)
write.print_dict(hand_out_dict)
print('\nDC_check=',DC_status)
if DC_status==False:
	hand_out_dict=hc.DC_correct(hand_out_dict)
	write.call_write_param(hand_out_dict,cir_filename)
	write.Run_Eldo()
	extract_param=pe.extract_output_param(chi_filename)
	print('***********************************After Correcting Hand Calculations of 1st Iteration for DC Voltages********************************')
	write.print_dict(extract_param)
	DC_status=hc.Sat_Vol_check(hand_out_dict)

if hc.Sat_Vol_check(hand_out_dict)== True :
	print("\n\nFirst Iteration Hand Calculated DC points are now okay")


#---------------------------------correcting the gm----------------------------------------------

count=25
flag=0
if DC_status==True:				# gm correction block it will make sure that gm is 95% of 20mS
	if abs(extract_param['Io']-hand_out_dict['Io'])<0.2*hand_out_dict['Io']:
		print("DC current is ok")
		while extract_param['gm1']<0.95*20e-3:
			gm_prev=extract_param['gm1']
			if flag==0:
				hand_out_dict['Io']=1.05*hand_out_dict['Io']
				hand_out_dict['Rb']=(hand_out_dict['Vdd']-hand_out_dict['Vosw'])/hand_out_dict['Io']-2*hand_out_dict['Rs']-hand_out_dict['Rd']
			elif flag==1:
				hand_out_dict['W']=1.2*hand_out_dict['W']
			write.call_write_param(hand_out_dict,cir_filename)
			write.Run_Eldo()
			extract_param=pe.extract_output_param(chi_filename)
			gm_current=extract_param['gm1']
			if gm_current<gm_prev:
				if flag==0:
					hand_out_dict['Io']=hand_out_dict['Io']/1.05
				flag=flag+1

			if flag==2:
				print('flag')
				break
			print('gm=',gm_current,'Io=',extract_param['Io'],'W=',hand_out_dict['W'])
			count=count-1
			print(count,hc.Sat_Vol_check(hand_out_dict))
			if count==0:
				break
		#print('gm=',hc.to_units(extract_param['gm1']),'Io=',hc.to_units(extract_param['Io']),'W=',hc.to_units(hand_out_dict['W']))
		print('**********************************After Correcting the gm**************************************')
		write.print_dict(extract_param)



#-------------------Optimisation-------------------------------


CF_count_list=[]	# These are the lists that store the values like CF,iip3,gain,S11,Io 
gain_list=[]
s11_list=[]
iip3_list=[]
NF_list=[]
Io_list=[]
avg_Io=[]		# Running Average of the Current
avg_Io_slope=[]
stop_cond=1
output_dict=pe.Output_dict(extract_param)
sol=[]
CF,CF_wo_Io=optimize.cost_function(sys_req_dict,output_dict,hand_out_dict)
print('Cost function=',CF)
count=1
flag2=0
lf=40e-2 		# Common Learning Factor 

for i in range(250):
	CF_prev=CF
	CF_wo_prev=CF_wo_Io
	output_prev=output_dict.copy()
	hand_out_prev=hand_out_dict.copy()
	extract_prev=extract_param.copy()
	coeff_grad=optimize.Gradient(CF,CF_wo_prev,hand_out_dict,sys_req_dict,extract_param,cir_filename,chi_filename)
	#print(hand_out_dict)
	out_change1=0.25*lf 	#24e-9
	out_change2=2*lf	#20e-9
	out_change3=2*lf	#10e3
	out_change4=2.5*lf	#10e3

	if abs(out_change1*hand_out_dict['Io']**2*coeff_grad['Io']) <= 0.1*hand_out_dict['Io']:
		hand_out_dict['Io']=hand_out_dict['Io']-out_change1*hand_out_dict['Io']**2*coeff_grad['Io']		# Updating the Inputs
	else:
		hand_out_dict['Io']=hand_out_dict['Io']-0.1*hand_out_dict['Io']*abs(coeff_grad['Io'])/(coeff_grad['Io'])

	if abs(out_change2*hand_out_dict['W']**2*coeff_grad['W']) <= 0.1*hand_out_dict['W']:
		hand_out_dict['W']=hand_out_dict['W']-out_change2*hand_out_dict['W']**2*coeff_grad['W']
	else:
		hand_out_dict['W']=hand_out_dict['W']-0.1*hand_out_dict['W']*abs(coeff_grad['W'])/(coeff_grad['W'])

	if abs(out_change3*hand_out_dict['Rb']**2*coeff_grad['Rb']) <= 0.1*hand_out_dict['Rb']:
		hand_out_dict['Rb']=hand_out_dict['Rb']-out_change3*hand_out_dict['Rb']**2*coeff_grad['Rb']
	else:
		hand_out_dict['Rb']=hand_out_dict['Rb']-0.1*hand_out_dict['Rb']*abs(coeff_grad['Rb'])/(coeff_grad['Rb'])

	if abs(out_change4*hand_out_dict['Rd']**2*coeff_grad['Rd']) <= 0.1*hand_out_dict['Rd']:
		hand_out_dict['Rd']=hand_out_dict['Rd']-out_change4*hand_out_dict['Rd']**2*coeff_grad['Rd']
	else:
		hand_out_dict['Rd']=hand_out_dict['Rd']-0.1*hand_out_dict['Rd']*abs(coeff_grad['Rd'])/(coeff_grad['Rd'])


	

	output_dict,extract_param=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	CF,CF_wo_Io=optimize.cost_function(sys_req_dict,output_dict,hand_out_dict)
	CF_current=CF
	
	if CF>CF_prev:			#if CF increases consecutively then flag2 rises
		flag2=flag2+1		
	else :
		flag2=0
	if flag2>=5:			#if CF increases consecutively 5 times then Iterations stop 
		break
	
	print('****************************************Extracted Values from simulation (Iteration ',count,')*********************')
	print('Cost function=',CF,', Cost function wo Io=',CF_wo_Io,', Vgs-Vth=',extract_param['Vg']-extract_param['Vs']-extract_param['Vth'])
	write.print_dict(extract_param)
	print("****************************************Circuit Parameters (Iteration ",count,")***************************")
	print('Io=',hc.to_units(hand_out_dict['Io']))
	print('W=',hc.to_units(hand_out_dict['W']))
	print('Rd=',hc.to_units(hand_out_dict['Rd']))
	print('Rb=',hc.to_units(hand_out_dict['Rb']),'\n')
	print('lf=',lf)

	if CF_wo_Io<=0.0003:					# This if block finds the best Solution (i.e with CF<0.0003 and Minimum current)
		if len(sol)==0:
			sol.append(hand_out_dict.copy())
		else:
			if(sol[0]['Io']>hand_out_dict['Io']):
				sol[0]=hand_out_dict.copy()
	
	CF_count_list.append(CF)				# Updating the Lists with corresponding values
	gain_list.append(output_dict['gain_dB'])
	iip3_list.append(output_dict['iip3_dBm'])
	s11_list.append(output_dict['s11_dB'])
	NF_list.append(output_dict['NF_dB'])
	Io_list.append(hand_out_dict['Io']*1e6)
	
	if len(Io_list)==1:					# Initialising the Avg_Io
		avg_Io.append(hand_out_dict['Io']*1e6)
		avg_Io.append(hand_out_dict['Io']*1e6)
		avg_Io.append(hand_out_dict['Io']*1e6)


	if len(Io_list)>=4:					# Updating the Running Avg of Io
		avg_Io.append(sum(Io_list[-4:])/4)
		
	if len(avg_Io)>=2:					# Calculating the slope of Avg_Io
		avg_Io_slope.append(avg_Io[-1]-avg_Io[-2])

	if len(avg_Io_slope)>=5:				# Stopping Condition (Finding the Average slope for the last 6 Iterations)
		stop_cond=sum(avg_Io_slope[-6:])/6

	if abs(stop_cond)<1:					# If Avg Slope of Io is less than 1uA/Iteration it will break
		break
	
	#lf=lf/1.02	
	count=count+1

#-----------------------Saving all the Figures----------------

fig1=py.plot(CF_count_list)
#py.legend('CF')
py.savefig("CF.png")
py.clf()
fig2=py.plot(gain_list)
#py.legend('Gain in dB')
py.savefig("gain.png")
py.clf()
fig3=py.plot(iip3_list)
#py.legend('IIP3 in dBm')
py.savefig("iip3.png")
py.clf()
fig4=py.plot(s11_list)
#py.legend('s11 in dB')
py.savefig("s11.png")
py.clf()
fig5=py.plot(NF_list)
#py.legend('NF in dB')
py.savefig("NF.png")
py.clf()
fig6=py.plot(Io_list)
#py.legend('Current( in uA )')
py.savefig("Current.png")
fig7=py.plot(avg_Io)
py.savefig("Current_avg.png")
py.clf()
fig7=py.plot(avg_Io_slope)
py.savefig("Current_avg_slope.png")


#output_dict,extract_param=write.Run_simulation(sol[0],cir_filename,chi_filename)


#---Best Optimized solution---
write.print_dict(sol[0])
output_dict,extract_param=write.Run_simulation(sol[0],cir_filename,chi_filename)
write.print_dict(extract_param)

