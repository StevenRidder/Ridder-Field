"""
Template Injector Theory Component

This is a Cobaya Theory class that wraps the Cl computation and adds A_sh × T_ℓ.
It sits between CLASS and the likelihoods, modifying the Cl's before they're used.

Usage in config:
  theory:
    template_injector.TemplateInjector:
      template_file: /path/to/template.npz
    classy:
      extra_args: ...
"""

import numpy as np
from cobaya.theory import Theory
import os


class TemplateInjector(Theory):
    """
    Theory component that modifies Cl's by adding A_sh × T_ℓ.
    
    Requires Cl from classy, adds the template, and provides modified Cl to likelihoods.
    """
    
    # Template file
    template_file: str = "/home/azureuser/Ridder-Field/phase4/likelihoods/damping_tail_template.npz"
    
    # ℓ range for injection
    ell_min: int = 600
    ell_max: int = 2500
    
    def initialize(self):
        """Load the template."""
        if os.path.exists(self.template_file):
            data = np.load(self.template_file)
            self.T_ell = data["ell"].astype(int)
            self.T_tt = data["T_tt"]
            self.T_te = data["T_te"]
            self.T_ee = data["T_ee"]
            self.lmax_template = len(self.T_tt) - 1
            self.log.info(f"Template Injector: loaded template ℓ = 0 to {self.lmax_template}")
            self.log.info(f"Injection range: ℓ = {self.ell_min} to {self.ell_max}")
        else:
            raise FileNotFoundError(f"Template not found: {self.template_file}")
    
    def get_requirements(self):
        """Request Cl from classy."""
        return {"Cl": {"tt": self.ell_max + 100, "te": self.ell_max + 100, "ee": self.ell_max + 100}}
    
    def must_provide(self, **requirements):
        """We provide modified Cl."""
        # We intercept Cl requests and provide our modified version
        return requirements
    
    def get_Cl(self, ell_factor=False, units="FIRASmuK2"):
        """
        Return Cl with template injection.
        
        This overrides the provider's get_Cl to inject A_sh × T_ℓ.
        """
        # Get unmodified Cl from classy
        cl = self.provider.get_Cl(ell_factor=ell_factor, units=units)
        
        # Get A_sh from current parameter values
        A_sh = self.provider.get_param("A_sh")
        
        if A_sh == 0:
            return cl  # No modification needed
        
        # Make copies to avoid modifying cached values
        cl_mod = {}
        for key in cl:
            cl_mod[key] = cl[key].copy() if hasattr(cl[key], 'copy') else cl[key]
        
        # Inject template in the ACT range
        for ell in range(self.ell_min, min(self.ell_max + 1, len(cl_mod.get("tt", [])), self.lmax_template + 1)):
            # The template is in raw Cl units (not ell-factored)
            # We need to match the units of what we're modifying
            
            if ell_factor:
                # cl is ℓ(ℓ+1)Cl/2π, template is raw Cl
                factor = ell * (ell + 1) / (2 * np.pi)
            else:
                factor = 1.0
            
            if "tt" in cl_mod and ell < len(cl_mod["tt"]):
                cl_mod["tt"][ell] += A_sh * self.T_tt[ell] * factor
            if "te" in cl_mod and ell < len(cl_mod["te"]):
                cl_mod["te"][ell] += A_sh * self.T_te[ell] * factor
            if "ee" in cl_mod and ell < len(cl_mod["ee"]):
                cl_mod["ee"][ell] += A_sh * self.T_ee[ell] * factor
        
        return cl_mod
    
    def calculate(self, state, want_derived=True, **params_values):
        """Store A_sh for use in get_Cl."""
        state["A_sh"] = params_values.get("A_sh", 0.0)
    
    def get_param(self, p):
        """Provide A_sh to other components."""
        if p == "A_sh":
            return self.current_state.get("A_sh", 0.0)
        return None

