/**
 * @file ridder_unified_potential.c
 * 
 * Unified Ridder Potential: One field from inflation to heat death
 * 
 * V(θ) = V_tail(θ) + V_shelf(θ) + V_plateau(θ)
 * 
 * - Tail: Late dark energy (shallow minimum)
 * - Shelf: Early dark energy bump (localized in field space)
 * - Plateau: Inflationary phase (high energy at large |θ|)
 */

#include "background.h"
#include <math.h>

/* ========================================================================= */
/* Helper Functions                                                          */
/* ========================================================================= */

/**
 * Safe tanh function (can add clipping if needed for numerical stability)
 */
static inline double safe_tanh(double x) {
  /* For |x| > 20, tanh saturates to ±1 */
  if (x > 20.0) return 1.0;
  if (x < -20.0) return -1.0;
  return tanh(x);
}

/**
 * Safe sech^2 = 1 - tanh^2 (for derivatives)
 */
static inline double sech_squared(double x) {
  if (fabs(x) > 20.0) return 0.0;
  double t = tanh(x);
  return 1.0 - t * t;
}

/* ========================================================================= */
/* Tail Term: V_tail = Lambda_tail_eV^4 * [1 - cos(theta)]^n_tail              */
/* ========================================================================= */

/**
 * Tail potential (late-time dark energy)
 */
double V_tail_theta(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_tail == _FALSE_) return 0.0;
  
  double one_minus_cos = 1.0 - cos(theta);
  if (one_minus_cos <= 0.0) return 0.0;
  
  double Lambda4 = pow(rp->Lambda_tail_eV, 4.0);
  double base = pow(one_minus_cos, rp->n_tail);
  
  return Lambda4 * base;
}

/**
 * First derivative: dV_tail/dtheta
 */
double dV_tail_dtheta(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_tail == _FALSE_) return 0.0;
  
  double one_minus_cos = 1.0 - cos(theta);
  if (one_minus_cos <= 0.0) return 0.0;
  
  double Lambda4 = pow(rp->Lambda_tail_eV, 4.0);
  double n = rp->n_tail;
  
  /* d/dtheta [1 - cos]^n = n [1 - cos]^(n-1) * sin(theta) */
  double factor = n * pow(one_minus_cos, n - 1.0) * sin(theta);
  
  return Lambda4 * factor;
}

/**
 * Second derivative: d²V_tail/dtheta²
 */
double d2V_tail_dtheta2(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_tail == _FALSE_) return 0.0;
  
  double one_minus_cos = 1.0 - cos(theta);
  double s = sin(theta);
  double c = cos(theta);
  
  if (one_minus_cos <= 0.0) return 0.0;
  
  double Lambda4 = pow(rp->Lambda_tail_eV, 4.0);
  double n = rp->n_tail;
  
  /* Product rule on n [1 - cos]^(n-1) * sin(theta) */
  double term1 = (n - 1.0) * pow(one_minus_cos, n - 2.0) * s * s;
  double term2 = pow(one_minus_cos, n - 1.0) * c;
  
  double d2 = n * (term1 + term2);
  
  return Lambda4 * d2;
}

/* ========================================================================= */
/* Shelf Term: V_shelf = Lambda_EDE^4 * W(theta) * [1-cos(theta)]^n_EDE     */
/* ========================================================================= */

/**
 * Shelf window function: top-hat in theta space using tanh edges
 */
static double W_EDE(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_shelf == _FALSE_) return 0.0;
  
  double x1 = (theta - rp->theta_EDE_low) / rp->sigma_theta_EDE;
  double x2 = (theta - rp->theta_EDE_high) / rp->sigma_theta_EDE;
  
  double t1 = safe_tanh(x1);
  double t2 = safe_tanh(x2);
  
  /* W = 0.5*(1 + tanh(x1)) - 0.5*(1 + tanh(x2)) */
  double W = 0.5 * (1.0 + t1) - 0.5 * (1.0 + t2);
  
  return W;
}

/**
 * Derivative of window function: dW/dtheta
 */
static double dW_EDE_dtheta(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_shelf == _FALSE_) return 0.0;
  
  double x1 = (theta - rp->theta_EDE_low) / rp->sigma_theta_EDE;
  double x2 = (theta - rp->theta_EDE_high) / rp->sigma_theta_EDE;
  
  double sech2_x1 = sech_squared(x1);
  double sech2_x2 = sech_squared(x2);
  
  double dW = 0.5 * sech2_x1 / rp->sigma_theta_EDE 
            - 0.5 * sech2_x2 / rp->sigma_theta_EDE;
  
  return dW;
}

/**
 * Shelf potential (EDE bump)
 * 
 * AxiCLASS form: V = m² f² [1-cos(theta)]^n × W(theta)
 * where m = m_axion × H0, f = f_axion × M_Pl
 */
double V_shelf_theta(double theta, const struct ridder_unified_params *rp) {
  static int shelf_debug_count = 0;
  if (shelf_debug_count < 3) {
    printf("V_SHELF_DEBUG[%d]: theta=%.2e use_shelf=%d m_eV=%.2e f=%.2e f_eV=%.2e\n",
           shelf_debug_count, theta, rp->use_shelf, rp->m_eV, rp->f, rp->f_eV);
    shelf_debug_count++;
  }
  
  if (rp->use_shelf == _FALSE_) return 0.0;
  
  double W = W_EDE(theta, rp);
  if (W <= 0.0) return 0.0;
  
  double one_minus_cos = 1.0 - cos(theta);
  if (one_minus_cos <= 0.0) return 0.0;
  
  /* Hybrid form: use Lambda^4 for scale, m²f² for dynamics */
  /* V = Lambda_EDE^4 * [1-cos]^n when m_eV or f_eV not set */
  /* V = (m_eV * f_eV)^2 * [1-cos]^n / scale when m_eV and f_eV set */
  double V_scale;
  if (rp->m_eV > 1e-20 && rp->f > 1e10) {
    /* m²f² form with normalization to avoid huge values */
    double m2f2 = rp->m_eV * rp->m_eV * rp->f * rp->f;
    V_scale = m2f2 / 1e50;  /* Normalize to cosmological scale */
  } else {
    /* Lambda^4 form */
    V_scale = pow(rp->Lambda_EDE, 4.0);
  }
  double base = pow(one_minus_cos, rp->n_EDE);
  
  return V_scale * W * base;
}

double dV_shelf_dtheta(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_shelf == _FALSE_) return 0.0;
  
  double W = W_EDE(theta, rp);
  double dW = dW_EDE_dtheta(theta, rp);
  
  double one_minus_cos = 1.0 - cos(theta);
  if (one_minus_cos <= 0.0) return 0.0;
  
  double s = sin(theta);
  double n = rp->n_EDE;
  
  /* Use same V_scale logic as V_shelf_theta for consistency */
  double V_scale;
  if (rp->m_eV > 1e-20 && rp->f > 1e10) {
    double m2f2 = rp->m_eV * rp->m_eV * rp->f * rp->f;
    V_scale = m2f2 / 1e50;
  } else {
    V_scale = pow(rp->Lambda_EDE, 4.0);
  }
  
  double base = pow(one_minus_cos, n);
  double dbase = n * pow(one_minus_cos, n - 1.0) * s;
  
  /* Product rule: d(W * base) = dW * base + W * dbase */
  double dV = V_scale * (dW * base + W * dbase);
  
  return dV;
}

/**
 * Second derivative: d²V_shelf/dtheta²
 */
double d2V_shelf_dtheta2(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_shelf == _FALSE_) return 0.0;
  
  double one_minus_cos = 1.0 - cos(theta);
  if (one_minus_cos <= 0.0) return 0.0;
  
  double s = sin(theta);
  double c = cos(theta);
  double n = rp->n_EDE;
  
  /* Use same V_scale logic as V_shelf_theta for consistency */
  double V_scale;
  if (rp->m_eV > 1e-20 && rp->f > 1e10) {
    double m2f2 = rp->m_eV * rp->m_eV * rp->f * rp->f;
    V_scale = m2f2 / 1e50;
  } else {
    V_scale = pow(rp->Lambda_EDE, 4.0);
  }
  
  /* This requires d²W/dtheta² which is complex; simplified version */
  /* For now, use numerical approximation or full analytical expansion */
  /* Full implementation left as TODO for numerical stability */
  
  /* Approximate: ignore W'' term for simplicity in first pass */
  double W = W_EDE(theta, rp);
  double dW = dW_EDE_dtheta(theta, rp);
  
  double base = pow(one_minus_cos, n);
  double dbase = n * pow(one_minus_cos, n - 1.0) * s;
  
  /* d²base/dtheta² */
  double d2base_term1 = (n - 1.0) * pow(one_minus_cos, n - 2.0) * s * s;
  double d2base_term2 = pow(one_minus_cos, n - 1.0) * c;
  double d2base = n * (d2base_term1 + d2base_term2);
  
  /* Product rule: d²(W * base) ≈ W * d²base + 2 * dW * dbase (ignoring d²W) */
  double d2V = V_scale * (W * d2base + 2.0 * dW * dbase);
  
  return d2V;
}

/* ========================================================================= */
/* Plateau Term: V_plateau = Lambda_inf^4 * chi_inf(theta) * F_inf(theta)   */
/* ========================================================================= */

/**
 * Inflation window function: turns on at large |theta|
 */
static double chi_inf(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_plateau == _FALSE_) return 0.0;
  
  double abs_theta = fabs(theta);
  double x = (abs_theta - rp->theta_inf_on) / rp->sigma_inf;
  double t = safe_tanh(x);
  
  return 0.5 * (1.0 + t);
}

/**
 * Plateau shape function: rises smoothly from 0 to constant
 */
static double F_inf(double theta, const struct ridder_unified_params *rp) {
  double theta0 = rp->theta0_inf;
  if (theta0 <= 0.0) return 0.0;
  
  double ratio = theta / theta0;
  double arg = 1.0 + ratio * ratio;
  double root = sqrt(arg);
  
  /* F = sqrt(1 + (theta/theta0)²) - 1 */
  double F = root - 1.0;
  
  return F;
}

/**
 * Plateau potential (inflation)
 */
double V_plateau_theta(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_plateau == _FALSE_) return 0.0;
  
  double chi = chi_inf(theta, rp);
  if (chi <= 0.0) return 0.0;
  
  double F = F_inf(theta, rp);
  double Lambda4 = pow(rp->Lambda_inf, 4.0);
  
  return Lambda4 * chi * F;
}

/**
 * First derivative: dV_plateau/dtheta
 */
double dV_plateau_dtheta(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_plateau == _FALSE_) return 0.0;
  
  double Lambda4 = pow(rp->Lambda_inf, 4.0);
  double chi = chi_inf(theta, rp);
  double F = F_inf(theta, rp);
  
  /* dchi/dtheta */
  double abs_theta = fabs(theta);
  double sign_theta = (theta > 0.0) ? 1.0 : -1.0;
  double x = (abs_theta - rp->theta_inf_on) / rp->sigma_inf;
  double sech2_x = sech_squared(x);
  double dchi = 0.5 * sech2_x * sign_theta / rp->sigma_inf;
  
  /* dF/dtheta = theta / (theta0² * sqrt(1 + (theta/theta0)²)) */
  double theta0 = rp->theta0_inf;
  double ratio = theta / theta0;
  double arg = 1.0 + ratio * ratio;
  double root = sqrt(arg);
  double dF = theta / (theta0 * theta0 * root);
  
  /* Product rule */
  double dV = Lambda4 * (dchi * F + chi * dF);
  
  return dV;
}

/**
 * Second derivative: d²V_plateau/dtheta²
 */
double d2V_plateau_dtheta2(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_plateau == _FALSE_) return 0.0;
  
  /* Simplified implementation - full version TODO */
  /* For slow-roll, V and V' are most critical; V'' can be approximate */
  
  return 0.0;  /* Placeholder */
}

/* ========================================================================= */
/* Total Unified Potential: Sum of all three terms                          */
/* ========================================================================= */

/**
 * Total potential: V(θ) = V_tail + V_shelf + V_plateau
 */
double V_unified_theta(double theta, const struct ridder_unified_params *rp) {
  static int call_count = 0;
  double V = 0.0;
  
  double V_tail_val = 0.0, V_shelf_val = 0.0, V_plateau_val = 0.0;
  
  if (rp->use_tail)    { V_tail_val = V_tail_theta(theta, rp); V += V_tail_val; }
  if (rp->use_shelf)   { V_shelf_val = V_shelf_theta(theta, rp); V += V_shelf_val; }
  if (rp->use_plateau) { V_plateau_val = V_plateau_theta(theta, rp); V += V_plateau_val; }
  
  /* Debug: print every 1000 calls */
  if (call_count % 1000 == 0) {
    printf("V_UNIFIED_DEBUG [call %d]: theta=%e, use_tail=%d, use_shelf=%d, use_plateau=%d\n",
           call_count, theta, rp->use_tail, rp->use_shelf, rp->use_plateau);
    printf("  V_tail=%e, V_shelf=%e, V_plateau=%e, V_total=%e\n",
           V_tail_val, V_shelf_val, V_plateau_val, V);
  }
  call_count++;
  
  return V;
}

/**
 * First derivative: dV/dtheta
 */
double dV_unified_dtheta(double theta, const struct ridder_unified_params *rp) {
  double dV = 0.0;
  
  if (rp->use_tail)    dV += dV_tail_dtheta(theta, rp);
  if (rp->use_shelf)   dV += dV_shelf_dtheta(theta, rp);
  if (rp->use_plateau) dV += dV_plateau_dtheta(theta, rp);
  
  return dV;
}

/**
 * Second derivative: d²V/dtheta²
 */
double d2V_unified_dtheta2(double theta, const struct ridder_unified_params *rp) {
  double d2V = 0.0;
  
  if (rp->use_tail)    d2V += d2V_tail_dtheta2(theta, rp);
  if (rp->use_shelf)   d2V += d2V_shelf_dtheta2(theta, rp);
  if (rp->use_plateau) d2V += d2V_plateau_dtheta2(theta, rp);
  
  return d2V;
}

/* ========================================================================= */
/* Conversion to phi derivatives (for CLASS integration)                    */
/* ========================================================================= */

/**
 * Compute potential and derivatives in terms of phi
 * 
 * @param phi Physical field value
 * @param V Output: V(phi)
 * @param dV_dphi Output: dV/dphi
 * @param d2V_dphi2 Output: d²V/dphi²
 * @param rp Unified potential parameters
 * @return SUCCESS or FAILURE
 */
int ridder_unified_potential_and_derivatives(
    double phi,
    double *V,
    double *dV_dphi,
    double *d2V_dphi2,
    const struct ridder_unified_params *rp) {
  
  /* Convert phi to theta */
  double theta = phi / rp->f;
  
  /* Compute in theta space */
  double V_theta = V_unified_theta(theta, rp);
  double dV_dtheta = dV_unified_dtheta(theta, rp);
  double d2V_dtheta2 = d2V_unified_dtheta2(theta, rp);
  
  /* Convert derivatives: chain rule */
  /* dphi = f * dtheta, so d/dphi = (1/f) * d/dtheta */
  *V = V_theta;
  *dV_dphi = dV_dtheta / rp->f;
  *d2V_dphi2 = d2V_dtheta2 / (rp->f * rp->f);
  
  return _SUCCESS_;
}

