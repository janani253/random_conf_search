#!/usr/local/env python

# Extract the unique conformations obtained from conformational search (by random search method) 
# Compile them into 1 PDB file as separate models

import os
import re


base_name = raw_input("Enter base-name of conformation file/folder names [AAA]: ") or "AAA"
conf_no = [int(f.split("_")[1]) for f in os.listdir('.') if re.match('^'+base_name+'_\d+$', f)]

conf_no = sorted(conf_no)
#print conf_no
fo = open(base_name+"_ensemble.pdb","w")
for i in conf_no:
	fo.write("MODEL      %3s\n" %(i))
	fi = open(base_name+"_"+str(i)+"/"+base_name+".coor","r")
	lines = fi.readlines()
	fi.close()
	lines = [line for line in lines if re.match("^ATOM",line)]
	fo.writelines(lines)
	fo.write("ENDMDL\n\n")
fo.close()
		
