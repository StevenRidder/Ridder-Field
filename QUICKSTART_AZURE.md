# V3 Model: Azure VM Quick Start

**You have existing MCMC infrastructure. This adapts it for v3 with ONE command.**

---

## On Your Azure VM

```bash
# Pull latest code
cd ~/Ridder-Field
git pull origin v3-development

# Run deployment (auto-builds CLASS + tests v3)
bash phase3/deploy_v3_to_azure.sh
```

**Wait 10 minutes.**

---

## What Happens

1. ✅ Pulls v3 code
2. ✅ Rebuilds CLASS (2 min)
3. ✅ Tests v3 button API (30 sec)
4. ✅ Runs smoke test (5 min)
5. ✅ Checks Cobaya + Planck data

**Result:** "✓ V3 DEPLOYMENT COMPLETE"

---

## Then Run MCMC

**Quick test (2-4 hours):**
```bash
cd ~/Ridder-Field/phase3
cobaya-run ridder_v3_quick_test.yaml
```

**Production (3-5 days):**
```bash
nohup cobaya-run ridder_v3_baseline.yaml > logs/v3_baseline.log 2>&1 &
nohup cobaya-run ridder_v3_trgb.yaml > logs/v3_trgb.log 2>&1 &
nohup cobaya-run ridder_v3_shoes.yaml > logs/v3_shoes.log 2>&1 &
```

**Monitor:**
```bash
tail -f logs/v3_baseline.log
```

---

## Files You Need

- ✅ `phase3/V3_MIGRATION_GUIDE.md` - Complete strategy
- ✅ `AZURE_VM_READY.md` - Detailed deployment guide
- ✅ `MCMC_STRATEGY.md` - Full roadmap

All in the repo at commit `a42e49d`.

---

## Expected Results

- **Baseline:** H0 ~ 67.2 (data prefers Planck)
- **TRGB:** H0 ~ 69.8, Δχ² ~ +2.9 (acceptable)
- **SH0ES:** H0 ~ 73.0, Δχ² ~ +30.2 (disfavored)

---

**Ready in 10 minutes. Posteriors in ~1 week.** 🚀

