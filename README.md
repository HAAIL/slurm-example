# How to use the MSU High Performance Computing Cluster

### 0. Assumptions
This guide makes the following assumptions:

* You have basic familiarity with how to navigate (`cd`, `ls`, `pwd`), edit files (`vim`,`nano`), change permissions (`chmod`) and execute software (`./`) within Unix/Linux environments. If you are not familiar with `bash` scripting, [this resource might be helpful](https://ryanstutorials.net/bash-scripting-tutorial/).
* You understand how to remotely access a remote machine via `ssh` (Terminal on Mac, or Powershell on Windows), how to perform port forwarding, and how to make and use `ssh keys`. If you are not familiar with ssh keys, [this resource might be helpful.](https://www.digitalocean.com/community/tutorials/how-to-set-up-ssh-keys-2). If you are not familiar with SSH port forwarding, please [see this resource](https://www.ssh.com/academy/ssh/tunneling/example).
* You have an account with the MSU High Performance Computing Customer; if you do not, please [contact me](mailto:mohammad@ghassemi.xyz) and I will create an account for you. 
* You have functional familiarity with virtual enrionments; if you do not, [this resource might be helpful](https://realpython.com/python-virtual-environments-a-primer/).


### 1. SSH into hpcc.msu.edu
To begin, you will access the cluster via `ssh`

```ssh <your-net-id>@hpcc.msu.edu```

You will be prompted for a password; this should be the same password you use for other MSU functions.

### 2. Add your SSH Public key

create (or use an existing) public ssh key and add this ssh key to the set of `authorized_keys`

```vim ~/.ssh/authorized_keys```


### 3. SSH into a development node

Choose a development node from the [list here](https://wiki.hpcc.msu.edu/display/ITH/Development+nodes). For instance:

```ssh dev-intel18```

### 3. Create a Symbolic Link to the Lab Directory
Your cluster account has two kinds of storage: your personal drive `/mnt/home/<your-net-id>` (50BG limit), and a shared drive for the lab `/mnt/research/ghassemi-lab/` (1TB). We can always request more space on the shared drive if needed, but your personal drive is static. You should create a [symbolic link](https://linuxize.com/post/how-to-create-symbolic-links-in-linux-using-the-ln-command/) to the lab shared drive from your home directory so it's easy to access

```ln -s /mnt/research/ghassemi-lab/ lab-directory```

You can then go to the lab directory by `cd lab-directory`


### 4. Crete a personal directory
Within the lab directory, create a personal folder to house your research work and change into that directory.

```
mkdir <your-first-name>-<your-last-name
cd <your-first-name>-<your-last-name>
```

#### 5. Modules and Python virtual environments
The cluster uses shared machines (gateways and development nodes) that serve as an intemediaries to other nodes on thre cluster. As such, you are not allowed to install packages (e.g. with `pip`) on the gateway machines directly. You can, however, install any packaes you might need in a virtual environment. To create the virtual environment run the following command:

```python3 -m venv venv```

### 6. Bind to the virtual environment. 
Once the virtual environement is created, you can now bind to it.

```source venv/bin/activate```

Once bound, you should see `(venv)` show up on the left of your command prompt. You can now `pip install` any packages you might need to run your code. When you are done installing packages, detach from the virtual environment using the `deactivate` command.

### 7. Create Data directories and input.
Ultimatly, software takes inputs and generates outputs. Let's generate folders to hold each.

```
mkdir input
mkdir output
```

Within the input data directory, let's create a dummy input dataset `input.jsonl` with the following contents:

```
{'x':1,'y':2}
{'x':2,'y':4}
{'x':3,'y':1}
```

### 8. Create your python script
Next, lets create a simple python script `python_script.py` that takes as an input argument a given line number from `input.jsonl` that we want to use to compute the output of a function, and store the results into a `results/` directory: 

```
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
```

### 9. Create SLURM Script
The point of a parallel computing custer is that We may want to compute the value of the function `func(x)` in parallel instead of sequentially. To use the cluster for this, we must specify the parameters of the machines we want to use for the parallel computation. To do this, let's create `slurm_job.sb`

```
#!/bin/bash
#SBATCH --job-name=exmaple
#SBATCH --nodes=1
#SBATCH --tasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --gres=gpu:0
#SBATCH --mem=1G
#SBATCH --time=1:00
#SBATCH --output=python_out/row_%a.out
#SBATCH --error=python_err/row_%a.err
#----------------------------------------------------
source /mnt/research/ghassemi-lab/mohammad-ghassemi/venv/bin/activate
python3 /mnt/research/ghassemi-lab/mohammad-ghassemi/python_script.py $SLURM_ARRAY_TASK_ID
```

### 10. Submit your jobs
Now all that's left to do is to execute the `python_script.py` according to the parameters in `slurm_job.sb`. We will do this by creating a third script `execute.sh`:

```
#!/bin/bash

echo '-----------------------------------------------'
echo ' SUBMITTING JOB TO CLUSTER'
echo '-----------------------------------------------'
mkdir python_out
mkdir python_err
rm -r python_out/*
rm -r python_err/*

####################################################
# GET THE SIZE OF THE INPUT DATA (NUMBER OF LINES)
####################################################
INPUT_SIZE=$(wc -l input/input.jsonl | cut -f1 -d' ') 

####################################################
# SEND A BATCH OF DATA
####################################################
sbatch --array=0-$INPUT_SIZE slurm_job.sb 
watch squeue -u $USER
```

### 11. Run your job

```./execute.sh```


#### Additional Resources:
* The MSU HPCC Wiki (https://wiki.hpcc.msu.edu/) is actually very well put together, and contains example scripts and other resources that suggest how to use the cluster.
