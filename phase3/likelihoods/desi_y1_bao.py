"""
DESI Y1 BAO Likelihood for Cobaya
Based on DESI Collaboration arXiv:2404.03002 (Y1 BAO results)

CORRECTED VERSION v2: 
- Properly handles D_V/r_d (BGS, QSO) vs D_M/r_d + D_H/r_d (LRG, ELG, Lya)
- Fixed D_V formula: D_V = [D_M^2 * z * D_H]^(1/3)
"""
import numpy as np
from cobaya.likelihood import Likelihood

class DESI_Y1_BAO(Likelihood):
    """DESI Year 1 BAO likelihood with proper handling of D_V and D_M/D_H measurements."""
    speed = 10
    
    def initialize(self):
        # D_M/r_d and D_H/r_d measurements (anisotropic BAO)
        self.aniso_data = [
            # LRG z=0.51
            {'z': 0.510, 'DM_rd': 13.62, 'DM_err': 0.25, 'DH_rd': 20.98, 'DH_err': 0.61, 'rho': -0.42},
            # LRG z=0.71
            {'z': 0.706, 'DM_rd': 16.85, 'DM_err': 0.32, 'DH_rd': 20.08, 'DH_err': 0.60, 'rho': -0.38},
            # LRG+ELG z=0.93
            {'z': 0.930, 'DM_rd': 21.71, 'DM_err': 0.28, 'DH_rd': 17.88, 'DH_err': 0.35, 'rho': -0.39},
            # ELG z=1.32
            {'z': 1.317, 'DM_rd': 27.79, 'DM_err': 0.69, 'DH_rd': 13.82, 'DH_err': 0.42, 'rho': -0.44},
            # Lya z=2.33
            {'z': 2.330, 'DM_rd': 39.71, 'DM_err': 0.94, 'DH_rd': 8.52, 'DH_err': 0.17, 'rho': -0.48},
        ]
        
        # D_V/r_d measurements (isotropic BAO)
        self.iso_data = [
            # BGS z=0.30
            {'z': 0.295, 'DV_rd': 7.93, 'DV_err': 0.15},
            # QSO z=1.49
            {'z': 1.491, 'DV_rd': 26.07, 'DV_err': 0.67},
        ]
        
        self.log.info(f"DESI Y1 BAO: {len(self.aniso_data)} anisotropic + {len(self.iso_data)} isotropic bins")
    
    def get_requirements(self):
        zs_aniso = [d['z'] for d in self.aniso_data]
        zs_iso = [d['z'] for d in self.iso_data]
        all_zs = sorted(set(zs_aniso + zs_iso))
        return {'angular_diameter_distance': {'z': all_zs}, 'Hubble': {'z': all_zs}, 'rdrag': None}
    
    def logp(self, **params_values):
        provider = self.provider
        rdrag = provider.get_param('rdrag')
        c_km_s = 299792.458
        chi2 = 0.0
        
        # Anisotropic measurements (D_M/r_d and D_H/r_d)
        for d in self.aniso_data:
            z = d['z']
            DA = provider.get_angular_diameter_distance(z)
            H = provider.get_Hubble(z)
            DM = (1 + z) * DA
            DH = c_km_s / H
            DM_rd_theory = DM / rdrag
            DH_rd_theory = DH / rdrag
            
            delta_DM = DM_rd_theory - d['DM_rd']
            delta_DH = DH_rd_theory - d['DH_rd']
            sigma_DM, sigma_DH, rho = d['DM_err'], d['DH_err'], d['rho']
            
            # 2x2 covariance matrix inversion
            det = sigma_DM**2 * sigma_DH**2 * (1 - rho**2)
            chi2 += (delta_DM**2 * sigma_DH**2 + delta_DH**2 * sigma_DM**2 
                     - 2 * rho * sigma_DM * sigma_DH * delta_DM * delta_DH) / det
        
        # Isotropic measurements (D_V/r_d)
        # D_V = [D_M^2 * z * D_H]^(1/3)  <-- CORRECT formula with z factor
        for d in self.iso_data:
            z = d['z']
            DA = provider.get_angular_diameter_distance(z)
            H = provider.get_Hubble(z)
            DM = (1 + z) * DA
            DH = c_km_s / H
            # CORRECT: D_V = [D_M^2 * z * D_H]^(1/3)
            DV = (DM**2 * z * DH)**(1.0/3.0)
            DV_rd_theory = DV / rdrag
            
            delta_DV = DV_rd_theory - d['DV_rd']
            chi2 += (delta_DV / d['DV_err'])**2
        
        return -0.5 * chi2
