#!/usr/bin/env python3
"""Fix dV_shelf_dtheta to use same V_scale logic as V_shelf_theta."""

# Read file
with open("phase2/class/source/ridder_unified_potential.c", "r") as f:
    content = f.read()

# Fix dV_shelf_dtheta - replace Lambda^4 with V_scale logic
old_dv = """double dV_shelf_dtheta(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_shelf == _FALSE_) return 0.0;
  
  double W = W_EDE(theta, rp);
  double dW = dW_EDE_dtheta(theta, rp);
  
  double one_minus_cos = 1.0 - cos(theta);
  if (one_minus_cos <= 0.0) return 0.0;
  
  double s = sin(theta);
  double n = rp->n_EDE;
  
  /* Lambda^4 form */
  double Lambda4 = pow(rp->Lambda_EDE, 4.0);
  
  double base = pow(one_minus_cos, n);
  double dbase = n * pow(one_minus_cos, n - 1.0) * s;
  
  /* Product rule: d(W * base) = dW * base + W * dbase */
  double dV = Lambda4 * (dW * base + W * dbase);
  
  return dV;
}"""

new_dv = """double dV_shelf_dtheta(double theta, const struct ridder_unified_params *rp) {
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
}"""

if old_dv in content:
    content = content.replace(old_dv, new_dv)
    print("Fixed dV_shelf_dtheta")
else:
    print("WARNING: Could not find dV_shelf_dtheta to fix")

# Fix d2V_shelf_dtheta2 
old_d2v = """double d2V_shelf_dtheta2(double theta, const struct ridder_unified_params *rp) {
  if (rp->use_shelf == _FALSE_) return 0.0;
  
  double one_minus_cos = 1.0 - cos(theta);
  if (one_minus_cos <= 0.0) return 0.0;
  
  double s = sin(theta);
  double c = cos(theta);
  double n = rp->n_EDE;
  double Lambda4 = pow(rp->Lambda_EDE, 4.0);"""

new_d2v = """double d2V_shelf_dtheta2(double theta, const struct ridder_unified_params *rp) {
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
  }"""

if old_d2v in content:
    content = content.replace(old_d2v, new_d2v)
    print("Fixed d2V_shelf_dtheta2 header")
else:
    print("WARNING: Could not find d2V_shelf_dtheta2 to fix")

# Also fix the Lambda4 reference in d2V_shelf_dtheta2
if "double d2V = Lambda4 * (W * d2base" in content:
    content = content.replace("double d2V = Lambda4 * (W * d2base", "double d2V = V_scale * (W * d2base")
    print("Fixed d2V calculation")
else:
    print("WARNING: Lambda4 reference not found")

# Write back
with open("phase2/class/source/ridder_unified_potential.c", "w") as f:
    f.write(content)

print("Done!")

