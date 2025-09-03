# run_heuristic_bench.py
import random, time, statistics
import networkx as nx

print("[main] script imported", flush=True)

def gen_gnp(n, p, seed=None):
    if seed is not None and not isinstance(seed, int):
        try:
            seed = int(seed)
        except Exception:
            seed = None
    rng = random.Random(seed)
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for u in range(n):
        for v in range(u+1, n):
            if rng.random() < p:
                G.add_edge(u, v)
    return G

def cut_size(G, S):
    c = 0
    for u, v in G.edges():
        if (u in S) ^ (v in S):
            c += 1
    return c

def heuristic_maxcut(G, restarts=10):
    import random
    nodes = list(G.nodes())
    best_c, best_S = -1, None

    for _ in range(restarts):
        # random start cut
        S = set(u for u in nodes if random.random() < 0.5)

        # initial gains: g[v] = (#opposite) - (#same)
        g = {}
        for v in nodes:
            a = sum(1 for w in G[v] if w in S)          # same-side neighbors
            b = sum(1 for w in G[v] if w not in S)      # opposite-side neighbors
            g[v] = b - a

        # initial cut value
        c = 0
        for u, v in G.edges():
            c += (u in S) ^ (v in S)

        max_iters = 5 * G.number_of_edges() + 5 * G.number_of_nodes()
        iters = 0

        improved = True
        while improved and iters < max_iters:
            improved = False

            # pick the best single-vertex move
            best_u, best_gain = None, 0
            for v in nodes:
                if g[v] > best_gain:
                    best_gain, best_u = g[v], v

            if best_u is not None and best_gain > 0:
                # flip best_u
                if best_u in S:
                    S.remove(best_u)
                else:
                    S.add(best_u)

                # update cut value
                c += best_gain
                improved = True

                # flipping a vertex inverts its own gain
                g[best_u] = -g[best_u]

                # update neighbors' gains in O(deg)
                # Correct rule: after flipping best_u, for any neighbor w,
                # if w is on the SAME side as best_u (after the flip), then the edge (u,w)
                # is within the same side and w's gain decreases by 2; otherwise it increases by 2.
                for w in G[best_u]:
                    if w in S:
                        g[w] -= 2
                    else:
                        g[w] += 2

                iters += 1

    #         if c > best_c:
    #             best_c, best_S = c, set(S)
        if c > best_c:
            best_c, best_S = c, set(S)

    return best_c, best_S

def brute_force_maxcut(G):
    n = G.number_of_nodes()
    nodes = list(G.nodes())
    best_c, best_S = -1, None
    from itertools import product
    for bits in product([0,1], repeat=n-1):
        S = {nodes[0]}
        for i, b in enumerate(bits, start=1):
            if b: S.add(nodes[i])
        c = cut_size(G, S)
        if c > best_c:
            best_c, best_S = c, set(S)
    return best_c, best_S

def run_bench():
    print("[run_bench] start", flush=True)
    Ns = [30, 40, 50]
    Ps = [0.2, 0.5]
    SEEDS_PER = 3
    RESTARTS = 5

    rows = []
    series = {p: [] for p in Ps}

    DO_VALIDATE = False

    for n in Ns:
        for p in Ps:
            print(f"[run_bench] n={n}, p={p} ...", flush=True)
            times, cuts = [], []
            for s in range(SEEDS_PER):
                seed_val = int(10000 + 97*n + 13*int(p*100) + s)
                print(f"  - seed {s+1}/{SEEDS_PER} (seed_val={seed_val})", flush=True)
                G = gen_gnp(n, p, seed=seed_val)
                t0 = time.perf_counter()
                c_h, S_h = heuristic_maxcut(G, restarts=RESTARTS)
                t1 = time.perf_counter()
                dt = t1 - t0
                print(f"    time for this seed: {dt:.3f}s", flush=True)
                times.append(dt)
                cuts.append(c_h)

                if DO_VALIDATE and n <= 18:
                    c_opt, _ = brute_force_maxcut(G)
                    if c_h > c_opt:
                        print("?? Heuristic > optimal?!", n, p, s, flush=True)

            med_t = statistics.median(times)
            med_c = statistics.median(cuts)

            rows.append((n, "G(n,p)", p, SEEDS_PER, med_t, med_c))
            series[p].append((n, med_t))

    print("\n=== LaTeX table rows ===", flush=True)
    for n, model, p, k, med_t, med_c in rows:
        print(f"{n} & ${model}$ & {p:.1f} & {k} & {med_t:.3f} & {int(med_c)} \\", flush=True)

    print("\n=== pgfplots coordinates per p ===", flush=True)
    for p in Ps:
        coords = " ".join(f"({n},{t:.3f})" for (n, t) in series[p])
        print(f"% p={p}\n{coords}\n", flush=True)

    print("[run_bench] done", flush=True)

if __name__ == "__main__":
    print("[main] calling run_bench()", flush=True)
    try:
        run_bench()
    except Exception as e:
        import traceback
        print("[ERROR] exception while running benchmark:", e, flush=True)
        traceback.print_exc()
    finally:
        print("[main] done", flush=True)