#!/bin/bash
# Enhanced chain status checker with debugging
# FAIL AND FIX EARLY POLICY: Show everything

echo "=========================================="
echo "ACT CHAIN STATUS (ENHANCED DEBUG)"
echo "=========================================="
echo ""

# Running processes
echo "Running processes:"
RUNNING=$(ps aux | grep 'act_world' | grep -v grep | wc -l)
echo "   $RUNNING"
echo ""

# Detailed process info
echo "Process details:"
ps aux | grep 'act_world' | grep -v grep | while read line; do
    PID=$(echo $line | awk '{print $2}')
    CPU=$(echo $line | awk '{print $3}')
    MEM=$(echo $line | awk '{print $4}')
    RSS=$(echo $line | awk '{print $6}')
    CMD=$(echo $line | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
    echo "  PID $PID: CPU=${CPU}%, MEM=${MEM}%, RSS=${RSS}KB"
    echo "    CMD: $CMD"
    
    # Check process state
    STATE=$(ps -p $PID -o stat --no-headers 2>/dev/null)
    ETIME=$(ps -p $PID -o etime --no-headers 2>/dev/null)
    echo "    State: $STATE, Runtime: $ETIME"
done
echo ""

# Chain files
echo "Chain files (samples written):"
for chain_type in lcdm ede; do
    for i in 1 2 3 4; do
        chainfile="chains/act_world_${chain_type}_c${i}.1.txt"
        if [ -f "$chainfile" ]; then
            LINES=$(wc -l < "$chainfile")
            SIZE=$(du -h "$chainfile" | cut -f1)
            MTIME=$(stat -c %y "$chainfile" | cut -d' ' -f1,2 | cut -d'.' -f1)
            echo "  ${chain_type}_c${i}: $LINES samples, $SIZE, modified $MTIME"
        else
            echo "  ${chain_type}_c${i}: no file yet (still in burn-in)"
        fi
    done
done
echo ""

# Log status
echo "Log file status:"
for chain_type in lcdm ede; do
    for i in 1 2 3 4; do
        logfile="logs/act_world_${chain_type}_c${i}.log"
        if [ -f "$logfile" ]; then
            SIZE=$(du -h "$logfile" | cut -f1)
            MTIME=$(stat -c %y "$logfile" | cut -d' ' -f1,2 | cut -d'.' -f1)
            AGE_SEC=$(($(date +%s) - $(stat -c %Y "$logfile")))
            AGE_MIN=$((AGE_SEC / 60))
            
            # Get last status
            LAST_LINE=$(tail -1 "$logfile" 2>/dev/null)
            STATUS=$(echo "$LAST_LINE" | grep -oE '(Sampling|Progress|Measuring|initializing|Burn-in)' | head -1 || echo "unknown")
            
            echo "  ${chain_type}_c${i}: $SIZE, modified $MTIME (${AGE_MIN}m ago), status: $STATUS"
            
            # Check for errors
            ERRORS=$(grep -E '(ERROR|Exception|Traceback)' "$logfile" 2>/dev/null | tail -1)
            if [ -n "$ERRORS" ]; then
                echo "    ERROR: $ERRORS"
            fi
        fi
    done
done
echo ""

# System resources
echo "System resources:"
free -h | head -2
echo ""

# Recent OOM kills
echo "Recent system events (OOM/kills):"
dmesg 2>/dev/null | tail -20 | grep -iE 'oom|killed' | tail -5 || echo "  None found"
echo ""

# Progress files
echo "Progress file status:"
for chain_type in lcdm ede; do
    for i in 1 2 3 4; do
        progressfile="chains/act_world_${chain_type}_c${i}.progress"
        if [ -f "$progressfile" ]; then
            LINES=$(wc -l < "$progressfile")
            if [ "$LINES" -gt 1 ]; then
                LAST_PROGRESS=$(tail -1 "$progressfile")
                echo "  ${chain_type}_c${i}: $LAST_PROGRESS"
            fi
        fi
    done
done
echo ""

echo "=========================================="
