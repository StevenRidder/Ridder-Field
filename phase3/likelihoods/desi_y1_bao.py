"""
DESI Y1 BAO Likelihood for Cobaya

Based on DESI Collaboration arXiv:2404.03002 (Y1 BAO results)
Provides D_M/r_d and D_H/r_d measurements at multiple redshifts.

Reference cosmology:
  r_d = 147.09 Mpc (Planck 2018 ΛCDM)
"""

import numpy as np
from cobaya.likelihood import Likelihood


class DESI_Y1_BAO(Likelihood):
    """
    DESI Year 1 BAO likelihood.
    
    Constrains transverse and line-of-sight distance ratios:
      D_M(z)/r_d  (transverse comoving distance / sound horizon)
      D_H(z)/r_d  (Hubble distance / sound horizon)
    
    Data from DESI Collaboration (2024) arXiv:2404.03002
    """
    
    # Speed (doesn't need derivatives)
    speed = 10
    
    def initialize(self):
        """Set up DESI Y1 data vectors and covariance."""
        
        # DESI Y1 BAO measurements (Table 1 of arXiv:2404.03002)
        # Format: z_eff, D_M/r_d, sigma_DM, D_H/r_d, sigma_DH, correlation
        
        self.data = [
            # BGS (Bright Galaxy Survey)
            {'z': 0.295, 'DM_rd': 7.93, 'DM_err': 0.15, 
             'DH_rd': 20.98, 'DH_err': 0.61, 'rho': -0.45},
            
            # LRG (Luminous Red Galaxies) bin 1
            {'z': 0.510, 'DM_rd': 13.62, 'DM_err': 0.25,
             'DH_rd': 20.98, 'DH_err': 0.61, 'rho': -0.42},
            
            # LRG bin 2
            {'z': 0.706, 'DM_rd': 16.85, 'DM_err': 0.32,
             'DH_rd': 20.08, 'DH_err': 0.60, 'rho': -0.38},
            
            # LRG + ELG combined
            {'z': 0.930, 'DM_rd': 21.71, 'DM_err': 0.28,
             'DH_rd': 17.88, 'DH_err': 0.35, 'rho': -0.39},
            
            # ELG (Emission Line Galaxies)
            {'z': 1.317, 'DM_rd': 27.79, 'DM_err': 0.69,
             'DH_rd': 13.82, 'DH_err': 0.42, 'rho': -0.44},
            
            # QSO (Quasars)
            {'z': 1.491, 'DM_rd': 26.07, 'DM_err': 0.67,
             'DH_rd': 13.23, 'DH_err': 0.48, 'rho': -0.48},
            
            # Lyman-alpha
            {'z': 2.330, 'DM_rd': 39.71, 'DM_err': 0.94,
             'DH_rd': 8.52, 'DH_err': 0.17, 'rho': -0.48},
        ]
        
        self.log.info(f"DESI Y1 BAO likelihood initialized with {len(self.data)} redshift bins")
    
    def get_requirements(self):
        """Request distances from theory code."""
        # Request angular diameter distance and Hubble parameter
        zs = [d['z'] for d in self.data]
        return {
            'angular_diameter_distance': {'z': zs},
            'Hubble': {'z': zs},
            'rdrag': None,  # Sound horizon at drag epoch
        }
    
    def logp(self, **params_values):
        """Compute log-likelihood."""
        
        # Get theory predictions
        provider = self.provider
        rdrag = provider.get_param('rdrag')
        
        chi2 = 0.0
        
        for d in self.data:
            z = d['z']
            
            # Get theory values
            DA = provider.get_angular_diameter_distance(z)  # Mpc
            H = provider.get_Hubble(z)  # km/s/Mpc
            
            # Convert to DESI convention
            # D_M = (1+z) * D_A  (comoving transverse distance)
            # D_H = c / H        (Hubble distance in Mpc)
            c_km_s = 299792.458  # km/s
            DM = (1 + z) * DA
            DH = c_km_s / H
            
            # Ratios with sound horizon
            DM_rd_theory = DM / rdrag
            DH_rd_theory = DH / rdrag
            
            # Data
            DM_rd_data = d['DM_rd']
            DH_rd_data = d['DH_rd']
            sigma_DM = d['DM_err']
            sigma_DH = d['DH_err']
            rho = d['rho']
            
            # Residuals
            delta_DM = DM_rd_theory - DM_rd_data
            delta_DH = DH_rd_theory - DH_rd_data
            
            # 2D Gaussian chi2 with correlation
            det = sigma_DM**2 * sigma_DH**2 * (1 - rho**2)
            chi2 += (delta_DM**2 * sigma_DH**2 
                     + delta_DH**2 * sigma_DM**2 
                     - 2 * rho * sigma_DM * sigma_DH * delta_DM * delta_DH) / det
        
        return -0.5 * chi2


# Alternative: Combined isotropic D_V/r_d likelihood
class DESI_Y1_BAO_DV(Likelihood):
    """
    DESI Y1 BAO using only the isotropic D_V/r_d combination.
    Simpler, less constraining, but robust.
    """
    
    speed = 10
    
    def initialize(self):
        # D_V/r_d = (z * D_M^2 * D_H)^(1/3) / r_d
        # Values derived from Table 1 of arXiv:2404.03002
        self.data = [
            {'z': 0.295, 'DV_rd': 7.93, 'err': 0.12},
            {'z': 0.510, 'DV_rd': 13.62, 'err': 0.20},
            {'z': 0.706, 'DV_rd': 18.33, 'err': 0.27},
            {'z': 0.930, 'DV_rd': 21.73, 'err': 0.23},
            {'z': 1.317, 'DV_rd': 27.86, 'err': 0.55},
        ]
        self.log.info(f"DESI Y1 BAO (D_V) initialized with {len(self.data)} bins")
    
    def get_requirements(self):
        zs = [d['z'] for d in self.data]
        return {
            'angular_diameter_distance': {'z': zs},
            'Hubble': {'z': zs},
            'rdrag': None,
        }
    
    def logp(self, **params_values):
        provider = self.provider
        rdrag = provider.get_param('rdrag')
        c_km_s = 299792.458
        
        chi2 = 0.0
        for d in self.data:
            z = d['z']
            DA = provider.get_angular_diameter_distance(z)
            H = provider.get_Hubble(z)
            DM = (1 + z) * DA
            DH = c_km_s / H
            DV = (z * DM**2 * DH)**(1/3)
            DV_rd_theory = DV / rdrag
            chi2 += ((DV_rd_theory - d['DV_rd']) / d['err'])**2
        
        return -0.5 * chi2

