import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

plt.rcParams.update({
    "figure.dpi": 120,
    "font.size": 13,
    "axes.titleweight": "semibold"
})

raw = pd.read_csv('perf_heu_raw.csv')
summ = pd.read_csv('perf_heu_summary.csv')

for df in (raw, summ):
    for col in ('n','p'):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

time_col = next(c for c in raw.columns if c.lower() in ('time','runtime','elapsed','t'))
p_target = 0.5 if ('p' in raw and (raw['p'] == 0.5).any()) else raw['p'].mode().iat[0]

outdir = Path("images")
outdir.mkdir(exist_ok=True)

# ---- Boxplot (daha estetik) ----
sub = raw[raw['p']==p_target] if 'p' in raw else raw
ns = sorted(sub['n'].dropna().unique())
data = [sub.loc[sub['n']==n, time_col].dropna().values for n in ns]

plt.figure(figsize=(10,5.4))
bp = plt.boxplot(
    data,
    tick_labels=[str(int(n)) for n in ns],
    showfliers=False,
    patch_artist=True
)
for b in bp['boxes']:
    b.set(facecolor="#8ecae6", edgecolor="#222222", linewidth=1.2)
for med in bp['medians']:
    med.set(color="#d00000", linewidth=1.6)
for whisk in bp['whiskers']:
    whisk.set(color="#222222", linewidth=1.0)
for cap in bp['caps']:
    cap.set(color="#222222", linewidth=1.0)

plt.grid(axis="y", linestyle="--", alpha=0.35)
plt.xlabel("n (vertices)"); plt.ylabel("Runtime (s)")
plt.title(f"Heuristic runtime distribution per n (p={p_target})")
plt.tight_layout()
plt.savefig(outdir / "heuristic_candle_plot.png", dpi=300)
plt.close()

# ---- Mean vs n (normal + isteğe bağlı 90% CI) ----
sum_sub = summ[summ['p']==p_target].sort_values('n') if 'p' in summ else summ.sort_values('n')
have_ci = {'ci_low','ci_high'}.issubset(sum_sub.columns)
if not have_ci and {'mean','se','N'}.issubset(sum_sub.columns):
    z = 1.645
    sum_sub['ci_low']  = sum_sub['mean'] - z*sum_sub['se']
    sum_sub['ci_high'] = sum_sub['mean'] + z*sum_sub['se']
    have_ci = True

plt.figure(figsize=(10,5.4))
plt.plot(sum_sub['n'], sum_sub['mean'], marker='o', linewidth=2)
if have_ci:
    yerr = np.vstack([sum_sub['mean']-sum_sub['ci_low'], sum_sub['ci_high']-sum_sub['mean']])
    plt.errorbar(sum_sub['n'], sum_sub['mean'], yerr=yerr, fmt='none', capsize=5, linewidth=1)
plt.grid(True, linestyle="--", alpha=0.35)
plt.xlabel("n (vertices)"); plt.ylabel("Mean runtime (s)")
plt.title(f"Heuristic mean runtime vs n (p={p_target})")
plt.tight_layout()
plt.savefig(outdir / "heuristic_performance_normal.png", dpi=300)
plt.close()

# ---- Mean vs n (log–log) ----
plt.figure(figsize=(10,5.4))
plt.loglog(sum_sub['n'], sum_sub['mean'], marker='s', linewidth=2)
plt.grid(True, which='both', linestyle="--", alpha=0.35)
plt.xlabel("log n"); plt.ylabel("log mean runtime (s)")
plt.title(f"Heuristic mean runtime vs n (log–log, p={p_target})")
plt.tight_layout()
plt.savefig(outdir / "heuristic_performance_log.png", dpi=300)
plt.close()