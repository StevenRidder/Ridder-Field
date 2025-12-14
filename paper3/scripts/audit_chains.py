import sys, argparse, math
from pathlib import Path

def read_chain(path: Path):
    lines = path.read_text().splitlines()
    header = None
    data = []
    for ln in lines:
        if not ln.strip():
            continue
        if ln.lstrip().startswith("#"):
            header = ln.lstrip("#").strip().split()
            continue
        toks = ln.split()
        data.append(toks)

    if header is None:
        raise RuntimeError(f"No header found in {path}")

    ncols_data = len(data[0])
    if len(header) == ncols_data + 1:
        header = header[1:]
    elif len(header) != ncols_data:
        raise RuntimeError(
            f"Column mismatch in {path}: header={len(header)} data={ncols_data}. "
            f"First data row: {data[0][:10]}"
        )

    cols = {name: i for i, name in enumerate(header)}
    mat = [[float(x) for x in row] for row in data]
    return header, cols, mat

def colset(prefix, header):
    return {c for c in header if c.startswith(prefix)}

def best_row(mat, cols, burn_frac):
    n = len(mat)
    b = int(math.floor(n * burn_frac))
    if b >= n - 1:
        b = max(0, n - 2)
    sub = mat[b:]
    i_mlp = cols["minuslogpost"]
    best = min(sub, key=lambda r: r[i_mlp])
    return best, b

def summarize(path, header, cols, mat, burn_frac):
    best, b = best_row(mat, cols, burn_frac)
    out = {}
    out["file"] = str(path)
    out["samples_total"] = len(mat)
    out["burn_in_rows"] = b
    for k in ["minuslogpost", "chi2", "H0", "omega_b", "omega_cdm", "w0_fld"]:
        if k in cols:
            out[k] = best[cols[k]]
    pieces = {}
    for c in header:
        if c.startswith("chi2__") and c in cols:
            pieces[c] = best[cols[c]]
    out["pieces"] = pieces
    return out

def tail_best(mat, cols, tail_frac):
    n = len(mat)
    start = int(math.floor(n * (1.0 - tail_frac)))
    start = max(0, min(start, n-1))
    sub = mat[start:]
    i_mlp = cols["minuslogpost"]
    best = min(sub, key=lambda r: r[i_mlp])
    return best, start

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lcdm")
    ap.add_argument("model")
    ap.add_argument("--burn", type=float, default=0.30, help="fraction to discard as burn-in")
    ap.add_argument("--tail", type=float, default=0.50, help="fraction of chain tail used for stability check")
    args = ap.parse_args()

    p0 = Path(args.lcdm).expanduser()
    p1 = Path(args.model).expanduser()

    h0, c0, m0 = read_chain(p0)
    h1, c1, m1 = read_chain(p1)

    chi0 = colset("chi2__", h0)
    chi1 = colset("chi2__", h1)
    only0 = sorted(list(chi0 - chi1))
    only1 = sorted(list(chi1 - chi0))

    base_ignore = {"weight", "minuslogpost"}
    pset0 = {c for c in h0 if not c.startswith("chi2__") and c not in base_ignore}
    pset1 = {c for c in h1 if not c.startswith("chi2__") and c not in base_ignore}
    p_only0 = sorted(list(pset0 - pset1))
    p_only1 = sorted(list(pset1 - pset0))

    s0 = summarize(p0, h0, c0, m0, args.burn)
    s1 = summarize(p1, h1, c1, m1, args.burn)

    tb0, tstart0 = tail_best(m0, c0, args.tail)
    tb1, tstart1 = tail_best(m1, c1, args.tail)

    def grab(row, cols, name):
        return row[cols[name]] if name in cols else None

    print("\n=== A) LIKELIHOOD (chi2__*) PARITY CHECK ===")
    print(f"LCDM chi2__ cols:  {len(chi0)}")
    print(f"MODEL chi2__ cols: {len(chi1)}")
    if only0 or only1:
        print("WARNING: Not the same likelihood breakdown columns.")
        if only0: print("  Only in LCDM:", *only0, sep="\n    ")
        if only1: print("  Only in MODEL:", *only1, sep="\n    ")
    else:
        print("PASS: Same chi2__* column set.")

    print("\n=== B) PARAMETER PARITY CHECK (are we giving extra freedom?) ===")
    if p_only0 or p_only1:
        print("NOTE: Column sets differ (this can be fine, but it must be intentional).")
        if p_only0: print("  Only in LCDM:", *p_only0, sep="\n    ")
        if p_only1: print("  Only in MODEL:", *p_only1, sep="\n    ")
    else:
        print("PASS: Same non-chi2 column set.")

    print("\n=== C) BEST-FIT COMPARISON (AFTER BURN-IN) ===")
    def fmt(s):
        keys = ["minuslogpost","chi2","H0","omega_b","omega_cdm","w0_fld"]
        parts = [f"{k}={s[k]:.6g}" for k in keys if k in s]
        return ", ".join(parts)
    print("LCDM :", fmt(s0), f"(samples={s0['samples_total']}, burn_rows={s0['burn_in_rows']})")
    print("MODEL:", fmt(s1), f"(samples={s1['samples_total']}, burn_rows={s1['burn_in_rows']})")

    if "chi2" in s0 and "chi2" in s1:
        dchi2 = s1["chi2"] - s0["chi2"]
        print(f"\nDelta chi2 (MODEL - LCDM) = {dchi2:+.3f}  (negative means MODEL better)")

    print("\n=== D) PER-LIKELIHOOD DELTAS (NAMED chi2__* COLUMNS) ===")
    common = sorted(list(chi0 & chi1))
    if not common:
        print("No common chi2__* columns to compare.")
    else:
        deltas = []
        for k in common:
            d = s1["pieces"].get(k, float("nan")) - s0["pieces"].get(k, float("nan"))
            deltas.append((abs(d), d, k))
        deltas.sort(reverse=True)
        for _, d, k in deltas[:15]:
            print(f"{k}: {d:+.3f}")

    print("\n=== E) STABILITY CHECK (BEST-FIT IN LAST TAIL) ===")
    mlp0 = s0.get("minuslogpost", None)
    mlp1 = s1.get("minuslogpost", None)
    tmlp0 = grab(tb0, c0, "minuslogpost")
    tmlp1 = grab(tb1, c1, "minuslogpost")
    if mlp0 is not None and tmlp0 is not None:
        print(f"LCDM: best_mlp(post-burn)={mlp0:.6g} ; best_mlp(last {int(args.tail*100)}%)={tmlp0:.6g} (tail starts at row {tstart0})")
    if mlp1 is not None and tmlp1 is not None:
        print(f"MODEL: best_mlp(post-burn)={mlp1:.6g} ; best_mlp(last {int(args.tail*100)}%)={tmlp1:.6g} (tail starts at row {tstart1})")

    if mlp0 is not None and tmlp0 is not None and (tmlp0 - mlp0) > 5.0:
        print("WARNING: LCDM best-fit is not showing up in the tail; chain may not be stable/mixed yet.")
    if mlp1 is not None and tmlp1 is not None and (tmlp1 - mlp1) > 5.0:
        print("WARNING: MODEL best-fit is not showing up in the tail; chain may not be stable/mixed yet.")

if __name__ == "__main__":
    main()
