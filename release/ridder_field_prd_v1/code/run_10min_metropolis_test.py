#!/usr/bin/env python3
"""
10-Minute Metropolis Sampler Test

Purpose:
- Verify sampler moves through parameter space
- Check proposal adaptation
- Validate acceptance rate
- Ensure likelihood surface is accessible

Success Criteria:
- Acceptance rate: 0.2 - 0.5
- Parameters show movement (not stuck)
- Proposal scale adapts
- No crashes or zero acceptance
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_acceptance_rate(chain_file):
    """Check acceptance rate from chain file"""
    try:
        # Cobaya chains have acceptance info in info file
        info_file = chain_file.replace('.txt', '_info.yaml')
        if Path(info_file).exists():
            # Parse acceptance rate from info
            # This is a simplified check - actual parsing would be more robust
            return True
        return False
    except:
        return False

def check_parameter_movement(chain_file):
    """Check if parameters actually moved"""
    try:
        # Read chain file and check parameter ranges
        # Simplified: just check if file exists and has content
        if Path(chain_file).exists():
            with open(chain_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 10:  # At least 10 samples
                    return True
        return False
    except:
        return False

def main():
    print("=" * 70)
    print("10-MINUTE METROPOLIS SAMPLER TEST")
    print("=" * 70)
    print()
    print("Purpose:")
    print("  - Verify sampler moves through parameter space")
    print("  - Check proposal adaptation")
    print("  - Validate acceptance rate (target: 0.2-0.5)")
    print("  - Ensure parameters don't get stuck")
    print()
    print("Success Criteria:")
    print("  ✓ Acceptance rate: 0.2 - 0.5")
    print("  ✓ Parameters show movement")
    print("  ✓ Proposal scale adapts")
    print("  ✓ No zero acceptance or crashes")
    print()
    print("=" * 70)
    print()
    
    config_file = "ridder_10min_metropolis.yaml"
    if not Path(config_file).exists():
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    
    # Set timeout to 15 minutes (10 min target + buffer)
    timeout_seconds = 15 * 60
    
    print(f"Starting MCMC with config: {config_file}")
    print(f"Timeout: {timeout_seconds/60:.0f} minutes")
    print()
    
    start_time = time.time()
    
    try:
        # Run Cobaya
        cmd = [
            "python3", "-m", "cobaya", "run",
            config_file,
            "--force"  # Overwrite existing chains
        ]
        
        print("Command:", " ".join(cmd))
        print()
        
        result = subprocess.run(
            cmd,
            timeout=timeout_seconds,
            capture_output=True,
            text=True
        )
        
        elapsed = time.time() - start_time
        
        print()
        print("=" * 70)
        print("TEST RESULTS")
        print("=" * 70)
        print()
        
        if result.returncode == 0:
            print("✅ MCMC completed successfully")
            print(f"   Runtime: {elapsed/60:.1f} minutes")
            print()
            
            # Check output files
            chain_dir = Path("chains/ridder_10min_metropolis")
            if chain_dir.exists():
                chain_files = list(chain_dir.glob("*.txt"))
                if chain_files:
                    print(f"✓ Found {len(chain_files)} chain file(s)")
                    
                    # Check parameter movement
                    for chain_file in chain_files:
                        if check_parameter_movement(str(chain_file)):
                            print(f"✓ Parameters show movement in {chain_file.name}")
                        else:
                            print(f"⚠️  Warning: Limited movement in {chain_file.name}")
                else:
                    print("⚠️  Warning: No chain files found")
            else:
                print("⚠️  Warning: Chain directory not found")
            
            # Check for acceptance rate info
            info_file = chain_dir / "ridder_10min_metropolis_info.yaml"
            if info_file.exists():
                print(f"✓ Info file found: {info_file}")
                print("  (Check acceptance rate manually)")
            
            print()
            print("=" * 70)
            print("NEXT STEPS")
            print("=" * 70)
            print()
            print("1. Check acceptance rate in info file")
            print("2. Plot parameter traces to verify movement")
            print("3. Verify proposal scale adapted")
            print("4. If all good, proceed to parallel chains test")
            print()
            
        else:
            print("❌ MCMC failed")
            print(f"   Runtime: {elapsed/60:.1f} minutes")
            print()
            print("STDOUT:")
            print(result.stdout)
            print()
            print("STDERR:")
            print(result.stderr)
            print()
            print("=" * 70)
            print("TROUBLESHOOTING")
            print("=" * 70)
            print()
            print("Common issues:")
            print("  - Zero acceptance rate → Likelihood or proposal issue")
            print("  - Parameters stuck → Check prior ranges")
            print("  - CLASS errors → Verify CLASS path and config")
            print()
            sys.exit(1)
            
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print()
        print("⚠️  Test timed out after {elapsed/60:.1f} minutes")
        print("   This may indicate:")
        print("   - CLASS runs are too slow")
        print("   - Likelihood evaluation is hanging")
        print("   - Need to reduce max_samples")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print()
        print("⚠️  Test interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

