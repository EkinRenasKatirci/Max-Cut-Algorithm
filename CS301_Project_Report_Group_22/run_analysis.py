import time, math, csv, random, sys
from run_heuristic_bench import gen_gnp, heuristic_maxcut
from statistics import mean, stdev
import numpy as np

def time_heuristic_once(n, p=0.5, R=5, seed=None):
    if seed is None:
        seed = random.randrange(10**9)
    random.seed(seed)
    np.random.seed(seed % (2**32 - 1))
    G = gen_gnp(n, p, seed)
    t0 = time.perf_counter()
    _ = heuristic_maxcut(G, R)
    t1 = time.perf_counter()
    return t1 - t0

def performance_sweep(n_list, p=0.5, R_small=5, R_big=2, N_full=30, use_t=True, out_prefix="perf_heu", cap_seconds_per_n=25.0, big_n_thresh=1200):
    rows_summary = []
    all_points = []
    _ = time_heuristic_once(max(20, n_list[0]//2), p=p, R=R_small, seed=12345)

    with open(f"{out_prefix}_summary.csv", "w", newline="") as f:
        csv.writer(f).writerow(["n","p","N","mean","std","se","b","b/a","ci_low","ci_high"])
    with open(f"{out_prefix}_raw.csv", "w", newline="") as f:
        csv.writer(f).writerow(["n","p","time"])

    for n in n_list:
        if n <= 800:
            Nn = N_full
            Rn = R_small
        elif n <= 2000:
            Nn = max(12, N_full//3)
            Rn = R_big
        else:
            Nn = max(6, N_full//5)
            Rn = R_big

        samples = []
        t_start = time.perf_counter()
        for i in range(Nn):
            if time.perf_counter() - t_start > cap_seconds_per_n and len(samples) >= max(6, Nn//2):
                break
            seed = 100000 + n*100 + i
            samples.append(time_heuristic_once(n, p=p, R=Rn, seed=seed))

        if len(samples) == 0:
            continue

        m = mean(samples)
        sd = stdev(samples) if len(samples) > 1 else 0.0
        sm = sd / math.sqrt(len(samples)) if len(samples) > 0 else 0.0
        t90 = 1.699 if use_t else 1.645
        b = t90 * sm
        ba = (b / m) if m > 0 else float('inf')
        lo, hi = m - b, m + b

        with open(f"{out_prefix}_summary.csv", "a", newline="") as f:
            csv.writer(f).writerow([n, p, len(samples), m, sd, sm, b, ba, lo, hi])
        with open(f"{out_prefix}_raw.csv", "a", newline="") as f:
            w = csv.writer(f)
            for val in samples:
                w.writerow([n, p, val])

        print(f"{n} & {p:.1f} & {len(samples)} & {m:.3e} & {sd:.3e} & {sm:.3e} & {ba:.3f} & [{lo:.3e},{hi:.3e}] \\\\")
        print(f"(LaTeX table) {n} & {m:.3e} & {sd:.3e} & {sm:.3e} & {ba:.3f} & {lo:.3e} & {hi:.3e} \\\\")
        rows_summary.append([n, m])

    X = np.log(np.array([r[0] for r in rows_summary if r[1] > 0], dtype=float))
    Y = np.log(np.array([r[1] for r in rows_summary if r[1] > 0], dtype=float))
    if len(X) >= 2:
        a, b0 = np.polyfit(X, Y, 1)
        c = math.exp(b0)
        print(f"\nFitted T(n) ≈ {c:.3e} * n^{a:.3f}")
        print(rf"LaTeX:  $T(n) \approx {c:.3e}\, n^{{{a:.3f}}}$")
        return rows_summary, (a, c)
    return rows_summary, (float("nan"), float("nan"))

if __name__ == "__main__":
    ns = [10,20,40,50, 100, 200, 400, 800, 1200, 2000, 3000]
    performance_sweep(ns, p=0.5, R_small=5, R_big=2, N_full=30, out_prefix="perf_heu", cap_seconds_per_n=25.0)