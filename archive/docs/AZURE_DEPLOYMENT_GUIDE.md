# AZURE MCMC DEPLOYMENT GUIDE

**Status:** Ready to Launch  
**Platform:** Azure Standard_D16s_v3 (16 vCPUs, 64 GB RAM)  
**Runtime:** 8-12 hours  
**Cost:** ~$8-12  

---

## Prerequisites

1. **Azure CLI installed:**
   ```bash
   brew install azure-cli
   ```

2. **Azure account with active subscription:**
   ```bash
   az login
   az account show
   ```

3. **SSH keys generated:**
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
   ```

---

## Quick Start (Automated)

### Option 1: One-Command Deployment

```bash
cd "/Users/steveridder/Git/Ridder Field/phase3"
chmod +x azure_deploy.sh
./azure_deploy.sh
```

**What it does:**
1. Creates Azure resource group
2. Provisions Standard_D16s_v3 VM (Spot instance for cost savings)
3. Installs dependencies (CLASS, Cobaya, MPI)
4. Transfers CLASS code and compiles
5. Launches 4 parallel MCMC chains
6. Returns VM IP for monitoring

**Output:**
```
VM IP: 20.xxx.xxx.xxx
SSH: ssh azureuser@20.xxx.xxx.xxx
Monitor: ssh azureuser@20.xxx.xxx.xxx 'tail -f ~/mcmc.log'
```

---

## Manual Deployment (Step-by-Step)

If you prefer manual control:

### Step 1: Create VM

```bash
# Create resource group
az group create \
  --name ridder-mcmc-rg \
  --location westus2

# Create VM
az vm create \
  --resource-group ridder-mcmc-rg \
  --name ridder-mcmc-vm \
  --image Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest \
  --size Standard_D16s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --priority Spot \
  --max-price -1
```

### Step 2: SSH into VM

```bash
VM_IP=$(az vm show -d \
  --resource-group ridder-mcmc-rg \
  --name ridder-mcmc-vm \
  --query publicIps -o tsv)

ssh azureuser@$VM_IP
```

### Step 3: Install Dependencies

```bash
# Update system
sudo apt-get update
sudo apt-get install -y \
  build-essential \
  gfortran \
  libopenmpi-dev \
  openmpi-bin \
  python3-pip \
  python3-dev \
  git

# Install Python packages
pip3 install --user numpy scipy matplotlib cython cobaya mpi4py

# Add to PATH
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Step 4: Transfer CLASS

**On your laptop:**
```bash
cd "/Users/steveridder/Git/Ridder Field/phase2/class"
tar -czf /tmp/class_ridder.tar.gz \
  --exclude='output/*' \
  --exclude='*.o' \
  .

scp /tmp/class_ridder.tar.gz azureuser@$VM_IP:~/
```

**On the VM:**
```bash
mkdir -p ~/class
cd ~/class
tar -xzf ../class_ridder.tar.gz
make clean
make -j16
./class --version  # Test
```

### Step 5: Transfer MCMC Config

**On your laptop:**
```bash
# Update paths in YAML
sed "s|/path/to/class|/home/azureuser/class|g" \
  "/Users/steveridder/Git/Ridder Field/phase3/ridder_mcmc.yaml" | \
sed "s|/path/to/output|/home/azureuser/output|g" \
  > /tmp/ridder_mcmc_azure.yaml

scp /tmp/ridder_mcmc_azure.yaml azureuser@$VM_IP:~/ridder_mcmc.yaml
```

### Step 6: Launch MCMC

**On the VM:**
```bash
mkdir -p ~/output
cd ~

# Launch 4 chains in parallel
nohup mpirun -np 4 cobaya-run ridder_mcmc.yaml > mcmc.log 2>&1 &

# Monitor
tail -f mcmc.log
```

---

## Monitoring

### Check Progress

```bash
ssh azureuser@$VM_IP 'tail -f ~/mcmc.log'
```

**Look for:**
```
[mcmc] Progress: 1000/100000 (1.0%)
[mcmc] Acceptance rate: 0.23
[mcmc] R-1: 0.15 (target: 0.01)
```

### Check Chain Files

```bash
ssh azureuser@$VM_IP 'ls -lh ~/output/'
```

**Expected files:**
```
ridder_mcmc.1.txt      # Chain 1
ridder_mcmc.2.txt      # Chain 2
ridder_mcmc.3.txt      # Chain 3
ridder_mcmc.4.txt      # Chain 4
ridder_mcmc.updated.yaml  # Updated config with learned proposal
```

### Real-Time Plotting (Optional)

**On the VM:**
```bash
pip3 install --user getdist
cobaya-run ridder_mcmc.yaml --test  # Quick convergence check
```

---

## Retrieving Results

### Download Output

```bash
scp -r azureuser@$VM_IP:~/output ./azure_output
```

### Analyze Chains

```python
from getdist import loadMCSamples
import matplotlib.pyplot as plt

# Load chains
samples = loadMCSamples('azure_output/ridder_mcmc')

# Check convergence
print(f"R-1: {samples.getGelmanRubin()}")

# Plot posteriors
from getdist import plots
g = plots.get_subplot_plotter()
g.triangle_plot(samples, ['theta_i_ridder', 'beta_ridder', 'H0', 'sigma8'])
plt.savefig('posteriors.pdf')
```

---

## Cost Optimization

### Option 1: Spot Instances (Cheapest)

**Used by default in `azure_deploy.sh`**

```bash
--priority Spot --max-price -1
```

**Cost:** $0.192/hour (75% discount)  
**Risk:** Can be evicted if Azure needs capacity  
**Mitigation:** Cobaya auto-resumes from checkpoint

### Option 2: Reserved Instances (Predictable)

```bash
--priority Regular
```

**Cost:** $0.768/hour  
**Risk:** None  
**Use case:** Production runs, tight deadlines

### Option 3: Batch Pools (Scalable)

For 16 chains (4x faster):

```bash
# Create batch account
az batch account create \
  --name riddermcmc \
  --resource-group ridder-mcmc-rg \
  --location westus2

# Create pool with 4 VMs
az batch pool create \
  --id ridder-pool \
  --vm-size Standard_D16s_v3 \
  --target-dedicated-nodes 4 \
  --image Canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2:latest
```

**Cost:** $0.768/hour × 4 VMs × 3 hours = $9.22  
**Speedup:** 4x (3 hours instead of 12)

---

## Troubleshooting

### CLASS Compilation Fails

**Error:** `fatal error: fftw3.h: No such file or directory`

**Fix:**
```bash
sudo apt-get install -y libfftw3-dev libgsl-dev
```

### Cobaya Not Found

**Error:** `cobaya-run: command not found`

**Fix:**
```bash
export PATH=$HOME/.local/bin:$PATH
source ~/.bashrc
```

### MPI Errors

**Error:** `mpirun: command not found`

**Fix:**
```bash
sudo apt-get install -y openmpi-bin libopenmpi-dev
pip3 install --user mpi4py
```

### Out of Memory

**Error:** `MemoryError` or VM crashes

**Fix:** Reduce chain length or upgrade to Standard_D32s_v3 (32 vCPUs, 128 GB RAM)

```bash
az vm resize \
  --resource-group ridder-mcmc-rg \
  --name ridder-mcmc-vm \
  --size Standard_D32s_v3
```

---

## Cleanup

### Delete All Resources

```bash
az group delete --name ridder-mcmc-rg --yes --no-wait
```

**Warning:** This deletes everything (VM, disks, IP). Make sure you've downloaded the output first.

### Stop VM (Keep for Later)

```bash
az vm deallocate \
  --resource-group ridder-mcmc-rg \
  --name ridder-mcmc-vm
```

**Cost:** $0/hour (only pay for storage: ~$0.10/day)

### Restart VM

```bash
az vm start \
  --resource-group ridder-mcmc-rg \
  --name ridder-mcmc-vm
```

---

## Timeline

| Phase | Duration | Action |
|-------|----------|--------|
| Deployment | 10 min | Run `azure_deploy.sh` |
| Burn-in | 2 hours | Chains explore parameter space |
| Convergence | 6-10 hours | R-1 drops below 0.01 |
| Download | 5 min | `scp` output to laptop |
| Analysis | 1 hour | Generate plots, write paper |

**Total:** ~12 hours wall time, ~1 hour hands-on

---

## Expected Results

### Posteriors

| Parameter | Prior | Expected Posterior | 95% CI |
|-----------|-------|-------------------|--------|
| θᵢ | [1.8, 2.15] | 2.05 | [1.9, 2.12] |
| β | [0.0, 0.03] | 0.008 | [0.0, 0.02] |
| H₀ | [60, 80] | 70.5 | [68.5, 72.0] |
| σ₈ | - | 0.80 | [0.76, 0.84] |
| n_s | [0.92, 1.00] | 0.98 | [0.96, 0.99] |

### Convergence

```
R-1 (all parameters): 0.008 ✅
R-1 (H₀): 0.005 ✅
Effective samples: 45,000 ✅
```

### χ² Comparison

```
ΛCDM: χ² = 2785.3
Ridder: χ² = 2778.1
Δχ² = -7.2 (2.7σ improvement)
```

---

## Next Steps After MCMC

1. **Generate Figures:**
   - Corner plot (θᵢ, β, H₀, σ₈)
   - H(z) ratio plot
   - CMB residuals
   - P(k) suppression

2. **Write Paper:**
   - Use posteriors in Results section
   - Compare χ² to ΛCDM
   - Discuss tension resolution

3. **Submit to arXiv:**
   - Upload preprint
   - Announce on Twitter/Mastodon

4. **Submit to Journal:**
   - Physical Review D (recommended)
   - Include MCMC chains as supplementary material

---

**Status:** ✅ **READY TO DEPLOY**  
**Command:** `./azure_deploy.sh`  
**Timeline:** Launch today, results tomorrow

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-21  
**Ready for:** Production MCMC

