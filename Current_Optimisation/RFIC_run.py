import numpy as np
import os
import RFIC_Write as write
import RFIC_Hand_calculations as hc
import RFIC_Param_Extraction as pe
import RFIC_optimize as optimize
import pylab as py


lib_name='/home/ee18b064/Eldo_files/Models_UMC180/ibm013.lib'
file_dir='/home/ee18b064/Optimization/Current_Optimisation/'
recquirements_name=file_dir+'RFIC_req.txt'
save_data_path=file_dir+'data.csv'
cir_filename="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics/default/CGA_CurrentMirror_1_With_parasitics_default_default.cir"
chi_filename="/home/ee18b064/Eldo_files/CGA_CurrentMirror_1_With_parasitics/default/CGA_CurrentMirror_1_With_parasitics_default_default.chi"

hand_out_dict={}
hand_out_dict['Io']=553e-6
hand_out_dict['W']=67.7e-6
hand_out_dict['Rb']=194.145
hand_out_dict['Rd']=946.623
hand_out_dict['L']=130e-9
hand_out_dict['C1']=318.155e-12
hand_out_dict['C2']=206.896e-12
hand_out_dict['fo']=1e9

write.call_write_param(hand_out_dict,cir_filename)
write.Run_Eldo()
extract_param1=pe.extract_output_param(chi_filename)

write.print_dict(extract_param1)
print('Vgs-Vth=',extract_param1['Vg']-extract_param1['Vs']-extract_param1['Vth'],'\n')

hand_out_dict['Io']=1.01*hand_out_dict['Io']

write.call_write_param(hand_out_dict,cir_filename)
write.Run_Eldo()
extract_param2=pe.extract_output_param(chi_filename)

write.print_dict(extract_param2)
print('Vgs-Vth=',extract_param2['Vg']-extract_param2['Vs']-extract_param2['Vth'],'\n')

I=(extract_param2['Io']-extract_param1['Io'])/extract_param1['Io']
gain=(extract_param2['gain_dB']-extract_param1['gain_dB'])/extract_param1['gain_dB']
s11=(extract_param2['s11_dB']-extract_param1['s11_dB'])/extract_param1['s11_dB']
iip3=(extract_param2['iip3_dBm']-extract_param1['iip3_dBm'])/extract_param1['iip3_dBm']
nf=(extract_param2['NF_dB']-extract_param1['NF_dB'])/extract_param1['NF_dB']


print('gain : ',gain,'\n')
print('s11 : ',s11,'\n')
print('iip3 : ',iip3,'\n')
print('nf : ',nf,'\n')
print('I : ',I,'\n')
