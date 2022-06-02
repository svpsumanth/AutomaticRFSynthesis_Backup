import os

param_list=['Io','Rb','W1']
main_file_path='/home/ee18b064/cadence_project/CGA_LNA_differential/non_ideal/hb_single_pin_diff/circ.scs'
main_file_dir='/home/ee18b064/Optimization/Cadence_Current_Optimisation/'
out_file_dir='/home/ee18b064/Optimization/Cadence_Current_Optimisation/duplicate_files/'

def scs_file_generate(param_list,main_file_path,out_file_dir):
	
	f=open(main_file_path)
	lines=f.readlines()
	f.close()
	
	s=''
	for line in lines:
		s=s+line


	for param in param_list:
		file_dir=out_file_dir+'slope_'+param+'/'
		out_file_path=file_dir+'circ.scs'

		if not os.path.exists(file_dir):
			os.makedirs(file_dir)
	
		f_out=open(out_file_path,'w')
		f_out.write(s)
		f_out.close()

def tcsh_file_generate(param_list,out_file_dir):
		
	


	for param in param_list:
		out_file_path=out_file_dir+'tcsh_run_'+param+'.tcsh'

		if not os.path.exists(out_file_dir):
			os.makedirs(out_file_dir)
	
		s=''
	
		s='#tcsh\n'
		s=s+'source ~/.cshrc\n'
		s=s+'cd '+out_file_dir+'\n'
		s=s+'spectre circ_slope_'+param+'.scs =log display.log\n'
		s=s+'exit'

		f_out=open(out_file_path,'w')
		f_out.write(s)
		f_out.close()


scs_file_generate(param_list,main_file_path,out_file_dir)
tcsh_file_generate(param_list,out_file_dir)
		
