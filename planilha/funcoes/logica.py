"""Funções lógicas e de tratamento de erro."""

from __future__ import annotations

from ..valores import VALOR, VAZIO, Erro, eh_erro, eh_numero, logico
from .base import achatar, escalar, registrar


@registrar("SE", minimo=2, maximo=3)
def se(condicao, entao, senao=False):
    """Escolhe entre dois valores conforme o teste."""
    teste = logico(escalar(condicao))
    if eh_erro(teste):
        return teste
    return escalar(entao) if teste else escalar(senao)


@registrar("SES", minimo=2)
def ses(*argumentos):
    """Primeira condição verdadeira vence, em pares condição/valor."""
    if len(argumentos) % 2:
        return VALOR

    for posicao in range(0, len(argumentos), 2):
        teste = logico(escalar(argumentos[posicao]))
        if eh_erro(teste):
            return teste
        if teste:
            return escalar(argumentos[posicao + 1])

    from ..valores import NAO_DISPONIVEL

    return NAO_DISPONIVEL


@registrar("E", minimo=1)
def e_logico(*argumentos):
    """Verdadeiro só se todos forem verdadeiros."""
    return _reduzir(argumentos, todos=True)


@registrar("OU", minimo=1)
def ou_logico(*argumentos):
    """Verdadeiro se pelo menos um for verdadeiro."""
    return _reduzir(argumentos, todos=False)


@registrar("NAO", minimo=1, maximo=1)
def nao(valor):
    """Inverte o valor lógico."""
    teste = logico(escalar(valor))
    return teste if eh_erro(teste) else not teste


@registrar("SEERRO", minimo=2, maximo=2)
def seerro(valor, alternativa):
    """Devolve a alternativa quando o primeiro argumento é erro."""
    atual = escalar(valor)
    return escalar(alternativa) if eh_erro(atual) else atual


@registrar("EERRO", minimo=1, maximo=1)
def eerro(valor):
    """Indica se o valor é um erro."""
    return eh_erro(escalar(valor))


@registrar("ENUM", minimo=1, maximo=1)
def enum(valor):
    """Indica se o valor é um número."""
    return eh_numero(escalar(valor))


@registrar("ETEXTO", minimo=1, maximo=1)
def etexto(valor):
    """Indica se o valor é texto."""
    return isinstance(escalar(valor), str)


@registrar("EVAZIO", minimo=1, maximo=1)
def evazio(valor):
    """Indica se a célula está vazia."""
    return escalar(valor) is VAZIO


@registrar("VERDADEIRO", minimo=0, maximo=0)
def verdadeiro():
    """A constante verdadeira."""
    return True


@registrar("FALSO", minimo=0, maximo=0)
def falso():
    """A constante falsa."""
    return False


def _reduzir(argumentos, todos: bool) -> bool | Erro:
    valores = achatar(argumentos)
    resultado = todos

    for valor in valores:
        if valor is VAZIO:
            continue

        teste = logico(valor)
        if eh_erro(teste):
            return teste

        resultado = (resultado and teste) if todos else (resultado or teste)

    return resultado
