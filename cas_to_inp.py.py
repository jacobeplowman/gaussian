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
        # Save SMILES to a .smi file
        smi_filename = f"{cas_number}.smi"
        xyz_filename = f"{cas_number}.xyz"
        
        with open(smi_filename, "w") as smi_file:
            smi_file.write(smiles)

        # Run OpenBabel to generate .xyz file
        obabel_command = f"obabel -ismi {smi_filename} -oxyz -h --gen3d -O {xyz_filename}"
        subprocess.run(obabel_command, shell=True, check=True)

        print(f"✅ XYZ file generated: {xyz_filename}")
        return xyz_filename

    except Exception as e:
        print(f"❌ Error generating XYZ for {cas_number}: {e}")
        return None

def xyz_to_gaussian_inp(xyz_filename, cas_number, functional, basis_set, solvent):
    """Converts XYZ file into Gaussian input file."""
    try:
        with open(xyz_filename, "r") as xyz_file:
            lines = xyz_file.readlines()

        # Extract atomic coordinates (skip first two lines in XYZ format)
        atom_lines = lines[2:]

        # Generate filenames
        base_name = cas_number.replace("-", "_")
        solvent_clean = solvent.replace("(", "").replace(")", "")
        inp_filename = f"{base_name}_{functional}_{basis_set.replace('*', 's')}_{solvent_clean}.inp"
        chk_filename = f"{base_name}_{functional}_{basis_set.replace('*', 's')}_{solvent_clean}.chk"

        # Gaussian input file content
        gaussian_input = (
            f"%nproc=4\n"
            f"%mem=16GB\n"
            f"%chk={chk_filename}\n"
            f"#p opt freq {functional}/{basis_set} int=ultrafine scrf=(cpcm,solvent={solvent})\n\n"
            f"{base_name}_{functional}_{basis_set}_{solvent}\n\n"
            f"0 1\n"
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
    "142-29-0"
]

# Define functionals to test
functionals = [
    "B3LYP",      # Popular hybrid functional
    #"PBE0",       # Hybrid GGA functional
    #"M06-2X",     # Good for redox reactions
    #"ωB97X-D"     # Long-range corrected with dispersion
]

# Define basis sets to test
basis_sets = [
    "3-21G*",     # Small basis set for quick testing
    #"6-31G(d)",   # Standard Pople basis set
    #"Def2SVP",    # Split-valence basis set from Karlsruhe
    #"Def2TZVP"    # Triple-zeta valence with polarization
]


# Define solvents to test (Gaussian supported solvent names)
solvents = [
    #"water",         # Aqueous redox reactions
    "acetonitrile",  # Common for experimental electrochemistry
    #"methanol"       # Polar solvent alternative
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
                        xyz_to_gaussian_inp(xyz_filename, cas_number, functional, basis_set, solvent)

print("✅ All Gaussian .inp files have been generated successfully!")
