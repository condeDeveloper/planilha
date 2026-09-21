"""Avalia a árvore de uma fórmula contra uma fonte de valores.

O avaliador não conhece a planilha: ele recebe uma função que sabe ler uma
célula. É isso que permite testá-lo com um dicionário e, na planilha de verdade,
plugar o recálculo com detecção de ciclo.
"""

from __future__ import annotations

import math
from typing import Callable

from . import funcoes, sintaxe
from .matriz import Matriz
from .referencia import Referencia
from .valores import (
    DIV_ZERO,
    NOME,
    NUM,
    VALOR,
    VAZIO,
    Erro,
    eh_erro,
    eh_numero,
    numero,
)
from .valores import texto as como_texto

#: Assinatura da função que lê o valor de uma célula.
Fonte = Callable[[Referencia], object]

_COMPARADORES = {
    "=": lambda ordem: ordem == 0,
    "<>": lambda ordem: ordem != 0,
    "<": lambda ordem: ordem < 0,
    "<=": lambda ordem: ordem <= 0,
    ">": lambda ordem: ordem > 0,
    ">=": lambda ordem: ordem >= 0,
}


def avaliar(no: sintaxe.No, fonte: Fonte) -> object:
    """Calcula o valor da árvore, lendo as células pela fonte."""
    if isinstance(no, sintaxe.Numero):
        return no.valor

    if isinstance(no, sintaxe.Texto):
        return no.valor

    if isinstance(no, sintaxe.Booleano):
        return no.valor

    if isinstance(no, sintaxe.ErroLiteral):
        return no.valor

    if isinstance(no, sintaxe.Celula):
        return fonte(no.referencia.sem_travas())

    if isinstance(no, sintaxe.Faixa):
        return _matriz(no, fonte)

    if isinstance(no, sintaxe.Unario):
        return _unario(no, fonte)

    if isinstance(no, sintaxe.Percentual):
        valor = numero(_escalar(avaliar(no.operando, fonte)))
        return valor if eh_erro(valor) else valor / 100

    if isinstance(no, sintaxe.Binario):
        return _binario(no, fonte)

    if isinstance(no, sintaxe.Chamada):
        return _chamada(no, fonte)

    raise TypeError(f"Nó desconhecido: {no!r}")


def _matriz(no: sintaxe.Faixa, fonte: Fonte) -> Matriz:
    intervalo = no.intervalo
    linhas = []

    for linha in range(intervalo.inicio.linha, intervalo.fim.linha + 1):
        atual = []
        for coluna in range(intervalo.inicio.coluna, intervalo.fim.coluna + 1):
            atual.append(fonte(Referencia(linha, coluna)))
        linhas.append(atual)

    return Matriz.de(linhas)


def _unario(no: sintaxe.Unario, fonte: Fonte) -> object:
    valor = numero(_escalar(avaliar(no.operando, fonte)))
    if eh_erro(valor):
        return valor
    return -valor if no.operador == "-" else valor


def _binario(no: sintaxe.Binario, fonte: Fonte) -> object:
    esquerda = _escalar(avaliar(no.esquerda, fonte))
    direita = _escalar(avaliar(no.direita, fonte))

    if eh_erro(esquerda):
        return esquerda
    if eh_erro(direita):
        return direita

    operador = no.operador

    if operador == "&":
        return como_texto(esquerda) + como_texto(direita)

    if operador in _COMPARADORES:
        ordem = _ordenar(esquerda, direita)
        return _COMPARADORES[operador](ordem)

    a = numero(esquerda)
    if eh_erro(a):
        return a

    b = numero(direita)
    if eh_erro(b):
        return b

    return _aritmetica(operador, a, b)


def _aritmetica(operador: str, a: float, b: float) -> object:
    if operador == "+":
        return a + b
    if operador == "-":
        return a - b
    if operador == "*":
        return a * b

    if operador == "/":
        return DIV_ZERO if b == 0 else a / b

    if operador == "^":
        try:
            resultado = a**b
        except (OverflowError, ZeroDivisionError):
            return NUM

        if isinstance(resultado, complex) or (isinstance(resultado, float) and math.isnan(resultado)):
            return NUM

        return float(resultado)

    return VALOR


def _ordenar(esquerda: object, direita: object) -> int:
    """Ordem entre dois valores seguindo a regra da planilha.

    Número vem antes de texto, que vem antes de booleano. Comparar tipos
    diferentes nunca dá igual, e é por isso que a ordem entre eles precisa ser
    definida, mesmo parecendo arbitrária.
    """
    esquerda = VAZIO if esquerda == "" else esquerda
    direita = VAZIO if direita == "" else direita

    if esquerda is VAZIO and direita is VAZIO:
        return 0

    if esquerda is VAZIO:
        esquerda = 0.0 if eh_numero(direita) else ""
    if direita is VAZIO:
        direita = 0.0 if eh_numero(esquerda) else ""

    ranque_esquerda = _ranque(esquerda)
    ranque_direita = _ranque(direita)

    if ranque_esquerda != ranque_direita:
        return (ranque_esquerda > ranque_direita) - (ranque_esquerda < ranque_direita)

    if ranque_esquerda == 0:
        a, b = float(esquerda), float(direita)
    elif ranque_esquerda == 1:
        a, b = str(esquerda).casefold(), str(direita).casefold()
    else:
        a, b = bool(esquerda), bool(direita)

    return (a > b) - (a < b)


def _ranque(valor: object) -> int:
    if eh_numero(valor):
        return 0
    if isinstance(valor, str):
        return 1
    return 2


def _escalar(valor: object) -> object:
    """Uma matriz de um valor só vale pelo valor; as demais são erro de tipo."""
    if isinstance(valor, Matriz):
        return valor.valores()[0] if len(valor) == 1 else VALOR
    return valor


def _chamada(no: sintaxe.Chamada, fonte: Fonte) -> object:
    funcao = funcoes.buscar(no.nome)
    if funcao is None:
        return NOME

    if not funcao.aridade_ok(len(no.argumentos)):
        return VALOR

    argumentos = [avaliar(argumento, fonte) for argumento in no.argumentos]

    try:
        return _normalizar(funcao.implementacao(*argumentos))
    except ZeroDivisionError:
        return DIV_ZERO
    except (OverflowError, ValueError):
        return NUM


def _normalizar(valor: object) -> object:
    """Converte int em float para que toda a planilha fale a mesma língua."""
    if isinstance(valor, bool) or isinstance(valor, (str, Erro)) or valor is VAZIO:
        return valor
    if isinstance(valor, int):
        return float(valor)
    return valor
