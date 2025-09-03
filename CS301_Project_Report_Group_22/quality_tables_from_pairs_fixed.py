import pandas as pd
from pathlib import Path

pairs = pd.read_csv("maxcut_pairs.csv")

pairs["ratio"] = pairs[["cut_H", "cut_BF"]].apply(lambda r: r["cut_H"] / r["cut_BF"] if r["cut_BF"] > 0 else 0.0, axis=1)
pairs["fail"] = pairs["cut_H"] < pairs["cut_BF"]
pairs["gap"] = pairs["cut_BF"] - pairs["cut_H"]

failed_cols = ["n", "m", "p", "cut_BF", "cut_H", "gap"]
failed = pairs.loc[pairs["fail"], failed_cols].sort_values(["n", "p"])
fail_tex = failed.to_latex(index=False, escape=False, float_format=lambda x: f"{x:.3f}")
Path("quality_failed_cases.tex").write_text(fail_tex, encoding="utf-8")

grp_n = pairs.groupby(["n"], as_index=False).agg(
    mean_ratio=("ratio", "mean"),
    fail_rate=("fail", "mean"),
    count=("ratio", "size"),
)
grp_n["fail_rate"] = grp_n["fail_rate"] * 100.0
grp_n = grp_n.sort_values("n")
n_tex = grp_n[["n", "mean_ratio", "fail_rate", "count"]].to_latex(
    index=False, escape=False, float_format=lambda x: f"{x:.3f}"
)
Path("quality_summary_n.tex").write_text(n_tex, encoding="utf-8")

grp_np = pairs.groupby(["n", "p"], as_index=False).agg(
    mean_ratio=("ratio", "mean"),
    fail_rate=("fail", "mean"),
    count=("ratio", "size"),
)
grp_np["fail_rate"] = grp_np["fail_rate"] * 100.0
grp_np = grp_np.sort_values(["n", "p"])
np_tex = grp_np[["n", "p", "mean_ratio", "fail_rate", "count"]].to_latex(
    index=False, escape=False, float_format=lambda x: f"{x:.3f}"
)
Path("quality_summary_np.tex").write_text(np_tex, encoding="utf-8")

total = len(pairs)
fails = int(pairs["fail"].sum())
fail_pct = (100.0 * fails / total) if total > 0 else 0.0
print(f"Total instances: {total}")
print(f"Fails: {fails} ({fail_pct:.1f}%)")
print("Wrote: quality_failed_cases.tex, quality_summary_n.tex, quality_summary_np.tex")