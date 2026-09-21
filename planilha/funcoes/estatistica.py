"""Funções estatísticas e de contagem."""

from __future__ import annotations

import math

from ..matriz import Matriz
from ..valores import DIV_ZERO, NUM, VALOR, VAZIO, eh_erro, eh_numero
from .base import achatar, como_numero, numeros, primeiro_erro, registrar
from .criterio import interpretar


@registrar("MEDIA", minimo=1)
def media(*argumentos):
    """Média aritmética dos números."""
    valores = numeros(argumentos)
    if eh_erro(valores):
        return valores
    if not valores:
        return DIV_ZERO
    return math.fsum(valores) / len(valores)


@registrar("MEDIANA", minimo=1)
def mediana(*argumentos):
    """Valor do meio, ou a média dos dois do meio."""
    valores = numeros(argumentos)
    if eh_erro(valores):
        return valores
    if not valores:
        return NUM

    ordenados = sorted(valores)
    meio = len(ordenados) // 2

    if len(ordenados) % 2:
        return ordenados[meio]
    return (ordenados[meio - 1] + ordenados[meio]) / 2


@registrar("MINIMO", minimo=1)
def minimo(*argumentos):
    """Menor número. Sem números, devolve zero, como a planilha."""
    valores = numeros(argumentos)
    if eh_erro(valores):
        return valores
    return min(valores) if valores else 0.0


@registrar("MAXIMO", minimo=1)
def maximo(*argumentos):
    """Maior número. Sem números, devolve zero, como a planilha."""
    valores = numeros(argumentos)
    if eh_erro(valores):
        return valores
    return max(valores) if valores else 0.0


@registrar("MAIOR", minimo=2, maximo=2)
def maior(intervalo, posicao):
    """O enésimo maior valor."""
    return _enesimo(intervalo, posicao, maior_primeiro=True)


@registrar("MENOR", minimo=2, maximo=2)
def menor(intervalo, posicao):
    """O enésimo menor valor."""
    return _enesimo(intervalo, posicao, maior_primeiro=False)


@registrar("CONT.NUM", minimo=1)
def cont_num(*argumentos):
    """Conta quantas células são número."""
    valores = achatar(argumentos)
    return float(sum(1 for valor in valores if eh_numero(valor)))


@registrar("CONT.VALORES", minimo=1)
def cont_valores(*argumentos):
    """Conta quantas células não estão vazias."""
    valores = achatar(argumentos)
    return float(sum(1 for valor in valores if valor is not VAZIO and valor != ""))


@registrar("CONT.VAZIO", minimo=1)
def cont_vazio(*argumentos):
    """Conta quantas células estão vazias."""
    valores = achatar(argumentos)
    return float(sum(1 for valor in valores if valor is VAZIO or valor == ""))


@registrar("CONT.SE", minimo=2, maximo=2)
def cont_se(intervalo, criterio):
    """Conta as células que atendem ao critério."""
    if not isinstance(intervalo, Matriz):
        return VALOR

    teste = interpretar(criterio)
    if eh_erro(teste):
        return teste

    valores = intervalo.valores()

    erro = primeiro_erro(valores)
    if erro is not None:
        return erro

    return float(sum(1 for valor in valores if teste(valor)))


@registrar("DESVPAD", minimo=1)
def desvpad(*argumentos):
    """Desvio padrão amostral, com denominador n-1."""
    variancia_amostral = var(*argumentos)
    if eh_erro(variancia_amostral):
        return variancia_amostral
    return math.sqrt(variancia_amostral)


@registrar("VAR", minimo=1)
def var(*argumentos):
    """Variância amostral, com denominador n-1."""
    valores = numeros(argumentos)
    if eh_erro(valores):
        return valores
    if len(valores) < 2:
        return DIV_ZERO

    m = math.fsum(valores) / len(valores)
    return math.fsum((valor - m) ** 2 for valor in valores) / (len(valores) - 1)


def _enesimo(intervalo, posicao, maior_primeiro: bool):
    valores = numeros([intervalo])
    if eh_erro(valores):
        return valores

    n = como_numero(posicao)
    if eh_erro(n):
        return n

    indice = int(n)
    if indice < 1 or indice > len(valores):
        return NUM

    ordenados = sorted(valores, reverse=maior_primeiro)
    return ordenados[indice - 1]
