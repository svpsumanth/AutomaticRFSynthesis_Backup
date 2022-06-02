import pandas as pd 
import matplotlib
import matplotlib.pyplot as plt

file_dir='/home/ee18b064/Optimization/Mixer_optimization/Simulation_Results/LOSS/latest_result/results/'
save_data_path=file_dir+'output_parameters.csv'
df=pd.read_csv(save_data_path)

#print('\n\n')
#print(df.groupby('fo')['FOM'].idxmax(),df.groupby('fo')['FOM'].max())
#print('\n\n')

#df=df[df['fo']<=10e9]
#df=df[df['PWR']<=10e-3]
#df=df[df['nf']<=13]
#df=df[df['gain']>=1]
#df=df[df['iip3']>=-15]
#df=df[df['s11']<=-15]
#df=df[df['FOM']>=df['FOM'].max()-1]	

print(df[df.columns[0:15]].head())
print('\n\n')

df.plot.scatter(x='Iteration No',y='Io')
'''df.plot.scatter(x='fo',y='FOM')
df.plot.scatter(x='n',y='Io')
df.plot.scatter(x='n',y='FOM')'''
plt.show()
