from csv import reader
import json

cwd = os.getcwd() # working directory for static files
path = cwd+'/static/standards_data_complete.csv'
rd = list(reader(open(path)))[1:]
grades = set([r[0] for r in rd])
obj = {}

# creating an object with this hierarchy
# {grade:
#	{domain:
#		{standard:description}
#	}
# } 

# get the grade keys
for g in grades:
	obj[g] = {}
	domains = set([r[1] for r in rd if r[0] == g])
	for d in domains:
		obj[g][d] = {}
		standards = [(r[3],r[6]) for r in rd if r[0] == g and r[1] == d]
		for s in standards:
			obj[g][d][s[0]] = s[1].decode('ascii','ignore')

# write the file
objects_file = cwd+'/static/js/standards.js'
with open(objects_file,'w') as outfile:
	json.dump(obj,outfile,indent=4)

