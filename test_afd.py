import pytest
from afd import AFD, AFDInvalido, completar
from itertools import product


TERMINA_EM_1 = AFD(
    estados=frozenset({"q0", "q1"}),
    alfabeto=frozenset({"0", "1"}),
    transicoes={
        ("q0", "0"): "q0",
        ("q0", "1"): "q1",
        ("q1", "0"): "q0",
        ("q1", "1"): "q1",
    },
    inicial="q0",
    finais=frozenset({"q1"}),
)


@pytest.mark.parametrize("w", ["1", "01", "11", "1011", "0000001"])
def test_aceita(w):
    assert TERMINA_EM_1.aceita(w)


@pytest.mark.parametrize("w", ["", "0", "10", "100", "1111110"])
def test_rejeita(w):
    assert not TERMINA_EM_1.aceita(w)


def test_cadeia_vazia_depende_so_do_inicial():
    # ε é aceita se e somente se q₀ ∈ F. Aqui q0 ∉ F.
    assert TERMINA_EM_1.aceita("") is False


def test_simbolo_fora_do_alfabeto():
    with pytest.raises(ValueError, match="não pertence a Σ"):
        TERMINA_EM_1.aceita("1a1")


def todas_cadeias(alfabeto, ate):
    """Gera todas as cadeias de comprimento 0 até `ate`, em ordem."""
    simbolos = sorted(alfabeto)
    for n in range(ate + 1):
        for tupla in product(simbolos, repeat=n):
            yield "".join(tupla)


def test_contra_oraculo():
    oraculo = lambda w: w.endswith("1")       # a definição da linguagem, em Python
    for w in todas_cadeias({"0", "1"}, ate=12):
        assert TERMINA_EM_1.aceita(w) == oraculo(w), f"divergiu em {w!r}"