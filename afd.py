from dataclasses import dataclass, field


class AFDInvalido(Exception):
    """A quíntupla fornecida não satisfaz a definição de AFD."""


@dataclass(frozen=True)
class AFD:
    estados: frozenset[str]                    # Q
    alfabeto: frozenset[str]                   # Σ
    transicoes: dict[tuple[str, str], str]     # δ
    inicial: str                               # q₀
    finais: frozenset[str]                     # F

    def __post_init__(self) -> None:
        self.validar()

    def validar(self) -> None:
        if not self.estados:
            raise AFDInvalido("Q não pode ser vazio.")
        if not self.alfabeto:
            raise AFDInvalido("Σ não pode ser vazio.")
        if self.inicial not in self.estados:
            raise AFDInvalido(f"q₀={self.inicial!r} não pertence a Q.")

        fora = self.finais - self.estados
        if fora:
            raise AFDInvalido(f"F contém estados fora de Q: {sorted(fora)}")

        faltando = [
            (q, a)
            for q in sorted(self.estados)
            for a in sorted(self.alfabeto)
            if (q, a) not in self.transicoes
        ]
        if faltando:
            raise AFDInvalido(
                f"δ não é total. Faltam {len(faltando)} transições: {faltando}"
            )

        for (q, a), destino in self.transicoes.items():
            if q not in self.estados:
                raise AFDInvalido(f"δ parte de {q!r}, que não está em Q.")
            if a not in self.alfabeto:
                raise AFDInvalido(f"δ lê {a!r}, que não está em Σ.")
            if destino not in self.estados:
                raise AFDInvalido(f"δ({q},{a}) leva a {destino!r}, fora de Q.")

    def passo(self, estado: str, simbolo: str) -> str:
        """Um passo de δ. Erro claro se o símbolo não pertence a Σ."""
        if simbolo not in self.alfabeto:
            raise ValueError(f"símbolo {simbolo!r} não pertence a Σ={sorted(self.alfabeto)}")
        return self.transicoes[(estado, simbolo)]

    def delta_estendida(self, cadeia: str) -> str:
        """δ̂(q₀, w) — o estado onde a computação termina."""
        estado = self.inicial
        for simbolo in cadeia:
            estado = self.passo(estado, simbolo)
        return estado

    def aceita(self, cadeia: str) -> bool:
        """w ∈ L(M)?"""
        return self.delta_estendida(cadeia) in self.finais

    def trace(self, cadeia: str) -> list[tuple[str, str, str]]:
        """A computação completa, como lista de (antes, símbolo, depois)."""
        passos: list[tuple[str, str, str]] = []
        estado = self.inicial
        for simbolo in cadeia:
            proximo = self.passo(estado, simbolo)
            passos.append((estado, simbolo, proximo))
            estado = proximo
        return passos

def formatar_trace(m: AFD, cadeia: str) -> str:
    linhas = [f"entrada: {cadeia!r}", f"início:  {m.inicial}"]
    estado = m.inicial
    for i, (antes, simbolo, depois) in enumerate(m.trace(cadeia), start=1):
        linhas.append(f"  passo {i}: δ({antes}, {simbolo}) = {depois}")
        estado = depois
    veredito = "ACEITA" if estado in m.finais else "REJEITA"
    linhas.append(f"fim:     {estado}  ({'∈' if estado in m.finais else '∉'} F) -> {veredito}")
    return "\n".join(linhas)

def completar(
    estados: set[str],
    alfabeto: set[str],
    transicoes: dict[tuple[str, str], str],
    inicial: str,
    finais: set[str],
    nome_poco: str = "poco",
) -> AFD:
    """Recebe uma descrição parcial e devolve um AFD válido, com poço se preciso."""
    faltando = [
        (q, a) for q in estados for a in alfabeto if (q, a) not in transicoes
    ]

    novas = dict(transicoes)
    novos_estados = set(estados)

    if faltando:
        if nome_poco in estados:
            raise AFDInvalido(f"{nome_poco!r} já é um estado; escolha outro nome.")
        novos_estados.add(nome_poco)
        for (q, a) in faltando:
            novas[(q, a)] = nome_poco
        for a in alfabeto:
            novas[(nome_poco, a)] = nome_poco

    return AFD(
        estados=frozenset(novos_estados),
        alfabeto=frozenset(alfabeto),
        transicoes=novas,
        inicial=inicial,
        finais=frozenset(finais),
    )