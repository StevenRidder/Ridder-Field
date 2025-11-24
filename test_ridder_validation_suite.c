/**
 * @file test_ridder_validation_suite.c
 * @brief Unit tests for Ridder unified potential
 * 
 * Systematic validation following "fail and fix early" philosophy:
 * 1. Derivative consistency (numerical vs analytic)
 * 2. Energy conservation check
 * 3. ΛCDM recovery when Ridder disabled
 * 4. Known EDE benchmark reproduction
 * 5. Component isolation tests
 */

#include "background.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

#define TEST_TOLERANCE 1e-4
#define TEST_DERIVATIVE_DELTA 1e-8

/**
 * Test 1: Derivative Consistency
 * Check that analytic dV/dφ matches finite difference
 */
int test_derivative_consistency(struct background *pba) {
  printf("\n");
  printf("=" ,"=", 80);
  printf("\nTEST 1: DERIVATIVE CONSISTENCY\n");
  printf("=" ,"=", 80);
  printf("\n");
  
  int n_test_points = 10;
  double phi_min = 1e15;  /* eV */
  double phi_max = 3e16;  /* eV */
  double delta_phi = TEST_DERIVATIVE_DELTA;
  
  int failures = 0;
  
  for (int i = 0; i < n_test_points; i++) {
    double phi = phi_min + (phi_max - phi_min) * i / (n_test_points - 1.0);
    double theta = phi / pba->ridder_unified.f;
    
    /* Compute V at phi, phi+δ, phi-δ */
    double V_center = V_unified_theta(theta, &pba->ridder_unified);
    double V_plus = V_unified_theta((phi + delta_phi) / pba->ridder_unified.f, 
                                    &pba->ridder_unified);
    double V_minus = V_unified_theta((phi - delta_phi) / pba->ridder_unified.f,
                                     &pba->ridder_unified);
    
    /* Finite difference: (V+ - V-) / (2δφ) */
    double dV_numerical = (V_plus - V_minus) / (2.0 * delta_phi);
    
    /* Analytic derivative */
    double dV_analytic = dV_unified_dtheta(theta, &pba->ridder_unified) / pba->ridder_unified.f;
    
    /* Relative error */
    double error = fabs(dV_numerical - dV_analytic) / (fabs(dV_analytic) + 1e-30);
    
    printf("  φ = %.3e eV:  dV_num = %.6e,  dV_ana = %.6e,  err = %.2e",
           phi, dV_numerical, dV_analytic, error);
    
    if (error < TEST_TOLERANCE) {
      printf("  ✓\n");
    } else {
      printf("  ✗ FAIL\n");
      failures++;
    }
  }
  
  printf("\n");
  if (failures == 0) {
    printf("✅ DERIVATIVE TEST PASSED (%d/%d points)\n", n_test_points, n_test_points);
  } else {
    printf("❌ DERIVATIVE TEST FAILED (%d/%d points failed)\n", failures, n_test_points);
  }
  
  return (failures == 0) ? _SUCCESS_ : _FAILURE_;
}

/**
 * Test 2: Energy Conservation
 * Check ρ'_φ + 3(1+w_φ)Hρ_φ ≈ 0 from background evolution
 */
int test_energy_conservation(struct background *pba) {
  printf("\n");
  printf("=","=", 80);
  printf("\nTEST 2: ENERGY CONSERVATION\n");
  printf("=","=", 80);
  printf("\n");
  
  /* This requires reading background table after integration */
  /* For now, print instructions for manual check */
  
  printf("MANUAL CHECK REQUIRED:\n");
  printf("  1. Run CLASS with write_background = yes\n");
  printf("  2. Extract columns: a, rho_ridder, p_ridder, H\n");
  printf("  3. Compute: w_phi = p_ridder / rho_ridder\n");
  printf("  4. Compute: drho_da = numerical derivative of rho_ridder\n");
  printf("  5. Check: drho_da/rho_ridder + 3*(1+w_phi)*H/a ≈ 0\n");
  printf("\n");
  printf("Expected: |conservation error| < 1e-6 throughout evolution\n");
  printf("\n");
  printf("⚠️  DEFERRED: Requires post-processing background output\n");
  
  return _SUCCESS_;
}

/**
 * Test 3: ΛCDM Recovery
 * Verify that Ridder OFF reproduces exact ΛCDM
 */
int test_lcdm_recovery() {
  printf("\n");
  printf("=","=", 80);
  printf("\nTEST 3: ΛCDM RECOVERY\n");
  printf("=","=", 80);
  printf("\n");
  
  printf("TEST PROCEDURE:\n");
  printf("  1. Create two .ini files:\n");
  printf("     - test_lcdm_baseline.ini: use_ridder = no\n");
  printf("     - test_lcdm_with_ridder_off.ini: use_ridder = yes, but all ridder_use_* = no\n");
  printf("  2. Run CLASS on both\n");
  printf("  3. Compare: H(z), r_s, D_A(z), C_ℓ^TT, P(k)\n");
  printf("\n");
  printf("ACCEPTANCE CRITERIA:\n");
  printf("  - |H_with_ridder(z) - H_baseline(z)| / H_baseline < 1e-10 for all z\n");
  printf("  - |r_s_with_ridder - r_s_baseline| < 1e-10 Mpc\n");
  printf("  - max|ΔC_ℓ / C_ℓ| < 1e-10 for ℓ = 2..2500\n");
  printf("\n");
  printf("⚠️  DEFERRED: Requires running CLASS twice and comparing outputs\n");
  
  return _SUCCESS_;
}

/**
 * Test 4: Reproduce Known EDE Benchmark
 * Match Poulin et al. or Smith et al. axion EDE results
 */
int test_ede_benchmark() {
  printf("\n");
  printf("=","=", 80);
  printf("\nTEST 4: EDE BENCHMARK REPRODUCTION\n");
  printf("=","=", 80);
  printf("\n");
  
  printf("BENCHMARK: Smith et al. 2020 (arXiv:1908.06995) or Poulin et al. 2019\n");
  printf("\n");
  printf("TEST PROCEDURE:\n");
  printf("  1. Set unified potential to match known axion EDE:\n");
  printf("     - use_tail = no\n");
  printf("     - use_shelf = yes, with their (m, f, theta_i, n)\n");
  printf("     - use_plateau = no\n");
  printf("     - beta_ridder = 0 (no CDM coupling)\n");
  printf("  2. Run CLASS and extract:\n");
  printf("     - f_EDE(z) curve\n");
  printf("     - z_c (redshift of max f_EDE)\n");
  printf("     - r_s (sound horizon)\n");
  printf("     - w_phi(z)\n");
  printf("  3. Compare to published values\n");
  printf("\n");
  printf("EXAMPLE TARGET (from Smith et al.):\n");
  printf("  - f_EDE(z_c) ≈ 0.10-0.13\n");
  printf("  - z_c ≈ 3000-5000\n");
  printf("  - r_s ≈ 143-145 Mpc (depending on f_EDE)\n");
  printf("  - w_phi: large negative → 0 → positive (tracking)\n");
  printf("\n");
  printf("ACCEPTANCE: Match published values within 5%%\n");
  printf("\n");
  printf("⚠️  DEFERRED: Requires literature parameter mapping and CLASS run\n");
  
  return _SUCCESS_;
}

/**
 * Test 5: Component Isolation
 * Test tail-only, shelf-only, plateau-only modes
 */
int test_component_isolation() {
  printf("\n");
  printf("=","=", 80);
  printf("\nTEST 5: COMPONENT ISOLATION\n");
  printf("=","=", 80);
  printf("\n");
  
  printf("5A. TAIL ONLY (Late-Time Quintessence)\n");
  printf("  Config: use_tail=yes, use_shelf=no, use_plateau=no\n");
  printf("  Expected:\n");
  printf("    - w(z) ≈ -1 at z=0 (if tuned correctly)\n");
  printf("    - Ω_ridder(z=0) ≈ 0.7 (mimics Ω_Λ)\n");
  printf("    - No EDE bump at high z\n");
  printf("\n");
  
  printf("5B. SHELF ONLY (Pure EDE)\n");
  printf("  Config: use_tail=no, use_shelf=yes, use_plateau=no\n");
  printf("  Expected:\n");
  printf("    - f_ridder peaks at z ~ few thousand\n");
  printf("    - f_ridder(z=0) ≈ 0 (decayed away)\n");
  printf("    - w(z) large negative early, crosses zero, goes positive\n");
  printf("\n");
  
  printf("5C. PLATEAU ONLY (Inflation)\n");
  printf("  Config: use_tail=no, use_shelf=no, use_plateau=yes\n");
  printf("  Expected:\n");
  printf("    - Field starts on plateau at very early times\n");
  printf("    - Slow-roll inflation phase\n");
  printf("    - Eventually decays (depending on exit mechanism)\n");
  printf("  Note: May require dedicated early-universe CLASS run\n");
  printf("\n");
  printf("⚠️  DEFERRED: Requires 3 CLASS runs with different configs\n");
  
  return _SUCCESS_;
}

/**
 * Main validation runner
 */
int main(int argc, char **argv) {
  printf("\n");
  printf("════════════════════════════════════════════════════════════════════════════════\n");
  printf("RIDDER UNIFIED POTENTIAL: VALIDATION SUITE\n");
  printf("Following 'Fail and Fix Early' Philosophy\n");
  printf("════════════════════════════════════════════════════════════════════════════════\n");
  
  /* Note: For C-level tests, we'd need to initialize a background struct */
  /* For now, this serves as a validation roadmap */
  
  printf("\nVALIDATION ROADMAP:\n");
  printf("  ☐ Test 1: Derivative Consistency (C-level unit test)\n");
  printf("  ☐ Test 2: Energy Conservation (post-processing check)\n");
  printf("  ☐ Test 3: ΛCDM Recovery (2 CLASS runs + compare)\n");
  printf("  ☐ Test 4: EDE Benchmark Reproduction (CLASS + literature)\n");
  printf("  ☐ Test 5: Component Isolation (3 CLASS runs)\n");
  printf("\n");
  printf("PRIORITY ORDER:\n");
  printf("  1. Test 1 (derivative) - fastest, catches coding errors\n");
  printf("  2. Test 3 (ΛCDM) - verifies we don't break vanilla cosmology\n");
  printf("  3. Test 4 (EDE benchmark) - validates physics correctness\n");
  printf("  4. Test 2 (energy conservation) - checks numerical integration\n");
  printf("  5. Test 5 (isolation) - confirms component independence\n");
  printf("\n");
  printf("AFTER ALL PASS → Shooting calibration becomes meaningful\n");
  printf("\n");
  
  /* Run C-level tests that don't need full CLASS initialization */
  /* (In practice, would need proper struct initialization) */
  
  printf("════════════════════════════════════════════════════════════════════════════════\n");
  printf("\nNext step: Implement Test 1 (derivative check) in background.c\n");
  printf("Then: Create .ini files for Tests 3-5 and run systematically\n");
  printf("\n");
  
  return 0;
}

