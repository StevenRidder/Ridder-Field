/**
 * ridder_v3_potential.c
 * 
 * V3 CANONICAL UNIFIED POTENTIAL
 * 
 * V(phi, a) = V_floor + V_EDE(theta, a) + V_tail(theta)
 * 
 * where:
 *   V_floor = Lambda_floor^4  (constant)
 * 
 *   V_EDE(theta, a) = Lambda_EDE^4 * S(a; a_c, sigma_lna) * B(theta; theta_E, n_EDE)
 *     S(a) = exp[-(ln a - ln a_c)^2 / (2*sigma_lna^2)]  (time window)
 *     B(theta) = [1 - cos(theta - theta_E)]^n_EDE       (field bump)
 * 
 *   V_tail(theta) = Lambda_tail^4 * [1 + alpha_tail * (1 - cos(theta))^n_tail]
 * 
 * This is the frozen v3 canon. Do not modify without updating V3_COMPLETE_SPEC.md.
 */

#include "background.h"
#include <math.h>

/* Helper to get scale factor from background pointer */
static double get_scale_factor(struct background *pba) {
  /* This will be passed from background.c - for now assume stored in pba */
  /* In actual integration, 'a' will be passed as a parameter */
  return 1.0; /* Placeholder - will be fixed when integrating with background.c */
}

/* ======================================================================== */
/* EDE BUMP (Time and field windowed)                                       */
/* ======================================================================== */

/**
 * Time window S(a; a_c, sigma_lna)
 * Gaussian in log(a) space centered at a_c
 */
static double S_time_window(double a, double a_c, double sigma_lna) {
  if (a_c <= 0.0 || sigma_lna <= 0.0) return 0.0;
  
  double ln_a = log(a);
  double ln_a_c = log(a_c);
  double delta_ln_a = ln_a - ln_a_c;
  
  /* Early return for very far from peak - avoids tiny nonzero values */
  double exponent = -0.5 * (delta_ln_a * delta_ln_a) / (sigma_lna * sigma_lna);
  if (exponent < -25.0) return 0.0;  /* exp(-25) ~ 1e-11, negligible */
  
  return exp(exponent);
}

/**
 * Field bump B(theta; theta_E, n_EDE)
 * Cosine-based bump centered at theta_E
 */
static double B_field_bump(double theta, double theta_E, double n_EDE) {
  double delta_theta = theta - theta_E;
  double one_minus_cos = 1.0 - cos(delta_theta);
  if (one_minus_cos < 0.0) one_minus_cos = 0.0;
  
  return pow(one_minus_cos, n_EDE);
}

/**
 * V_EDE(theta, a) = Lambda_EDE^4 * S(a) * B(theta)
 */
static double V_EDE_v3(double theta, double a, const struct ridder_unified_params *rp) {
  if (!rp->use_EDE) return 0.0;
  if (rp->Lambda_EDE_eV <= 0.0) return 0.0;  /* Guard against zero Lambda */
  
  double S = S_time_window(a, rp->a_c, rp->sigma_lna);
  if (S < 1e-50) return 0.0;  /* Return zero when time window is negligible */
  
  double Lambda4 = pow(rp->Lambda_EDE_eV, 4.0);
  double B = B_field_bump(theta, rp->theta_E_center, rp->n_EDE);
  
  double V = Lambda4 * S * B;
  
  /* Guard against numerical issues */
  if (!isfinite(V)) return 0.0;
  
  return V;
}

static double dV_EDE_dtheta_v3(double theta, double a, const struct ridder_unified_params *rp) {
  if (!rp->use_EDE) return 0.0;
  if (rp->Lambda_EDE_eV <= 0.0) return 0.0;
  
  /* Time window S(a) - must be included in derivative! */
  double S = S_time_window(a, rp->a_c, rp->sigma_lna);
  if (S < 1e-50) return 0.0;  /* Return zero when time window is negligible */
  
  double Lambda4 = pow(rp->Lambda_EDE_eV, 4.0);
  
  /* Field bump derivative: d/dtheta of B(theta) = (1 - cos(theta - theta_E))^n */
  double delta_theta = theta - rp->theta_E_center;
  double one_minus_cos = 1.0 - cos(delta_theta);
  if (one_minus_cos < 0.0) one_minus_cos = 0.0;
  double s = sin(delta_theta);
  double n = rp->n_EDE;
  
  /* dB/dtheta = n * (1 - cos)^(n-1) * sin(delta_theta) */
  double dB_dtheta = 0.0;
  if (one_minus_cos > 1e-20 && n > 0.0) {
    dB_dtheta = n * pow(one_minus_cos, n - 1.0) * s;
  }
  
  double dV = Lambda4 * S * dB_dtheta;
  if (!isfinite(dV)) return 0.0;
  
  return dV;
}

static double d2V_EDE_dtheta2_v3(double theta, double a, const struct ridder_unified_params *rp) {
  if (!rp->use_EDE) return 0.0;
  if (rp->Lambda_EDE_eV <= 0.0) return 0.0;
  
  /* Time window S(a) - must be included in derivative! */
  double S = S_time_window(a, rp->a_c, rp->sigma_lna);
  if (S < 1e-50) return 0.0;  /* Return zero when time window is negligible */
  
  double Lambda4 = pow(rp->Lambda_EDE_eV, 4.0);
  
  /* Field bump second derivative: d2/dtheta2 of B(theta) = (1 - cos(theta - theta_E))^n */
  double delta_theta = theta - rp->theta_E_center;
  double one_minus_cos = 1.0 - cos(delta_theta);
  if (one_minus_cos < 0.0) one_minus_cos = 0.0;
  double s = sin(delta_theta);
  double c = cos(delta_theta);
  double n = rp->n_EDE;
  
  /* d2B/dtheta2 = n*(n-1)*(1-cos)^(n-2)*sin^2 + n*(1-cos)^(n-1)*cos */
  double d2B_dtheta2 = 0.0;
  if (one_minus_cos > 1e-20 && n >= 1.0) {
    if (n >= 2.0) {
      double term1 = n * (n - 1.0) * pow(one_minus_cos, n - 2.0) * s * s;
      double term2 = n * pow(one_minus_cos, n - 1.0) * c;
      d2B_dtheta2 = term1 + term2;
    } else {
      /* n = 1 case */
      d2B_dtheta2 = c;
    }
  }
  
  double d2V = Lambda4 * S * d2B_dtheta2;
  if (!isfinite(d2V)) return 0.0;
  
  return d2V;
}

/* ======================================================================== */
/* TAIL (late-time quintessence with constant floor)                        */
/* ======================================================================== */

static double V_tail_v3(double theta, const struct ridder_unified_params *rp) {
  if (!rp->use_tail) return 0.0;
  if (rp->Lambda_tail_eV <= 0.0) return 0.0;  /* Guard against zero Lambda */
  
  double Lambda4 = pow(rp->Lambda_tail_eV, 4.0);
  
  /* Modulation around theta_T_center */
  double delta_theta = theta - rp->theta_T_center;
  double one_minus_cos = 1.0 - cos(delta_theta);
  if (one_minus_cos < 0.0) one_minus_cos = 0.0;
  
  double modulation = pow(one_minus_cos, rp->n_tail);
  
  /* V_tail = Lambda^4 * [1 + alpha * modulation] */
  double V = Lambda4 * (1.0 + rp->alpha_tail * modulation);
  
  /* Guard against numerical issues */
  if (!isfinite(V)) return Lambda4;  /* Return base value if modulation is bad */
  
  return V;
}

static double dV_tail_dtheta_v3(double theta, const struct ridder_unified_params *rp) {
  if (!rp->use_tail) return 0.0;
  
  double Lambda4 = pow(rp->Lambda_tail_eV, 4.0);
  double delta_theta = theta - rp->theta_T_center;
  double one_minus_cos = 1.0 - cos(delta_theta);
  if (one_minus_cos < 0.0) one_minus_cos = 0.0;
  
  double s = sin(delta_theta);
  double n = rp->n_tail;
  
  /* d/dtheta [1 - cos(delta_theta)]^n = n * [1 - cos]^(n-1) * sin(delta_theta) */
  double dmodulation = (one_minus_cos > 1e-30) ? n * pow(one_minus_cos, n - 1.0) * s : 0.0;
  
  return Lambda4 * rp->alpha_tail * dmodulation;
}

static double d2V_tail_dtheta2_v3(double theta, const struct ridder_unified_params *rp) {
  if (!rp->use_tail) return 0.0;
  
  double Lambda4 = pow(rp->Lambda_tail_eV, 4.0);
  double delta_theta = theta - rp->theta_T_center;
  double one_minus_cos = 1.0 - cos(delta_theta);
  if (one_minus_cos < 0.0) one_minus_cos = 0.0;
  
  double s = sin(delta_theta);
  double c = cos(delta_theta);
  double n = rp->n_tail;
  
  double d2modulation = 0.0;
  if (one_minus_cos > 1e-30) {
    double term1 = n * (n - 1.0) * pow(one_minus_cos, n - 2.0) * s * s;
    double term2 = n * pow(one_minus_cos, n - 1.0) * c;
    d2modulation = term1 + term2;
  }
  
  return Lambda4 * rp->alpha_tail * d2modulation;
}

/* ======================================================================== */
/* CONSTANT FLOOR (optional)                                                */
/* ======================================================================== */

static double V_floor_v3(const struct ridder_unified_params *rp) {
  if (!rp->use_floor) return 0.0;
  return pow(rp->Lambda_floor_eV, 4.0);
}

/* Derivatives of constant are zero */
static double dV_floor_dtheta_v3(const struct ridder_unified_params *rp) {
  (void)rp; /* unused */
  return 0.0;
}

static double d2V_floor_dtheta2_v3(const struct ridder_unified_params *rp) {
  (void)rp; /* unused */
  return 0.0;
}

/* ======================================================================== */
/* TOTAL V3 POTENTIAL                                                       */
/* ======================================================================== */

/**
 * V3 unified potential in theta space
 * 
 * V(theta) = V_floor + V_EDE(theta) + V_tail(theta)
 */
double ridder_V_v3_theta(double theta, double a, const struct ridder_unified_params *rp) {
  double V = 0.0;
  
  V += V_floor_v3(rp);
  V += V_EDE_v3(theta, a, rp);
  V += V_tail_v3(theta, rp);
  
  return V;
}

/**
 * First derivative dV/dtheta
 */
double ridder_dV_v3_dtheta(double theta, double a, const struct ridder_unified_params *rp) {
  double dV = 0.0;
  
  dV += dV_floor_dtheta_v3(rp);
  dV += dV_EDE_dtheta_v3(theta, a, rp);  /* Pass a for time window */
  dV += dV_tail_dtheta_v3(theta, rp);
  
  return dV;
}

/**
 * Second derivative d2V/dtheta2
 */
double ridder_d2V_v3_dtheta2(double theta, double a, const struct ridder_unified_params *rp) {
  double d2V = 0.0;
  
  d2V += d2V_floor_dtheta2_v3(rp);
  d2V += d2V_EDE_dtheta2_v3(theta, a, rp);  /* Pass a for time window */
  d2V += d2V_tail_dtheta2_v3(theta, rp);
  
  return d2V;
}

/**
 * Convert from theta-space to phi-space
 * 
 * V(phi) = V(theta) where theta = phi / f
 * dV/dphi = (dV/dtheta) * (dtheta/dphi) = (dV/dtheta) / f
 * d2V/dphi2 = (d2V/dtheta2) / f^2
 */
int ridder_potential_v3(
    double phi, double a, 
    double *V, 
    double *dV_dphi, 
    double *d2V_dphi2,
    const struct ridder_unified_params *rp
) {
  double f = rp->f_eV;
  if (f <= 0.0) {
    *V = 0.0;
    *dV_dphi = 0.0;
    *d2V_dphi2 = 0.0;
    return 0; /* error: invalid f */
  }
  
  double theta = phi / f;
  
  double V_theta = ridder_V_v3_theta(theta, a, rp);
  double dV_dtheta = ridder_dV_v3_dtheta(theta, a, rp);
  double d2V_dtheta2 = ridder_d2V_v3_dtheta2(theta, a, rp);
  
  static int v3_pot_count = 0;
  if (v3_pot_count < 5) {
    printf("V3_POT: a=%.3e theta=%.2f V_theta=%.3e Lambda_EDE=%.3e\n",
           a, theta, V_theta, rp->Lambda_EDE_eV);
    v3_pot_count++;
  }
  
  *V = V_theta;
  *dV_dphi = dV_dtheta / f;
  *d2V_dphi2 = d2V_dtheta2 / (f * f);
  
  return 1; /* success */
}

