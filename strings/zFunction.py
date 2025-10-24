import time

def findZ(P: str, T: str) -> list[int]:
    S = P + T 
    Z = [0] * len(S)
    l, r = 0, 0

    for i in range(1, len(S)):
        if i < r:
            Z[i] = min(r - i, Z[i - l])
        while i + Z[i] < len(S) and S[Z[i]] == S[i + Z[i]]:
            Z[i] += 1
        if i + Z[i] > r:
            l = i
            r = i + Z[i]

    matches = []
    for i in range(len(P) + 1, len(S)):
        if Z[i] >= len(P):
            matches.append(i - len(P) - 1)
    return matches

def search_in_file(file_name: str, words: list[str]) -> None:
    with open(file_name, 'r') as f:
        text = f.read()

    for word in words:
        start_time = time.time()  
        matches = findZ(word, text)  
        
        print(f"Resultados para la palabra: '{word}'")
        if matches:
            for match in matches:
                start_idx = max(0, match - 25) 
                end_idx = min(len(text), match + len(word) + 25)
                snippet = text[start_idx:end_idx]
                print(f"Encontrado en la posición {match}: ...{snippet}...")
        else:
            print("No se encontraron ocurrencias.")
        
        end_time = time.time()  
        print(f"Tiempo de búsqueda: {end_time - start_time:.6f} segundos\n")

words_to_search = ["stillness", "horse", "inheritance", "gallop", "summit", "passenger", "humongous", "warning", "rider", "joy"]

search_in_file("A_Tale_Of_Two_Cities.txt", words_to_search)
