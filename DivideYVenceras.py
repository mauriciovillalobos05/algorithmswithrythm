import time
import random

n = 20
objects = [[random.randint(10,100), random.randint(5,20)] for _ in range(n)]
maxWeight = 50


def divideConquer(objects, maxWeight):
    if not objects or maxWeight <= 0:
        return 0

    option1 = divideConquer(objects[:-1], maxWeight)

    if objects[-1][1] > maxWeight:
        option2 = -float("inf")
    else:
        option2 = objects[-1][0] + divideConquer(objects[:-1], maxWeight - objects[-1][1])

    mejor = max(option1, option2)

    print(f"considerando objeto {objects[-1]} con capacidad {maxWeight}")
    print(f"  option1 (no tomar) = {option1}")
    if option2 == -float('inf'):
        print(f"  option2 (tomar) = -inf (no cabe)")
    else:
        print(f"  option2 (tomar) = {option2}")
    print(f"  mejor = {mejor}\n")

    return mejor

start = time.time()
print("Valor máximo:", divideConquer(objects, maxWeight))
end = time.time()
print(f"Tiempo de ejecución: {end - start:.6f} segundos")
