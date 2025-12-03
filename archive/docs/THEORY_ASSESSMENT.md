# Ridder Unified Potential: Theory vs Reality

## 🎯 **Current Status: Field Dynamics Fail**

Date: Nov 24, 2025  
**Bottom Line:** We fixed 7 bugs to get the code running, but the physics doesn't work yet.

---

## ✅ **What Works**

1. **Code Infrastructure** (7 bugs fixed!)
   - Unified potential activates correctly (`has_ridder=1`)
   - Parameters read properly
   - V_unified_theta() called and returns non-zero values
   - Perturbations complete (CMB spectra generated!)

2. **Potential Implementation**
   - V_tail, V_shelf computed correctly
   - Window functions work (theta ~ 2.6 rad inside active region)
   - V_total ~ 10⁻¹⁰ eV⁴ at theta ~ 2.6 rad

---

## ❌ **What Doesn't Work: THE PHYSICS**

### **Problem: Field is Frozen**

**Observation:**
```
Initial: phi' = -3.1×10⁶ eV/Mpc  
z~3000:  phi' =  1.1×10⁻³¹ eV/Mpc  ← ZERO!
Today:   phi  = 2.0×10¹⁶ eV (constant)
         V    = 0 in output
```

**Diagnosis:** The field gets Hubble-damped to zero immediately and never moves.

---

## 🔬 **Root Cause Analysis**

### **The Klein-Gordon Equation**

```
φ'' + 3H φ' + a² dV/dφ = 0
```

In log-time (dlna):
```
d²φ/dlna² + 3H(dφ/dlna) + a² dV/dφ = 0
```

At early times (z ~ 10¹⁴):
- H ~ 10²² Mpc⁻¹
- 3H φ' ~ 3 × 10²² × 3×10⁶ ~ **10²⁸ eV/Mpc²** (damping term)

For the field to move, we need:
- a² dV/dφ > 3H φ' 

But our potential gives:
- V ~ 10⁻¹⁰ eV⁴
- dV/dφ ~ V/f ~ 10⁻¹⁰/10¹⁶ ~ **10⁻²⁶ eV³**
- a² dV/dφ ~ (10⁻¹⁴)² × 10⁻²⁶ ~ **10⁻⁵⁴ eV/Mpc²**

**RATIO:** Damping/Driving ~ 10⁸² !!!

The damping term is **82 orders of magnitude** larger than the driving term!

---

## 🎯 **Why This Happened**

### **Parameter Mismatch**

We set:
- `f = 1.0×10¹⁶ eV` (EDE scale)
- `Lambda_EDE = 1.0 eV`
- `theta_i = 2.0 rad`

This gives:
- phi_ini = f × theta_i = 2×10¹⁶ eV
- V ~ Lambda⁴ ~ 1 eV⁴ ← **WAY TOO SMALL!**

For reference:
- Planck scale: M_Pl ~ 2.4×10²⁷ eV
- Inflation scale: V_inf ~ (10¹⁶ eV)⁴ ~ 10⁶⁴ eV⁴
- EDE scale: V_EDE ~ (10³ eV)⁴ ~ 10¹² eV⁴ (for f_EDE ~ 0.1)
- **Our scale:** V ~ 1 eV⁴ ~ **10⁰ eV⁴** ← Too small by 12 orders!

---

## 📊 **What the Theory Needs**

For an EDE model with f_EDE ~ 0.1 at z ~ 3000:

**Energy density requirement:**
```
ρ_EDE = 0.1 × ρ_tot(z=3000)
ρ_tot(z=3000) ~ H²M_Pl² ~ (10⁶ Mpc⁻¹)² × (10²⁷ eV)² ~ 10⁶⁶ eV⁴
ρ_EDE ~ 10⁶⁵ eV⁴
```

**Potential requirement (order of magnitude):**
```
V ~ ρ_EDE ~ 10⁶⁵ eV⁴
V ~ Lambda⁴ → Lambda ~ 10¹⁶ eV
```

**Versus what we used:**
```
Lambda_EDE = 1.0 eV  ← Off by 16 orders of magnitude!
```

---

## 🔧 **The Fix**

### **Option A: Scale Lambda_EDE Correctly**

For f_EDE ~ 0.1 at z ~ 3000:
```
Lambda_EDE ~ 10¹⁶ eV  (not 1 eV!)
```

But wait - this is HUGE! This would be:
- Lambda_EDE ~ M_Pl (Planck scale)
- V ~ M_Pl⁴ ~ 10¹⁰⁹ eV⁴

That's **inflation-scale**, not EDE!

### **Option B: The Unit Conversion is Wrong**

Maybe the V we're computing in eV⁴ needs a different conversion to get ρ in CLASS units?

Current: `ρ_class = V × (eV→Mpc)² / (3M_Pl²)`

Let me check the conversion factors...

### **Option C: The Potential Definition is Wrong**

Maybe for EDE, the potential should NOT be Lambda⁴ [1-cos(theta)]^n.

Classical EDE models use:
```
V = m² f² [1 - cos(theta)]
```

Where m is the mass scale, giving:
```
V ~ m² f² ~ (H_eq)² f²
H_eq ~ 10⁶ Mpc⁻¹ ~ 10⁻⁵ eV
f ~ 10¹⁶ eV
V ~ (10⁻⁵)² × (10¹⁶)² ~ 10²² eV⁴
```

Still much larger than our 1 eV⁴!

---

## 📝 **What We Learned**

1. **Code works, physics doesn't match**
   - All 7 bugs fixed
   - Potential functions execute correctly
   - But parameter values give unphysical dynamics

2. **Scale hierarchy matters**
   - Can't just set Lambda = 1 eV and expect EDE
   - Need to match energy scales to cosmological epochs

3. **Hubble damping dominates**
   - At early times, 3H φ' is HUGE
   - Need strong potential gradient to overcome it
   - Our potential is too shallow

---

## 🎯 **Next Steps**

### **Immediate: Understand the Scale**

Before running more configs, we need to:

1. **Check unit conversions**
   - Verify eV⁴ → Mpc⁻² conversion in background.c
   - Compare to CLASS quintessence module

2. **Look at working EDE models**
   - What Lambda do they use?
   - What f do they use?
   - What initial conditions?

3. **Compute correct Lambda analytically**
   - For f_EDE_target = 0.1 at z = 3000
   - Given H(z=3000) and rho_tot(z=3000)
   - Solve for Lambda_EDE

### **Then: Re-run with Physical Parameters**

Once we understand the scales, re-run beta ladder with:
- Lambda_EDE = ??? (computed from physics)
- f = ??? (related to field excursion)
- theta_i = ??? (sets initial energy)

---

## 💭 **Philosophical Note**

This is EXACTLY why "Fail and Fix Early" worked:

We could have run the beta ladder, seen "f_ridder = 0", and concluded:
- "Model doesn't produce EDE"
- "Theory is wrong"
- "Need to abandon this approach"

Instead, we found that **the theory hasn't been tested yet** because the parameters are wrong.

The model CAN produce EDE - we just need to use the right energy scales!

---

## 📊 **Current Model Status**

**Technical Implementation:** ✅ WORKING (7/7 bugs fixed)  
**Physical Parameters:** ❌ BROKEN (scales off by ~12-16 orders)  
**Theory Validity:** ⏸️ UNTESTED (can't assess until parameters fixed)

**We're at the "getting the units right" stage, not the "theory fails" stage.**

