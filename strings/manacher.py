import re
import time

def manacher(s: str) -> str:
    s = ''.join(re.findall(r'[a-zA-Z0-9]', s)).lower()
    T = '^|' + '|'.join(f'{s}') + '|$'
    r = c = 0
    L = [0] * len(T)
    imax = Lmax = start = 0
    
    for i in range(1, len(T) - 1):
        if i < r:
            L[i] = min(r - i, L[2 * c - i])
        while T[i + L[i] + 1] == T[i - L[i] - 1]:
            L[i] += 1
        if i + L[i] > r:
            c = i
            r = i + L[i]
        if L[i] > L[imax]:
            imax = i
            Lmax = L[i]
            start = (imax - Lmax) // 2
    
    return s[start:start + Lmax]

def find_longest_palindrome_for_book(file: str) -> None:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            text = f.read()

        start_time = time.time()

        longest_palindrome = manacher(text)

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Archivo: {file}")
        print(f"Palíndromo más largo encontrado: {longest_palindrome}")
        print(f"Longitud: {len(longest_palindrome)}")
        print(f"Tiempo de búsqueda: {elapsed_time:.6f} segundos\n")

    except Exception as e:
        print(f"No se pudo procesar el archivo {file}: {e}")

files = ["A_Tale_Of_Two_Cities.txt", "gatsby.txt", "metamorphosis.txt", "republic.txt", "sherlock_holmes.txt"]

for file in files:
    find_longest_palindrome_for_book(file)