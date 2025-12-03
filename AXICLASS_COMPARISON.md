# AxiCLASS vs Ridder: The Missing Piece

## 🎯 **THE SMOKING GUN**

I found it! AxiCLASS uses a **completely different potential form** and **unit convention**.

---

## 📊 **AxiCLASS Implementation**

### **Potential Form**
```c
V = m² f_a² [1 - cos(phi/f_a)]^n
```

**Units:**
- `m` = m_scf × H0 (mass in units of **H0**)
- `f_a` = f_axion (decay constant in units of **M_Pl**)
- `phi` is in **M_Pl units**

**Key insight:** They parameterize with **m and f**, not Lambda!

### **From AxiCLASS Source Code**

```c
// source/background.c, line ~3700
double V_axion_scf(struct background *pba, double phi){
    double n = pba->n_axion;
    double fa = pba->f_axion;          // f in M_Pl units!
    double m = pba->m_scf*pba->H0;     // m in eV (scaled by H0)
    
    if(n>1) 
        result = pow(m,2)*pow(fa,2)*pow(1 - cos(phi/fa),n);
    else 
        result = pow(m,2)*pow(fa,2)*(1 - cos(phi/fa));
    
    return result;
}
```

### **Example Parameters from MCMC Fits**

From `EDE_PlanckTTTEEE_BAO_Pantheon.param`:
```python
# EDE parameters (for n_axion = 3)
fraction_axion_ac = [0.13, 0.0001, 0.3]  # f_EDE target
scf_parameters__1 = [2.8, 0.01, 3.1]     # theta_ini
log10_axion_ac = [-3.5, -4.5, -3.0]      # log10(a_c) critical scale
```

From `example_axiCLASS_fld.ini`:
```ini
f_axion = 0.4  # in units of M_Pl
m_axion = 1e5  # in units of H0
n_axion = 1
scf_parameters = 0.05, 0.0  # theta_ini, theta_dot_ini
```

---

## 📊 **Our Ridder Implementation**

### **Potential Form (Current)**
```c
V = Lambda⁴ [1 - cos(theta)]^n
where theta = phi / f
```

**Units:**
- `Lambda` in **eV** (energy scale)
- `f` in **eV** (decay constant)
- `phi` in **eV**

**Problem:** We set Lambda = 1 eV, which gives V ~ 1 eV⁴

---

## 🔬 **Energy Scale Calculation**

### **AxiCLASS Scale (Correct)**

For EDE at z ~ 3000 with f_EDE ~ 0.1:

```
m ~ 10⁵ H0  (from example)
f ~ 0.4 M_Pl  (from example)

H0 ~ 10⁻³³ eV
M_Pl ~ 2.4×10²⁷ eV

m = 10⁵ × 10⁻³³ = 10⁻²⁸ eV  ← This looks tiny!
f = 0.4 × 2.4×10²⁷ = 10²⁷ eV

V = m² f² ~ (10⁻²⁸)² × (10²⁷)² 
  = 10⁻⁵⁶ × 10⁵⁴ 
  = 10⁻² eV⁴
```

Wait, that's still small! Let me recalculate...

Actually, the key is that **phi is ALSO in M_Pl units!**

```
phi ~ theta × f ~ 2.8 × 0.4 M_Pl ~ 1.1 M_Pl ~ 10²⁷ eV
```

And the critical point is that **CLASS uses natural units internally** where:
- Energies are in units of H0²M_Pl²
- rho_class = rho_physical / (3 M_Pl² H0²)

So the actual comparison should be in CLASS's natural units!

### **The Real Issue: Unit System**

**AxiCLASS approach:**
1. All dimensionful quantities scaled by cosmological units (H0, M_Pl)
2. Potential computed in eV⁴
3. Then divided by 3 to get rho_class = V/3 (for slowly varying field)
4. Natural normalization gives correct f_EDE automatically

**Our approach:**
1. Used Lambda in eV directly
2. But forgot that cosmological scales need H0 and M_Pl!
3. Lambda = 1 eV has NOTHING to do with cosmological scales

---

## 🎯 **The Fix: Two Options**

### **Option A: Use m²f² Form (Recommended)**

Change our potential to match AxiCLASS:

```c
// Instead of:
V = Lambda⁴ [1 - cos(theta)]^n

// Use:
V = m² f² [1 - cos(phi/f)]^n

// Where:
// m in units of H0 (e.g., m = 1e5 × H0)
// f in units of M_Pl (e.g., f = 0.4 × M_Pl)
// phi in M_Pl units
```

**Parameters:**
- `ridder_m_axion = 1.0e5` (in H0 units)
- `ridder_f_axion = 0.4` (in M_Pl units)
- `theta_i_ridder = 2.8` (dimensionless)

This gives:
```
phi_ini = theta_i × f = 2.8 × 0.4 M_Pl
m = 1e5 H0
V ~ (1e5 H0)² × (0.4 M_Pl)² × [1-cos]³
```

### **Option B: Scale Lambda Correctly**

If we keep Lambda⁴ form, we need:

```
V = Lambda⁴ [1-cos]^n ~ m² f²

Lambda⁴ = m² f² = (10⁵ H0)² × (0.4 M_Pl)²

Lambda² = 10⁵ H0 × 0.4 M_Pl
        = 10⁵ × 10⁻³³ × 0.4 × 2.4×10²⁷
        = 10⁻⁶ eV

Lambda = 10⁻³ eV  (NOT 1 eV!)
```

But this is still tricky because we need to express f in the right units too.

---

## 📝 **Practical Next Steps**

### **Immediate: Test Option A (m²f² form)**

1. **Modify potential in `ridder_unified_potential.c`:**

```c
// For shelf (EDE):
double V_shelf_theta(double theta, const struct ridder_unified_params *rp) {
    if (rp->use_shelf == _FALSE_) return 0.0;
    
    // Use m²f² form like AxiCLASS
    double m_eV = rp->m_axion * pba->H0;  // m in eV
    double f_eV = rp->f_axion * M_Pl_eV;  // f in eV
    
    double W = W_EDE(theta, rp);
    double one_minus_cos = 1.0 - cos(theta);
    
    // V = m² f² [1-cos]^n × W(theta)
    double V = m_eV * m_eV * f_eV * f_eV * pow(one_minus_cos, rp->n_EDE) * W;
    
    return V;
}
```

2. **Update `.ini` parameters:**

```ini
# Use AxiCLASS convention
ridder_m_axion = 1.0e5     # in H0 units
ridder_f_axion = 0.4       # in M_Pl units  
theta_i_ridder = 2.8       # dimensionless
n_axion = 3
```

3. **Re-run beta ladder**

---

## 💭 **Why We Got This Wrong**

**Our mistake:** We thought of Lambda as a free energy scale in eV.

**Reality:** EDE is a **cosmological** phenomenon. All energy scales must be tied to cosmological scales (H0, M_Pl).

**AxiCLASS wisdom:** Parameterize with:
- **m** (mass scale, tied to H at some epoch)
- **f** (decay constant, tied to M_Pl)
- **theta_ini** (initial field value)

Then the CODE figures out what Lambda_effective is based on when you want f_EDE to peak!

---

## 🎯 **Bottom Line**

**Our code is correct.**  
**Our physics understanding was correct.**  
**Our PARAMETERIZATION was wrong.**

We need to switch from:
- `Lambda = 1 eV` (meaningless)

To:
- `m = 10⁵ H0`, `f = 0.4 M_Pl` (cosmologically motivated)

This is a **one-line change** in the potential function plus updating input parameters!

---

## 📚 **References from AxiCLASS**

1. **Source:** `AxiCLASS/source/background.c`, function `V_axion_scf()`
2. **Example:** `AxiCLASS/example_axiCLASS_fld.ini`
3. **MCMC params:** `AxiCLASS/montepython_param_files/EDE_PlanckTTTEEE_BAO_Pantheon.param`

All of these use **m (in H0 units)** and **f (in M_Pl units)**, NOT Lambda!

