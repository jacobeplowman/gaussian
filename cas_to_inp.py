import requests
import os
import subprocess

def cas_to_smiles(cas_number):
    """Fetches SMILES string from a CAS number using PubChem."""
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{cas_number}/property/CanonicalSMILES/TXT"
    response = requests.get(url)

    if response.status_code == 200:
        smiles = response.text.strip()
        print(f"✅ CAS {cas_number} → SMILES: {smiles}")
        return smiles
    else:
        print(f"❌ CAS {cas_number} not found in PubChem.")
        return None

def smiles_to_xyz(smiles, cas_number):
    """Converts a SMILES string to a 3D optimized XYZ file using OpenBabel CLI."""
    try:
        smi_filename = f"{cas_number}.smi"
        xyz_filename = f"{cas_number}.xyz"

        with open(smi_filename, "w") as smi_file:
            smi_file.write(smiles)

        # Run OpenBabel with force-field optimization
        obabel_command = f"obabel -ismi {smi_filename} -oxyz -h --gen3d -O {xyz_filename}"
        subprocess.run(obabel_command, shell=True, check=True)

        print(f"✅ XYZ file generated: {xyz_filename}")
        return xyz_filename

    except Exception as e:
        print(f"❌ Error generating XYZ for {cas_number}: {e}")
        return None

def xyz_to_gaussian_inp(xyz_filename, cas_number, functional, basis_set, solvent, charge, spin, state):
    """Converts XYZ file into Gaussian input file for Neutral or Cationic species using (U)DFT."""
    try:
        with open(xyz_filename, "r") as xyz_file:
            lines = xyz_file.readlines()

        # Extract atomic coordinates (skip first two lines in XYZ format)
        atom_lines = lines[2:]

        # Generate filenames
        base_name = cas_number.replace("-", "_")
        solvent_clean = solvent.replace("(", "").replace(")", "")

        # Clean basis set name for filenames
        basis_set_clean = basis_set.replace("*", "s").replace("+", "p").replace(",", "").replace("(", "").replace(")", "")

        # Apply unrestricted DFT (UDFT) if spin is >1
        functional_corrected = f"U{functional}" if spin > 1 else functional

        inp_filename = f"{base_name}_{functional_corrected}_{basis_set_clean}_{solvent_clean}_{state}.inp"
        chk_filename = f"{base_name}_{functional_corrected}_{basis_set_clean}_{solvent_clean}_{state}.chk"

        # Gaussian input file content
        gaussian_input = (
            f"%nproc=4\n"
            f"%mem=32GB\n"
            f"%chk={chk_filename}\n"
            f"#p opt freq {functional_corrected}/{basis_set} scf=(tight,xqc,maxcycles=1000) int=ultrafine scrf=(cpcm,solvent={solvent})\n\n"
            f"{base_name}_{functional_corrected}_{basis_set}_{solvent}_{state}\n\n"
            f"{charge} {spin}\n"
            + "".join(atom_lines) + "\n"
        )

        # Save the Gaussian input file
        with open(inp_filename, "w") as inp_file:
            inp_file.write(gaussian_input)

        print(f"✅ Gaussian input file saved: {inp_filename}")

    except Exception as e:
        print(f"❌ Error processing {xyz_filename}: {e}")

# ---- Main Script ----

# Define CAS numbers
cas_numbers = [
    "763-29-1",
    "110-83-8",
    "142-29-0",
    "498-66-8",
    "556-82-1",
    "1000-86-8",
    "513-35-9",
    "100-42-5",
    "13271-10-8",
    "591-49-1"
]

# Define functionals to test
functionals = [
    "B3LYP",       # (U)B3LYP - Popular hybrid functional used in the paper
    #"M06-2X",      # (U)M06-2X - Good for redox reactions (more accurate but slower)
    #"PBE0",        # (U)PBE0 - Hybrid GGA functional (decent balance of speed and accuracy)
    #"ωB97X-D",     # (U)ωB97X-D - Long-range corrected functional with dispersion corrections
    #"CAM-B3LYP",   # (U)CAM-B3LYP - Range-separated hybrid functional
]

# Define basis sets to test
basis_sets = [
    #3-21G*,         # Small basis set for quick calculations
    "6-31+G(d,p)",    # Exact basis set from the paper
    #"Def2SVP",       # Split-valence basis set (alternative)
    #"Def2TZVP",      # Higher accuracy triple-zeta basis set
    #"aug-cc-pVDZ",   # Dunning correlation-consistent basis set
]

# Define solvents to test
solvents = [
    "acetonitrile",  # Common for experimental electrochemistry
]

# Load OpenBabel module (if running on a cluster)
os.system("module load apps/openbabel/3.1.1/gcc-5.5.0+eigen-3.3.0")

# Process each CAS number
for cas_number in cas_numbers:
    smiles = cas_to_smiles(cas_number)
    if smiles:
        xyz_filename = smiles_to_xyz(smiles, cas_number)
        if xyz_filename:
            for functional in functionals:
                for basis_set in basis_sets:
                    for solvent in solvents:
                        # Generate Neutral species input file
                        xyz_to_gaussian_inp(xyz_filename, cas_number, functional, basis_set, solvent, charge=0, spin=1, state="neutral")
                        # Generate Cation species input file
                        xyz_to_gaussian_inp(xyz_filename, cas_number, functional, basis_set, solvent, charge=1, spin=2, state="cation")

print("✅ All Gaussian .inp files have been generated successfully!")
