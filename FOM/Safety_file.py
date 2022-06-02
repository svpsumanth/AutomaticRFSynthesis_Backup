import numpy as np
from si_prefix import si_format
import RFIC_Write as cir_w
import RFIC_Hand_calculations as hc

# System specifications from the model file (In SI units)

L_min=180*1e-9
mew_n=0.02738
Cox=0.00862875
Vdd=1.8
Vth=0.5


# Recquired Specifications from the System

gain_dB=12
s11_dB_max=-15
iip3_dBm_min=-5
NF_max_dB=4
f=1e9           #frequency of operation
Rs=50
# From this we need to get good starting points for inputs Rd,Rb,Io,W
k=1.5   # Let us define k=1+gds*Rd
gamma=2/3  # Noise factor for the mosfet

def to_units(x_):
    units = {-12: "T",-9: "G",-6: "Meg",-3: "k",0: "",3: "m",6: "u",9: "n",12: "p",15: "f"}
    k = -12
    while x_ * 10.0**k < 1: 
        k += 3
    y_=round(x_*10.0**k,3)
    return f"{y_}{units[k]}"


hand_in=['gain_dB','s11_dB_max','iip3_dBm_min','NF_max_dB','f','Rs','k','gamma','L_min','mew_n','Cox','Vth','Vdd']
hand_in_dict={'gain_dB':gain_dB,'s11_dB_max':s11_dB_max,'iip3_dBm_min':iip3_dBm_min,'NF_max_dB':NF_max_dB,'f':f,'Rs':Rs,'k':k,'gamma':gamma,'L_min':L_min,'mew_n':mew_n,'Cox':Cox,'Vth':Vth,'Vdd':Vdd}

#hand_out=['Io','W','L','Rd','Rb','C1','C2','Rs','Vth']
#hand_out_dict={'Io':Io,'W':W,'L':L,'Rd':Rd,'Rb':Rb,'C1':C1,'C2':C2,'Rs':Rs,'Vth':Vth}

#gain_dB,s11_dB_max,iip3_dBm_min,NF_max_dB,f,Rs,k,gamma
'''def circuit_parameters(hand_in,hand_in_dict):
    L=L_min  # For RF Applications L is always choosen as minimum length possible
    gain=10**(gain_dB/20)
    s11_max=10**(s11_dB_max/10)
    F_max=10**(NF_max_dB/10)
    
    #To get Rd we can use ideal gain expression
    Rd=2*Rs*gain
    P1dBm_min=iip3_dBm_min-9.6
    Pin=(1e-3)*10**(P1dBm_min/10)
    Vosw_min=gain*np.sqrt(8*Rs*Pin)
    Vosw=0.1+Vosw_min
    
    #From S11
    Zim_max=100*np.sqrt(s11_max/(1-s11_max))
    Io_min=(k**2)*np.pi*2*f*(L**2)/(3*mew_n*Zim_max)        # Got the value for Io_min so we will start off with this thing
    Io=Io_min
    Vdsat=2*Rs*Io
    W=2*Io*L/(mew_n*Cox*(Vdsat**2))                         # Got the Value of W
    Rb=(Vdd-Vosw)/Io-2*Rs-Rd                                # Got the value for Rb and with this we know Rb,Rd,W,L,Io
    F_sim=1+gamma+4*Rs/Rd+Rs/Rb
    C1=100/(2*np.pi*f*2*Rs)
    C2=100/(2*np.pi*f*(Rb+Rs))

    return [Io,W,L,Rd,Rb,C1,C2,Io_min,Vosw]

def Sat_Vol_check(Io,Rs,Rd,Rb):
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

par=circuit_parameters(gain_dB,s11_dB_max,iip3_dBm_min,NF_max_dB,f,Rs,k,gamma)
Io=par[0]
W=par[1]
L=par[2]
Rd=par[3]
Rb=par[4]
C1=par[5]
C2=par[6]
Io_min=par[7]
Vosw=par[8]
DC_status=Sat_Vol_check(Io,Rs,Rd,Rb)
'''
'''
if DC_status==False:
    while DC_status==False:
        #print('sdg')
        Io=Io+0.01*Io
        W=2*Io*L/(mew_n*Cox*((2*Rs*Io)**2))
        #Vosw=Vosw+0.01*Vosw
        Rb=(Vdd-Vosw)/Io-2*Rs-Rd
        DC_status=Sat_Vol_check(Io,Rs,Rd,Rb)

def check_NF(gamma,Rs,Rd,Rb):
    NF_stat=False
    F_sim=1+gamma+4*Rs/Rd+Rs/Rb
    F_max=10**(NF_max_dB/10)
    if np.log(F_sim)<np.log(F_max):
            NF_stat=True
    return NF_stat,F_max

if check_NF(gamma,Rs,Rd,Rb)[0]==False:
    print("NF check entered")
    F_sim=1+gamma+4*Rs/Rd+Rs/Rb
    F_max=check_NF(gamma,Rs,Rd,Rb)[1]
    if F_max<1+gamma+4*Rs/Rd:
        print("Design for NF is not possible") #Atleast for the zeroth model
    else:
        while DC_status==True and F_sim> F_max:
            if Io>Io_min:
                Io=Io-0.01*Io
                W=2*Io*L/(mew_n*Cox*((2*Rs*Io)**2))
                #Vosw=Vosw-0.01*Vosw
            else:
                print("Current minimum reached so cant design NF")
                break
            Rb=(Vdd-Vosw)/Io-2*Rs-Rd
            F_sim=1+gamma+4*Rs/Rd+Rs/Rb
            DC_status=Sat_Vol_check(Io,Rs,Rd,Rb)
            if DC_status==False:
                print("Voltage node limit reached so cant design NF")    
'''        
#F_sim=1+gamma+4*Rs/Rd+Rs/Rb
par=hc.circuit_parameters(hand_in,hand_in_dict)
Io=par[0]
W=par[1]
L=par[2]
Rd=par[3]
Rb=par[4]
C1=par[5]
C2=par[6]
Io_min=par[7]
Vosw=par[8]
#DC_status=Sat_Vol_check(Io,Rs,Rd,Rb)
#print("DC_status : ",DC_status)
print("W : ",W)
print("L : ",L)
print("Rb : ",Rb)
print("Io : ",Io)
print("Rd : ",Rd)
print("C1 : ",C1)
print("C2 : ",C2)
#print("NF : ",10*np.log(F_sim)/np.log(10))
#print("NF_stat : ",check_NF(gamma,Rs,Rd,Rb)[0])
print('\n')

param=['W','L','Io','Rb','Rd','C1','C2']
param_dict={'W':to_units(W),'L':to_units(L),'Io':to_units(Io),'Rb':to_units(Rb),'Rd':to_units(Rd),'C1':to_units(C1),'C2':to_units(C2)}
filename="CGA_CurrentMirror_1_With_parasitics_default_default"
cir_w.write_param(filename,param,param_dict)









#hand_out=['Io','W','L','Rd','Rb','C1','C2','Rs','Vth']
#hand_out_dict={'Io':Io,'W':W,'L':L,'Rd':Rd,'Rb':Rb,'C1':C1,'C2':C2,'Rs':Rs,'Vth':Vth}

#gain_dB,s11_dB_max,iip3_dBm_min,NF_max_dB,f,Rs,k,gamma





import numpy as np
from si_prefix import si_format
import RFIC_Write as cir_w
import RFIC_Hand_calculations as hc
import RFIC_Param_Extraction as pe

# System specifications from the model file (In SI units)
lib_name='tsmc018.lib'
Lmin=180*1e-9
Vdd=1.8
gain_dB=12                      # Recquired Specifications from the System
s11_dB_max=-15
iip3_dBm_min=-5
NF_max_dB=4
f=1e9           
Rs=50

mos_file_parameters = {'mew_n':0,'Cox':0,'Vth':0,'Lmin':Lmin,'Vdd':Vdd}
mos_param_dict=pe.extract_mosfet_param(lib_name,'NMOS',mos_file_parameters)
sys_req_dict={'gain_dB':gain_dB,'s11_dB_max':s11_dB_max,'iip3_dBm_min':iip3_dBm_min,'NF_max_dB':NF_max_dB,'f':f,'Rs':Rs}
print(mos_param_dict)
'''
mew_n=0.02738
Cox=0.00862875

Vth=0.7


k=1.5   # Let us define k=1+gds*Rd
gamma=2/3  # Noise factor for the mosfet

hand_in=['gain_dB','s11_dB_max','iip3_dBm_min','NF_max_dB','f','Rs','k','gamma','L_min','mew_n','Cox','Vth','Vdd']
hand_in_dict={'gain_dB':gain_dB,'s11_dB_max':s11_dB_max,'iip3_dBm_min':iip3_dBm_min,'NF_max_dB':NF_max_dB,'f':f,'Rs':Rs,'k':k,'gamma':gamma,'L_min':L_min,'mew_n':mew_n,'Cox':Cox,'Vth':Vth,'Vdd':Vdd}

hand_out,hand_out_dict=hc.circuit_parameters(hand_in,hand_in_dict)

DC_status=hc.Sat_Vol_check(hand_out,hand_out_dict)
if DC_status==False:
    while DC_status==False:
        hand_out_dict['Io']=1.01*hand_out_dict['Io']
        hand_out_dict['W']=2*hand_out_dict['Io']*hand_out_dict['L']/(hand_in_dict['mew_n']*hand_in_dict['Cox']*((2*hand_out_dict['Io']*hand_out_dict['Rs'])**2))
        #hand_out_dict['Vosw']=1.01*hand_out_dict['Vosw']
        hand_out_dict['Rb']=(hand_out_dict['Vdd']-hand_out_dict['Vosw'])/hand_out_dict['Io']-2*hand_out_dict['Rs']-hand_out_dict['Rd']
        DC_status=hc.Sat_Vol_check(hand_out,hand_out_dict)


if hc.check_NF(hand_in,hand_in_dict,hand_out,hand_out_dict)[0]==False:
    print("NF check entered")
    F_sim=1+hand_out_dict['gamma']+4*hand_out_dict['Rs']/hand_out_dict['Rd']+hand_out_dict['Rs']/hand_out_dict['Rb']
    F_max=check_NF(hand_out,hand_out_dict)[1]
    if F_max<1+hand_out_dict['gamma']+4*hand_out_dict['Rs']/hand_out_dict['Rd']:
        print("Design for NF is not possible") #Atleast for the zeroth model
    else:
        while DC_status==True and F_sim> F_max:
            if hand_out_dict['Io']>hand_out_dict['Io_min']:
                hand_out_dict['Io']=0.99*hand_out_dict['Io']
                hand_out_dict['W']=2*hand_out_dict['Io']*hand_out_dict['L']/(hand_in_dict['mew_n']*hand_in_dict['Cox']*((2*hand_out_dict['Io']*hand_out_dict['Rs'])**2))
                #hand_out_dict['Vosw']=0.99*hand_out_dict['Vosw']
            else:
                print("Current minimum reached so cant design NF")
                break
            hand_out_dict['Rb']=(hand_out_dict['Vdd']-hand_out_dict['Vosw'])/hand_out_dict['Io']-2*hand_out_dict['Rs']-hand_out_dict['Rd']
            F_sim=1+hand_out_dict['gamma']+4*hand_out_dict['Rs']/hand_out_dict['Rd']+hand_out_dict['Rs']/hand_out_dict['Rb']
            hand_ot_
            DC_status=Sat_Vol_check(hand_out,hand_out_dict)
            if DC_status==False:
                print("Voltage node limit reached so cant design NF")

param=['W','L','Io','Rb','Rd','C1','C2']
param_dict={'W':hc.to_units(hand_out_dict['W']),'L':hc.to_units(hand_out_dict['L']),'Io':hc.to_units(hand_out_dict['Io']),'Rb':hc.to_units(hand_out_dict['Rb']),'Rd':hc.to_units(hand_out_dict['Rd']),'C1':hc.to_units(hand_out_dict['C1']),'C2':hc.to_units(hand_out_dict['C2'])}
filename="CGA_CurrentMirror_1_With_parasitics_default_default"
cir_w.write_param(filename,param,param_dict)

'''









'''
if DC_status==False:
    while DC_status==False:
        hand_out_dict['Io']=1.01*hand_out_dict['Io']
        hand_out_dict['W']=2*hand_out_dict['Io']*hand_out_dict['L']/(hand_in_dict['mew_n']*hand_in_dict['Cox']*((2*hand_out_dict['Io']*hand_out_dict['Rs'])**2))
        #hand_out_dict['Vosw']=1.01*hand_out_dict['Vosw']
        hand_out_dict['Rb']=(hand_out_dict['Vdd']-hand_out_dict['Vosw'])/hand_out_dict['Io']-2*hand_out_dict['Rs']-hand_out_dict['Rd']
        DC_status=hc.Sat_Vol_check(hand_out_dict)
'''




'''

if hc.check_NF(sys_req_dict,hand_out_dict)[0]==False:
    print("NF check entered")
    F_sim=1+hand_out_dict['gamma']+4*hand_out_dict['Rs']/hand_out_dict['Rd']+hand_out_dict['Rs']/hand_out_dict['Rb']
    F_max=hc.check_NF(hand_out,hand_out_dict)[1]
    if F_max<1+hand_out_dict['gamma']+4*hand_out_dict['Rs']/hand_out_dict['Rd']:
        print("Design for NF is not possible") #Atleast for the zeroth model
    else:
        while DC_status==True and F_sim> F_max:
            if hand_out_dict['Io']>hand_out_dict['Io_min']:
                hand_out_dict['Io']=0.99*hand_out_dict['Io']
                hand_out_dict['W']=2*hand_out_dict['Io']*hand_out_dict['L']/(hand_in_dict['mew_n']*hand_in_dict['Cox']*((2*hand_out_dict['Io']*hand_out_dict['Rs'])**2))
                #hand_out_dict['Vosw']=0.99*hand_out_dict['Vosw']
            else:
                print("Current minimum reached so cant design NF")
                break
            hand_out_dict['Rb']=(hand_out_dict['Vdd']-hand_out_dict['Vosw'])/hand_out_dict['Io']-2*hand_out_dict['Rs']-hand_out_dict['Rd']
            F_sim=1+hand_out_dict['gamma']+4*hand_out_dict['Rs']/hand_out_dict['Rd']+hand_out_dict['Rs']/hand_out_dict['Rb']
            hand_ot_
            DC_status=Sat_Vol_check(hand_out_dict)
            if DC_status==False:
                print("Voltage node limit reached so cant design NF")


'''







      









      
