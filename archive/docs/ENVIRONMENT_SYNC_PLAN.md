## Environment & Sync Plan for Tier 3/4 (US East + Australia)

This document locks in how we keep the two Azure machines in sync so Tier 3/4 never break again due to environment drift.

### 1. Roles

- **GitHub (`main` branch)**: Single source of truth for **code and configs**:
  - YAML configs (`*tier*_production.yaml`, etc.)
  - Scripts (`run_*_production.sh`, `*_status.sh`, etc.)
- **Australia VM**:
  - **Canonical runtime environment** (Python, CLASS, Cobaya, Planck/BAO/SN data).
  - All installs/updates happen **here first**, tested here.
- **US East VM**:
  - **Mirror of Australia’s environment**.
  - Never installs anything by itself; it only:
    - `git pull` for code.
    - `rsync` from Australia for environment & data.

### 2. Python / Cobaya / CLASS Versions (Canonical on Australia)

On Australia (as of Tier 3 fix):

- `python3`: 3.10.12
- `numpy`: 1.24.4
- `Cython`: 0.29.28
- `classy`: 3.3.3 (from `classy-3.3.3-py3.10-linux-x86_64.egg`)
- `cobaya`: (version reported by `python3 -c 'import cobaya; print(cobaya.__version__)'`)

**Rule:** If any of these change on Australia, we:

1. Update this section with the new versions.
2. Re‑test Tier 3 (and Tier 4 if needed) on **Australia**.
3. Only after it passes, we sync `.local` from Australia → US East (see below).

### 3. Allowed Operations by Machine

#### Australia (canonical)

- Allowed:
  - `pip3 install --user ...`
  - `cobaya-install ...`
  - Rebuild CLASS if needed (but do it carefully and test).
  - `git pull` for code updates.
- Not allowed:
  - Direct env changes without immediately documenting versions here and testing Tier 3.

#### US East (mirror)

- Allowed:
  - `git pull` for code.
  - **Only** environment changes via `rsync` from Australia (no local installs).
- **Not allowed**:
  - `pip3 install ...`
  - `cobaya-install ...`
  - Rebuilding CLASS directly.

If we break this rule, the two machines will diverge again.

### 4. Environment Sync Commands (Australia → US East)

Run these **from US East** when we want to sync to whatever is now working on Australia.

#### 4.1. Sync Python packages / Cobaya / CLASS

```bash
ssh <VM_USER>@<VM_IP> "
  rsync -avz \
    <VM_USER>@172.174.34.125:/home/<VM_USER>/.local/ \
    /home/<VM_USER>/.local/
"
```

This copies:

- `~/.local/lib/python3.10/site-packages` (including `classy`, `cobaya`, `numpy`, etc.)
- `~/.local/share/cobaya` (Planck/Cobaya code and helper modules)

#### 4.2. Sync likelihood data (Planck, BAO, SN, etc.)

```bash
ssh <VM_USER>@<VM_IP> "
  rsync -avz \
    <VM_USER>@172.174.34.125:/home/<VM_USER>/Ridder-Field/phase3/packages/data/ \
    /home/<VM_USER>/Ridder-Field/phase3/packages/data/
"
```

This ensures both machines use the exact same Planck/BAO/SN data and any custom files.

### 5. Code / Config Sync (Both Machines)

For **code and configs**, both machines should do:

```bash
cd ~/Ridder-Field
git pull
```

All Tier‑3/Tier‑4 YAMLs and scripts live in the repo, so `git pull` keeps them aligned.

### 6. CLASS Loading Policy

Current Tier‑3 configs (`ridder_tier3_production.yaml`, `lcdm_tier3_production.yaml`) use:

```yaml
theory:
  classy:
    extra_args:
      output: tCl, mPk
      l_max_scalars: 2508
      lensing: yes
      gauge: newtonian
      recombination: recfast
      non_linear: none
      Lambda_EDE_ridder: 1.0
      f_axion_ridder: 1.0e27
      n_ridder: 3
```

No `path:` is specified, so Cobaya imports the installed `classy` (identical on both machines thanks to `rsync`).

**Rule:** Do not reintroduce `path: ../phase2/class` or rebuild CLASS differently on US East.  
If we ever need to change CLASS:

1. Change/rebuild it on **Australia**.
2. Test Tier 3 there.
3. `rsync` `~/.local/` from Australia → US East as in §4.1.

### 7. SH0ES Likelihood Policy (Tier 3+)

To avoid the “SH0ES is just a weak prior” problem, Tier 3 (and Tier 4 if used) must **always**:

- Implement SH0ES as an **external likelihood** term:

  ```yaml
  sh0es_h0:
    external: |
      lambda _self=None, H0=None, **params_values: (
        -0.5 * ((H0 - 73.04) / 1.04)**2
      )
    requires:
      H0:
        latex: H_0
  ```

- Treat `H0` as a regular parameter with a wide prior:

  ```yaml
  H0:
    prior: {min: 60, max: 80}
    ref: 70.3
    proposal: 0.5
  ```

This guarantees SH0ES enters the total χ² with full statistical strength, instead of only biasing proposals.

### 8. Operational Checklist (Going Forward)

**When changing anything in the environment:**

1. Make the change on **Australia**.
2. Update §2 in this file with new versions if relevant.
3. Run a short Tier‑3 test on Australia to confirm:
   - CLASS + Ridder load,
   - Planck/BAO/SH0ES likelihoods evaluate,
   - Chains actually produce samples.
4. From **US East**, run the two `rsync` commands in §4.1 and §4.2.

**When changing configs or scripts:**

1. Edit files locally (or on one machine).
2. Commit and push to GitHub (`main`).
3. On both machines: `git pull` in `~/Ridder-Field`.

**Never do**:

- Local `pip install` / `cobaya-install` / CLASS rebuild **only** on US East.
- Manual edits to `/usr/local/lib/*` on one machine but not the other.


