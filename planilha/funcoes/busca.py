"""Funções de procura em intervalos."""

from __future__ import annotations

from ..matriz import Matriz
from ..valores import NAO_DISPONIVEL, REF, VALOR, eh_erro, eh_numero, logico
from ..valores import texto as como_texto
from .base import como_numero, escalar, registrar


@registrar("PROCV", minimo=3, maximo=4)
def procv(procurado, tabela, coluna, aproximado=False):
    """Procura na primeira coluna e devolve o valor da coluna pedida."""
    if not isinstance(tabela, Matriz):
        return VALOR

    alvo = escalar(procurado)
    if eh_erro(alvo):
        return alvo

    indice = como_numero(coluna)
    if eh_erro(indice):
        return indice
    if indice < 1 or int(indice) > tabela.colunas:
        return REF

    modo = logico(escalar(aproximado))
    if eh_erro(modo):
        return modo

    linha = _procurar(alvo, tabela.coluna(1), modo)
    if linha is None:
        return NAO_DISPONIVEL

    return tabela.em(linha, int(indice))


@registrar("PROCH", minimo=3, maximo=4)
def proch(procurado, tabela, linha, aproximado=False):
    """Procura na primeira linha e devolve o valor da linha pedida."""
    if not isinstance(tabela, Matriz):
        return VALOR

    alvo = escalar(procurado)
    if eh_erro(alvo):
        return alvo

    indice = como_numero(linha)
    if eh_erro(indice):
        return indice
    if indice < 1 or int(indice) > tabela.linhas:
        return REF

    modo = logico(escalar(aproximado))
    if eh_erro(modo):
        return modo

    coluna = _procurar(alvo, tabela.linha(1), modo)
    if coluna is None:
        return NAO_DISPONIVEL

    return tabela.em(int(indice), coluna)


@registrar("CORRESP", minimo=2, maximo=3)
def corresp(procurado, intervalo, tipo=1):
    """Posição do valor dentro do intervalo, contando de 1."""
    if not isinstance(intervalo, Matriz):
        return VALOR

    alvo = escalar(procurado)
    if eh_erro(alvo):
        return alvo

    modo = como_numero(tipo)
    if eh_erro(modo):
        return modo

    valores = intervalo.valores()

    if modo == 0:
        posicao = _exata(alvo, valores)
    else:
        # Com tipo 1 a lista está em ordem crescente e vale o maior valor que
        # não passa do procurado; com -1 é o espelho disso.
        posicao = _aproximada(alvo, valores, crescente=modo > 0)

    return NAO_DISPONIVEL if posicao is None else float(posicao)


@registrar("INDICE", minimo=2, maximo=3)
def indice(matriz, linha, coluna=None):
    """Valor em uma posição da matriz."""
    if not isinstance(matriz, Matriz):
        return VALOR

    l = como_numero(linha)
    if eh_erro(l):
        return l

    if coluna is None:
        # Em uma faixa de uma linha ou uma coluna só, o segundo argumento anda
        # pelo eixo que existe.
        if matriz.linhas == 1:
            return _em(matriz, 1, int(l))
        if matriz.colunas == 1:
            return _em(matriz, int(l), 1)
        return REF

    c = como_numero(coluna)
    if eh_erro(c):
        return c

    return _em(matriz, int(l), int(c))


@registrar("ESCOLHER", minimo=2)
def escolher(posicao, *opcoes):
    """Devolve a enésima opção."""
    n = como_numero(posicao)
    if eh_erro(n):
        return n

    indice_escolhido = int(n)
    if indice_escolhido < 1 or indice_escolhido > len(opcoes):
        return VALOR

    return escalar(opcoes[indice_escolhido - 1])


@registrar("LINHAS", minimo=1, maximo=1)
def linhas(matriz):
    """Quantidade de linhas do intervalo."""
    return float(matriz.linhas) if isinstance(matriz, Matriz) else 1.0


@registrar("COLUNAS", minimo=1, maximo=1)
def colunas(matriz):
    """Quantidade de colunas do intervalo."""
    return float(matriz.colunas) if isinstance(matriz, Matriz) else 1.0


def _em(matriz: Matriz, linha: int, coluna: int):
    if linha < 1 or coluna < 1 or linha > matriz.linhas or coluna > matriz.colunas:
        return REF
    return matriz.em(linha, coluna)


def _procurar(alvo, valores, aproximado: bool) -> int | None:
    if not aproximado:
        return _exata(alvo, valores)
    return _aproximada(alvo, valores, crescente=True)


def _exata(alvo, valores) -> int | None:
    for posicao, valor in enumerate(valores, start=1):
        if _igual(alvo, valor):
            return posicao
    return None


def _aproximada(alvo, valores, crescente: bool) -> int | None:
    encontrado = None

    for posicao, valor in enumerate(valores, start=1):
        ordem = _comparar(valor, alvo)
        if ordem is None:
            continue

        if (crescente and ordem <= 0) or (not crescente and ordem >= 0):
            encontrado = posicao
        else:
            break

    return encontrado


def _igual(alvo, valor) -> bool:
    if eh_erro(alvo) or eh_erro(valor):
        return False
    if eh_numero(alvo) and eh_numero(valor):
        return float(alvo) == float(valor)
    if isinstance(alvo, str) or isinstance(valor, str):
        return como_texto(alvo).casefold() == como_texto(valor).casefold()
    return alvo == valor


def _comparar(valor, alvo) -> int | None:
    if eh_erro(valor) or eh_erro(alvo):
        return None

    if eh_numero(valor) and eh_numero(alvo):
        a, b = float(valor), float(alvo)
    elif isinstance(valor, str) and isinstance(alvo, str):
        a, b = valor.casefold(), alvo.casefold()
    else:
        return None

    return (a > b) - (a < b)
