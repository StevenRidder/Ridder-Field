#!/usr/bin/env python3
"""
Memory Safety Audit for Ridder Field CLASS Code
Read-only analysis - no changes made
"""
import re
import os

def audit_file(filepath, issues):
    """Audit a C file for common memory safety issues."""
    if not os.path.exists(filepath):
        return
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    filename = os.path.basename(filepath)
    
    for i, line in enumerate(lines, 1):
        # Check for array access without bounds checking
        # Pattern: array[index] where index might be unvalidated
        if re.search(r'\[.*index.*\]', line) and 'class_test' not in line:
            # Check if there's validation nearby
            context_start = max(0, i-5)
            context_end = min(len(lines), i+5)
            context = ''.join(lines[context_start:context_end])
            
            # Look for common unsafe patterns
            if re.search(r'pvecback\[.*index.*\]', line):
                if 'class_test' not in context.lower() and 'if' not in context.lower():
                    issues.append({
                        'file': filename,
                        'line': i,
                        'type': 'Unvalidated array access',
                        'code': line.strip(),
                        'severity': 'HIGH'
                    })
        
        # Check for division by zero
        if '/' in line and not line.strip().startswith('//'):
            # Look for division by variables that might be zero
            if re.search(r'/\s*(phi_prime|rho_cdm|a|a_prime_over_a|M_Pl)', line):
                if 'if' not in line and '?' not in line:
                    issues.append({
                        'file': filename,
                        'line': i,
                        'type': 'Potential division by zero',
                        'code': line.strip(),
                        'severity': 'MEDIUM'
                    })
        
        # Check for uninitialized pointer access
        if '->' in line and 'if' not in line and '?' not in line:
            if re.search(r'pba->|pv->|ppw->', line):
                # Check if pointer is validated
                context_start = max(0, i-10)
                context = ''.join(lines[context_start:i])
                if 'if' not in context and 'class_test' not in context:
                    issues.append({
                        'file': filename,
                        'line': i,
                        'type': 'Potential uninitialized pointer access',
                        'code': line.strip(),
                        'severity': 'MEDIUM'
                    })
        
        # Check for buffer overflow patterns
        if re.search(r'pvecback\[.*\+.*\]|y\[.*\+.*\]', line):
            issues.append({
                'file': filename,
                'line': i,
                'type': 'Array access with arithmetic (check bounds)',
                'code': line.strip(),
                'severity': 'MEDIUM'
            })
        
        # Check for large stack allocations
        if re.search(r'static.*\[.*\d{4,}', line):
            issues.append({
                'file': filename,
                'line': i,
                'type': 'Large static array (potential stack overflow)',
                'code': line.strip(),
                'severity': 'LOW'
            })

def main():
    issues = []
    
    # Files to audit
    files_to_check = [
        'phase2/class/source/background.c',
        'phase2/class/source/perturbations.c',
    ]
    
    print("="*80)
    print("RIDDER FIELD MEMORY SAFETY AUDIT")
    print("="*80)
    print()
    print("Scanning for common memory safety issues...")
    print()
    
    for filepath in files_to_check:
        if os.path.exists(filepath):
            print(f"Auditing {filepath}...")
            audit_file(filepath, issues)
        else:
            print(f"WARNING: {filepath} not found")
    
    print()
    print("="*80)
    print("AUDIT RESULTS")
    print("="*80)
    print()
    
    if not issues:
        print("✓ No obvious memory safety issues found")
        return
    
    # Group by severity
    high = [i for i in issues if i['severity'] == 'HIGH']
    medium = [i for i in issues if i['severity'] == 'MEDIUM']
    low = [i for i in issues if i['severity'] == 'LOW']
    
    if high:
        print(f"🔴 HIGH SEVERITY: {len(high)} issues")
        print("-"*80)
        for issue in high[:10]:  # Show first 10
            print(f"{issue['file']}:{issue['line']} - {issue['type']}")
            print(f"  {issue['code'][:70]}")
            print()
    
    if medium:
        print(f"🟡 MEDIUM SEVERITY: {len(medium)} issues")
        print("-"*80)
        for issue in medium[:10]:  # Show first 10
            print(f"{issue['file']}:{issue['line']} - {issue['type']}")
            print(f"  {issue['code'][:70]}")
            print()
    
    if low:
        print(f"🟢 LOW SEVERITY: {len(low)} issues (not shown)")
        print()
    
    print("="*80)
    print("MANUAL CHECKS NEEDED:")
    print("="*80)
    print()
    print("1. Verify all index_bg_* and index_pt_* indices are properly initialized")
    print("2. Check that pvecback[] array size matches all index accesses")
    print("3. Verify division by phi_prime, rho_cdm, etc. have zero checks")
    print("4. Check for thread-safety issues (static variables in multi-threaded context)")
    print("5. Verify all pointer dereferences (pba->, pv->, ppw->) are validated")
    print()

if __name__ == '__main__':
    main()
