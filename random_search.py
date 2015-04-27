#! /usr/local/env python

import re
import os
import numpy
from copy import copy, deepcopy


fn = raw_input("Enter path/name of original PDB file [AAA.pdb]: ") or "AAA.pdb"
opdir = raw_input("Enter path/name of output directory [./]: ") or "."
opdir = os.path.dirname(opdir+"/")
# Read Original PDB file 
fi = open(fn,"r") 
lines = fi.readlines()
atoms = []
for line in lines:
	atom = {}
	if re.search("^ATOM",line):
		atom['b4xyz']=line[0:30]
		atom['x']=float(line[30:38]) 
		atom['y']=float(line[38:46]) 
		atom['z']=float(line[46:54])
		atom['afterxyz']=line[54:]
		atoms.append(atom)

def gen_new_coords(atoms,fno):
	new_atoms = deepcopy(atoms)
	try:
		fo = open(fno,"w")
		for atom in new_atoms:
			atom['x']=atom['x']+numpy.random.randn(1)[0]
			atom['y']=atom['y']+numpy.random.randn(1)[0]
			atom['z']=atom['z']+numpy.random.randn(1)[0]
			fo.write("%s%8.3f%8.3f%8.3f%s" %(atom['b4xyz'],atom['x'],atom['y'],atom['z'],atom['afterxyz']))
		fo.close()
	except:
		pass

def gen_psf(opdir,fno,i):
	fo = open(fno+"_"+str(i)+".tcl","w")
	fo.write("./psfgen << ENDMOL\n")
	fo.write("topology top_all22_prot.inp\n")
	fo.write("segment "+fno+" {\npdb "+opdir+fno+".pdb\n}\n")
	fo.write("coordpdb "+opdir+fno+".pdb "+fno+"\n")
	fo.write("guesscoord\n")
	fo.write("writepsf "+opdir+fno+"_autopsf.psf\n")
	fo.write("writepdb "+opdir+fno+"_autopsf.pdb\n")
	fo.write("ENDMOL")
	fo.close()
	os.system("bash "+fno+"_"+str(i)+".tcl > "+opdir+fno+"_tcl.log")
	
def run_namd(opdir,fno,i):
	fo = open(fno+"_"+str(i)+".namd","w")
	fo.write("numsteps\t\t10000\nminimization\t\ton\ndielectric\t\t1.0\n")
	fo.write("coordinates\t\t"+opdir+fno+"_autopsf.pdb\noutputname\t\t"+opdir+fno+"\n")
	fo.write("outputEnergies\t\t100\nbinaryoutput\t\tno\nDCDFreq\t\t\t100\nrestartFreq\t\t100\n")
	fo.write("structure\t\t"+opdir+fno+"_autopsf.psf\n")
	fo.write("paraTypeCharmm\t\ton\nparameters\t\tpar_all22_prot.prm\nexclude\t\t\tscaled1-4\n1-4scaling\t\t1.0\nswitching\t\ton\nswitchdist\t\t8.0\ncutoff\t\t\t12.0\npairlistdist\t\t13.5\nmargin\t\t\t0.0\nstepspercycle\t\t20\n")
	fo.close()
	os.system("./namd2 "+fno+"_"+str(i)+".namd > "+opdir+fno+".log")
	os.system("grep \"ENERGY:   10000\" "+opdir+fno+".log > last_energy.txt")
	fi = open("last_energy.txt","r")
	energy_line = fi.readline()
	fi.close()
	energy_line = re.split(" +",energy_line)
	return energy_line[11]

energies = []
fn = re.sub("\..*$","",fn)
fn = re.sub("^.*/","",fn)
i = 1
fo = open("energies_list.txt","w")
while i<=200:
	try:
	    os.stat(opdir+"/"+fn+"_"+str(i))
	except:
	    os.mkdir(opdir+"/"+fn+"_"+str(i)) 
	finally:
		gen_new_coords(atoms,opdir+"/"+fn+"_"+str(i)+"/"+fn+".pdb")
		gen_psf(opdir+"/"+fn+"_"+str(i)+"/",fn,i)
		last_energy = run_namd(opdir+"/"+fn+"_"+str(i)+"/",fn,i)
		le = "%.1f" %(float(last_energy))
		if float(last_energy)<=0 and le not in energies:
			energies.append(le)
			print str(i)+" : "+last_energy
			fo.write(str(i)+" : "+last_energy+"\n")
			i = i + 1

fo.close()
		
