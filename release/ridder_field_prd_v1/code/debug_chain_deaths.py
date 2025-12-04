#!/usr/bin/env python3
"""
Debug script to investigate why ACT chains are dying silently.
FAIL AND FIX EARLY POLICY: Surface all problems immediately.
"""
import subprocess
import sys
import os
from datetime import datetime

def run_cmd(cmd):
    """Run command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", 124

def main():
    print("=" * 80)
    print("ACT CHAIN DEATH INVESTIGATION")
    print("=" * 80)
    print(f"Time: {datetime.now()}")
    print()
    
    # 1. Check all ACT world processes
    print("1. RUNNING PROCESSES")
    print("-" * 80)
    stdout, stderr, code = run_cmd("ps aux | grep 'act_world' | grep -v grep")
    if stdout:
        print(stdout)
        lines = stdout.split('\n')
        print(f"\nTotal running: {len(lines)}")
        for line in lines:
            parts = line.split()
            if len(parts) >= 11:
                pid = parts[1]
                cpu = parts[2]
                mem = parts[3]
                vsz = parts[4]
                rss = parts[5]
                print(f"  PID {pid}: CPU={cpu}%, MEM={mem}%, VSZ={vsz}KB, RSS={rss}KB")
    else:
        print("NO ACT WORLD PROCESSES RUNNING")
    print()
    
    # 2. Check system logs for kills
    print("2. SYSTEM LOGS - OOM KILLS / SIGNALS")
    print("-" * 80)
    stdout, stderr, code = run_cmd("dmesg 2>/dev/null | tail -50 | grep -iE 'oom|killed|act_world|cobaya' || journalctl -n 100 2>/dev/null | grep -iE 'oom|killed|act_world|cobaya' | tail -20")
    if stdout:
        print(stdout)
    else:
        print("No OOM/kill evidence in system logs")
    print()
    
    # 3. Check each chain's log for errors
    print("3. CHAIN LOG ERRORS")
    print("-" * 80)
    for chain_type in ['lcdm', 'ede']:
        for chain_num in [1, 2, 3, 4]:
            logfile = f"logs/act_world_{chain_type}_c{chain_num}.log"
            if os.path.exists(logfile):
                print(f"\n{chain_type}_c{chain_num}:")
                # Check for errors
                stdout, stderr, code = run_cmd(f"grep -E '(ERROR|Exception|Traceback|failed|Failed|Fatal|killed|Killed|Segmentation|Abort|timeout|Timeout)' {logfile} | tail -5")
                if stdout:
                    print(f"  ERRORS FOUND:")
                    for line in stdout.split('\n'):
                        print(f"    {line}")
                else:
                    print(f"  No explicit errors")
                
                # Check last 5 lines
                stdout, stderr, code = run_cmd(f"tail -5 {logfile}")
                if stdout:
                    print(f"  Last 5 lines:")
                    for line in stdout.split('\n'):
                        print(f"    {line}")
                
                # Check file size and modification time
                stat = os.stat(logfile)
                size_kb = stat.st_size / 1024
                mtime = datetime.fromtimestamp(stat.st_mtime)
                print(f"  Log size: {size_kb:.1f} KB, Last modified: {mtime}")
    print()
    
    # 4. Check chain files
    print("4. CHAIN FILES STATUS")
    print("-" * 80)
    for chain_type in ['lcdm', 'ede']:
        for chain_num in [1, 2, 3, 4]:
            chainfile = f"chains/act_world_{chain_type}_c{chain_num}.1.txt"
            progressfile = f"chains/act_world_{chain_type}_c{chain_num}.progress"
            
            if os.path.exists(chainfile):
                stat = os.stat(chainfile)
                size_kb = stat.st_size / 1024
                mtime = datetime.fromtimestamp(stat.st_mtime)
                with open(chainfile, 'r') as f:
                    lines = len(f.readlines())
                print(f"{chain_type}_c{chain_num}.1.txt: {lines} lines, {size_kb:.1f} KB, modified {mtime}")
            else:
                print(f"{chain_type}_c{chain_num}.1.txt: NOT FOUND")
            
            if os.path.exists(progressfile):
                stat = os.stat(progressfile)
                mtime = datetime.fromtimestamp(stat.st_mtime)
                with open(progressfile, 'r') as f:
                    progress_lines = f.readlines()
                if len(progress_lines) > 1:
                    last_progress = progress_lines[-1].strip()
                    print(f"  Progress: {last_progress}")
                print(f"  Progress file modified: {mtime}")
    print()
    
    # 5. Check memory usage
    print("5. SYSTEM RESOURCES")
    print("-" * 80)
    stdout, stderr, code = run_cmd("free -h")
    print(stdout)
    print()
    
    stdout, stderr, code = run_cmd("df -h . | tail -1")
    print(f"Disk space: {stdout}")
    print()
    
    # 6. Check for zombie processes
    print("6. ZOMBIE PROCESSES")
    print("-" * 80)
    stdout, stderr, code = run_cmd("ps aux | grep -E 'act_world|cobaya' | grep -E '<defunct>|Z'")
    if stdout:
        print("ZOMBIES FOUND:")
        print(stdout)
    else:
        print("No zombie processes")
    print()
    
    # 7. Check process limits
    print("7. PROCESS LIMITS (for current user)")
    print("-" * 80)
    stdout, stderr, code = run_cmd("ulimit -a")
    print(stdout)
    print()
    
    # 8. Check for stuck file locks
    print("8. FILE LOCKS")
    print("-" * 80)
    for chain_type in ['lcdm', 'ede']:
        for chain_num in [1, 2, 3, 4]:
            lockfile = f"chains/act_world_{chain_type}_c{chain_num}.input.yaml.locked"
            if os.path.exists(lockfile):
                stat = os.stat(lockfile)
                mtime = datetime.fromtimestamp(stat.st_mtime)
                size = stat.st_size
                print(f"{chain_type}_c{chain_num}.locked: {size} bytes, modified {mtime}")
                # Check if lock is stale (older than 1 hour)
                age_seconds = (datetime.now().timestamp() - stat.st_mtime)
                if age_seconds > 3600:
                    print(f"  WARNING: Lock file is {age_seconds/3600:.1f} hours old (possibly stale)")
    print()
    
    # 9. Check Python processes
    print("9. ALL PYTHON PROCESSES")
    print("-" * 80)
    stdout, stderr, code = run_cmd("ps aux | grep python | grep -v grep | head -20")
    if stdout:
        print(stdout)
        lines = stdout.split('\n')
        print(f"\nTotal Python processes: {len(lines)}")
    else:
        print("No Python processes found")
    print()
    
    print("=" * 80)
    print("INVESTIGATION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
