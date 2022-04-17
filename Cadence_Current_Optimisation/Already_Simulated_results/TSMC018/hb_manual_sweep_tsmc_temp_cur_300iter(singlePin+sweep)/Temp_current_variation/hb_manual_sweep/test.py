import pandas as pd 
from matplotlib import pylab
from pylab import *

'''
df=pd.read_csv('temp_cur_var.csv')
df1=df[df['Input_Current'].round(10)==round(0.0015253161550319986,10)]
#df1=df[df["Input_Current"].all() >0.9*0.000381329 and df["Input_Current"].all() < 1.1*0.000381329]
#df2=df[df['Temperature']==-40]

fig=df1.plot(x='Input_Current',y='Io',label='-20')
#fig.legend(loc='center left',bbox_to_anchor=(0.5, 1.05))


box = fig.get_position()
fig.set_position([box.x0, box.y0, box.width * 0.8, box.height])

# Put a legend to the right of the current axis
fig.legend(loc='center left', bbox_to_anchor=(1, 0.5))


#df2.plot(x='Input_Current',y='Io',ax=fig,label='-40')
show()
#print(df1.head())
#print(df['Input_Current'][9])
#print(round(0.001525316155032,10))



'''
print([-1]*5)

hb_manual_sweep_tsmc_temp_cur_300iter(singlePin+sweep)
