from dataclasses import dataclass
from typing import List, Tuple
import time
import random

@dataclass
class Item:
    value: int
    weight: int

def knapsack_dp_value_items(items: List[Item], W: int) -> int:
    dp = [0] * (W + 1)
    for it in items:
        w, v = it.weight, it.value
        for cap in range(W, w - 1, -1):
            cand = dp[cap - w] + v
            if cand > dp[cap]:
                dp[cap] = cand
    return dp[W]

def big_case_bt(n: int = 10, W: int = 200, seed: int = 4242) -> Tuple[str, List[Item], int, int]:
    random.seed(seed)
    items = [Item(value=random.randint(5, 120), weight=random.randint(1, 40)) for _ in range(n)]

    # include a few zero-weight, small-value items to ensure your zero-weight logic still behaves
    zc = 2
    for _ in range(zc):
        items.append(Item(value=random.randint(1, 10), weight=0))

    expected = knapsack_dp_value_items(items, W)
    return ("BIG", items, W, expected)

def knapsackProblemBT(S, W, index, vacc, wacc, path, best_val, best_path):
    if wacc > W:
        return best_val, best_path

    if index == len(S):
        if vacc > best_val:
            return vacc, path.copy()  
        return best_val, best_path

    path.append(index)
    best_val, best_path = knapsackProblemBT(S, W, index + 1, vacc + S[index].value, wacc + S[index].weight, path, best_val, best_path)
    path.pop()

    best_val, best_path = knapsackProblemBT(S, W, index + 1, vacc, wacc, path, best_val, best_path)

    return best_val, best_path

def run_bt_with_path(items: List[Item], W: int) -> Tuple[int, List[Item]]:
    best_val, best_path_idx = knapsackProblemBT(items, W, 0, 0, 0, [], 0, [])
    return best_val, [items[i] for i in best_path_idx]


# --- test cases ---
def cases() -> List[Tuple[str, List[Item], int, int]]:
    base = [
        ("A", [Item(6,1), Item(10,2), Item(12,3)], 5, 22),
        ("B", [Item(24,24), Item(18,10), Item(18,10), Item(10,7)], 25, 36),
        ("C", [Item(5,0), Item(5,0), Item(1,2)], 2, 11),
        ("D", [Item(5,6), Item(4,7), Item(3,8)], 5, 0),
        ("E", [Item(8,3), Item(8,3), Item(8,3)], 6, 16),
        ("F", [Item(20,1), Item(5,2), Item(10,3), Item(40,8), Item(15,7), Item(25,4)], 10, 60),
    ]
    base.append(big_case_bt())  
    return base

def main():
    print("Running backtracking tests...\n")
    all_ok = True
    for name, items, W, expected in cases():
        start = time.perf_counter()
        best_value, best_path = run_bt_with_path(items, W)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        print(f"Case {name}: capacity={W}, items={[ (it.value,it.weight) for it in items ]}")
        print(f"  Your BT value:   {best_value}, path: {[ (it.value,it.weight) for it in best_path ]}")
        print(f"  Expected value:  {expected}")
        print(f"  Time: {elapsed_ms:.3f} ms")
        ok = (best_value == expected)
        all_ok &= ok
        print(f"  PASS? {ok}\n")
    print("ALL PASS:", all_ok)

if __name__ == "__main__":
    main()