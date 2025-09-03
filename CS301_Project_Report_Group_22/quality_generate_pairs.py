import itertools as it
import random
import time
from pathlib import Path
import pandas as pd
import numpy as np
import networkx as nx

def cut_size(G, S):
    S = set(S)
    c = 0
    for u, v in G.edges():
        if (u in S) ^ (v in S):
            c += 1
    return c

def brute_force_maxcut(G):
    V = list(G.nodes())
    if not V:
        return set(), 0
    v0 = V[0]
    best = -1
    bestS = set()
    for mask in range(1 << (len(V) - 1)):
        S = {v0}
        for i, v in enumerate(V[1:]):
            if (mask >> i) & 1:
                S.add(v)
        c = cut_size(G, S)
        if c > best:
            best = c
            bestS = set(S)
    return bestS, best

def heuristic_local_search(G, R=5, rng=None):
    V = list(G.nodes())
    if rng is None:
        rng = random.Random()
    adj = {v: set(G.neighbors(v)) for v in V}
    def run_once():
        S = {v for v in V if rng.random() < 0.5}
        g = {}
        for v in V:
            a = sum((w in S) for w in adj[v])
            b = len(adj[v]) - a
            g[v] = b - a
        c = cut_size(G, S)
        while True:
            u = max(V, key=lambda x: g[x])
            if g[u] <= 0:
                break
            if u in S:
                S.remove(u)
            else:
                S.add(u)
            c += g[u]
            g[u] = -g[u]
            for w in adj[u]:
                if w in S:
                    g[w] += 2
                else:
                    g[w] -= 2
        return S, c
    best = -1
    bestS = set()
    for _ in range(R):
        S, c = run_once()
        if c > best:
            best = c
            bestS = set(S)
    return bestS, best

def gen_pairs(N_list=(10,12,14,16,18), p=0.5, seeds_per_n=6):
    rows = []
    for n in N_list:
        for s in range(seeds_per_n):
            rng = random.Random(1000*n + s)
            G = nx.gnp_random_graph(n, p, seed=1000*n + s, directed=False)
            G.remove_edges_from(nx.selfloop_edges(G))
            m = G.number_of_edges()
            S_bf, cut_bf = brute_force_maxcut(G)
            S_h, cut_h = heuristic_local_search(G, R=5, rng=rng)
            rows.append({"n": n, "p": p, "seed": s, "m": m, "cut_BF": int(cut_bf), "cut_H": int(cut_h)})
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = gen_pairs()
    Path("maxcut_pairs.csv").write_text(df.to_csv(index=False), encoding="utf-8")
    print("Wrote maxcut_pairs.csv with", len(df), "rows")