"""
DES Y3 S8 prior likelihood

Applies a Gaussian prior on S8 = sigma8 * sqrt(Omega_m / 0.3)
DES Y3 3x2pt: S8 = 0.776 ± 0.017
"""

from cobaya.likelihood import Likelihood
import numpy as np


class DES_S8_Prior(Likelihood):
    """Gaussian prior on S8 from DES Y3"""
    
    # DES Y3 values
    S8_mean: float = 0.776
    S8_sigma: float = 0.017
    
    def initialize(self):
        self.log.info(f"DES S8 prior: {self.S8_mean} ± {self.S8_sigma}")
    
    def get_requirements(self):
        return {"sigma8": None, "Omega_m": None}
    
    def logp(self, **params_values):
        sigma8 = self.provider.get_param("sigma8")
        Omega_m = self.provider.get_param("Omega_m")
        S8 = sigma8 * np.sqrt(Omega_m / 0.3)
        
        chi2 = ((S8 - self.S8_mean) / self.S8_sigma) ** 2
        return -0.5 * chi2

