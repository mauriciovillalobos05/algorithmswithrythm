import heapq, math
from dataclasses import dataclass
from typing import List, Tuple
import time
import random

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

def calculate_vpos(S, pMax, vAcc, wAcc, index):
    if wAcc > pMax:
        return -math.inf

    n = len(S)
    k = index + 1
    vPos = float(vAcc)
    wTmp = wAcc

    while k < n and wTmp + S[k].weight <= pMax:
        vPos += S[k].value
        wTmp += S[k].weight
        k += 1

    if k < n and wTmp < pMax:
        vPos += (pMax - wTmp) * S[k].ratio

    return vPos

def knapsackProblemBB(items_vw, W, path, best_path):
    S = [Item(v, w, (v / w) if w != 0 else float("inf")) for (v, w) in items_vw]
    S.sort(key=lambda it: it.ratio, reverse=True)
    n = len(S)

    best = Node(0, 0, 0.0, -1, [])
    best_path.clear()
    path.clear()

    frontier = []
    counter = 0
    root_vpos = calculate_vpos(S, W, 0, 0, -1)
    heapq.heappush(frontier, (-root_vpos, counter, Node(0, 0, root_vpos, -1, [])))
    counter += 1

    while frontier:
        _neg, _cnt, node = heapq.heappop(frontier)

        if node.wacc <= W and node.vacc > best.vacc:
            best = node
            best_path.clear()
            best_path.extend(node.path)

        #do I need to check this node?
        if node.vpos >= best.vacc:
            index = node.index + 1
            if index < n:
                # skip next node
                skip_vpos = calculate_vpos(S, W, node.vacc, node.wacc, index)
                if node.wacc <= W:
                    heapq.heappush(frontier, (-skip_vpos, counter, Node(node.vacc, node.wacc, skip_vpos, index, node.path)))
                    counter += 1

                # take next node
                path.append(S[index].value)
                take_w = node.wacc + S[index].weight
                take_v = node.vacc + S[index].value
                take_vpos = calculate_vpos(S, W, take_v, take_w, index)
                if take_w <= W:
                    new_path = node.path + [(S[index].value, S[index].weight)]
                    heapq.heappush(frontier, (-take_vpos, counter, Node(take_v, take_w, take_vpos, index, new_path)))
                    counter += 1

    return best, best_path

# --- test cases ---

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
        t0 = time.perf_counter()
        best, best_path = knapsackProblemBB(items, W, [], [])
        dt_ms = (time.perf_counter() - t0) * 1000.0

        got = best.vacc
        print(f"Case {name}: W={W}, items={items}")
        print(f"  Best value: {got} (expected {expected})")
        print(f"  Best path:  {best_path}")
        print(f"  Time:       {dt_ms:.3f} ms")
        ok = (got == expected)
        all_ok &= ok
        print(f"  PASS? {ok}\n")

    print("ALL PASS:", all_ok)
