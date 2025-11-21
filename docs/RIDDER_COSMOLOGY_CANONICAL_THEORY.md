# Ridder Cosmology: Canonical Theory Definition

**Status**: Complete theoretical framework ready for numerical implementation and peer review  
**Version**: 1.0  
**Date**: 2025  
**Author**: Steve Ridder

---

## Abstract

We propose an effective field theory of cosmology in which a single real scalar field, which we call the Ridder field, drives inflation, sources a percent-level early dark energy component near matter–radiation equality, generates the dark matter abundance through a feeble branching at reheating, and leaves behind a small vacuum term that behaves as a cosmological constant today. The model lives in four dimensional general relativity on a spatially flat Friedmann–Robertson–Walker background and remains agnostic about ultraviolet completion above a fixed cutoff.

This work represents a complete theoretical framework developed with the goal of addressing multiple cosmological tensions simultaneously through a unified scalar field mechanism. The model makes specific, testable predictions that can be confronted with current and future observational data.

At high field values the Ridder potential reduces to a Starobinsky-like plateau that yields cold or weakly warm inflation with a scalar tilt $n_s \simeq 0.96$ and a tensor-to-scalar ratio $r \sim 10^{-3} - 10^{-2}$, in the region already favoured by current CMB data. At lower energies the potential contains an axion-like "shelf" which holds a fractional energy density $f_{\rm EDE} \sim$ few percent at redshift $z_c \sim 3000$, then decays away, shrinking the sound horizon and easing the Hubble tension. A Yukawa coupling between the Ridder field and a fermionic dark matter species induces a mild, localized mass drift when the field leaves the shelf, which leads to a specific, percent-level feature in the growth factor and matter power spectrum. At late times the field sits in a deep minimum with vacuum energy tuned to the observed $\rho_\Lambda$, and is heavy enough that the effective equation of state is $w(z) \approx -1$ for $z \lesssim 1$.

---

## 1. Framework and Field Content

### 1.1 Effective Action and Validity

We work in four dimensional general relativity with metric signature $(-,+,+,+)$. The background spacetime is spatially flat Friedmann–Robertson–Walker,

$$ds^2 = -dt^2 + a(t)^2 d\vec x^2,$$

with scale factor $a(t)$, Hubble parameter $H \equiv \dot a/a$, and reduced Planck mass $M_{\rm Pl} = (8\pi G)^{-1/2}$.

The field content consists of:
- a real scalar field $\phi$ (the Ridder field),
- a visible sector $\chi_a$ which reduces to the Standard Model at energies below some cutoff,
- a fermionic dark matter field $\psi$.

The effective action is

$$S = \int d^4x \sqrt{-g} \left[ \frac{M_{\rm Pl}^2}{2} R - \frac{1}{2}g^{\mu\nu}\partial_\mu\phi\partial_\nu\phi - V(\phi) + \mathcal{L}_{\rm vis}(\chi_a) + i\bar\psi\gamma^\mu\nabla_\mu\psi - m_\psi(\phi)\,\bar\psi\psi \right].$$

We assume:
1. The theory is valid below an ultraviolet cutoff $\Lambda$ with $H,\ T,\ m_\phi \ll \Lambda \ll M_{\rm Pl}$, so that curvature corrections and higher derivative operators are negligible.
2. The visible sector behaves as a standard thermal bath after reheating, with energy density $\rho_{\rm vis} = \rho_\gamma + \rho_\nu + \rho_b$ matching Standard Model expectations at late times.
3. The dark matter field $\psi$ is stable on cosmological timescales and carries negligible pressure at late times, so $p_{\rm DM} \simeq 0$.

### 1.2 Energy-Momentum Tensor

The energy–momentum tensor is

$$T_{\mu\nu} = T_{\mu\nu}^{(\phi)} + T_{\mu\nu}^{\rm (vis)} + T_{\mu\nu}^{\rm (DM)},$$

with scalar contribution

$$T_{\mu\nu}^{(\phi)} = \partial_\mu\phi \partial_\nu\phi - g_{\mu\nu}\left[\frac{1}{2}(\partial\phi)^2 + V(\phi)\right].$$

On the homogeneous background, the scalar energy density and pressure are

$$\rho_\phi = \frac{1}{2}\dot\phi^2 + V(\phi),\qquad p_\phi = \frac{1}{2}\dot\phi^2 - V(\phi).$$

---

## 2. Scalar Potential and Cosmological Regimes

### 2.1 Potential Design

We require a single potential $V(\phi)$ to support three distinct behaviours:
- a high scale plateau for inflation,
- a shallow shelf at lower scales that acts as early dark energy for a short period,
- a deep minimum whose vacuum energy matches the observed $\rho_\Lambda$.

A minimal form that accomplishes this is

$$V(\phi) = V_{\rm inf}(\phi) + V_{\rm EDE}(\phi) + V_\Lambda,$$

where:
- $V_*$ sets the inflation scale,
- $\lambda = \sqrt{2/3}$ fixes the plateau shape as in Starobinsky inflation,
- $\Lambda_{\rm EDE}$ and $f$ fix the height and curvature of the EDE shelf,
- $V_\Lambda$ is a constant chosen so that $V(\phi_0) = \rho_\Lambda$ at the late-time minimum $\phi_0$.

### 2.2 Inflationary Plateau

During inflation the dynamics are governed by the plateau piece,

$$V_{\rm inf}(\phi) = V_* \left[1 - \exp\left(-\lambda\frac{\phi}{M_{\rm Pl}}\right)\right]^2,$$

where $\lambda = \sqrt{2/3}$.

The slow-roll parameters are

$$\epsilon(\phi) = \frac{M_{\rm Pl}^2}{2}\left(\frac{V'}{V}\right)^2,\qquad \eta(\phi) = M_{\rm Pl}^2\frac{V''}{V},$$

with derivatives of $V_{\rm inf}$. Inflation ends when $\epsilon(\phi_{\rm end}) = 1$. The number of e-folds between field values $\phi$ and $\phi_{\rm end}$ is

$$N(\phi) = \int_{\phi_{\rm end}}^{\phi} \frac{V}{M_{\rm Pl}^2 V'}\,d\phi.$$

For the Starobinsky form, this yields, to leading order in $1/N$,

$$n_s \simeq 1 - \frac{2}{N},\qquad r \simeq \frac{12}{N^2}.$$

For $N=50$–$60$ this gives $n_s \simeq 0.96$–$0.967$ and $r \simeq 2$–$5\times 10^{-3}$, consistent with current CMB bounds. We adopt $N=55$ as a benchmark, which implies $n_s \approx 0.964$ and $r \approx 4.0\times 10^{-3}$.

The primordial scalar amplitude $A_s$ measured at the pivot scale $k_*$ fixes $V_*$. In slow-roll,

$$A_s \simeq \frac{1}{24\pi^2}\frac{V(\phi_*)}{M_{\rm Pl}^4\epsilon(\phi_*)},$$

where $\phi_*$ is the field value when the pivot scale exits the horizon. Imposing $A_s \simeq 2.1\times 10^{-9}$ selects

$$V_*^{1/4} \sim 8\times 10^{15}\,\text{GeV},$$

up to order-one corrections, which sets the inflationary Hubble scale $H_* \sim 10^{13}\,\text{GeV}$.

### 2.3 Early Dark Energy Shelf

At much later times, after reheating and during radiation domination, the axion-like term

$$V_{\rm EDE}(\phi) = \Lambda_{\rm EDE}^4\left[1 - \cos\left(\frac{\phi}{f}\right)\right]$$

can hold a small fraction of the total energy density if the field is initially displaced from the minimum.

For small displacements $\delta\phi = \phi - \phi_{\rm min}$ one has

$$V_{\rm EDE}(\phi) \approx \frac{1}{2}m_{\rm EDE}^2 (\delta\phi)^2,\qquad m_{\rm EDE}^2 = \frac{\Lambda_{\rm EDE}^4}{f^2}.$$

When $3H \gg m_{\rm EDE}$, Hubble friction freezes the field and its energy density is nearly constant. When $3H \sim m_{\rm EDE}$ at scale factor $a_c$ or redshift $z_c$, the field begins to roll and subsequently oscillates, and its energy density redshifts away.

The fractional contribution of $\phi$ at that epoch is

$$f_{\rm EDE}(z_c) \equiv \frac{\rho_\phi(z_c)}{\rho_{\rm tot}(z_c)} \approx \frac{\Lambda_{\rm EDE}^4 \,[1 - \cos(\theta_i)]}{\rho_{\rm tot}(z_c)},$$

where $\theta_i \simeq \phi_i/f$ is the initial misalignment angle. Given $\rho_{\rm tot}(z_c)$ from the standard radiation and matter components, one can choose $\Lambda_{\rm EDE}$ and $\theta_i$ such that $f_{\rm EDE}(z_c) \sim 0.05$–$0.08$ at $z_c \sim 3000$–$4000$. This range is known to significantly reduce the sound horizon at recombination and can raise the CMB-inferred $H_0$, while remaining close to current bounds on EDE.

After $z_c$, the field's oscillations cause $\rho_\phi$ to redshift approximately as matter or faster, and its fractional contribution rapidly drops below a percent.

### 2.4 Late Vacuum and Equation of State

At late times the combined potential

$$V(\phi) = V_{\rm inf}(\phi) + V_{\rm EDE}(\phi) + V_\Lambda$$

has a minimum at $\phi = \phi_0$ where

$$V'(\phi_0) = 0,\qquad V(\phi_0) = \rho_\Lambda.$$

Defining the local curvature

$$m_\phi^2 \equiv V''(\phi_0),$$

we require

$$m_\phi^2 \gg H_0^2,$$

so that $\phi$ is effectively frozen by its own mass rather than by Hubble friction. In this regime,

$$\rho_\phi \simeq V(\phi_0) = \rho_\Lambda,\qquad p_\phi \simeq -\rho_\Lambda,$$

and the late-time equation of state is

$$w(z) \equiv \frac{p_\phi}{\rho_\phi} \approx -1$$

for all $z \lesssim 1$, up to corrections of order $H_0^2/m_\phi^2$.

---

## 3. Dark Matter Coupling and Background Evolution

### 3.1 $\phi$-Dependent Mass

We model the dark matter coupling as a $\phi$-dependent mass,

$$m_\psi(\phi) = m_0 \exp\left[\beta\frac{\phi - \phi_0}{M_{\rm Pl}}\right],$$

with constant $\beta$. The present-day mass is $m_0 = m_\psi(\phi_0)$. Varying the action with respect to $\phi$ gives a source term proportional to $\partial m_\psi/\partial\phi$,

$$\ddot\phi + 3H\dot\phi + V'(\phi) = -\beta \frac{\rho_{\rm DM}}{M_{\rm Pl}},$$

where we have used $\partial \mathcal{L}_{\rm DM}/\partial m_\psi \simeq -\bar\psi\psi$ and $\rho_{\rm DM} \simeq m_\psi \bar\psi\psi$ in the nonrelativistic limit.

Energy–momentum conservation for the dark matter fluid yields

$$\dot\rho_{\rm DM} + 3H\rho_{\rm DM} = \beta \frac{\dot\phi}{M_{\rm Pl}}\rho_{\rm DM}.$$

The sign convention is such that when $\beta\dot\phi > 0$, energy flows from $\phi$ into dark matter.

For $|\beta| \ll 1$, this coupling has two key effects:
1. It slightly distorts the background $\rho_{\rm DM}(a)$ away from pure $a^{-3}$, in a way localized around the epoch when $\phi$ moves significantly.
2. It introduces extra terms in the dark matter perturbation equations that alter the growth factor $D(a)$.

In the present model, the main epoch of interest is the time when $\phi$ leaves the EDE shelf, so the coupling imprints a one-time "kink" in the dark matter sector.

### 3.2 Dark Matter from Reheating Branching

We assume dark matter is produced by inflaton decay at reheating. Let $\Gamma_{\rm tot}$ be the total decay width of $\phi$ and $\Gamma_{\rm dark}$ the partial width into $\psi\bar\psi$. Their ratio

$$B_{\rm DM} \equiv \frac{\Gamma_{\rm dark}}{\Gamma_{\rm tot}}$$

fixes the initial ratio of dark matter to radiation after reheating.

If decay is fast compared to $H^{-1}(T_R)$, then at temperature $T_R$ we have

$$\rho_{\rm DM}(T_R) \simeq B_{\rm DM}\,\rho_\phi(T_R^-),\qquad \rho_{\rm rad}(T_R) \simeq (1-B_{\rm DM})\,\rho_\phi(T_R^-).$$

As the Universe expands,

$$\rho_{\rm DM}(T) \propto a^{-3} \propto T^3,\qquad \rho_{\rm rad}(T) \propto a^{-4} \propto T^4,$$

ignoring changes in $g_*$. The ratio at later temperature $T$ is approximately

$$\frac{\rho_{\rm DM}}{\rho_{\rm rad}}(T) \simeq B_{\rm DM} \frac{T_R}{T}.$$

At matter–radiation equality, $\rho_{\rm DM} \simeq \rho_{\rm rad}$, so

$$B_{\rm DM} \simeq \frac{T_{\rm eq}}{T_R}.$$

With benchmark values $T_R \sim 10^9\,\text{GeV} = 10^{18}\,\text{eV}$ and $T_{\rm eq} \sim 1\,\text{eV}$, this gives

$$B_{\rm DM} \sim 10^{-18}.$$

Thus a branching at the level of one part in $10^{18}$ is sufficient to generate the observed dark matter abundance, provided the dark matter is nonrelativistic after production.

---

## 4. Background Evolution

### 4.1 Friedmann Equations

The Friedmann equations are

$$H^2 = \frac{1}{3M_{\rm Pl}^2}\left(\rho_\phi + \rho_{\rm vis} + \rho_{\rm DM}\right),$$

$$\dot H = -\frac{1}{2M_{\rm Pl}^2}\left(\rho_\phi + p_\phi + \rho_{\rm vis} + p_{\rm vis} + \rho_{\rm DM} + p_{\rm DM}\right).$$

### 4.2 Scalar Field Equation

The homogeneous scalar equation of motion is

$$\ddot\phi + 3H\dot\phi + V'(\phi) = -\beta \frac{\rho_{\rm DM}}{M_{\rm Pl}}.$$

### 4.3 Modified Dark Matter Continuity

The dark matter energy density obeys a modified continuity equation:

$$\dot\rho_{\rm DM} + 3H\rho_{\rm DM} = \beta \frac{\dot\phi}{M_{\rm Pl}}\rho_{\rm DM}.$$

Radiation and baryons satisfy the standard uncoupled continuity equations.

This system realises three distinct epochs with a single degree of freedom:
1. At large $\phi$ on the exponential plateau, $\phi$ slow–rolls and drives inflation. The axion–like term and the dark matter coupling are negligible.
2. After reheating, $\phi$ evolves toward the region where the cosine term is relevant and becomes Hubble–frozen, so $V_{\rm EDE}$ provides a small early dark energy fraction around a redshift $z_c$ determined by $\Lambda_{\rm EDE}$ and $f$.
3. As the Hubble rate falls below the effective mass near the minimum of the combined potential, $\phi$ relaxes to $\phi_0$ and the universe enters a late time phase driven by the constant term $V_\Lambda$.

---

## 5. Linear Perturbations

### 5.1 Metric and Gauge Choice

We work in conformal time $\tau$ with the perturbed flat FRW metric in Newtonian gauge,

$$ds^2 = a(\tau)^2\left[-(1+2\Psi)\,d\tau^2 + (1-2\Phi)\,d\vec x^2\right],$$

where $\Psi$ and $\Phi$ are the scalar gravitational potentials. For the field content we consider, anisotropic stress is negligible on large scales, so to leading order we take $\Phi = \Psi$.

We expand the scalar field and dark matter density around the homogeneous background,

$$\phi(\tau,\vec x) = \bar\phi(\tau) + \delta\phi(\tau,\vec x),$$

$$\rho_{\rm DM}(\tau,\vec x) = \bar\rho_{\rm DM}(\tau)\,[1 + \delta_{\rm DM}(\tau,\vec x)],$$

with $\delta_{\rm DM}$ the dark matter density contrast.

### 5.2 Scalar Field Perturbation

In Newtonian gauge and in Fourier space, the scalar field perturbation equation takes the form

$$\delta\phi'' + 2\mathcal{H}\delta\phi' + (k^2 + a^2 V''(\bar\phi))\delta\phi = 4\bar\phi'\Phi' - 2a^2 V'(\bar\phi)\Phi - a^2\beta\frac{\bar\rho_{\rm DM}}{M_{\rm Pl}}\delta_{\rm DM},$$

where primes denote derivatives with respect to conformal time, $\mathcal{H} = a'/a$, and the last term encodes the linearised coupling between $\phi$ and dark matter.

### 5.3 Dark Matter Perturbations with Coupling

The dark matter sector obeys modified conservation equations because energy and momentum exchange with $\phi$ is allowed. In Newtonian gauge and Fourier space,

$$\delta_{\rm DM}' + \theta_{\rm DM} - 3\Phi' = \beta\frac{\bar\phi'}{M_{\rm Pl}}\,\Phi + \beta\frac{\delta\phi'}{M_{\rm Pl}},$$

$$\theta_{\rm DM}' + \mathcal{H}\theta_{\rm DM} - k^2\Psi = \beta\frac{k^2}{M_{\rm Pl}}\,\delta\phi.$$

In the limit $\beta \to 0$, these reduce to the familiar equations for cold dark matter. For small but nonzero $\beta$ the right-hand side terms generate:
- A small modification to the friction term in the evolution of $\delta_{\rm DM}$ when $\bar\phi'$ is nonzero.
- A scale-dependent source term proportional to $k^2\delta\phi$, which can introduce mild scale dependence in the growth factor $D(a,k)$ around the transition epoch.

---

## 6. Observables and Predictions

### 6.1 Primordial Spectra

The plateau part of the potential sets the primordial scalar and tensor power spectra. To leading order in slow roll, the scalar spectrum is

$$P_\mathcal{R}(k) = A_s\left(\frac{k}{k_*}\right)^{n_s - 1},$$

with amplitude $A_s$ fixed by the ratio $V(\phi_*)/\epsilon(\phi_*)$ and spectral index

$$n_s \simeq 1 - \frac{2}{N(\phi_*)}.$$

For $N \simeq 55$ and the chosen plateau, we obtain $n_s \approx 0.964$. The tensor spectrum has amplitude

$$P_T(k) = r\,A_s\left(\frac{k}{k_*}\right)^{n_T},$$

with $r \simeq 12/N^2 \approx 4\times 10^{-3}$ and nearly scale-invariant tilt $n_T \simeq -2\epsilon$.

### 6.2 Background Expansion and the Hubble Tension

The early dark energy shelf modifies the pre-recombination expansion rate. When $\rho_\phi$ contributes a fraction $f_{\rm EDE}(z)$ around redshift $z_c$, the total energy density is

$$\rho_{\rm tot}(z) = \rho_{\rm rad}(z) + \rho_{\rm m}(z) + \rho_\phi(z),$$

and the Hubble parameter is

$$H^2(z) = \frac{1}{3M_{\rm Pl}^2}\rho_{\rm tot}(z).$$

A nonzero $f_{\rm EDE}(z_c)$ increases $H(z)$ around the drag epoch and reduces the sound horizon,

$$r_s = \int_{z_*}^{\infty} \frac{c_s(z)}{H(z)}\,dz,$$

where $z_*$ is the redshift of last scattering and $c_s(z)$ is the baryon–photon sound speed. For fixed angular acoustic scale $\theta_s = r_s / D_A(z_*)$, a smaller $r_s$ implies a smaller angular diameter distance $D_A(z_*)$, which in turn pushes the inferred $H_0$ upward once late-time distances are matched.

### 6.3 Growth of Structure and Matter Power Spectrum

The coupling between $\phi$ and dark matter modifies the growth history. The linear growth factor $D(a,k)$ is defined by

$$\delta_{\rm DM}(k,a) = D(a,k)\,\delta_{\rm DM}(k,a_{\rm ini}),$$

with initial conditions set deep in the radiation era.

In $\Lambda$CDM, on subhorizon scales and during matter domination, $D(a)$ satisfies

$$D'' + \left(\frac{3}{a} + \frac{H'}{H}\right)D' - \frac{3}{2}\frac{\Omega_{\rm m}(a)}{a^2}D = 0,$$

where primes denote derivatives with respect to the scale factor. With a coupled scalar, this equation receives corrections that depend on $\beta$, $\phi'$, and the perturbations $\delta\phi$. The net effect in RC-X with $|\beta| \sim 0.01$ is:
- A slight enhancement or suppression of growth across the redshift interval when $\bar\phi$ rolls, leading to a feature in $D(a)$ as a function of $\ln a$.
- A correlated, small, scale-dependent distortion in the matter power spectrum, $P(k,z) = P_{\rm prim}(k)\,T^2(k,z)$, where the transfer function $T(k,z)$ encodes the modified growth.

---

## 7. Parameter Summary

| Parameter | Symbol | Fiducial Value | Prior Range |
|-----------|--------|----------------|-------------|
| Inflation scale | $V_*$ | $8 \times 10^{15}$ GeV | Fixed by $A_s$ |
| EDE scale | $\Lambda_{\rm EDE}$ | TBD (MCMC) | $10^{-2} - 10^{0}$ eV |
| Decay constant | $f$ | TBD (MCMC) | $10^{17} - 10^{19}$ GeV |
| Initial angle | $\theta_i$ | TBD (MCMC) | $[0, \pi]$ |
| Coupling strength | $\beta$ | 0.01–0.05 | $[-0.05, 0.05]$ |
| Vacuum energy | $V_\Lambda$ | $(2.3 \text{ meV})^4$ | Fixed by $\Omega_\Lambda$ |
| EDE fraction | $f_{\rm EDE}(z_c)$ | 0.05–0.08 | $[0, 0.1]$ |
| EDE redshift | $z_c$ | 3000–4000 | $[2000, 5000]$ |

---

## 8. Implementation Strategy

### 8.1 Background Module

A modified CLASS or CAMB module would:
1. Add the Ridder scalar as a new fluid.
2. Evolve $\bar\phi$ according to $\bar\phi'' + 2\mathcal{H}\bar\phi' + a^2 V'(\bar\phi) = -a^2 \beta \frac{\bar\rho_{\rm DM}}{M_{\rm Pl}}$.
3. Compute $\bar\rho_\phi$ and $\bar p_\phi$ from $\bar\rho_\phi = \frac{\bar\phi'^2}{2a^2} + V(\bar\phi)$, $\bar p_\phi = \frac{\bar\phi'^2}{2a^2} - V(\bar\phi)$.
4. Modify dark matter conservation: $\bar\rho_{\rm DM}' + 3\mathcal{H}\bar\rho_{\rm DM} = \beta \frac{\bar\phi'}{M_{\rm Pl}} \bar\rho_{\rm DM}$.

### 8.2 Perturbation Module

The perturbation module must:
1. Evolve the scalar perturbation $\delta\phi$ with coupling to dark matter.
2. Modify the dark matter continuity and Euler equations to include coupling terms proportional to $\beta$.
3. Update the Einstein equations with the scalar field contributions to $\delta\rho$ and $\delta p$.

### 8.3 Parameter Estimation

Sample over:
- Standard cosmological parameters: $\{\Omega_b h^2,\, \Omega_c h^2,\, \theta_s,\, \tau,\, A_s,\, n_s\}$
- Ridder field parameters: $\{V_*,\, \Lambda_{\rm EDE},\, f,\, \theta_i,\, \beta\}$ (or equivalently $\{f_{\rm EDE}, z_c, \beta\}$)

Fit to:
- Primary CMB temperature and polarization power spectra
- CMB lensing reconstruction
- Baryon acoustic oscillation distances
- Type Ia supernovae Hubble diagram
- Large-scale structure measurements of $P(k,z)$ and $f\sigma_8(z)$

---

## 9. Falsifiability

The model is **falsified** if any of the following occur:
1. CMB+BAO+SNe joint analysis yields $\chi^2$ significantly worse than $\Lambda$CDM
2. Direct $H_0$ measurements converge to $< 70$ km/s/Mpc
3. Detection of primordial tensor modes with $r > 0.01$
4. BBN constraints rule out the required $\beta$ coupling strength
5. Future growth measurements find no evidence for the predicted kink

---

## References

- Planck Collaboration (2018): CMB constraints
- Riess et al. (2022): SH0ES $H_0$ measurement
- Starobinsky (1980): R² inflation
- Smith et al. (2020): Early dark energy with axion-like fields
- Hill et al. (2020): EDE and the Hubble tension
- Wetterich (1988): Exponential DM coupling

---

**This document serves as the canonical theoretical definition for all numerical implementations and publications.**

