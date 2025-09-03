import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

summ = pd.read_csv("perf_heu_summary.csv")
raw = pd.read_csv("perf_heu_raw.csv")

for df in (summ, raw):
    for col in ("n", "p"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

p_target = 0.5 if ("p" in summ and (summ["p"] == 0.5).any()) else summ["p"].mode().iat[0]
S = summ[summ["p"] == p_target].sort_values("n") if "p" in summ else summ.sort_values("n")

outdir = Path("images")
outdir.mkdir(exist_ok=True)

sub = raw[raw["p"] == p_target] if "p" in raw else raw
ns = sorted(sub["n"].dropna().unique())
time_col = next(c for c in raw.columns if c.lower() in ("time", "runtime", "elapsed", "t"))
data = [sub.loc[sub["n"] == n, time_col].dropna().values for n in ns]
plt.figure(figsize=(9, 4.8))
plt.boxplot(data, tick_labels=[str(int(n)) for n in ns], showfliers=False)
plt.xlabel("n (vertices)")
plt.ylabel("Runtime (s)")
plt.title(f"Heuristic runtime distribution per n (p={p_target})")
plt.tight_layout()
plt.savefig(outdir / "heuristic_candle_plot.png", dpi=200)
plt.close()

plt.figure(figsize=(9, 4.8))
plt.plot(S["n"], S["mean"], marker="o")
if {"ci_low", "ci_high"}.issubset(S.columns):
    yerr = np.vstack([S["mean"] - S["ci_low"], S["ci_high"] - S["mean"]])
    plt.errorbar(S["n"], S["mean"], yerr=yerr, fmt="none", capsize=4)
plt.xlabel("n (vertices)")
plt.ylabel("Mean runtime (s)")
plt.title(f"Heuristic mean runtime vs n (p={p_target})")
plt.tight_layout()
plt.savefig(outdir / "heuristic_performance_normal.png", dpi=200)
plt.close()

plt.figure(figsize=(9, 4.8))
plt.loglog(S["n"], S["mean"], marker="s")
plt.xlabel("log n")
plt.ylabel("log mean runtime (s)")
plt.title(f"Heuristic mean runtime vs n (log–log, p={p_target})")
plt.tight_layout()
plt.savefig(outdir / "heuristic_performance_log.png", dpi=200)
plt.close()

x = np.log(S["n"].to_numpy(dtype=float))
y = np.log(S["mean"].to_numpy(dtype=float))
alpha, intercept = np.polyfit(x, y, 1)
c = float(np.exp(intercept))

print("\n=== LaTeX rows (90% CI) ===")
have_ci = {"ci_low", "ci_high"}.issubset(S.columns)
for _, r in S.iterrows():
    n = int(r["n"])
    mean = r["mean"]
    std = r.get("std", np.nan)
    se = r.get("se", np.nan)
    ba = r.get("b/a", np.nan)
    if have_ci:
        lo, hi = r["ci_low"], r["ci_high"]
        print(f"{n} & {mean:.3e} & {std:.3e} & {se:.3e} & {ba:.3f} & [{lo:.3e},{hi:.3e}] \\\\")
    else:
        print(f"{n} & {mean:.3e} & {std:.3e} & {se:.3e} & {ba:.3f} & [\\,\\,] \\\\")
print("============================\n")

print(f"Fitted:  T(n) ≈ {c:.3e} · n^{alpha:.3f}")
print(rf"LaTeX:  $T(n) \approx {c:.3e}\, n^{{{alpha:.3f}}}$")