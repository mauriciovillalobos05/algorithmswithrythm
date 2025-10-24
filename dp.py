from time import perf_counter

def time_call(label, fn, *args, **kwargs):
    t0 = perf_counter()
    _ = fn(*args, **kwargs)
    t1 = perf_counter()
    print(f"{label} took {(t1 - t0)*1000:.3f} ms")

prices = {1:1, 2:5, 3:8, 4:9, 5:10, 6:17, 7:17, 8:20, 9:24, 10:30}

def price_of(i):
    return prices.get(i, 0)

def cut(n, k):
    # base: nada que vender
    if n == 0:
        return 0
    # no se deben probar más tamaños, pero aún queda longitud → camino imposible
    if k > n:
        return -1

    # optcion 1: saltar este tamaño e intentar el siguiente
    best = cut(n, k + 1)

    # opcion 2: tomar este tamaño (si cabe), y se puede reutilizar k (ilimitado)
    if k <= n:
        best = max(best, price_of(k) + cut(n - k, k))

    return best

def memo_cut(n, k, memo=None):
    if memo is None: #así podemos llamar sin pasar el diccionario
        memo = {}

    # base: nada que vender
    if n == 0:
        return 0
    # no se deben probar más tamaños, pero aún queda longitud → camino imposible
    if k > n:
        return -1

    if (n, k) in memo:
        return memo[(n, k)]

    # optcion 1: saltar este tamaño e intentar el siguiente
    best = memo_cut(n, k + 1, memo)

    # opcion 2: tomar este tamaño (si cabe), y se puede reutilizar k (ilimitado)
    if k <= n:
        best = max(best, price_of(k) + memo_cut(n - k, k, memo))

    memo[(n, k)] = best
    return best

def dp_cut(n):
    dp = [-1] * (n + 1)
    dp[0] = 0

    for i in range(1, n + 1):
        best = -1
        for k in range(1, i + 1):
            best = max(best, price_of(k) + dp[i - k])
        dp[i] = best

    return dp[n]

print(dp_cut(4))
print(dp_cut(5))
print(dp_cut(10))
print(memo_cut(4, 1))
print(memo_cut(5, 1))
print(memo_cut(10, 1))
print(cut(4, 1))
print(cut(5, 1))
print(cut(10, 1))

time_call("dp_cut(4)", dp_cut, 4)
time_call("dp_cut(5)", dp_cut, 5)
time_call("dp_cut(10)", dp_cut, 10)

time_call("memo_cut(4,1)", memo_cut, 4, 1)
time_call("memo_cut(5,1)", memo_cut, 5, 1)
time_call("memo_cut(10,1)", memo_cut, 10, 1)

time_call("cut(4,1)", cut, 4, 1)
time_call("cut(5,1)", cut, 5, 1)
time_call("cut(10,1)", cut, 10, 1)