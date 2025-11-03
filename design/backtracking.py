from typing import List, Optional

TARGET = 10
NUMS = list(range(1, 7))
SIDES = [(0, 1, 2), (2, 3, 4), (4, 5, 0)]  # (A,AB,B), (B,BC,C), (C,CA,A)

def is_feasible(partial: List[Optional[int]]) -> bool:
    used = {x for x in partial if x is not None}
    remaining = set(NUMS) - used

    for a, b, c in SIDES:
        va, vb, vc = partial[a], partial[b], partial[c]
        assigned = [v for v in (va, vb, vc) if v is not None]

        if len(assigned) == 3:
            if va + vb + vc != TARGET:
                return False
        elif len(assigned) == 2:
            s = sum(assigned)
            need = TARGET - s
            # must be a valid unused number
            if need not in remaining:
                return False
            # also, the partial two can’t already exceed TARGET-1 (since min third is 1)
            if s > TARGET - 1:
                return False
    return True

def backtrack(pos: int, partial: List[Optional[int]], solutions: List[List[int]]):
    if pos == 6:
        # all positions filled; feasibility guarantees validity
        solutions.append(partial.copy())
        return

    for v in NUMS:
        if v in partial:
            continue
        partial[pos] = v
        if is_feasible(partial):
            backtrack(pos + 1, partial, solutions)
        partial[pos] = None

def solve_magic_triangle():
    solutions: List[List[int]] = []
    backtrack(0, [None]*6, solutions)
    return solutions

if __name__ == "__main__":
    sols = solve_magic_triangle()
    print(f"Found {len(sols)} solutions (order: [A, AB, B, BC, C, CA]):")
    for s in sols:
        print(s)