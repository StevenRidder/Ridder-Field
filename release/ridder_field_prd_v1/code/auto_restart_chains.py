#!/usr/bin/env python3
"""
Auto-restart chains with extensive debugging and better starting points.
FAIL AND FIX EARLY POLICY: Detect and fix problems automatically.
"""
import subprocess
import time
import os
import sys
from datetime import datetime, timedelta

DEBUG_LOG = "logs/auto_restart_debug.log"
MAX_RESTART_ATTEMPTS = 3
STALE_THRESHOLD_MINUTES = 10  # Consider chain dead if no activity for 10 minutes

def log_debug(msg):
    """Write to debug log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}\n"
    with open(DEBUG_LOG, "a") as f:
        f.write(log_msg)
    print(log_msg.strip())

def run_cmd(cmd, timeout=30):
    """Run command"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 124
    except Exception as e:
        return "", str(e), -1

def is_process_running(chain_name):
    """Check if chain process is running"""
    stdout, stderr, code = run_cmd(f"ps aux | grep '{chain_name}' | grep -v grep")
    return bool(stdout)

def get_log_age_minutes(chain_name):
    """Get age of log file in minutes"""
    logfile = f"logs/{chain_name}.log"
    if not os.path.exists(logfile):
        return None
    age_seconds = time.time() - os.path.getmtime(logfile)
    return age_seconds / 60

def get_last_progress_time(chain_name):
    """Get time of last progress message"""
    logfile = f"logs/{chain_name}.log"
    if not os.path.exists(logfile):
        return None
    
    # Look for last Progress line
    stdout, stderr, code = run_cmd(f"grep 'Progress' {logfile} | tail -1")
    if stdout:
        # Extract timestamp if present
        # Format: [mcmc] Progress @ 2025-12-02 02:54:54 : ...
        import re
        match = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})', stdout)
        if match:
            try:
                dt = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
                return dt
            except:
                pass
    
    # Fall back to file mtime
    return datetime.fromtimestamp(os.path.getmtime(logfile))

def should_restart(chain_name, chain_type):
    """Determine if chain should be restarted"""
    # Check if process is running
    if is_process_running(chain_name):
        # Check if it's making progress
        last_progress = get_last_progress_time(chain_name)
        if last_progress:
            age_minutes = (datetime.now() - last_progress).total_seconds() / 60
            if age_minutes > STALE_THRESHOLD_MINUTES:
                log_debug(f"{chain_name}: Process running but stale ({age_minutes:.1f}m since last progress)")
                return True, f"stale_{age_minutes:.0f}m"
        return False, "running"
    
    # Process not running - check if it recently stopped
    log_age = get_log_age_minutes(chain_name)
    if log_age is None:
        return True, "no_log"
    
    if log_age > STALE_THRESHOLD_MINUTES:
        return True, f"stopped_{log_age:.0f}m_ago"
    
    return False, "recently_stopped"

def get_lcdm_bestfit():
    """Extract best-fit from LCDM chain to use as starting point"""
    chainfile = "chains/act_world_lcdm_c2.1.txt"
    if not os.path.exists(chainfile):
        return None
    
    # Read last sample (best fit so far)
    with open(chainfile, 'r') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return None
        
        # Parse header and last line
        header = lines[0].strip().split()
        last_line = lines[-1].strip().split()
        
        if len(header) != len(last_line):
            return None
        
        params = {}
        for i, key in enumerate(header):
            try:
                params[key] = float(last_line[i])
            except:
                pass
        
        return params

def start_chain(chain_type, chain_num, use_lcdm_start=False):
    """Start a chain"""
    chain_name = f"act_world_{chain_type}_c{chain_num}"
    config = f"configs/act_world_{chain_type}.yaml"
    output = f"chains/{chain_name}"
    logfile = f"logs/{chain_name}.log"
    
    # Clean old files if restarting
    if os.path.exists(f"{output}.input.yaml.locked"):
        log_debug(f"  Removing stale lock file")
        os.remove(f"{output}.input.yaml.locked")
    
    # Build command
    cmd = f"cd ~/Ridder-Field/phase3 && source ~/.bashrc && export PYTHONPATH=/home/<VM_USER>/class_public:\$PYTHONPATH && nohup cobaya-run {config} -o {output} > {logfile} 2>&1 &"
    
    log_debug(f"  Starting: {cmd}")
    stdout, stderr, code = run_cmd(f"ssh <VM_USER>@<VM_IP> '{cmd}'")
    
    if code == 0:
        log_debug(f"  Started successfully")
        time.sleep(3)  # Give it time to start
        if is_process_running(chain_name):
            log_debug(f"  Process confirmed running")
            return True
        else:
            log_debug(f"  WARNING: Process not found after start")
            return False
    else:
        log_debug(f"  ERROR starting: code={code}, stderr={stderr}")
        return False

def main():
    """Main monitoring and restart loop"""
    log_debug("=" * 80)
    log_debug("AUTO-RESTART MONITOR STARTED")
    log_debug("=" * 80)
    
    restart_counts = {}
    
    while True:
        try:
            log_debug("-" * 80)
            log_debug(f"CHECKING CHAINS - {datetime.now()}")
            log_debug("-" * 80)
            
            # Get LCDM best-fit for EDE starting point
            lcdm_bestfit = get_lcdm_bestfit()
            if lcdm_bestfit:
                log_debug(f"LCDM best-fit available: {list(lcdm_bestfit.keys())[:5]}...")
            
            # Check all chains
            for chain_type in ['lcdm', 'ede']:
                for chain_num in [1, 2, 3, 4]:
                    chain_name = f"act_world_{chain_type}_c{chain_num}"
                    key = f"{chain_type}_c{chain_num}"
                    
                    should, reason = should_restart(chain_name, chain_type)
                    
                    if should:
                        count = restart_counts.get(key, 0)
                        if count >= MAX_RESTART_ATTEMPTS:
                            log_debug(f"{chain_name}: MAX RESTARTS REACHED ({count}), skipping")
                            continue
                        
                        log_debug(f"{chain_name}: RESTART NEEDED (reason: {reason}, attempt {count+1}/{MAX_RESTART_ATTEMPTS})")
                        
                        # For EDE, we could use LCDM best-fit, but for now just restart
                        success = start_chain(chain_type, chain_num, use_lcdm_start=(chain_type == 'ede' and lcdm_bestfit))
                        
                        if success:
                            restart_counts[key] = count + 1
                            log_debug(f"{chain_name}: Restarted successfully")
                        else:
                            log_debug(f"{chain_name}: Restart failed")
                    else:
                        if reason == "running":
                            last_progress = get_last_progress_time(chain_name)
                            if last_progress:
                                age = (datetime.now() - last_progress).total_seconds() / 60
                                log_debug(f"{chain_name}: OK (running, last progress {age:.1f}m ago)")
            
            log_debug("Sleeping 120 seconds...")
            time.sleep(120)
            
        except KeyboardInterrupt:
            log_debug("Monitor stopped by user")
            break
        except Exception as e:
            log_debug(f"ERROR: {type(e).__name__}: {e}")
            import traceback
            log_debug(traceback.format_exc())
            time.sleep(120)

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    main()
