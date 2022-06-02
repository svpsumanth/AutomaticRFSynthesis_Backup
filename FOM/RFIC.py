import os
import RFIC_Write as write
import RFIC_Hand_calculations as hc
import RFIC_Param_Extraction as pe
import RFIC_optimize as optimize
import pylab as py
import time
import numpy as np
import csv
import pandas

start=time.time()

#----------------------Recquired File Names-----------------------------#


lib_name='/home/ee18b064/Eldo_files/Models_UMC180/ibm013.lib'
file_dir='/home/ee18b064/Optimization/FOM/'
recquirements_name=file_dir+'RFIC_req.txt'
save_data_path=file_dir+'data.csv'

cir_filename="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics/default/CGA_CurrentMirror_1_With_parasitics_default_default.cir"
chi_filename="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics/default/CGA_CurrentMirror_1_With_parasitics_default_default.chi"

#cir_filename="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics-parallel/default/CGA_CurrentMirror_1_With_parasitics-parallel_default_default.cir"
#chi_filename="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics-parallel/default/CGA_CurrentMirror_1_With_parasitics-parallel_default_default.chi"


#---------------------Defining Some constants---------------------------#

L_min=130*1e-9
Vdd=1.3
recquirements_dict={'gain_dB':0,'s11_dB_max':0,'iip3_dBm_min':0,'NF_max_dB':0,'f':0,'Rs':0}
mos_file_parameters = {'mew_n':0,'Cox':0,'Vth':0,'L_min':L_min,'Vdd':Vdd}

#--------------------Extracting Parmaeters of MOSFET,Recquirements----------------#

mos_param_dict=pe.extract_mosfet_param(lib_name,'NMOS',mos_file_parameters)
recquirements_dict=pe.extract_sys_req(recquirements_name,recquirements_dict)
recquirements_dict['k']=1   # Let us define k=1+gds*Rd
recquirements_dict['gamma']=2/3  # Noise multiplication factor for the mosfet

#--------------------------------------Hand Calculations-----------------------------


hand_out_dict=hc.circuit_parameters(mos_param_dict,recquirements_dict)
DC_status=hc.Sat_Vol_check(hand_out_dict)
print('******************************Hand Calculated Values*****************************************')
write.print_dict(hand_out_dict)


#----------------------------------------Node Voltages check------------------


if DC_status==False:
	print("****************After Hand Claculations are corrected For DC Voltages*****************************************")
	hand_out_dict=hc.DC_correct(hand_out_dict)
	

#----------------Running the 1st Iteration with hand calculated value-----------------------


print('**********************************Running the first Iteration*********************************************************')

output_dict,extract_param=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)


#----------------Updating recquired input parametres from simulation after one Iteration-------


hand_out_dict['Vth']=extract_param['Vth']
hand_out_dict['C2']=100*abs(extract_param['csg1'])

#-----------------Simulating with these new values-------------------------------

 
output_dict,extract_param=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
DC_status=hc.Sat_Vol_check(hand_out_dict)
write.print_dict(hand_out_dict)
print('\nDC_check=',DC_status)
if DC_status==False:
	hand_out_dict=hc.DC_correct(hand_out_dict)
	output_dict,extract_param=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	print('*******************************After Correcting Hand Calculations of 1st Iteration for DC Voltages****************************')
	write.print_dict(extract_param)
	DC_status=hc.Sat_Vol_check(hand_out_dict)

if hc.Sat_Vol_check(hand_out_dict)== True :
	print("\n\nFirst Iteration Hand Calculated DC points are now okay")


'''
#---------------------------------correcting the gm----------------------------------------------
if DC_status==True:
	hand_out_dict,extract_param=hc.gm_correction(hand_out_dict,extract_param,cir_filename,chi_filename)

'''

#----------------------------------Opening the csv File for saving the data ----------------------
save_file=open(save_data_path,'w')
writer=csv.writer(save_file)
header=['n','Io','W','Rb','Rd','fo','Vg','Vs','Vd','Vth','iip3','gain','s11','nf','FOM','PWR','gm']
writer.writerow(header)




'''hand_out_dict_new=hc.circuit_parameters_new(mos_param_dict,recquirements_dict)
hand_out_dict['Io']=hand_out_dict_new['Io']
hand_out_dict['W']=hand_out_dict_new['W']
hand_out_dict['Rb']=hand_out_dict_new['Rb']
hand_out_dict['Rd']=hand_out_dict_new['Rd']
hand_out_dict['fo']=hand_out_dict_new['fo']
hand_out_dict['C1']=hand_out_dict_new['C1']
hand_out_dict['C2']=100*abs(extract_param['csg1'])
initial_cond=hand_out_dict.copy()
output_dict,extract_param=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)'''


#-------------------Optimisation-------------------------------


CF_count_list=[]	# These are the lists that store the values like CF,iip3,gain,S11,Io 
CF_wo_s11_list=[]
gain_list=[]
s11_list=[]
iip3_list=[]
NF_list=[]
Io_list=[]
W_list=[]
Rb_list=[]
Rd_list=[]
avg_Io=[]		# Running Average of the Current
avg_Io_slope=[]
stop_cond=1
output_dict=pe.Output_dict(extract_param)
sol=[]
#CF,CF_wo_s11=optimize.cost_function(recquirements_dict,output_dict,hand_out_dict)
#print('Cost function=',CF)
count=1
flag2=0
lf=2e-2 		# Common Learning Factor 



recquirements_dict['f']=1e9
for j in range(1):

	hand_out_dict_new=hc.circuit_parameters_new(mos_param_dict,recquirements_dict)
	hand_out_dict['Io']=hand_out_dict_new['Io']
	hand_out_dict['W']=hand_out_dict_new['W']
	hand_out_dict['Rb']=hand_out_dict_new['Rb']
	hand_out_dict['Rd']=hand_out_dict_new['Rd']
	hand_out_dict['fo']=hand_out_dict_new['fo']
	hand_out_dict['C1']=hand_out_dict_new['C1']
	hand_out_dict['C2']=100*abs(extract_param['csg1'])
	#initial_cond=hand_out_dict.copy()
	output_dict,extract_param=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
	write.print_dict(hand_out_dict)

	CF,CF_wo_s11=optimize.cost_function(recquirements_dict,output_dict,hand_out_dict)
	print('Cost function=',CF)
	
	write.print_dict(hand_out_dict)

	for i in range(500):
		CF_prev=CF
		CF_wo_prev=CF_wo_s11
		output_prev=output_dict.copy()
		hand_out_prev=hand_out_dict.copy()
		extract_prev=extract_param.copy()
		coeff_grad,coeff_lf=optimize.Gradient(CF,CF_wo_s11,hand_out_dict,recquirements_dict,extract_param,cir_filename,chi_filename)
		#print(hand_out_dict)
		'''out_change1=coeff_lf['Io']*lf 	#24e-9
		out_change2=coeff_lf['W']*lf	#20e-9
		out_change3=coeff_lf['Rb']*lf	#10e3
		out_change4=coeff_lf['Rd']*lf	#10e3'''

		out_change1=lf 	
		out_change2=lf	
		out_change3=lf	
		out_change4=lf
		out_change5=0.05*lf*0

		#print(count%2)

		'''if count%150==0:
			hand_out_dict['fo']=hand_out_dict['fo']+1e9'''

		ceil=0.5
		
		if abs(out_change1*hand_out_dict['Io']**2*coeff_grad['Io']) <= ceil*hand_out_dict['Io']:
			hand_out_dict['Io']=hand_out_dict['Io']-out_change1*hand_out_dict['Io']**2*coeff_grad['Io']		# Updating the Inputs
		else:
			hand_out_dict['Io']=hand_out_dict['Io']-ceil*hand_out_dict['Io']*abs(coeff_grad['Io'])/(coeff_grad['Io'])

		if abs(out_change2*hand_out_dict['W']**2*coeff_grad['W']) <= ceil*hand_out_dict['W']:
			hand_out_dict['W']=hand_out_dict['W']-out_change2*hand_out_dict['W']**2*coeff_grad['W']
		else:
			hand_out_dict['W']=hand_out_dict['W']-ceil*hand_out_dict['W']*abs(coeff_grad['W'])/(coeff_grad['W'])

		if abs(out_change3*hand_out_dict['Rb']**2*coeff_grad['Rb']) <= ceil*hand_out_dict['Rb']:
			hand_out_dict['Rb']=hand_out_dict['Rb']-out_change3*hand_out_dict['Rb']**2*coeff_grad['Rb']
		else:
			hand_out_dict['Rb']=hand_out_dict['Rb']-ceil*hand_out_dict['Rb']*abs(coeff_grad['Rb'])/(coeff_grad['Rb'])

		if abs(out_change4*hand_out_dict['Rd']**2*coeff_grad['Rd']) <= ceil*hand_out_dict['Rd']:
			hand_out_dict['Rd']=hand_out_dict['Rd']-out_change4*hand_out_dict['Rd']**2*coeff_grad['Rd']
		else:
			hand_out_dict['Rd']=hand_out_dict['Rd']-ceil*hand_out_dict['Rd']*abs(coeff_grad['Rd'])/(coeff_grad['Rd'])

		if abs(out_change5*hand_out_dict['fo']**2*coeff_grad['fo']) <= ceil*hand_out_dict['fo']:
			hand_out_dict['fo']=hand_out_dict['fo']-out_change5*hand_out_dict['fo']**2*coeff_grad['fo']
		else:
			hand_out_dict['fo']=hand_out_dict['fo']-ceil*hand_out_dict['fo']*abs(coeff_grad['fo'])/(coeff_grad['fo'])


		output_dict,extract_param=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
		CF,CF_wo_s11=optimize.cost_function(recquirements_dict,output_dict,hand_out_dict)
		CF_current=CF
		
		if CF>CF_prev:			#if CF increases consecutively then flag2 rises
			flag2=flag2+1		
		else :
			flag2=0
		if flag2>=50:			#if CF increases consecutively 5 times then Iterations stop 
			break
		
		print('****************************************Extracted Values from simulation (Iteration ',count,')*********************')
		print('Cost function=',CF,', Cost function wo s11=',CF_wo_s11,', Vgs-Vth=',extract_param['Vg']-extract_param['Vs']-extract_param['Vth'])
		write.print_dict(extract_param)
		print("****************************************Circuit Parameters (Iteration ",count,")***************************")
		print('Io=',hc.to_units(hand_out_dict['Io']))
		print('W=',hc.to_units(hand_out_dict['W']))
		print('Rd=',hc.to_units(hand_out_dict['Rd']))
		print('Rb=',hc.to_units(hand_out_dict['Rb']))
		print('fo=',hc.to_units(hand_out_dict['fo']),'\n')
		print('lf=',lf)
		print('coefficients : ',coeff_lf)

		if output_dict['s11_dB']<(20):
			if len(sol)==0:
				sol.append(np.array([CF_wo_s11,count,hand_out_dict.copy()]))
			else:
				if(sol[0][0]>CF_wo_s11):
					sol[0]=np.array([CF_wo_s11,count,hand_out_dict.copy()])

		'''if CF_wo_s11<=0.0003:					
			if len(sol)==0:
				sol.append(hand_out_dict.copy())
			else:
				if(sol[0]['Io']>hand_out_dict['Io']):
					sol[0]=hand_out_dict.copy()'''
		
		CF_count_list.append(CF)				# Updating the Lists with corresponding values
		CF_wo_s11_list.append(CF_wo_s11)	
		gain_list.append(output_dict['gain_dB'])
		iip3_list.append(output_dict['iip3_dBm'])
		s11_list.append(output_dict['s11_dB'])
		NF_list.append(output_dict['NF_dB'])
		Io_list.append(hand_out_dict['Io']*1e6)
		W_list.append(hand_out_dict['W'])
		Rb_list.append(hand_out_dict['Rb'])
		Rd_list.append(hand_out_dict['Rd'])
		
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

		if abs(stop_cond)<0.1:					# If Avg Slope of Io is less than 1uA/Iteration it will break
			print("Stop Reached")		
			#break
		if output_dict['s11_dB']<(20):
			writer.writerow([count,hand_out_dict['Io'],hand_out_dict['W'],hand_out_dict['Rb'],hand_out_dict['Rd'],hand_out_dict['fo'],extract_param['Vg'],extract_param['Vs'],extract_param['Vd'],extract_param['Vth'],output_dict['iip3_dBm'],output_dict['gain_dB'],output_dict['s11_dB'],output_dict['NF_dB'],-1*(CF_wo_s11),output_dict['pwr_dc'],output_dict['gm1']])
		count=count+1
	#initial_cond['fo']=hand_out_dict['fo']
	#hand_out_dict=initial_cond.copy()
	#hand_out_dict['fo']=hand_out_dict['fo']+1e9
	recquirements_dict['f']=recquirements_dict['f']+1e9

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
fig8=py.plot(avg_Io_slope)
py.savefig("Current_avg_slope.png")
py.clf()
fig9=py.plot(CF_wo_s11_list)
py.savefig("CF_wo_s11.png")
py.clf()
fig9=py.plot(W_list)
py.savefig("W.png")
py.clf()
fig9=py.plot(Rb_list)
py.savefig("Rb.png")
py.clf()
fig9=py.plot(Rd_list)
py.savefig("Rd.png")


#output_dict,extract_param=write.Run_simulation(sol[0],cir_filename,chi_filename)


#---Best Optimized solution---
print('\n',sol[0][:2])
write.print_dict(sol[0][2])
output_dict,extract_param=write.Run_simulation(sol[0][2],cir_filename,chi_filename)
write.print_dict(extract_param)
end=time.time()

print("\n Running Time of the Program : ",end-start,' Sec\n')

