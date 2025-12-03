/**
 * @file ridder_shooting_solver.c
 * @brief Shooting mechanism to calibrate m_axion for target f_EDE at z_c
 * 
 * Implements AxiCLASS-style shooting to find m_axion that produces
 * desired EDE fraction at specified redshift.
 */

#include "background.h"

/**
 * Forward declaration of background solver (will be called during shooting)
 */
int background_solve_for_shooting(
  struct precision *ppr,
  struct background *pba,
  double m_axion_test,
  double *f_EDE_result,
  double *z_peak_result
);

/**
 * Compute f_ridder at a specific redshift from background table
 */
static int get_f_ridder_at_z(
  struct background *pba,
  double z_target,
  double *f_ridder_out
) {
  int index_z;
  double *pvecback;
  int last_index;
  
  /* Allocate vector for background quantities */
  pvecback = malloc(pba->bg_size * sizeof(double));
  
  /* Find background at target redshift */
  if (background_at_z(pba, z_target, normal_info, inter_normal, &last_index, pvecback) == _FAILURE_) {
    free(pvecback);
    return _FAILURE_;
  }
  
  /* Extract f_ridder */
  if (pba->has_ridder == _TRUE_) {
    double rho_ridder = pvecback[pba->index_bg_rho_ridder];
    double rho_crit = pvecback[pba->index_bg_rho_crit];
    *f_ridder_out = rho_ridder / rho_crit;
  } else {
    *f_ridder_out = 0.0;
  }
  
  free(pvecback);
  return _SUCCESS_;
}

/**
 * Find peak f_ridder and corresponding redshift in background table
 */
static int find_f_ridder_peak(
  struct background *pba,
  double z_min,
  double z_max,
  double *f_peak_out,
  double *z_peak_out
) {
  int i_z;
  double z, f_ridder, f_max;
  double z_at_max;
  int n_samples;
  
  f_max = 0.0;
  z_at_max = 0.0;
  
  /* Sample redshift range logarithmically */
  n_samples = 1000;
  for (i_z = 0; i_z < n_samples; i_z++) {
    /* Log spacing between z_min and z_max */
    double log_z = log(z_min) + (log(z_max) - log(z_min)) * i_z / (n_samples - 1.0);
    z = exp(log_z);
    
    if (get_f_ridder_at_z(pba, z, &f_ridder) == _SUCCESS_) {
      if (f_ridder > f_max) {
        f_max = f_ridder;
        z_at_max = z;
      }
    }
  }
  
  *f_peak_out = f_max;
  *z_peak_out = z_at_max;
  
  return _SUCCESS_;
}

/**
 * Main shooting solver: bisect on m_axion to hit f_EDE target at z_c
 */
int ridder_shoot_for_fEDE(
  struct precision *ppr,
  struct background *pba,
  char errmsg[_MAX_LENGTH_]
) {
  double m_low, m_high, m_mid;
  double f_low, f_high, f_mid;
  double z_peak_low, z_peak_high, z_peak_mid;
  int iteration;
  double f_target, z_target;
  double tolerance;
  int max_iter;
  
  /* Extract shooting parameters */
  f_target = pba->ridder_unified.f_EDE_target;
  z_target = pba->ridder_unified.z_c_target;
  m_low = pba->ridder_unified.shooting_m_min;
  m_high = pba->ridder_unified.shooting_m_max;
  tolerance = pba->ridder_unified.shooting_tolerance;
  max_iter = pba->ridder_unified.shooting_max_iterations;
  
  printf("\n========================================\n");
  printf("RIDDER SHOOTING: Finding m_axion for f_EDE = %.4f at z_c = %.1f\n", f_target, z_target);
  printf("  Initial bracket: m_axion ∈ [%.2e, %.2e] H0\n", m_low, m_high);
  printf("  f_axion = %.4f M_Pl (fixed)\n", pba->ridder_unified.f_axion);
  printf("  theta_i = %.4f (fixed)\n", pba->theta_i_ridder);
  printf("  Tolerance: %.2e\n", tolerance);
  printf("========================================\n");
  
  /* Evaluate f_EDE at bracket endpoints */
  printf("\nEvaluating lower bracket...\n");
  if (background_solve_for_shooting(ppr, pba, m_low, &f_low, &z_peak_low) == _FAILURE_) {
    class_stop(errmsg, "Shooting failed: background_solve failed for m_low = %.2e", m_low);
  }
  printf("  m = %.2e H0 → f_EDE = %.4f at z_peak = %.1f\n", m_low, f_low, z_peak_low);
  
  printf("\nEvaluating upper bracket...\n");
  if (background_solve_for_shooting(ppr, pba, m_high, &f_high, &z_peak_high) == _FAILURE_) {
    class_stop(errmsg, "Shooting failed: background_solve failed for m_high = %.2e", m_high);
  }
  printf("  m = %.2e H0 → f_EDE = %.4f at z_peak = %.1f\n", m_high, f_high, z_peak_high);
  
  /* Check that target is bracketed */
  if ((f_low - f_target) * (f_high - f_target) > 0.0) {
    class_stop(errmsg,
               "Shooting failed: target f_EDE = %.4f not bracketed by [%.4f, %.4f]. "
               "Adjust shooting_m_min/max.",
               f_target, f_low, f_high);
  }
  
  /* Bisection loop */
  printf("\nStarting bisection...\n");
  for (iteration = 1; iteration <= max_iter; iteration++) {
    /* Midpoint */
    m_mid = 0.5 * (m_low + m_high);
    
    /* Evaluate f_EDE at midpoint */
    if (background_solve_for_shooting(ppr, pba, m_mid, &f_mid, &z_peak_mid) == _FAILURE_) {
      class_stop(errmsg, "Shooting iteration %d failed: background_solve failed for m = %.2e",
                 iteration, m_mid);
    }
    
    printf("  [%2d] m = %.4e H0 → f_EDE = %.5f (Δ = %+.2e) at z = %.1f\n",
           iteration, m_mid, f_mid, f_mid - f_target, z_peak_mid);
    
    /* Check convergence */
    if (fabs(f_mid - f_target) < tolerance) {
      printf("\n✅ SHOOTING CONVERGED!\n");
      printf("  Final m_axion = %.6e H0\n", m_mid);
      printf("  Final f_EDE = %.6f (target: %.6f)\n", f_mid, f_target);
      printf("  Peak at z = %.2f\n", z_peak_mid);
      printf("========================================\n\n");
      
      /* Set final m_axion */
      pba->ridder_unified.m_axion = m_mid;
      
      /* Recompute m_eV and f_eV */
      double M_Pl_eV = 2.435e27;
      pba->ridder_unified.m_eV = pba->ridder_unified.m_axion * pba->H0 * 1e5 / _c_;
      pba->ridder_unified.f_eV = pba->ridder_unified.f_axion * M_Pl_eV;
      
      return _SUCCESS_;
    }
    
    /* Update bracket */
    if ((f_mid - f_target) * (f_low - f_target) < 0.0) {
      /* Root is between m_low and m_mid */
      m_high = m_mid;
      f_high = f_mid;
      z_peak_high = z_peak_mid;
    } else {
      /* Root is between m_mid and m_high */
      m_low = m_mid;
      f_low = f_mid;
      z_peak_low = z_peak_mid;
    }
  }
  
  /* Max iterations reached */
  class_stop(errmsg,
             "Shooting did not converge after %d iterations. "
             "Final Δf = %.2e (tolerance: %.2e)",
             max_iter, f_mid - f_target, tolerance);
  
  return _FAILURE_;
}

/**
 * Helper: Run background_solve with temporary m_axion value for shooting
 */
int background_solve_for_shooting(
  struct precision *ppr,
  struct background *pba,
  double m_axion_test,
  double *f_EDE_result,
  double *z_peak_result
) {
  /* Save original m_axion */
  double m_axion_original = pba->ridder_unified.m_axion;
  
  /* Set test value */
  pba->ridder_unified.m_axion = m_axion_test;
  
  /* Recompute m_eV */
  pba->ridder_unified.m_eV = m_axion_test * pba->H0 * 1e5 / _c_;
  
  /* Run background solver */
  if (background_solve(ppr, pba) == _FAILURE_) {
    /* Restore original and return failure */
    pba->ridder_unified.m_axion = m_axion_original;
    return _FAILURE_;
  }
  
  /* Find peak f_ridder */
  double z_min = pba->ridder_unified.z_c_target / 10.0;  /* Search around z_c */
  double z_max = pba->ridder_unified.z_c_target * 10.0;
  if (find_f_ridder_peak(pba, z_min, z_max, f_EDE_result, z_peak_result) == _FAILURE_) {
    pba->ridder_unified.m_axion = m_axion_original;
    return _FAILURE_;
  }
  
  /* Restore original m_axion */
  pba->ridder_unified.m_axion = m_axion_original;
  
  return _SUCCESS_;
}

