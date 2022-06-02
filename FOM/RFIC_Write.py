import fileinput
import RFIC_Hand_calculations as hc
import sys
import os
import RFIC_Param_Extraction as pe


def print_param(param_var,val):				 
    return ".PARAM "+param_var+'='+str(val)+'\n'


def write_param(filename,param,param_dict):			# Writing the .Param command in the .cir file
    f=open(filename,'r+')
    s=''
    for line in fileinput.input(filename):
            for i in param:
                if ".PARAM "+i+'=' in line:
                    line=line.replace(line,print_param(i,param_dict[i]))
            s=s+line
    f.truncate(0)
    f.write(s)
    f.close()

def print_dict(dict_):						# To print a Dictionary
    print('\n')
    for i in dict_:
        print(i,'=  ',hc.to_units(dict_[i]))
    print('\n')

def call_write_param(hand_out_dict,cir_filename):		# Taking the inputs and Writing the parameters in the file
	
	param=['W','L','Io','Rb','Rd','C1','C2','fo']
	param_dict={'W':(hand_out_dict['W']),'L':(hand_out_dict['L']),'Io':(hand_out_dict['Io']),'Rb':(hand_out_dict['Rb']),'Rd':(hand_out_dict['Rd']),'C1':(hand_out_dict['C1']),'C2':(hand_out_dict['C2']),'fo':(hand_out_dict['fo'])}
	param_write_dict={'W':hc.to_units(hand_out_dict['W']),'L':hc.to_units(hand_out_dict['L']),'Io':hc.to_units(hand_out_dict['Io']),'Rb':hc.to_units(hand_out_dict['Rb']),'Rd':hc.to_units(hand_out_dict['Rd'])}
	param_write_dict['C1']=hc.to_units(hand_out_dict['C1'])
	param_write_dict['C2']=hc.to_units(hand_out_dict['C2'])
	param_write_dict['fo']=hand_out_dict['fo']
	write_param(cir_filename,param,param_write_dict)
	#print_dict(param_dict)


def Run_Eldo():							# Running Eldo 
	os.system("cd /home/ee18b064/Eldo_files")
	#os.system("tcsh /home/ee18b064/Optimization/FOM/eldo_parallel.tcsh")
	os.system("tcsh /home/ee18b064/Optimization/FOM/eldo.tcsh")

def Run_simulation(hand_out_dict,cir_filename,chi_filename):
	call_write_param(hand_out_dict,cir_filename)
	Run_Eldo()
	extract_param=pe.extract_output_param(chi_filename)
	output_dict=pe.Output_dict(extract_param)

	return output_dict,extract_param

