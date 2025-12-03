#!/bin/bash
# Simple chain checker - shows what's actually running

echo "=========================================="
echo "ACT CHAIN STATUS"
echo "=========================================="
echo ""

# Check processes
echo "Running processes:"
ps aux | grep '[c]obaya.*act_world' | wc -l | xargs echo "  "

echo ""
echo "Chain files (samples written):"
for m in lcdm ede; do
  for c in 1 2 3 4; do
    file="chains/act_world_${m}_c${c}.1.txt"
    if [ -f "$file" ]; then
      lines=$(wc -l < "$file" 2>/dev/null || echo 0)
      echo "  ${m}_c${c}: $lines samples"
    else
      echo "  ${m}_c${c}: no file yet (still in burn-in)"
    fi
  done
done

echo ""
echo "Burn-in progress:"
for m in lcdm ede; do
  for c in 1 2 3 4; do
    log="logs/act_world_${m}_c${c}.log"
    if [ -f "$log" ]; then
      # Try to extract burn-in steps left
      progress=$(grep 'Progress' "$log" 2>/dev/null | tail -1)
      if echo "$progress" | grep -q "accepted steps left"; then
        steps_left=$(echo "$progress" | grep -oE '[0-9]+ accepted steps left' | grep -oE '[0-9]+')
        total_steps=$(echo "$progress" | grep -oE '[0-9]+ steps taken' | grep -oE '[0-9]+')
        echo "  ${m}_c${c}: $steps_left burn-in steps left ($total_steps total steps)"
      elif echo "$progress" | grep -q "Sampling"; then
        echo "  ${m}_c${c}: ✅ SAMPLING (burn-in complete!)"
      elif grep -q "Finished burn-in" "$log" 2>/dev/null; then
        echo "  ${m}_c${c}: ✅ Burn-in finished, sampling"
      else
        status=$(tail -1 "$log" 2>/dev/null | grep -oE '(Sampling|burning in|Progress|Finished|Getting|Measuring)' | head -1)
        [ -z "$status" ] && status="initializing"
        echo "  ${m}_c${c}: $status"
      fi
    else
      echo "  ${m}_c${c}: no log file"
    fi
  done
done

echo ""
echo "=========================================="
