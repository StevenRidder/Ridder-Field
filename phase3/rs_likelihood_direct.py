import sys
import os
import subprocess
import tempfile

def rs_likelihood(_self=None, theta_i_ridder=None, beta_ridder=None, **params_values):
    try:
        # Create temp .ini file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(f"""
h = 0.72
omega_b = 0.02237
omega_cdm = 0.120
A_s = 2.1e-9
n_s = 0.9649
tau_reio = 0.054

use_scf = yes
scf_tuning_index = 0
attractor_ic_scf = no
scf_parameters = 0.0, 0.0, 0.0, 0.0

Lambda_EDE_ridder = 1.0
f_axion_ridder = 1.0e27
theta_i_ridder = {theta_i_ridder}
beta_ridder = {beta_ridder}
n_ridder = 3

output = tCl
l_max_scalars = 1500
write_background = yes
gauge = newtonian
root = /tmp/class_test_
""")
            ini_file = f.name
        
        # Run CLASS
        result = subprocess.run(
            ['/home/<VM_USER>/Ridder-Field/phase2/class/class', ini_file],
            capture_output=True,
            text=True,
            cwd='/home/<VM_USER>/Ridder-Field/phase2/class'
        )
        
        if result.returncode != 0:
            return -1e10
        
        # Extract rs from background file
        bg_files = [f for f in os.listdir('/tmp') if f.startswith('class_test_') and f.endswith('_background.dat')]
        if not bg_files:
            return -1e10
        
        bg_file = f'/tmp/{bg_files[0]}'
        with open(bg_file, 'r') as bf:
            for line in bf:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 8:
                    try:
                        z = float(parts[0])
                        if 1090 <= z <= 1110:  # Drag epoch
                            rs = float(parts[7])  # rs column
                            # Cleanup
                            os.unlink(ini_file)
                            for f in bg_files:
                                try:
                                    os.unlink(f'/tmp/{f}')
                                except:
                                    pass
                            # Gaussian likelihood
                            return -0.5 * ((rs - 139.06) / 0.5)**2
                    except:
                        continue
        
        return -1e10
    except Exception as e:
        return -1e10
