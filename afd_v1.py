Q = {"q0", "q1"}
SIGMA = {"0", "1"}
DELTA = {
    ("q0", "0"): "q0",
    ("q0", "1"): "q1",
    ("q1", "0"): "q0",
    ("q1", "1"): "q1",
}
Q0 = "q0"
F = {"q1"}


def aceita(cadeia: str) -> bool:
    estado = Q0
    for simbolo in cadeia:
        estado = DELTA[(estado, simbolo)]
    return estado in F


if __name__ == "__main__":
    for w in ["", "0", "1", "10", "1011", "100"]:
        print(f"{w!r:8} -> {aceita(w)}")