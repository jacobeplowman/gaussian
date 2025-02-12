#!/bin/bash -l
# Use the current working directory
#SBATCH -D ./
# Use the current environment for this job.
#SBATCH --export=ALL
# Define job name
#SBATCH -J gaussian_batch
# Define a standard output file
#SBATCH -o g16-%j.out
# Define a standard error file
#SBATCH -e g16-%j.err
# Request the partition
#SBATCH -p nodes
# Request the number of nodes
#SBATCH -N 2
# Request the number of cores
#SBATCH -n 4
# Set time limit (adjust as needed)
#SBATCH -t 1-23:59:00
# Specify memory per core
#SBATCH --mem-per-cpu=10000M
# Insert your own username to get e-mail notifications
#SBATCH --mail-user=usernamenotneeded@liverpool.ac.uk
# Notify user by email when certain event types occur
#SBATCH --mail-type=ALL
#
# Set your maximum stack size to unlimited
ulimit -s unlimited

# Load GAUSSIAN module
module load apps/gaussian/16
# List all modules
module list

# Set Gaussian scratch directory
export GAUSS_SCRDIR=$TMPDIR
. $g16root/g16/bsd/g16.profile

echo "========================================================="
echo "SLURM job: submitted at $(date)"
date_start=$(date +%s)

echo "Hostname: $(hostname)"
echo "Job ID: $SLURM_JOB_ID"
echo "Number of nodes: $SLURM_JOB_NUM_NODES"
echo "Number of tasks: $SLURM_NTASKS"
echo "========================================================="

# Loop through all .inp files in the current directory
for inp_file in *.inp; do
    if [[ -f "$inp_file" ]]; then
        log_file="${inp_file%.inp}.log"
        echo "Running Gaussian on: $inp_file"
        g16 < "$inp_file" > "$log_file"
        echo "? Completed: $inp_file -> $log_file"
    else
        echo "?? No .inp files found in the directory."
    fi
done

echo "========================================================="
date_end=$(date +%s)
seconds=$((date_end - date_start))
minutes=$((seconds / 60))
seconds=$((seconds - 60 * minutes))
hours=$((minutes / 60))
minutes=$((minutes - 60 * hours))
echo "SLURM job finished at $(date)"
echo "Total run time: $hours Hours $minutes Minutes $seconds Seconds"
echo "========================================================="
exit 0
