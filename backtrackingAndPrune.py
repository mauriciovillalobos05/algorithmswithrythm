import math
from dataclasses import dataclass
from typing import List, Tuple
import time
import random

@dataclass
class Item:
    value: int
    weight: int
    ratio: float

@dataclass
class Node:
    vacc: int
    wacc: int
    vpos: float
    index: int
    path: List[Tuple[int,int]]

def knapsack_dp_value(items, W):
    """0/1 knapsack DP to compute the exact optimal value for verification."""
    dp = [0] * (W + 1)
    for v, w in items:
        for cap in range(W, w - 1, -1):
            cand = dp[cap - w] + v
            if cand > dp[cap]:
                dp[cap] = cand
    return dp[W]

def big_case(n=80, W=300, seed=1337):
    """Generate a large, reproducible test case and its exact expected value."""
    random.seed(seed)
    items = [(random.randint(1, 120), random.randint(1, 60)) for _ in range(n)]
    expected = knapsack_dp_value(items, W)
    return ("BIG", items, W, expected)

def calculate_vpos(S, pMax, vAcc, wAcc, index):
    if wAcc > pMax:
        return -math.inf

    n = len(S)
    k = index
    vPos = float(vAcc)
    wTmp = wAcc

    while k < n and wTmp + S[k].weight <= pMax:
        vPos += S[k].value
        wTmp += S[k].weight
        k += 1

    if k < n and wTmp < pMax and S[k].weight > 0:
        vPos += (pMax - wTmp) * S[k].ratio

    return vPos

def knapsackBB(S, W, best, path, best_path, vacc, wacc, index):

    if calculate_vpos(S, W, vacc, wacc, index) < best.vacc:
        return best, best_path

    if wacc > W:
        return best, best_path

    if index == len(S):
        if vacc > best.vacc:
            best.vacc = vacc
            best_path.clear()
            best_path.extend(path)
        return best, best_path

    # tomar el ítem
    path.append((S[index].value, S[index].weight))
    best, best_path = knapsackBB(S, W, best, path, best_path, vacc + S[index].value, wacc + S[index].weight, index + 1)
    path.pop()

    # no tomar el ítem
    best, best_path = knapsackBB(S, W, best, path, best_path, vacc, wacc, index + 1)

    return best, best_path

def cases() -> List[Tuple[str, List[Tuple[int,int]], int, int]]:
    return [
        ("A", [(6,1), (10,2), (12,3)], 5, 22),
        ("B", [(24,24), (18,10), (18,10), (10,7)], 25, 36),
        ("C", [(5,0), (5,0), (1,2)], 2, 11),
        ("D", [(5,6), (4,7), (3,8)], 5, 0),
        ("E", [(8,3), (8,3), (8,3)], 6, 16),
        ("F", [(20,1), (5,2), (10,3), (40,8), (15,7), (25,4)], 10, 60),
        big_case(),
    ]

if __name__ == "__main__":
    all_ok = True
    print("Branch & Bound knapsack tests\n")
    for name, items, W, expected in cases():
        S = [Item(v, w, (v / w) if w != 0 else float("inf")) for (v, w) in items]
        S.sort(key=lambda it: it.ratio, reverse=True)
        # inicializa 'best' como Node
        best = Node(vacc=0, wacc=0, vpos=0.0, index=0, path=[])
        path, best_path = [], []

        t0 = time.perf_counter()
        best, best_path = knapsackBB(S, W, best, path, best_path, 0, 0, 0)
        dt_ms = (time.perf_counter() - t0) * 1000.0

        got = best.vacc
        print(f"Case {name}: W={W}, items={items}")
        print(f"  Best value: {got} (expected {expected})")
        print(f"  Best path:  {best_path} ")
        print(f"  Time:       {dt_ms:.3f} ms")
        ok = (got == expected)
        all_ok &= ok
        print(f"  PASS? {ok}\n")

    print("ALL PASS:", all_ok)