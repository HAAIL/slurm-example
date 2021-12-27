import sys
import json
import subprocess

# Gets a specific line from the input file
def getInput(line_number):
    sed_command = """sed '""" + line_number + """q;d' input/input.jsonl"""
    proc = subprocess.Popen(sed_command ,stdout=subprocess.PIPE, shell=True)
    line = eval(proc.communicate()[0])
    return line

# Computes a function
def func(line):
    result = line['x'] * line['y'] * 2 + 1
    return result

# Saves the results
def save(result,savename):
    with open(savename, 'w') as f:
        json.dump(result, f)

#---------------------------------------
# MAIN
#--------------------------------------
line_number = sys.argv[1]
savedir     = 'output/row_' + line_number + 'output.json'

# Get the input, and apply the function
line      = getInput(line_number)
result = func(line)

# Save the results
save(result, savedir + line_number)  

