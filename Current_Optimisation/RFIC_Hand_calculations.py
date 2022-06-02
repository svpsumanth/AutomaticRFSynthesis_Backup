import numpy as np
import RFIC_Write as write
import RFIC_Hand_calculations as hc


def circuit_parameters(mos_param_dict,sys_req_dict):
    L=mos_param_dict['L_min']  # For RF Applications L is always choosen as minimum length possible
    gain=10**(sys_req_dict['gain_dB']/20)
    s11_max=10**(sys_req_dict['s11_dB_max']/10)
    F_max=10**(sys_req_dict['NF_max_dB']/10)
    Rs=sys_req_dict['Rs']
    iip3_dBm_min=sys_req_dict['iip3_dBm_min']
    f=sys_req_dict['f']
    k=sys_req_dict['k']
    gamma=sys_req_dict['gamma']
    mew_n=mos_param_dict['mew_n']
    Cox=mos_param_dict['Cox']
    Vdd=mos_param_dict['Vdd']
    Vth=mos_param_dict['Vth']
    
    #To get Rd we can use ideal gain expression
    Rd=max(4*Rs/(F_max-1-gamma),2*gain*Rs)
    P1dBm_min=iip3_dBm_min-9.6
    Pin=(1e-3)*10**(P1dBm_min/10)
    Vosw_min=gain*np.sqrt(8*Rs*Pin)
    Vosw=0.1+Vosw_min
    
    #From S11
    Zim_max=100*np.sqrt(s11_max/(1-s11_max)) 
    Io_min=(k**2)*np.pi*2*f*(L**2)/(3*mew_n*Zim_max) 
    #Yim_max=1=np.sqrt((1-s11_max)/s11_max)/(2*Rs)
    #Io_min=np.pi*2*f*(L**2)*Yim_max/(3*mew_n)        # Got the value for Io_min so we will start off with this thing
    Io=Io_min
    #Io=1e-3
    Vdsat=2*Rs*Io
    W=2*Io*L/(mew_n*Cox*(Vdsat**2))                         # Got the Value of W
    Rb=(Vdd-Vosw)/Io-2*Rs-Rd                                # Got the value for Rb and with this we know Rb,Rd,W,L,Io
    F_sim=1+gamma+4*Rs/Rd+Rs/Rb
    C1=100/(2*np.pi*f*2*Rs)
    #C2=100/(2*np.pi*f*(Rb+Rs))
    C2=200*W*L*Cox/3                                        #Valid only for one iteration and later we will chose this from opertating point

    return {'Io':Io,'W':W,'L':L,'Rd':Rd,'Rb':Rb,'fo':f,'C1':C1,'C2':C2,'Io_min':Io_min,'Vosw':Vosw,'Rs':Rs,'Vth':Vth,'Vdd':Vdd,'gamma':gamma,'mew_n':mew_n,'Cox':Cox}

def Sat_Vol_check(hand_out_dict):		# Checking the Voltage levels
    Io=hand_out_dict['Io']
    Rs=hand_out_dict['Rs']
    Rd=hand_out_dict['Rd']
    Rb=hand_out_dict['Rb']
    Vth=hand_out_dict['Vth']
    Vdd=hand_out_dict['Vdd']
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

def check_NF(sys_req_dict,hand_out_dict):
    Rs=hand_out_dict['Rs']
    Rd=hand_out_dict['Rd']
    Rb=hand_out_dict['Rb']
    gamma=sys_req_dict['gamma']
    NF_stat=False
    F_sim=1+gamma+4*Rs/Rd+Rs/Rb
    F_max=10**(sys_req_dict['NF_max_dB']/10)
    if np.log(F_sim)<np.log(F_max):
            NF_stat=True
    return NF_stat,F_max


def to_units(x_):		# Converting a number to unit form
    units = {-12: "T",-9: "G",-6: "Meg",-3: "k",0: "",3: "m",6: "u",9: "n",12: "p",15: "f"}
    k = -12
    z=x_
    x_=abs(x_)
    while x_ * 10.0**k < 1: 
        k += 3
    x_=x_*abs(z)/z
    y_=round(x_*10.0**k,3)
    return f"{y_}{units[k]}"

def DC_correct(hand_out_dict):		# Correcting the Bias Values
	DC_status=Sat_Vol_check(hand_out_dict)
	while DC_status==False:
		hand_out_dict['Io']=1.01*hand_out_dict['Io']
		hand_out_dict['W']=2*hand_out_dict['Io']*hand_out_dict['L']/(hand_out_dict['mew_n']*hand_out_dict['Cox']*((2*hand_out_dict['Io']*hand_out_dict['Rs'])**2))
		#hand_out_dict['Vosw']=1.01*hand_out_dict['Vosw']
		hand_out_dict['Rb']=(hand_out_dict['Vdd']-hand_out_dict['Vosw'])/hand_out_dict['Io']-2*hand_out_dict['Rs']-hand_out_dict['Rd']
		DC_status=Sat_Vol_check(hand_out_dict)

	return hand_out_dict

def gm_correction(hand_out_dict,extract_param,cir_filename,chi_filename):
	count=40
	flag=0
	if abs(extract_param['Io']-hand_out_dict['Io'])<0.2*hand_out_dict['Io']:
		print("DC current is ok")
		while extract_param['gm1']<0.95*20e-3:
			gm_prev=extract_param['gm1']
			if flag==0:
				hand_out_dict['Io']=1.1*hand_out_dict['Io']
				hand_out_dict['W']=2*hand_out_dict['Io']*hand_out_dict['L']/(hand_out_dict['mew_n']*hand_out_dict['Cox']*((2*hand_out_dict['Io']*hand_out_dict['Rs'])**2))
				hand_out_dict['Rb']=(hand_out_dict['Vdd']-hand_out_dict['Vosw'])/hand_out_dict['Io']-2*hand_out_dict['Rs']-hand_out_dict['Rd']
			elif flag==1:
				hand_out_dict['W']=1.2*hand_out_dict['W']
			output_dict,extract_param=write.Run_simulation(hand_out_dict,cir_filename,chi_filename)
			gm_current=extract_param['gm1']
			if gm_current<gm_prev:
				if flag==0:
					hand_out_dict['Io']=hand_out_dict['Io']/1.1
				flag=flag+1

			if flag==2:
				print('flag')
				break
			print('gm=',gm_current,'Io=',extract_param['Io'],'W=',hand_out_dict['W'])
			count=count-1
			print(count,hc.Sat_Vol_check(hand_out_dict))
			if count==0:
				break
		print('gm=',hc.to_units(extract_param['gm1']),'Io=',hc.to_units(extract_param['Io']),'W=',hc.to_units(hand_out_dict['W']))

		print('**********************************After Correcting the gm**************************************')
		write.print_dict(extract_param)
		


		return hand_out_dict,extract_param

	
