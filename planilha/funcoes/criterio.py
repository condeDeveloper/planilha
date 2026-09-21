"""Interpretação dos critérios de SOMASE e CONT.SE.

O critério da planilha é aquele texto meio estranho: ``">10"``, ``"<>0"``,
``"sim"``. Ele pode vir como número, como texto com operador na frente ou como
texto puro, e a comparação de texto ignora a caixa.
"""

from __future__ import annotations

from typing import Callable

from ..valores import Erro, eh_erro, eh_numero, numero

_OPERADORES = ("<=", ">=", "<>", "<", ">", "=")


def interpretar(criterio: object) -> Callable[[object], bool] | Erro:
    """Devolve uma função que diz se um valor atende ao critério."""
    if eh_erro(criterio):
        return criterio

    if not isinstance(criterio, str):
        alvo = criterio
        return lambda valor: _igual(valor, alvo)

    texto = criterio.strip()

    for operador in _OPERADORES:
        if texto.startswith(operador):
            resto = texto[len(operador) :].strip()
            return _comparador(operador, _converter(resto))

    return lambda valor: _igual(valor, _converter(texto))


def _converter(texto: str) -> object:
    if texto == "":
        return None

    convertido = numero(texto)
    return convertido if not eh_erro(convertido) else texto


def _comparador(operador: str, alvo: object) -> Callable[[object], bool]:
    if operador == "=":
        return lambda valor: _igual(valor, alvo)
    if operador == "<>":
        return lambda valor: not _igual(valor, alvo)

    def comparar(valor: object) -> bool:
        ordem = _ordenar(valor, alvo)
        if ordem is None:
            return False
        if operador == "<":
            return ordem < 0
        if operador == "<=":
            return ordem <= 0
        if operador == ">":
            return ordem > 0
        return ordem >= 0

    return comparar


def _igual(valor: object, alvo: object) -> bool:
    if eh_erro(valor) or eh_erro(alvo):
        return False

    if alvo is None:
        return valor is None or valor == ""

    if eh_numero(alvo):
        return eh_numero(valor) and float(valor) == float(alvo)

    if isinstance(alvo, str) and isinstance(valor, str):
        return valor.strip().casefold() == alvo.strip().casefold()

    return valor == alvo


def _ordenar(valor: object, alvo: object) -> int | None:
    """-1, 0 ou 1 comparando os dois, ou None quando não são comparáveis."""
    if eh_erro(valor) or eh_erro(alvo):
        return None

    if eh_numero(alvo):
        if not eh_numero(valor):
            return None
        a, b = float(valor), float(alvo)
    elif isinstance(alvo, str):
        if not isinstance(valor, str):
            return None
        a, b = valor.casefold(), alvo.casefold()
    else:
        return None

    return (a > b) - (a < b)
