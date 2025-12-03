# Azure Deployment for Ridder Field MCMC

This directory contains Terraform configuration to deploy a compute node on Azure for running MCMC analysis.

---

## Quick Start

### Prerequisites

1. **Azure CLI** installed and logged in:
   ```bash
   # Install Azure CLI (if not already installed)
   brew install azure-cli
   
   # Login to Azure
   az login
   ```

2. **Terraform** installed:
   ```bash
   # Install Terraform (if not already installed)
   brew install terraform
   ```

3. **SSH key** exists at `~/.ssh/id_rsa.pub`:
   ```bash
   # Generate if needed
   ssh-keygen -t rsa -b 4096
   ```

---

## Deployment Steps

### 1. Initialize Terraform

```bash
cd /Users/steveridder/Git/Ridder-Field/azure
terraform init
```

### 2. Review the Plan

```bash
terraform plan
```

This shows what will be created:
- Resource group: `ridder-cosmology-rg`
- Virtual network and subnet
- Public IP address
- Network security group (allows SSH)
- Ubuntu 22.04 VM (Standard_D16s_v3: 16 vCPUs, 64 GB RAM)

### 3. Deploy

```bash
terraform apply
```

Type `yes` when prompted.

**Deployment time:** ~3-5 minutes

### 4. Get Connection Info

```bash
terraform output public_ip_address
terraform output ssh_command
```

### 5. Connect to VM

```bash
ssh <VM_USER>@<PUBLIC_IP>
```

---

## What Gets Installed Automatically

The `provision.sh` script runs on first boot and installs:

- ✅ **Build tools:** GCC, G++, Gfortran, Make, CMake
- ✅ **OpenMPI:** For parallel computing
- ✅ **Python 3:** With NumPy, SciPy, Matplotlib
- ✅ **Cobaya:** MCMC sampler
- ✅ **GetDist:** Analysis tools
- ✅ **FFTW:** Required by CLASS

---

## After Connecting

### 1. Clone Repository

```bash
git clone https://github.com/StevenRidder/Ridder-Field.git
cd Ridder-Field
```

### 2. Compile CLASS

```bash
cd phase2/class
make clean && make -j16  # Uses all 16 cores
cd ../..
```

**Expected time:** ~2 minutes

### 3. Test CLASS

```bash
cd phase3
../phase2/class/class ridder_smoketest_spec.ini
```

**Expected time:** ~30 seconds

### 4. Run MCMC Test

```bash
python3 run_local_mcmc_test.py
```

**Expected time:** ~30-60 minutes (5000 samples)

---

## Cost Estimate

**VM Size:** Standard_D16s_v3
- **Hourly cost:** ~$0.768/hour
- **Daily cost:** ~$18.43/day

**Storage:** 200 GB Premium SSD
- **Monthly cost:** ~$30.72/month

**Total for 1-hour test:** ~$0.80

**Total for 48-hour MCMC:** ~$37

---

## Monitoring

### Check VM Status

```bash
# From your Mac
az vm list -g ridder-cosmology-rg -o table
```

### SSH into VM

```bash
ssh <VM_USER>@$(terraform output -raw public_ip_address)
```

### Monitor Resources

```bash
# On the VM
htop           # CPU and RAM usage
df -h          # Disk space
nvidia-smi     # GPU (if applicable)
```

---

## Cleanup

### Stop VM (keeps data, stops charges)

```bash
az vm deallocate -g ridder-cosmology-rg -n ridder-compute-01
```

### Start VM again

```bash
az vm start -g ridder-cosmology-rg -n ridder-compute-01
```

### Destroy Everything

```bash
terraform destroy
```

Type `yes` when prompted. This deletes:
- VM
- Disks
- Network resources
- Resource group

**⚠️ WARNING:** This is irreversible! Make sure you've downloaded any results first.

---

## Troubleshooting

### Can't SSH?

1. **Check NSG rules:**
   ```bash
   az network nsg rule list -g ridder-cosmology-rg --nsg-name ridder-nsg -o table
   ```

2. **Check VM is running:**
   ```bash
   az vm get-instance-view -g ridder-cosmology-rg -n ridder-compute-01 --query instanceView.statuses
   ```

3. **Check public IP:**
   ```bash
   terraform output public_ip_address
   ```

### CLASS won't compile?

1. **Check OpenMPI is installed:**
   ```bash
   mpicc --version
   ```

2. **Check build tools:**
   ```bash
   gcc --version
   make --version
   ```

3. **Try manual installation:**
   ```bash
   sudo apt-get update
   sudo apt-get install -y build-essential libopenmpi-dev
   ```

### MCMC fails?

1. **Check Cobaya is installed:**
   ```bash
   python3 -c "import cobaya; print(cobaya.__version__)"
   ```

2. **Check CLASS Python wrapper:**
   ```bash
   python3 -c "import classy"
   ```

3. **Reinstall if needed:**
   ```bash
   pip3 install --upgrade cobaya
   ```

---

## Files in This Directory

- **`main.tf`** - Terraform configuration (infrastructure as code)
- **`provision.sh`** - Cloud-init script (runs on first boot)
- **`README.md`** - This file

---

## Next Steps After Successful Test

1. **Download results:**
   ```bash
   # From your Mac
   scp -r <VM_USER>@<IP>:~/Ridder-Field/phase3/chains ./
   ```

2. **Analyze locally:**
   ```bash
   python3 analyze_chains.py
   ```

3. **Scale to cluster** (see `MCMC_ROADMAP.md` Phase 3)

---

## Support

**Issues?** Check:
- `MCMC_ROADMAP.md` - Full deployment guide
- `MCMC_STATUS.md` - Known issues and solutions
- Azure portal: https://portal.azure.com

**Cost concerns?** Remember to:
- Stop VM when not in use (`az vm deallocate`)
- Destroy resources when done (`terraform destroy`)

---

**Status:** Ready to deploy! 🚀

