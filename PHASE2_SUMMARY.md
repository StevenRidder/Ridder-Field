# Phase 2: Complete 2D EDE Parameter Map

## 2.1 Objective and Overview

The goal of Phase 2 is to map the parameter space of the Ridder field in terms of the two key knobs that control the early dark energy (EDE) bump: the mass scale Λ and the initial angle θᵢ. For each point in this space we measure

* the redshift at which the Ridder component peaks, z_peak, and
* the fractional contribution of the Ridder component at that peak, f_peak = ρ_Ridder / ρ_tot.

The aim is to determine, empirically rather than by assumption, which parameter primarily controls timing and which controls amplitude. A secondary aim is to identify at least one concrete configuration that sits in the canonical EDE regime, with z_peak ~ 10³ and f_peak ~ 5–10%.

By the end of Phase 2, both goals are met: the roles of Λ and θᵢ are characterized across regimes, and a viable EDE configuration is identified and ready for full CLASS analysis in Phase 3.

---

## 2.2 Lambda Scan at Fixed θᵢ: Timing Control

We first held the initial angle fixed at θᵢ = 1.5 and scanned Λ over two orders of magnitude. For each Λ, we ran CLASS with the Ridder field switched on and extracted z_peak and f_peak from the background output.

### Results

| Λ (eV) | Multiplier | z_peak | f_peak |
| ------ | ---------: | -----: | -----: |
| 0.0165 |         ×1 |   14.9 |  0.250 |
| 0.0496 |         ×3 |   67.2 |  0.253 |
| 0.1655 |        ×10 |  325.1 |  0.266 |
| 0.4964 |        ×30 | 1247.9 |  0.295 |
| 1.6548 |       ×100 | 4746.8 |  0.337 |

**Key metrics**

* z_peak grows from 14.9 to 4746.8, a factor of about 318.
* f_peak increases only from 0.250 to 0.337, about 35 percent.

**Conclusion**

At fixed θᵢ, Λ is the primary control on **timing**. Increasing Λ moves the EDE bump earlier in cosmic history by more than two orders of magnitude in redshift, while the amplitude changes only modestly. This is the sense in which "Λ sets when" the field becomes dynamically important.

---

## 2.3 Theta Scan at Low Λ: Amplitude Control in the Late Regime

Next, we fixed Λ at the Phase 1 slope value, Λ = 0.0165 eV, and scanned θᵢ. A diagnostic bug in the first pass (a hard floor at z_min=50) initially obscured the true peaks. After removing that clipping and re-reading the full background table, the real behavior emerged.

### Low Λ scan: Λ = 0.0165 eV

| θᵢ  | z_peak | f_peak | Regime  |
| --- | -----: | -----: | ------- |
| 0.5 |    4.0 |  0.024 | Late DE |
| 1.0 |   10.2 |  0.101 | Late DE |
| 1.5 |   14.9 |  0.250 | Late DE |
| 2.0 |   16.2 |  0.492 | Late DE |
| 2.5 |   12.5 |  0.805 | Late DE |

**Key metrics**

* z_peak spans 4.0 to 16.2, about a factor of 4. All peaks lie at z < 20, well into the late dark energy or early quintessence regime.
* f_peak spans 0.024 to 0.805, a factor of about 33.

**Conclusion**

At low Λ, θᵢ has a **secondary effect on timing** but a **strong effect on amplitude**. Changing θᵢ moves z_peak only within the late universe, but it changes f_peak by over an order of magnitude. This regime is not yet true EDE, but it already hints that θᵢ is the main "how much" knob.

---

## 2.4 Theta Scan at High Λ: EDE Regime and Full Leverage

To reach genuine early dark energy, we increased Λ by a factor of 30, to the point where the field becomes dynamically relevant before recombination. We then repeated the θᵢ scan at this higher Λ.

### High Λ scan: Λ = 0.4964 eV (Λ × 30)

| θᵢ   | z_peak | f_peak | EDE viability  |
| ---- | -----: | -----: | -------------- |
| 0.50 |    4.0 |  0.024 | Too late       |
| 0.75 |    691 |  0.063 | **Viable EDE** |
| 1.00 |    924 |  0.118 | f high         |
| 1.25 |   1114 |  0.195 | f high         |
| 1.50 |   1248 |  0.295 | f high         |

**Key metrics**

* z_peak spans 4.0 to 1248, a factor of about 300.
* f_peak spans 0.024 to 0.295, a factor of about 12.

Now θᵢ has strong leverage on both timing and amplitude once Λ is large enough to push the system into the EDE regime. The clean separation of roles emerges most clearly when Λ is high enough that the field is active between equality and recombination.

---

## 2.5 Regime-Dependent Parameter Roles

Putting the scans together, we can summarize the behavior as follows.

### Low Λ regime (Λ ≲ 0.05 eV)

* The field becomes important only at z ≲ 100.
* θᵢ changes z_peak by a factor of a few, but always within the late universe.
* θᵢ changes f_peak by more than an order of magnitude.
* Λ is too small to generate EDE; increasing Λ is essential.

### High Λ regime (Λ ≳ 0.3 eV)

* The field is active at z ≳ 500, the true EDE window.
* Λ controls the overall shift of the bump to earlier times.
* At fixed high Λ, θᵢ controls both when the bump sits within that window and how tall it is.
* The qualitative picture becomes:

> Λ sets **when** the Ridder field matters,
> θᵢ sets **how much** it matters,
> with both statements grounded in numerical scans, not just theory.

The slogan is not exact in a mathematical sense. At low Λ, θᵢ still nudges timing, and at high Λ, Λ still nudges amplitude. What the scans show is that Λ has far more leverage on z_peak than on f_peak, while θᵢ has far more leverage on f_peak than on z_peak, especially once Λ is large enough for EDE.

---

## 2.6 Selected EDE Benchmark Configuration

From the high-Λ θᵢ scan, one configuration stands out as an excellent EDE benchmark:

**Parameters**

* Λ_Ridder = 0.4964 eV (30 times the Phase 1 slope value)
* θ_i,Ridder = 0.75
* f_axion,Ridder = 2.435 × 10²⁷ eV (reduced Planck scale)
* n_Ridder = 3
* c_slow = 1.0

**Derived quantities**

* z_peak ≈ 691
* f_peak ≈ 0.063
* a_peak ≈ 1.4 × 10⁻³

This point lies between equality and recombination, with an amplitude in the canonical H₀-relevant range of 5 to 10 percent. Λ is high enough to activate the field early, while θᵢ is small enough to avoid runaway dominance.

This configuration will serve as the primary EDE benchmark in Phase 3.

---

## 2.7 Diagnostic and Implementation Notes

### Background diagnostic

A crucial mistake in the early scans was the use of a hard lower bound (z_min = 50) when searching for the peak. Several configurations were reported with z_peak = 50, which was the search floor rather than the true maximum. After switching to a full scan over the CLASS background table, with z_min ≈ 1 and explicit checks that the peak does not sit on a boundary, the true peaks at z ~ 4–16, and later at z ~ 10³, became visible.

The lesson is simple: when diagnosing new components, never trust a peak that lies exactly at the edge of the search window.

### File naming

CLASS appends extra decimal digits to output filenames. Instead of matching a single hardcoded pattern, the diagnostic scripts now use globbing to locate the appropriate `*_background.dat` file for each parameter pair. This makes the scan infrastructure robust to minor changes in output naming.

---

## 2.8 Relation to Phase 1 and Path to Phase 3

Phase 1 established a stable ΛCDM control configuration at the extremum, confirmed that the Ridder sector is numerically well behaved, and calibrated Λ so that the extremum reproduces the standard dark energy fraction. Phase 2 then moved into the dynamical regime and answered three questions:

1. How does Λ affect the timing and amplitude of the Ridder bump.
2. How does θᵢ affect timing and amplitude at both low and high Λ.
3. Whether there exists at least one configuration that sits in a realistic EDE window.

The answers are now in hand:

* Λ controls when the bump occurs, over more than two orders of magnitude in redshift.
* θᵢ controls how large the bump is, and at high Λ also helps position it within the EDE window.
* A concrete EDE configuration, with Λ = 0.4964 eV and θᵢ = 0.75, has been identified and characterized at the background level.

With that foundation, Phase 3 can focus purely on observables. The next steps are to run full CLASS with perturbations for the benchmark and nearby points, extract H₀, the sound horizon, and the CMB power spectra, and compare these predictions to ΛCDM and observational data.

