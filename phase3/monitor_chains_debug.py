#!/usr/bin/env python3
"""
Continuous chain monitoring with extensive debugging.
FAIL AND FIX EARLY POLICY: Surface every problem immediately.
"""
import subprocess
import time
import os
import sys
from datetime import datetime
import json

DEBUG_LOG = "logs/chain_monitor_debug.log"

def log_debug(msg):
    """Write to debug log with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}\n"
    with open(DEBUG_LOG, "a") as f:
        f.write(log_msg)
    print(log_msg.strip())

def run_cmd(cmd, timeout=10):
    """Run command with timeout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 124
    except Exception as e:
        return "", str(e), -1

def get_process_info(pid):
    """Get detailed process info"""
    if not pid:
        return None
    
    # Check if process exists
    stdout, stderr, code = run_cmd(f"ps -p {pid} -o pid,stat,etime,pcpu,pmem,vsz,rss,cmd --no-headers")
    if code != 0 or not stdout:
        return None
    
    parts = stdout.split()
    if len(parts) < 7:
        return None
    
    return {
        'pid': parts[0],
        'state': parts[1],
        'etime': parts[2],
        'cpu': parts[3],
        'mem': parts[4],
        'vsz': parts[5],
        'rss': parts[6],
        'cmd': ' '.join(parts[7:]) if len(parts) > 7 else ''
    }

def check_chain_status(chain_type, chain_num):
    """Check status of a specific chain"""
    chain_name = f"act_world_{chain_type}_c{chain_num}"
    logfile = f"logs/{chain_name}.log"
    chainfile = f"chains/{chain_name}.1.txt"
    progressfile = f"chains/{chain_name}.progress"
    lockfile = f"chains/{chain_name}.input.yaml.locked"
    
    status = {
        'chain': chain_name,
        'timestamp': datetime.now().isoformat(),
        'process_running': False,
        'pid': None,
        'log_exists': os.path.exists(logfile),
        'chain_file_exists': os.path.exists(chainfile),
        'progress_file_exists': os.path.exists(progressfile),
        'lock_exists': os.path.exists(lockfile),
    }
    
    # Find process
    stdout, stderr, code = run_cmd(f"ps aux | grep '{chain_name}' | grep -v grep")
    if stdout:
        lines = stdout.split('\n')
        if lines:
            parts = lines[0].split()
            if len(parts) >= 2:
                pid = parts[1]
                status['process_running'] = True
                status['pid'] = pid
                proc_info = get_process_info(pid)
                if proc_info:
                    status['process_info'] = proc_info
    
    # Check log file
    if status['log_exists']:
        stat = os.stat(logfile)
        status['log_size'] = stat.st_size
        status['log_mtime'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        status['log_age_seconds'] = time.time() - stat.st_mtime
        
        # Get last few lines
        stdout, stderr, code = run_cmd(f"tail -3 {logfile}")
        if stdout:
            status['log_tail'] = stdout.split('\n')
        
        # Check for errors
        stdout, stderr, code = run_cmd(f"grep -E '(ERROR|Exception|Traceback|killed|Killed)' {logfile} | tail -3")
        if stdout:
            status['errors'] = stdout.split('\n')
    
    # Check chain file
    if status['chain_file_exists']:
        stat = os.stat(chainfile)
        status['chain_size'] = stat.st_size
        status['chain_mtime'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        status['chain_age_seconds'] = time.time() - stat.st_mtime
        
        # Count samples
        with open(chainfile, 'r') as f:
            lines = f.readlines()
            status['chain_samples'] = len(lines) - 1  # minus header
    
    # Check progress file
    if status['progress_file_exists']:
        stat = os.stat(progressfile)
        status['progress_mtime'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
        with open(progressfile, 'r') as f:
            progress_lines = f.readlines()
            if len(progress_lines) > 1:
                status['progress_last_line'] = progress_lines[-1].strip()
    
    # Check lock file
    if status['lock_exists']:
        stat = os.stat(lockfile)
        status['lock_age_seconds'] = time.time() - stat.st_mtime
        if status['lock_age_seconds'] > 3600 and not status['process_running']:
            status['stale_lock'] = True
    
    return status

def check_system_resources():
    """Check system resource usage"""
    resources = {
        'timestamp': datetime.now().isoformat(),
    }
    
    # Memory
    stdout, stderr, code = run_cmd("free -m")
    if stdout:
        for line in stdout.split('\n'):
            if 'Mem:' in line:
                parts = line.split()
                if len(parts) >= 4:
                    resources['mem_total_mb'] = parts[1]
                    resources['mem_used_mb'] = parts[2]
                    resources['mem_free_mb'] = parts[3]
            elif 'Swap:' in line:
                parts = line.split()
                if len(parts) >= 4:
                    resources['swap_total_mb'] = parts[1]
                    resources['swap_used_mb'] = parts[2]
    
    # Disk
    stdout, stderr, code = run_cmd("df -h . | tail -1")
    if stdout:
        parts = stdout.split()
        if len(parts) >= 5:
            resources['disk_used'] = parts[2]
            resources['disk_avail'] = parts[3]
            resources['disk_percent'] = parts[4]
    
    # Load average
    stdout, stderr, code = run_cmd("uptime")
    if stdout:
        resources['uptime'] = stdout
    
    return resources

def main():
    """Main monitoring loop"""
    log_debug("=" * 80)
    log_debug("CHAIN MONITOR STARTED")
    log_debug("=" * 80)
    
    # Track previous states
    prev_states = {}
    
    while True:
        try:
            log_debug("-" * 80)
            log_debug(f"MONITORING CYCLE - {datetime.now()}")
            log_debug("-" * 80)
            
            # Check system resources
            resources = check_system_resources()
            log_debug(f"System: MEM={resources.get('mem_used_mb')}/{resources.get('mem_total_mb')}MB, "
                     f"DISK={resources.get('disk_percent')}")
            
            # Check all chains
            for chain_type in ['lcdm', 'ede']:
                for chain_num in [1, 2, 3, 4]:
                    status = check_chain_status(chain_type, chain_num)
                    
                    # Detect state changes
                    chain_key = f"{chain_type}_c{chain_num}"
                    prev_state = prev_states.get(chain_key)
                    
                    # Log current state
                    if status['process_running']:
                        proc = status.get('process_info', {})
                        log_debug(f"{chain_key}: RUNNING PID={status['pid']}, "
                                 f"CPU={proc.get('cpu', '?')}%, MEM={proc.get('mem', '?')}%, "
                                 f"RSS={proc.get('rss', '?')}KB, ETIME={proc.get('etime', '?')}")
                    else:
                        log_debug(f"{chain_key}: NOT RUNNING")
                        if status.get('log_exists'):
                            log_debug(f"  Log age: {status.get('log_age_seconds', 0):.0f}s, "
                                     f"last modified: {status.get('log_mtime', '?')}")
                            if status.get('log_age_seconds', 0) > 300:  # 5 minutes
                                log_debug(f"  WARNING: Chain stopped {status.get('log_age_seconds', 0)/60:.1f} minutes ago")
                    
                    # Detect process death
                    if prev_state and prev_state.get('process_running') and not status['process_running']:
                        log_debug(f"  ALERT: {chain_key} PROCESS DIED!")
                        log_debug(f"    Previous PID: {prev_state.get('pid')}")
                        log_debug(f"    Last log line: {status.get('log_tail', ['?'])[-1] if status.get('log_tail') else '?'}")
                        if status.get('errors'):
                            log_debug(f"    ERRORS FOUND: {status.get('errors')}")
                    
                    # Detect new samples
                    if status.get('chain_file_exists'):
                        samples = status.get('chain_samples', 0)
                        prev_samples = prev_state.get('chain_samples', 0) if prev_state else 0
                        if samples > prev_samples:
                            log_debug(f"  {chain_key}: New samples! {prev_samples} -> {samples}")
                    
                    # Check for stale locks
                    if status.get('stale_lock'):
                        log_debug(f"  WARNING: {chain_key} has stale lock file ({status.get('lock_age_seconds', 0)/3600:.1f}h old)")
                    
                    prev_states[chain_key] = status
            
            # Check for OOM kills
            stdout, stderr, code = run_cmd("dmesg 2>/dev/null | tail -5 | grep -i 'oom.*killed'")
            if stdout:
                log_debug(f"ALERT: Recent OOM kills detected: {stdout}")
            
            log_debug("Sleeping 60 seconds...")
            time.sleep(60)
            
        except KeyboardInterrupt:
            log_debug("Monitor stopped by user")
            break
        except Exception as e:
            log_debug(f"ERROR in monitor loop: {type(e).__name__}: {e}")
            import traceback
            log_debug(traceback.format_exc())
            time.sleep(60)

if __name__ == "__main__":
    # Ensure log directory exists
    os.makedirs("logs", exist_ok=True)
    main()
