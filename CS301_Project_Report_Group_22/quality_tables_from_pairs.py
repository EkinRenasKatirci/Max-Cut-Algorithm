import pandas as pd
from pathlib import Path

CSV_PATH = "maxcut_pairs.csv"

df = pd.read_csv(CSV_PATH)
df["ratio"] = df["cut_H"] / df["cut_BF"]
df["gap"] = df["cut_BF"] - df["cut_H"]
df["fail"] = df["cut_H"] < df["cut_BF"]

failed = df.sort_values(["n","p","seed"])[["n","m","p","cut_BF","cut_H","gap"]].loc[df["fail"]]
fail_tex = failed.to_latex(index=False, escape=False, float_format=lambda x: f"{x:.3f}" if isinstance(x,float) else x)
Path("quality_failed_cases.tex").write_text(fail_tex, encoding="utf-8")

grp_np = df.groupby(["n","p"], as_index=False).agg(
    mean_ratio=("ratio","mean"),
    fail_rate=("fail","mean"),
    count=("ratio","size")
)
grp_np["fail_rate"] = 100.0 * grp_np["fail_rate"]
grp_np = grp_np.sort_values(["n","p"])
np_tex = grp_np[["n","p","mean_ratio","fail_rate","count"]].to_latex(index=False, escape=False, float_format=lambda x: f"{x:.3f}")
Path("quality_summary_np.tex").write_text(np_tex, encoding="utf-8")

grp_n = df.groupby(["n"], as_index=False).agg(
    mean_ratio=("ratio","mean"),
    fail_rate=("fail","mean"),
    count=("ratio","size")
)
grp_n["fail_rate"] = 100.0 * grp_n["fail_rate"]
grp_n = grp_n.sort_values(["n"])
n_tex = grp_n[["n","mean_ratio","fail_rate","count"]].to_latex(index=False, escape=False, float_format=lambda x: f"{x:.3f}")
Path("quality_summary_n.tex").write_text(n_tex, encoding="utf-8")

total = len(df)
fails = int(df["fail"].sum())
fail_pct = 100.0*fails/total if total>0 else 0.0
print(f"Total instances: {total}")
print(f"Fails: {fails} ({fail_pct:.1f}%)")
print("Wrote: quality_failed_cases.tex, quality_summary_np.tex, quality_summary_n.tex")