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

