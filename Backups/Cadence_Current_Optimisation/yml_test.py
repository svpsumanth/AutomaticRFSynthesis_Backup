import yaml
import fileinput
from yaml.loader import SafeLoader

stream = open("res_model_param.yml", 'r')
library = yaml.load(stream, Loader=SafeLoader)
stream.close()

print((library[library['all_models'][0]]))

'''filename="/home/ee18b064/cadence_project/Cadence_test/circ.scs"
f=open(filename,'r+')
s=''

flag=0
for line in fileinput.input(filename):
	if "include" in line and flag==0:					# Change this line too
		line=library['tsmc018']
		flag=1
	elif "include" in line and flag==1:
		line=''
	s=s+line
f.truncate(0)
f.write(s)
f.close()

print(("M1 (Vout G1 S1 0) cmosn w=wid l=len".split()))'''
