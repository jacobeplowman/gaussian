import os
import glob
import csv

# Constants
FARADAY_CONSTANT = 96.485  
SCE_CORRECTION = 4.422  # Shift to SCE reference

def extract_gibbs_free_energy(log_file):
    """Extracts the Gibbs free energy from a Gaussian .log file."""
    try:
        with open(log_file, "r") as f:
            lines = f.readlines()
        
        # Read file in reverse to find the energy quickly
        for line in reversed(lines):
            if "Sum of electronic and thermal Free Energies=" in line:
                energy = float(line.split()[-1])  # Extract energy value
                return energy

    except Exception as e:
        print(f"Error extracting energy from {log_file}: {e}")
        return None
    return None

# Output CSV file
output_file = "oxidation_potentials.csv"

# Write CSV header
with open(output_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Molecule", "Functional", "Basis Set", "Solvent", "Oxidation Potential (V vs SCE)"])

# Find all .log files
log_files = glob.glob("*.log")

# Check if any log files exist
if not log_files:
    print("No .log files found in the current directory.")
    exit()

print(f"Found log files: {log_files}")

# Process each log file
for log_file in log_files:
    if "_cation.log" in log_file:
        base_name = log_file.replace("_cation.log", "")
        neutral_log = base_name + "_neutral.log"

        if not os.path.exists(neutral_log):
            print(f"Skipping {log_file} because neutral state log file {neutral_log} is missing.")
            continue

        # Extract Gibbs Free Energies
        cation_energy = extract_gibbs_free_energy(log_file)
        neutral_energy = extract_gibbs_free_energy(neutral_log)

        if neutral_energy is not None and cation_energy is not None:
            # Convert energy difference to oxidation potential
            delta_G = (cation_energy - neutral_energy) * 2625.5  # Convert Hartrees to kJ/mol
            oxidation_potential = (delta_G / FARADAY_CONSTANT) - SCE_CORRECTION

            # Extract parameters from filename
            # Split the filename and extract fields carefully
            parts = base_name.rsplit("_", 3)  # Splits from the right side, preserving CAS number
            if len(parts) == 4:
                cas_number, functional, basis_set, solvent = parts
            else:
                cas_number, functional, basis_set, solvent = base_name, "Unknown", "Unknown", "Unknown"


            # Append results to CSV
            with open(output_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([cas_number, functional, basis_set, solvent, f"{oxidation_potential:.3f}"])

            print(f"Extracted oxidation potential: {base_name} = {oxidation_potential:.3f} V")
        else:
            print(f"Skipping {log_file} due to missing energy values.")

print(f"All oxidation potentials saved to {output_file}.")
