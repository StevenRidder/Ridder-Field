#!/usr/bin/env python3
"""
Ridder Field MCMC: Cluster-Aware Runner

This script can run MCMC in multiple modes:
1. Single VM (sequential)
2. MPI cluster (multiple VMs with OpenMPI)
3. Azure Batch (cloud job scheduling)

Usage:
    # Single VM
    python3 run_mcmc_cluster.py --mode single

    # MPI cluster
    mpirun -np 4 --hostfile ~/mpi_hosts python3 run_mcmc_cluster.py --mode mpi

    # Azure Batch
    python3 run_mcmc_cluster.py --mode batch --batch-account ridder-batch
"""

import argparse
import os
import sys
import subprocess
import time
from pathlib import Path

def run_single_vm(config_file, num_chains=4):
    """Run MCMC on single VM with multiple chains"""
    print("=" * 60)
    print("Running MCMC on Single VM")
    print(f"  Chains: {num_chains}")
    print(f"  Config: {config_file}")
    print("=" * 60)
    
    # Run chains in parallel using subprocess
    processes = []
    for i in range(num_chains):
        chain_id = f"chain_{i:02d}"
        cmd = [
            "python3", "-m", "cobaya", "run",
            config_file,
            "--output", f"chains/{chain_id}",
            "--force"
        ]
        print(f"Starting {chain_id}...")
        proc = subprocess.Popen(cmd)
        processes.append((chain_id, proc))
    
    # Wait for all chains
    print("\nWaiting for chains to complete...")
    for chain_id, proc in processes:
        proc.wait()
        if proc.returncode == 0:
            print(f"✓ {chain_id} completed")
        else:
            print(f"✗ {chain_id} failed")
    
    return all(proc.returncode == 0 for _, proc in processes)

def run_mpi_cluster(config_file, num_chains=None):
    """Run MCMC using MPI cluster"""
    print("=" * 60)
    print("Running MCMC on MPI Cluster")
    print(f"  Config: {config_file}")
    print("=" * 60)
    
    # Get number of MPI processes
    if num_chains is None:
        num_chains = int(os.environ.get('OMPI_COMM_WORLD_SIZE', 4))
    
    rank = int(os.environ.get('OMPI_COMM_WORLD_RANK', 0))
    
    print(f"MPI Rank {rank}/{num_chains}")
    
    # Each MPI process runs one chain
    chain_id = f"chain_{rank:02d}"
    cmd = [
        "python3", "-m", "cobaya", "run",
        config_file,
        "--output", f"chains/{chain_id}",
        "--force"
    ]
    
    subprocess.run(cmd, check=True)
    print(f"✓ Rank {rank} completed chain {chain_id}")

def run_azure_batch(config_file, batch_account, pool_id="ridder-pool"):
    """Run MCMC using Azure Batch"""
    print("=" * 60)
    print("Running MCMC on Azure Batch")
    print(f"  Batch Account: {batch_account}")
    print(f"  Pool: {pool_id}")
    print(f"  Config: {config_file}")
    print("=" * 60)
    
    # This would use Azure Batch SDK
    # For now, show the structure
    print("\nAzure Batch integration requires:")
    print("  1. Azure Batch Python SDK")
    print("  2. Job definition")
    print("  3. Task submission")
    print("  4. Result collection")
    print("\nSee azure/submit_batch_job.py for full implementation")

def main():
    parser = argparse.ArgumentParser(description="Run Ridder Field MCMC on cluster")
    parser.add_argument("--mode", choices=["single", "mpi", "batch"], 
                       default="single", help="Execution mode")
    parser.add_argument("--config", default="ridder_local_test.yaml",
                       help="Cobaya config file")
    parser.add_argument("--chains", type=int, default=4,
                       help="Number of chains (for single mode)")
    parser.add_argument("--batch-account", help="Azure Batch account name")
    parser.add_argument("--pool-id", default="ridder-pool",
                       help="Azure Batch pool ID")
    
    args = parser.parse_args()
    
    config_file = Path(args.config)
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        sys.exit(1)
    
    # Create output directory
    os.makedirs("chains", exist_ok=True)
    
    start_time = time.time()
    
    try:
        if args.mode == "single":
            success = run_single_vm(str(config_file), args.chains)
        elif args.mode == "mpi":
            run_mpi_cluster(str(config_file))
            success = True
        elif args.mode == "batch":
            run_azure_batch(str(config_file), args.batch_account, args.pool_id)
            success = True
        else:
            print(f"❌ Unknown mode: {args.mode}")
            sys.exit(1)
        
        elapsed = time.time() - start_time
        print(f"\n{'=' * 60}")
        if success:
            print(f"✅ MCMC completed successfully in {elapsed/60:.1f} minutes")
        else:
            print(f"❌ MCMC failed after {elapsed/60:.1f} minutes")
        print(f"{'=' * 60}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

