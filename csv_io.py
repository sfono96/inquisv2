def isnumeric(s):
	try:
		float(s)
		return True
	except ValueError:
		return False

def read_csv(file_path):
	
	# headers
	headers = [h for h in open(file_path).readline().strip('\n').split(',')]

	# rows
	lines = open(file_path).readlines()[1:]
	data = []
	for line in lines:
		line = line.strip("\n").split(',')
		row = []
		counter = 0
		for l in line:
			if counter < 2: # if not one of the variables
				row.append(l)
			else:
				if l == '': # variable is null ('') replace with 0
					row.append(0)
				else:
					if isnumeric(l): # variable is numeric then convert string to float
						row.append(float(l))
					else:
						row.append(l) # else append variable to row
			counter += 1
		data.append(row)

	# results returned	
	return headers, data

def write_csv(file_path, data):
    with open(file_path,"w") as f:
        for line in data:
        	line = [str(l) for l in line] 
        	f.write(",".join(line) + "\n")