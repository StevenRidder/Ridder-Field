#!/bin/bash
# Verify column mappings and set up new chains

cd ~/Ridder-Field/phase3/chains

echo "============================================"
echo "COLUMN VERIFICATION"
echo "============================================"

echo ""
echo "LCDM columns:"
head -1 tier4_lcdm_shoes.1.txt | tr -s ' ' '\n' | nl | grep -E "chi2|logpost|H0|rs" | head -10

echo ""
echo "V3 columns:"
head -1 tier4_v3_shoes.1.txt | tr -s ' ' '\n' | nl | grep -E "chi2|logpost|H0|rs" | head -10

echo ""
echo "============================================"
echo "VERIFYING SCRIPT ASSUMPTIONS"
echo "============================================"

# Check if col 37 (LCDM) and col 40 (V3) are actually chi2_tot
echo "LCDM: col 37 should be chi2_tot"
head -1 tier4_lcdm_shoes.1.txt | awk '{print "col 37 =", $37}'

echo "V3: col 40 should be chi2_tot"  
head -1 tier4_v3_shoes.1.txt | awk '{print "col 40 =", $40}'

# Verify -logpost is col 2 for both
echo ""
echo "Both should use col 2 for -logpost (correct metric)"
sed -n '100p' tier4_lcdm_shoes.1.txt | awk '{print "LCDM col2 =", $2}'
sed -n '100p' tier4_v3_shoes.1.txt | awk '{print "V3 col2 =", $2}'

echo ""
echo "============================================"
echo "BEST FIT CHECK (using col 2 = -logpost)"
echo "============================================"
for w in baseline shoes trgb; do
    v3_best=$(awk 'NR>1 {if(NR==2||$2<m)m=$2} END {print m}' tier4_v3_${w}.1.txt 2>/dev/null)
    lcdm_best=$(awk 'NR>1 {if(NR==2||$2<m)m=$2} END {print m}' tier4_lcdm_${w}.1.txt 2>/dev/null)
    if [ ! -z "$v3_best" ] && [ ! -z "$lcdm_best" ]; then
        echo "$w: V3=$v3_best LCDM=$lcdm_best Δ=$(echo "$v3_best $lcdm_best" | awk '{printf "%+.1f", $1-$2}')"
    fi
done

echo ""
echo "============================================"
echo "SETTING UP NEW CHAINS"
echo "============================================"
cd ~/Ridder-Field/phase3

# Kill old chains
pkill -9 cobaya 2>/dev/null
sleep 1

# Get best fit params
best_lam=$(awk 'NR>1 {if(NR==2||$2<m){m=$2;v=$9}} END {print v}' chains/tier4_v3_shoes.1.txt)
best_ac=$(awk 'NR>1 {if(NR==2||$2<m){m=$2;v=$10}} END {print v}' chains/tier4_v3_shoes.1.txt)
best_sig=$(awk 'NR>1 {if(NR==2||$2<m){m=$2;v=$11}} END {print v}' chains/tier4_v3_shoes.1.txt)

echo "Best fit params: Lambda=$best_lam a_c=$best_ac sigma=$best_sig"

# Create config for 3 chains
for i in 1 2 3; do
    cat > tier4_v3_shoes_opt${i}.yaml << YAML
# V3 OPTIMIZED Chain ${i} - Starting near best fit
theory:
  classy:
    extra_args:
      output: tCl, pCl, lCl
      l_max_scalars: 2508
      lensing: "yes"
      gauge: newtonian
      recombination: recfast
      use_ridder: "yes"
      ridder_model_type: v3_canon
      ridder_use_shelf: "yes"
      ridder_use_tail: "no"
      ridder_f_eV: 2.0e26
      theta_i_ridder: 2.8
      ridder_c_slow: 0.0

likelihood:
  planck_2018_lowl.TT: null
  planck_2018_lowl.EE: null
  planck_2018_highl_plik.TTTEEE: null
  planck_2018_lensing.clik: null
  bao.sixdf_2011_bao: null
  bao.sdss_dr7_mgs: null
  bao.sdss_dr12_consensus_bao: null
  sh0es_h0:
    external: 'lambda _self=None, H0=None, **p: -0.5 * ((H0 - 73.04) / 1.04)**2'
    requires:
      H0:
        latex: H_0

params:
  logA: {prior: {min: 2.5, max: 3.5}, ref: 3.044, proposal: 0.01, drop: true}
  A_s: {value: 'lambda logA: 1e-10*np.exp(logA)'}
  n_s: {prior: {min: 0.92, max: 1.00}, ref: 0.9649, proposal: 0.004}
  H0: {prior: {min: 60, max: 80}, ref: 70.6, proposal: 0.5}
  omega_b: {prior: {min: 0.019, max: 0.025}, ref: 0.02237, proposal: 0.0002}
  omega_cdm: {prior: {min: 0.10, max: 0.14}, ref: 0.1200, proposal: 0.002}
  tau_reio: {prior: {min: 0.01, max: 0.10}, ref: 0.0544, proposal: 0.006}
  ridder_Lambda_EDE_eV: {prior: {min: 0.35, max: 0.55}, ref: ${best_lam}, proposal: 0.02}
  ridder_a_c: {prior: {min: 2.8e-4, max: 3.4e-4}, ref: ${best_ac}, proposal: 1.0e-5}
  ridder_sigma_lna: {prior: {min: 0.45, max: 0.70}, ref: ${best_sig}, proposal: 0.03}
  rs_drag: {latex: r_s}

sampler:
  mcmc:
    max_samples: 2000
    Rminus1_stop: 0.03
    burn_in: 0
    drag: false
    proposal_scale: 2.0

output: chains/tier4_v3_shoes_opt${i}
debug: false
resume: false
YAML
    # Fix variable substitution
    sed -i "s/\${best_lam}/${best_lam}/g" tier4_v3_shoes_opt${i}.yaml
    sed -i "s/\${best_ac}/${best_ac}/g" tier4_v3_shoes_opt${i}.yaml
    sed -i "s/\${best_sig}/${best_sig}/g" tier4_v3_shoes_opt${i}.yaml
    
    echo "Created tier4_v3_shoes_opt${i}.yaml"
done

# Also create 3 LCDM chains for comparison
for i in 1 2 3; do
    cp tier4_lcdm_shoes.yaml tier4_lcdm_shoes_clean${i}.yaml
    sed -i "s|chains/tier4_lcdm_shoes|chains/tier4_lcdm_shoes_clean${i}|g" tier4_lcdm_shoes_clean${i}.yaml
    echo "Created tier4_lcdm_shoes_clean${i}.yaml"
done

echo ""
echo "Starting 6 chains (3 V3 + 3 LCDM)..."
rm -f chains/*.locked chains/tier4_*_opt*.txt chains/tier4_*_clean*.txt

for i in 1 2 3; do
    nohup cobaya-run -f tier4_v3_shoes_opt${i}.yaml > logs/v3_opt${i}.log 2>&1 &
    nohup cobaya-run -f tier4_lcdm_shoes_clean${i}.yaml > logs/lcdm_clean${i}.log 2>&1 &
done

sleep 3
echo ""
echo "Active chains:"
ps aux | grep cobaya | grep -v grep | wc -l

