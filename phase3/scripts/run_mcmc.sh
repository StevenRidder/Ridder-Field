#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/run_mcmc.sh configs/ridder_test_1min.yaml local_1min 4

CONFIG_PATH="$1"
RUN_LABEL="$2"
NTHREADS="${3:-4}"

# Root directory of your project
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

CLASS_DIR="${ROOT_DIR}/../phase2/class"
OUTPUT_ROOT="${ROOT_DIR}/output/${RUN_LABEL}"

mkdir -p "${OUTPUT_ROOT}"

echo "=============================================================="
echo "RIDDER MCMC RUN"
echo "  Config : ${CONFIG_PATH}"
echo "  Label  : ${RUN_LABEL}"
echo "  Threads: ${NTHREADS}"
echo "  Output : ${OUTPUT_ROOT}"
echo "=============================================================="

# Optional: activate virtualenv if you use one
if [ -d "${ROOT_DIR}/cobaya_env" ]; then
  echo "[INFO] Activating cobaya_env virtualenv"
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/cobaya_env/bin/activate"
fi

export OMP_NUM_THREADS="${NTHREADS}"
export MKL_NUM_THREADS="${NTHREADS}"
export OPENBLAS_NUM_THREADS="${NTHREADS}"

# Make sure CLASS is visible to Cobaya
export CLASS_DIR

echo "[INFO] Using CLASS_DIR=${CLASS_DIR}"

# Run Cobaya MCMC
echo "[INFO] Starting Cobaya MCMC..."
python3 -m cobaya.run "${CONFIG_PATH}" \
  --output "${OUTPUT_ROOT}" \
  --resume \
  2>&1 | tee "${OUTPUT_ROOT}/log.txt"

echo "[INFO] MCMC completed."
echo "[INFO] Output written to ${OUTPUT_ROOT}"

