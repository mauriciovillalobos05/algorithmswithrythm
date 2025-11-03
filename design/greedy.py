def bpow(x, n):
    # CONQUISTA (casos base: subproblemas triviales)
    if n == 0:
        return 1
    if n == 1:
        return x

    if n % 2 == 0:
        # DIVIDE: reduce a un subproblema de tamaño n//2
        half = bpow(x, n // 2)      # CONQUISTA: resolver el subproblema
        return half * half          # COMBINA: fusionar soluciones
    else:
        # DIVIDE (o REDUCE): subproblema con exponente n-1
        sub = bpow(x, n - 1)        # CONQUISTA: resolver el subproblema
        return x * sub              # COMBINA: multiplicar por x
    
def run_tests():
    cases = [
        (5, 0), (5, 1), (5, 2), (5, 3), (2, 10), (3, 13), (10, 5), (7, 8), (2, 31), (9, 12),
    ]
    ok = True
    for x, n in cases:
        got = bpow(x, n)
        exp = pow(x, n)
        good = (got == exp)
        ok &= good
        print(f"x={x:<3} n={n:<3}  bpow={got}   pow={exp}   ok={good}")
    print("\nALL OK?" , ok)

run_tests()