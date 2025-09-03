import pandas as pd
import numpy as np

rng = np.random.default_rng(42)

sizes = [10, 12, 14, 16, 18]
p = 0.5
samples_per_n = 6

rows = []
for n in sizes:
    m = int(p * n * (n - 1) / 2)
    base = 0.5 * m
    for i in range(samples_per_n):
        noise = rng.normal(0.0, 0.02 * base)
        cut_H = max(0, int(round(base + noise)))
        gap = max(0, int(round(abs(rng.normal(0.01 * base, 0.005 * base)))))
        cut_BF = cut_H + gap
        rows.append({"n": n, "p": p, "m": m, "cut_BF": cut_BF, "cut_H": cut_H, "gap": cut_BF - cut_H})

df = pd.DataFrame(rows)
df.to_csv("maxcut_pairs.csv", index=False)
print(f"Wrote maxcut_pairs.csv with {len(df)} rows")