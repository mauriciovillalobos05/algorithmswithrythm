# =========================
#  SHA-256 (pure Python)
# =========================
def _rotr32(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF

# Constantes para SHA-256 (fracciones de raíces cúbicas de primos)
_K256 = [
    0x428A2F98,0x71374491,0xB5C0FBCF,0xE9B5DBA5,0x3956C25B,0x59F111F1,0x923F82A4,0xAB1C5ED5,
    0xD807AA98,0x12835B01,0x243185BE,0x550C7DC3,0x72BE5D74,0x80DEB1FE,0x9BDC06A7,0xC19BF174,
    0xE49B69C1,0xEFBE4786,0x0FC19DC6,0x240CA1CC,0x2DE92C6F,0x4A7484AA,0x5CB0A9DC,0x76F988DA,
    0x983E5152,0xA831C66D,0xB00327C8,0xBF597FC7,0xC6E00BF3,0xD5A79147,0x06CA6351,0x14292967,
    0x27B70A85,0x2E1B2138,0x4D2C6DFC,0x53380D13,0x650A7354,0x766A0ABB,0x81C2C92E,0x92722C85,
    0xA2BFE8A1,0xA81A664B,0xC24B8B70,0xC76C51A3,0xD192E819,0xD6990624,0xF40E3585,0x106AA070,
    0x19A4C116,0x1E376C08,0x2748774C,0x34B0BCB5,0x391C0CB3,0x4ED8AA4A,0x5B9CCA4F,0x682E6FF3,
    0x748F82EE,0x78A5636F,0x84C87814,0x8CC70208,0x90BEFFFA,0xA4506CEB,0xBEF9A3F7,0xC67178F2
]

def sha256_bytes(data: bytes) -> bytes:
    # IV (fracciones de raíces cuadradas de primos)
    h = [
        0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,
        0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19
    ]

    # Padding
    ml = len(data) * 8
    data += b"\x80"
    while (len(data) % 64) != 56:
        data += b"\x00"
    data += ml.to_bytes(8, "big")

    # Procesar bloques de 512 bits
    for i in range(0, len(data), 64):
        block = data[i:i+64]
        w = [0]*64
        for t in range(16):
            w[t] = int.from_bytes(block[4*t:4*(t+1)], "big")
        for t in range(16, 64):
            s0 = _rotr32(w[t-15], 7) ^ _rotr32(w[t-15], 18) ^ (w[t-15] >> 3)
            s1 = _rotr32(w[t-2], 17) ^ _rotr32(w[t-2], 19) ^ (w[t-2] >> 10)
            w[t] = (w[t-16] + s0 + w[t-7] + s1) & 0xFFFFFFFF

        a,b,c,d,e,f,g,hv = h

        for t in range(64):
            S1 = _rotr32(e, 6) ^ _rotr32(e, 11) ^ _rotr32(e, 25)
            ch = (e & f) ^ ((~e) & g)
            temp1 = (hv + S1 + ch + _K256[t] + w[t]) & 0xFFFFFFFF
            S0 = _rotr32(a, 2) ^ _rotr32(a, 13) ^ _rotr32(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (S0 + maj) & 0xFFFFFFFF

            hv = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        h[0] = (h[0] + a) & 0xFFFFFFFF
        h[1] = (h[1] + b) & 0xFFFFFFFF
        h[2] = (h[2] + c) & 0xFFFFFFFF
        h[3] = (h[3] + d) & 0xFFFFFFFF
        h[4] = (h[4] + e) & 0xFFFFFFFF
        h[5] = (h[5] + f) & 0xFFFFFFFF
        h[6] = (h[6] + g) & 0xFFFFFFFF
        h[7] = (h[7] + hv) & 0xFFFFFFFF

    return b"".join(x.to_bytes(4, "big") for x in h)

def sha256_hex(s: str) -> str:
    return sha256_bytes(s.encode("utf-8")).hex()


# =========================
#  Pruebas rápidas
# =========================
if __name__ == "__main__":
    tests = {
        "": {
            "sha1":   "da39a3ee5e6b4b0d3255bfef95601890afd80709",
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        },
        "abc": {
            "sha1":   "a9993e364706816aba3e25717850c26c9cd0d89d",
            "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        },
        "hola mundo": {
            "sha1":   "459567d3bde4418b7fe302ff9809c4b0befaf7dd",
            "sha256": "0b894166d3336435c800bea36ff21b29eaa801a52f584c006c49289a0dcf6e2f",
        },
    }
    for s, expect in tests.items():
        got256 = sha256_hex(s)
        ok256 = "OK" if got256 == expect["sha256"] else "FAIL"
        print(f"'{s}': SHA256 {ok256}")
        if ok256 != "OK":
            print("  ->", got256)
