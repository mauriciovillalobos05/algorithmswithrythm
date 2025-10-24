import time
import random

n = 20
objects = [[random.randint(10,100), random.randint(5,20)] for _ in range(n)]
maxWeight = 50

memo = [[-1] * (maxWeight + 1) for _ in range(len(objects) + 1)]

def prograDina(D,C):
    if memo[D][C]==-1:
        if D==len(objects) or C==0:
            return 0
                
        option1=prograDina(D+1,C)
        if objects[D][1] > C:
            option2 = -float("inf")
        else:
            option2 = objects[D][0] + prograDina(D+1, C-objects[D][1])

        memo[D][C]=(max(option1,option2))
        return memo[D][C]
    else:
        return memo[D][C]

start_time = time.time()

valor_max = prograDina(0, maxWeight)
print(f"Valor máximo: {valor_max}\n")

end_time = time.time()
print(f"Tiempo de ejecución: {end_time - start_time:.6f} segundos\n")

def pathing_paso_a_paso():
    D, C = 0, maxWeight
    paso = 1
    elegidos = []

    while D < len(objects) and C > 0:
        current = prograDina(D, C)
        opt1 = prograDina(D+1, C)
        if objects[D][1] > C:
            opt2 = -float("inf")
        else:
            opt2 = objects[D][0] + prograDina(D+1, C - objects[D][1])

        print(f"Paso {paso}: estado D={D}, C={C}")
        print(f"  option1 (no tomar obj {D}) = {opt1}")
        if opt2 == -float("inf"):
            print(f"  option2 (tomar obj {D} - peso {objects[D][1]}) = -inf (no cabe)")
        else:
            print(f"  option2 (tomar obj {D} - valor {objects[D][0]}, peso {objects[D][1]}) = {opt2}")
        print(f"  mejor (memo[{D}][{C}]) = {current}")

        if current == opt1:
            print("  => decisión: NO tomar el objeto.\n")
            D += 1
        else:
            print("  => decisión: TOMAR el objeto.\n")
            elegidos.append((D, objects[D]))
            C -= objects[D][1]
            D += 1

        paso += 1

    print("Objetos elegidos (índice, [valor, peso]):", elegidos)
    print("Suma de valores elegidos:", sum(item[1][0] for item in elegidos))

pathing_paso_a_paso()
