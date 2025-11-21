# Appendix A: Generalized Dark Matter Mapping for the Ridder Field

## A.1 Cycle-Averaged Potential Near the Minimum

The Ridder field potential in the EDE regime is:

$$V(\phi) = \Lambda^4 \left[1 - \cos\left(\frac{\phi}{f}\right)\right]^n$$

Near the minimum ($\phi \ll f$), we expand:

$$\cos\left(\frac{\phi}{f}\right) \approx 1 - \frac{1}{2}\left(\frac{\phi}{f}\right)^2 + \frac{1}{24}\left(\frac{\phi}{f}\right)^4 - \ldots$$

For small displacements:

$$1 - \cos\left(\frac{\phi}{f}\right) \approx \frac{1}{2}\left(\frac{\phi}{f}\right)^2$$

Therefore:

$$V(\phi) \approx \Lambda^4 \left[\frac{1}{2}\left(\frac{\phi}{f}\right)^2\right]^n = \frac{\Lambda^4}{(2f^2)^n} \phi^{2n}$$

This is a power-law potential $V \propto \phi^{2n}$.

## A.2 Virial Theorem for Oscillating Scalar Fields

For a homogeneous scalar field oscillating in a potential $V \propto \phi^{2n}$, the virial theorem relates the time-averaged kinetic and potential energies:

$$\langle K \rangle = n \langle V \rangle$$

where $K = \frac{1}{2}\dot{\phi}^2$ and the angle brackets denote cycle averaging.

The total energy density is:

$$\rho_\phi = K + V$$

The pressure is:

$$p_\phi = K - V$$

The cycle-averaged equation of state is:

$$w_{\rm eff} = \frac{\langle p_\phi \rangle}{\langle \rho_\phi \rangle} = \frac{\langle K \rangle - \langle V \rangle}{\langle K \rangle + \langle V \rangle}$$

Substituting the virial relation $\langle K \rangle = n \langle V \rangle$:

$$w_{\rm eff} = \frac{n \langle V \rangle - \langle V \rangle}{n \langle V \rangle + \langle V \rangle} = \frac{n-1}{n+1}$$

**For $n=3$:** $w_{\rm eff} = \frac{2}{4} = 0.5$

This is correct **only if** the oscillations are pure and the field is deep in the potential well.

## A.3 Sound Speed via WKB Approximation

For perturbations of an oscillating scalar field, the WKB approximation gives the effective sound speed as a function of scale $k$ and time $a$.

The effective mass squared is:

$$m_{\rm eff}^2 = V''(\phi) = \frac{d^2 V}{d\phi^2}$$

For $V \propto \phi^{2n}$:

$$V''(\phi) = 2n(2n-1) \frac{\Lambda^4}{(2f^2)^n} \phi^{2n-2}$$

During oscillations, the cycle-averaged value is:

$$\langle m_{\rm eff}^2 \rangle = 2n(2n-1) \frac{\Lambda^4}{(2f^2)^n} \langle \phi^{2n-2} \rangle$$

Using the virial relation, we can express this in terms of the energy density:

$$\langle m_{\rm eff}^2 \rangle \approx n(2n-1) \frac{\Lambda^4}{f^2} \left(\frac{2\langle V \rangle}{\Lambda^4}\right)^{(n-1)/n}$$

The sound speed squared is then:

$$c_s^2(k,a) = \frac{2 a^2 m_{\rm eff}^2 w_{\rm eff} + k^2}{2 a^2 m_{\rm eff}^2 + k^2}$$

### Limiting Cases:

1. **Superhorizon ($k \ll a m_{\rm eff}$):**
   $$c_s^2 \to w_{\rm eff}$$

2. **Subhorizon ($k \gg a m_{\rm eff}$):**
   $$c_s^2 \to 1$$

This scale-dependent sound speed is the key to removing the low-$k$ ghost.

## A.4 Adiabatic Sound Speed

To ensure gauge-invariant adiabaticity, we set:

$$c_a^2 = c_s^2$$

This enforces:

$$\delta p = c_s^2 \delta \rho$$

and eliminates the $(c_s^2 - c_a^2)$ term in the perturbation equations, which was the source of the $1/k^2$ instability.

## A.5 Generalized Dark Matter Variables

To avoid singularities when $w \to -1$ (during slow-roll), we use GDM variables:

$$\delta\rho = \text{energy density perturbation}$$
$$\Theta_{\rm flux} = (\rho + p) \theta = \text{momentum density}$$

These remain well-defined even when $\rho + p \to 0$.

The evolution equations are:

$$\delta\rho' = -3\mathcal{H}(\delta\rho + \delta p) - \Theta_{\rm flux} - (\rho+p)(3\Phi' + k\theta_{\rm metric})$$

$$\Theta_{\rm flux}' = -4\mathcal{H}\Theta_{\rm flux} + k^2 \delta p + (\rho+p)(k\Psi + F_{\rm coupling})$$

where $F_{\rm coupling}$ is the DM coupling force.

## A.6 Switching Criterion

The field transitions from field mode to fluid mode when:

$$3H < m_{\rm eff}$$

At this point, the oscillation frequency exceeds the Hubble rate, and individual oscillations cannot be resolved by the integrator.

**Critical:** At the switching surface, we must enforce:

$$\rho_{\rm fluid}(a_{\rm osc}) = \rho_{\rm field}(a_{\rm osc})$$
$$\delta_{\rm fluid}(k,a_{\rm osc}) = \delta_{\phi}(k,a_{\rm osc})$$
$$\Theta_{\rm fluid}(k,a_{\rm osc}) = (\rho+p)\theta_{\phi}(k,a_{\rm osc})$$

This ensures energy and momentum conservation across the transition.

## A.7 Summary of Implementation

1. **Background:** Use Klein-Gordon until $3H < m_{\rm eff}$, then switch to fluid with $w_{\rm eff} = (n-1)/(n+1)$.

2. **Perturbations:** Use GDM variables $(\delta\rho, \Theta_{\rm flux})$ throughout.

3. **Sound Speed:** Implement scale-dependent $c_s^2(k,a)$ using the WKB formula.

4. **Adiabaticity:** Set $c_a^2 = c_s^2$ to remove ghost modes.

5. **Switching:** Store $\rho_{\rm osc}$, $\delta_{\rm osc}$, $\Theta_{\rm osc}$ at transition and enforce continuity.

This completes the rigorous mathematical foundation for the GDM+CAFA implementation.
