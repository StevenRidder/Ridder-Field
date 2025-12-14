import numpy as np

def parse_chain(path):
    with open(path, "r") as f:
        lines = f.readlines()
    
    header = lines[0].strip().split()
    header[0] = header[0].lstrip("#")
    
    data = []
    for line in lines[1:]:
        if line.strip() and not line.startswith("#"):
            vals = line.strip().split()
            data.append([float(v) for v in vals])
    
    data = np.array(data)
    col_idx = {name: i for i, name in enumerate(header)}
    
    return data, col_idx, header

def get_best(data, col_idx, key="chi2"):
    if key not in col_idx:
        key = "minuslogpost"
    idx = col_idx[key]
    best_row_idx = np.argmin(data[:, idx])
    return data[best_row_idx, :]

print("="*70)
print("RIGOROUS CHAIN COMPARISON")
print("="*70)

xi_data, xi_cols, _ = parse_chain("/home/ridderadmin/ridder_v2/late_time/chains/xi_late_desi_v3.1.txt")
lcdm_data, lcdm_cols, _ = parse_chain("/home/ridderadmin/ridder_v2/late_time/chains/lcdm_desi_v3.1.txt")

print(f"\nxi_late chain: {len(xi_data)} samples")
print(f"LCDM chain: {len(lcdm_data)} samples")

xi_best = get_best(xi_data, xi_cols, "chi2")
lcdm_best = get_best(lcdm_data, lcdm_cols, "chi2")

print("\n" + "-"*70)
print("BEST-FIT BY TOTAL CHI2")
print("-"*70)

params = [
    ("chi2", "Total chi2"),
    ("minuslogpost", "minuslogpost"),
    ("H0", "H0"),
    ("omega_cdm", "omega_cdm"),
    ("w0_fld", "w0 (DE)"),
    ("chi2__planck_2018_highl_plik.TTTEEE", "Planck High-l"),
    ("chi2__planck_2018_lowl.TT", "Planck Low-l TT"),
    ("chi2__planck_2018_lowl.EE", "Planck Low-l EE"),
    ("chi2__planck_2018_lensing.clik", "Planck Lensing"),
    ("chi2__bao.desi_2024_bao_all", "DESI BAO"),
    ("chi2__sn.pantheon", "Pantheon SNe"),
]

print("%-35s %15s %15s %15s" % ("Parameter", "xi_late", "LCDM", "Delta"))
print("-"*80)

for col, label in params:
    xi_val = xi_best[xi_cols[col]] if col in xi_cols else None
    lcdm_val = lcdm_best[lcdm_cols[col]] if col in lcdm_cols else None
    
    if xi_val is not None and lcdm_val is not None:
        delta = xi_val - lcdm_val
        print("%-35s %15.4f %15.4f %+15.4f" % (label, xi_val, lcdm_val, delta))
    elif xi_val is not None:
        print("%-35s %15.4f %15s %15s" % (label, xi_val, "N/A", "N/A"))

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

xi_chi2 = xi_best[xi_cols["chi2"]]
lcdm_chi2 = lcdm_best[lcdm_cols["chi2"]]
delta_chi2 = xi_chi2 - lcdm_chi2

print("xi_late chi2 = %.2f" % xi_chi2)
print("LCDM chi2    = %.2f" % lcdm_chi2)
print("Delta chi2   = %+.2f" % delta_chi2)
print()
if delta_chi2 < 0:
    print("*** xi_late WINS by %.2f ***" % abs(delta_chi2))
else:
    print("*** LCDM WINS by %.2f ***" % delta_chi2)

xi_H0 = xi_best[xi_cols["H0"]]
lcdm_H0 = lcdm_best[lcdm_cols["H0"]]
print("\nH0: xi_late=%.2f, LCDM=%.2f" % (xi_H0, lcdm_H0))
if "w0_fld" in xi_cols:
    print("w0: xi_late=%.4f" % xi_best[xi_cols["w0_fld"]])
