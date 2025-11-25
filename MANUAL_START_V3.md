# Manual V3 MCMC Start Instructions

## Problem
SSH commands through automation tools are timing out. Need manual execution.

## Diagnosis Required
**Please run these commands in your terminal to diagnose:**

```bash
# 1. Test VM connectivity
ping -c 3 172.174.34.125

# 2. Test SSH connection
ssh ridderadmin@172.174.34.125 'echo "Connected successfully"'

# 3. If SSH works, check VM status
ssh ridderadmin@172.174.34.125 'uptime && df -h && free -h'
```

## If SSH Works: Start the MCMC Runs

```bash
# Open terminal and run each command:

# Start Baseline (no H0 prior)
ssh ridderadmin@172.174.34.125 << 'EOF'
cd ~/Ridder-Field/phase3
mkdir -p logs chains
nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &
echo "Baseline started: PID $!"
EOF

# Start TRGB (H0 = 69.8 ± 1.7)
ssh ridderadmin@172.174.34.125 << 'EOF'
cd ~/Ridder-Field/phase3
nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &
echo "TRGB started: PID $!"
EOF

# Start SH0ES (H0 = 73.0 ± 1.0)
ssh ridderadmin@172.174.34.125 << 'EOF'
cd ~/Ridder-Field/phase3
nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &
echo "SH0ES started: PID $!"
EOF
```

## Wait 30 seconds, then check status:

```bash
ssh ridderadmin@172.174.34.125 << 'EOF'
cd ~/Ridder-Field/phase3
echo "=== Running Processes ==="
ps aux | grep cobaya-run | grep -v grep

echo ""
echo "=== Log Files ==="
ls -lh logs/

echo ""
echo "=== Baseline Log (last 20 lines) ==="
tail -20 logs/v3_baseline.log 2>/dev/null || echo "Not started yet"

echo ""
echo "=== TRGB Log (last 20 lines) ==="
tail -20 logs/v3_trgb.log 2>/dev/null || echo "Not started yet"

echo ""
echo "=== SH0ES Log (last 20 lines) ==="
tail -20 logs/v3_shoes.log 2>/dev/null || echo "Not started yet"
EOF
```

## Monitor Progress

```bash
# Use the status checker (once SSH is working)
python3 check_v3_status.py

# Or SSH directly
ssh ridderadmin@172.174.34.125
cd ~/Ridder-Field/phase3
tail -f logs/v3_baseline.log  # Watch in real-time
```

## If SSH Doesn't Work

Possible issues:
1. **VM is stopped**: Check Azure portal, start the VM
2. **Network issue**: Check firewall/security groups allow SSH (port 22)
3. **SSH key issue**: Verify your SSH key is still valid
4. **IP changed**: VM might have a different IP now

Check Azure portal: https://portal.azure.com
- Resource Group: (check your Azure config)
- VM Name: (check your Azure config)
- Verify Status: "Running"
- Verify Public IP: 172.174.34.125

## Expected Behavior

Once running, you should see:
- 3 processes running (one per YAML file)
- Each process spawns 4 Cobaya chains
- Log files growing in `logs/` directory
- Chain files appearing in `chains/` directory
- Each run takes ~3-5 days to complete 10K samples per chain

## Error: The automation layer is failing, manual intervention required.

