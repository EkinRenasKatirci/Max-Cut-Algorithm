import pandas as pd
import numpy as np
from pathlib import Path

CSV_PATH = "perf_heu_summary.csv"

aliases_n = ["n", "N", "num_vertices", "vertices"]
aliases_p = ["p", "P", "prob", "probability", "density"]
aliases_m = ["m", "M", "num_edges", "edges", "|E|"]
aliases_bf = ["cut_BF", "bf_cut", "BF", "opt_cut", "optimal", "opt", "bruteforce", "brute_force", "best", "maxcut_opt"]
aliases_h = ["cut_H", "heu_cut", "H", "heuristic", "maxcut_heu", "approx", "algo", "value"]

def pick(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    for c in candidates:
        for col in df.columns:
            if col.lower() == c.lower():
                return col
    return None

df = pd.read_csv(CSV_PATH)

col_n = pick(df, aliases_n)
col_p = pick(df, aliases_p)
col_m = pick(df, aliases_m)
col_bf = pick(df, aliases_bf)
col_h = pick(df, aliases_h)

required = [col_n, col_bf, col_h]
if any(x is None for x in required):
    raise ValueError("Required columns not found. Make sure CSV has vertex count (n), brute force cut, and heuristic cut.")

if col_p is None:
    df["_p"] = 0.0
    col_p = "_p"

work = df[[c for c in [col_n, col_p, col_m, col_bf, col_h] if c is not None]].copy()
work = work.rename(columns={col_n:"n", col_p:"p", col_bf:"cut_BF", col_h:"cut_H"})
if col_m is not None:
    work = work.rename(columns={col_m:"m"})

work["ratio"] = work["cut_H"] / work["cut_BF"]
work["gap"] = work["cut_BF"] - work["cut_H"]
work["fail"] = work["cut_H"] < work["cut_BF"]

failed_cols = ["n"]
if "m" in work.columns: failed_cols.append("m")
failed_cols += ["p","cut_BF","cut_H","gap"]
failed = work.loc[work["fail"], failed_cols].sort_values(["n","p"])
fail_tex = failed.to_latex(index=False, escape=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x)
Path("quality_failed_cases.tex").write_text(fail_tex, encoding="utf-8")

grp_np = work.groupby(["n","p"], as_index=False).agg(
    mean_ratio=("ratio","mean"),
    fail_rate=("fail","mean"),
    count=("ratio","size")
)
grp_np["fail_rate"] = grp_np["fail_rate"]*100.0
grp_np = grp_np.sort_values(["n","p"])
np_tex = grp_np[["n","p","mean_ratio","fail_rate","count"]].to_latex(
    index=False, escape=False,
    float_format=lambda x: f"{x:.3f}"
)
Path("quality_summary_np.tex").write_text(np_tex, encoding="utf-8")

grp_n = work.groupby(["n"], as_index=False).agg(
    mean_ratio=("ratio","mean"),
    fail_rate=("fail","mean"),
    count=("ratio","size")
)
grp_n["fail_rate"] = grp_n["fail_rate"]*100.0
grp_n = grp_n.sort_values(["n"])
n_tex = grp_n[["n","mean_ratio","fail_rate","count"]].to_latex(
    index=False, escape=False,
    float_format=lambda x: f"{x:.3f}"
)
Path("quality_summary_n.tex").write_text(n_tex, encoding="utf-8")

total = len(work)
fails = int(work["fail"].sum())
fail_pct = 100.0*fails/total if total>0 else 0.0
print(f"Total instances: {total}")
print(f"Fails: {fails} ({fail_pct:.1f}%)")
print("Wrote: quality_failed_cases.tex, quality_summary_np.tex, quality_summary_n.tex")