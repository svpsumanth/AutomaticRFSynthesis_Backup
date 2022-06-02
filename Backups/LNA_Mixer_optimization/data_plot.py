#===========================================================================================================================
"""
Name: Pyneni Roopesh
Roll Number: EE18B028

Data Plot File:
"""
#===========================================================================================================================
import numpy as np
import math
import os
import common_functions as cf
import pandas as pd 
from matplotlib import pylab
from pylab import *
#===========================================================================================================================


#===========================================================================================================================
#----------------------------------- Extracting and Plotting Double Array --------------------------------------------------
	
#-----------------------------------------------------------------------------------------------
# Function to extract the loss data from csv file
def extract_double_array(filename_root,filename_name):
	
	# Extracting data from the files
	filename=filename_root+'/results/'+filename_name+'.csv'
	f=open(filename)
	lines=f.readlines()
	f.close()
	
	# Assigning the array to store the loss variables
	param_name=[]
	variable_name=[]
	
	# Extracting the first line of the csv file
	line=lines[0].split(',')
	lines=lines[1:]
	
	# Creating variables for the counting no of lines and variables
	n_iter=len(lines)
	n_param=0
	n_variable=0
	
	# Counting n_param and n_variable
	for char in line:
		if char == '\n':
			break
		n_param+=1
		
	n_param-=1 # CHANGE
	
	"""
	for i in range(2,n_param):
		if line[i]==line[1]:
			n_variable=i-2
			break
	"""
	
	for i in range(3,n_param):
		if line[i]==line[2]:
			n_variable=i-3
			break

	n_param=int(n_param/n_variable)
	
	
	# Storing n_param and n_variable
	for i in range(n_variable):
		variable_name.append(line[i+2])
		#variable_name.append(line[i+1])
	for i in range(n_param):
		param_name.append(line[(n_variable+1)*i+1])
		#param_name.append(line[(n_variable+1)*i])		
	
	# Creating array to store the values 
	loss_slope_array=np.zeros((n_iter,n_param,n_variable),dtype=float)
	
	# Extracting the values of the variables
	for i in range(n_iter):
	
		# Extracting the next line
		line=lines[0].split(',')
		lines=lines[1:]
		
		# Storing the variables
		for j in range(n_param):
			for k in range(n_variable):
				loss_slope_array[i,j,k]=float(line[(n_variable+1)*j+k+2])
				#loss_slope_array[i,j,k]=float(line[(n_variable+1)*j+k+1])
		
	return loss_slope_array,param_name,variable_name
	
#-----------------------------------------------------------------------------------------------
# Plotting loss slope vs iterations
def plot_double_array(filename_root,filename_name):
	
	loss_array,param_name,variable_name=extract_double_array(filename_root,filename_name)
	n_iter=loss_array.shape[0]
	n_param=loss_array.shape[1]
	n_variable=loss_array.shape[2]
	
	filename=filename_root+'/plots/'+filename_name+'/'
	if not os.path.exists(filename):
    		os.makedirs(filename)
	
	# Creating the new arrays
	arrX=np.zeros((n_iter,1),dtype=float)
	
	# Calculating values of new array
	i=0	
	while i<n_iter:
		arrX[i,0]=i+1	
		i+=1
		
	print('Starting Plots '+filename_name)
	
	color_dict={0:'r',1:'g',2:'b',3:'c',4:'m',5:'k',6:'y'}
	n_colour=7
	
	for i in range(n_param):
		figure()
		for j in range(n_variable):
			plot(arrX,loss_array[:,i,j],color_dict[int(j%n_colour)],label=variable_name[j])
		xlabel('Iterations')
		ylabel(param_name[i])
		legend()
		grid()
		savefig(filename+param_name[i]+'.pdf')
		close()
	
	print('Plotting Over '+filename_name)

	

#===========================================================================================================================
#------------------------------------Extracting and Plotting Single Array --------------------------------------------------

#-----------------------------------------------------------------------------------------------
# Function to extract the data from csv file
def extract_single_array(filename_root,filename_name):
	
	# Extracting data from the files
	filename=filename_root+'/results/'+filename_name+'.csv'
	f=open(filename)
	lines=f.readlines()
	f.close()
	
	# Assigning the array to store the loss variables
	param_name=[]
	
	# Extracting the first line of the csv file
	line=lines[0].split(',')
	lines=lines[1:]
	
	# Creating variables for the counting no of lines and variables
	n_iter=len(lines)
	n_param=0
	
	# Storing the variable names
	for char in line:
		if char == '\n':
			break
		if char != 'Iteration No':
			param_name.append(char)
		n_param+=1

	n_param-=1 # CHANGE
		
	# Creating array to store the values 
	loss_array=np.zeros((n_iter,n_param),dtype=float)
	
	# Extracting the values of the variables
	for i in range(n_iter):
	
		# Extracting the next line
		line=lines[0].split(',')
		lines=lines[1:]
		
		# Storing the variables
		for j in range(n_param):
			loss_array[i,j]=float(line[j+1])
			#loss_array[i,j]=float(line[j])
		
	return loss_array,param_name
	
	
#-----------------------------------------------------------------------------------------------
# Plotting average parameters vs iterations
def plot_single_array(filename_root,filename_name):
	
	loss_array,param_name=extract_single_array(filename_root,filename_name)
	n_iter=loss_array.shape[0]
	n_param=loss_array.shape[1]
	
	filename=filename_root+'/plots/'+filename_name+'/'
	if not os.path.exists(filename):
    		os.makedirs(filename)
	
	# Creating the new arrays
	arrX=np.zeros((n_iter,1),dtype=float)
	
	# Calculating values of new array
	i=0	
	while i<n_iter:
		arrX[i,0]=i+1	
		i+=1
		
	print('Starting Plots '+filename_name)
	
	color_dict={0:'r',1:'g',2:'b',3:'c',4:'m',5:'k',6:'y'}
	n_colour=7
	
	# Figure 1
	figure()
	for i in range(n_param):
		plot(arrX,loss_array[:,i],color_dict[int(i%n_colour)],label=param_name[i])
		annotate(cf.num_trunc(loss_array[n_iter-1,i],3),(arrX[n_iter-1,0],loss_array[n_iter-1,i]))
	xlabel('Iterations')
	ylabel('Parameter')
	legend()
	grid()
	savefig(filename+'all.pdf')
	close()
	
	
	# Figure 2	
	for i in range(n_param):
		figure()
		plot(arrX,loss_array[:,i],'g',label=param_name[i])
		annotate(cf.num_trunc(loss_array[n_iter-1,i],3),(arrX[n_iter-1,0],loss_array[n_iter-1,i]))
		xlabel('Iterations')
		ylabel(param_name[i])
		legend()
		grid()
		savefig(filename+param_name[i]+'.pdf')
		close()
	
	print('Plotting Over '+filename_name)



#-----------------------------------------------------------------------------------------------
# Plotting Output parameters vs Temperature

def plot_temp_var_plots(data_filename,results_dir,optimization_input_parameters):
	
	df=pd.read_csv(data_filename)

	print("Saving all the Plots of extracted parameters vs Temperature")
	for i in df.columns[1:]:
		fig=df.plot(x='Temperature', y=i)

		if i in optimization_input_parameters['output_specs_params_list']:
			lst1=[optimization_input_parameters['output_conditions'][i]]*len(optimization_input_parameters['temp_list'])
			lst2=optimization_input_parameters['temp_list']
			df2=pd.DataFrame(list(zip(lst1, lst2)),columns =[i,'Temperature'])
			df2.plot(x='Temperature', y=i,label='Spec',ax=fig,lw=3)
		fig.axvline(x=27, color='k', linestyle='--', label='T=27')

		filepath=results_dir+'png/'
		if not os.path.exists(filepath):
			os.makedirs(filepath)

		fig.figure.savefig(filepath+i+'.png')	

		filepath=results_dir+'pdf/'
		if not os.path.exists(filepath):
			os.makedirs(filepath)

		fig.figure.savefig(filepath+i+'.pdf')	

#-----------------------------------------------------------------------------------------------
# Plotting Output parameters vs Temperature

def plot_temp_with_current_var_plots(data_filename,results_dir,optimization_input_parameters,Io_list):
	
	temp_list=optimization_input_parameters['temp_list']
	df=pd.read_csv(data_filename)
	print("Saving all the Plots of extracted parameters vs Temperature")
	for i in df.columns[2:]:
		for j in range(len(Io_list)):
			df1=df[df["Input_Current"].round(10)==round(Io_list[j],10)]
			if j==0:		
				fig=df1.plot(x='Temperature', y=i,label='Ibias='+str(cf.num_trunc(Io_list[j],3)),linestyle = 'dashed',lw=0.75)
			else:
				if j==int(len(Io_list)/2):
					df1.plot(x='Temperature', y=i,label='Ibias(Opt_27)='+str(cf.num_trunc(Io_list[j],3)),ax=fig,lw=2)	# Bolds the plot of actual optimized point at 27C
					fig.axvline(x=27, color='k', linestyle='--', label='T=27')						# Vertical Reference for T=27C
				elif j<int(len(Io_list)/2):
					df1.plot(x='Temperature', y=i,label='Ibias='+str(cf.num_trunc(Io_list[j],3)),ax=fig,linestyle = 'dashed',lw=0.75)   # Dashed plot for I less than Ibias at 27
				elif j>int(len(Io_list)/2):
					df1.plot(x='Temperature', y=i,label='Ibias='+str(cf.num_trunc(Io_list[j],3)),ax=fig,lw=0.75)   	# Solid Plot for I more than Ibias at 27C
			
		if i in optimization_input_parameters['output_specs_params_list']:
			lst1=[optimization_input_parameters['output_conditions'][i]]*len(optimization_input_parameters['temp_list'])
			lst2=optimization_input_parameters['temp_list']
			df2=pd.DataFrame(list(zip(lst1, lst2)),columns =[i,'Temperature'])
			df2.plot(x='Temperature', y=i,label='Spec',ax=fig,lw=2.5)

		box = fig.get_position()
		fig.set_position([box.x0, box.y0, box.width * 0.7, box.height])

		# Put a legend to the right of the current axis
		fig.legend(loc='center left', bbox_to_anchor=(1, 0.5))


		filepath=results_dir+'png/'
		if not os.path.exists(filepath):
			os.makedirs(filepath)

		fig.figure.savefig(filepath+i+'.png')	

		filepath=results_dir+'pdf/'
		if not os.path.exists(filepath):
			os.makedirs(filepath)

		fig.figure.savefig(filepath+i+'.pdf')	


#-----------------------------------------------------------------------------------------------
# Plotting Output parameters vs Temperature

def plot_temp_process_var_plots(data_filename,results_dir,optimization_input_parameters):
	
	df=pd.read_csv(data_filename)
	Corner=optimization_input_parameters['model_process_corners']	
	
	
	print("Saving all the Plots of extracted parameters vs Temperature,Process")
	for i in df.columns[2:]:
		flag=0
		for model in Corner:
			df1=df[df["Corner"]==model]
			if flag==0:
				fig=df1.plot(x='Temperature', y=i,label=model)
				flag=1

				if i in optimization_input_parameters['output_specs_params_list']:
					lst1=[optimization_input_parameters['output_conditions'][i]]*len(optimization_input_parameters['temp_list'])
					lst2=optimization_input_parameters['temp_list']
					df2=pd.DataFrame(list(zip(lst1, lst2)),columns =[i,'Temperature'])
					df2.plot(x='Temperature', y=i,label='Spec',ax=fig,lw=3,color='k')
			
				

			else:
				df1.plot(x='Temperature', y=i,label=model,ax=fig)

			
		fig.axvline(x=27, color='k', linestyle='--', label='T=27')		# Vertical line for Temperature Reference

		filepath=results_dir+'png/'
		if not os.path.exists(filepath):
			os.makedirs(filepath)

		fig.figure.savefig(filepath+i+'.png')	

		filepath=results_dir+'pdf/'
		if not os.path.exists(filepath):
			os.makedirs(filepath)

		fig.figure.savefig(filepath+i+'.pdf')	


#===========================================================================================================================
#------------------------------------Main Program Code----------------------------------------------------------------------
def plot_complete(optimization_input_parameters):

	filename=optimization_input_parameters['filename']['output']
	
	plot_single_array(filename,'loss')
	plot_single_array(filename,'alpha_parameters')
	plot_single_array(filename,'output_parameters')
	plot_single_array(filename,'circuit_parameters')
	plot_single_array(filename,'average_parameters')
	
	plot_double_array(filename,'loss_slope')
	plot_double_array(filename,'sensitivity')
	

#===========================================================================================================================


