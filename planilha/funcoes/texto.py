"""Funções de texto."""

from __future__ import annotations

from ..valores import VALOR, eh_erro, numero
from ..valores import texto as como_texto
from .base import achatar, como_numero, escalar, primeiro_erro, registrar


@registrar("CONCATENAR", minimo=1)
def concatenar(*argumentos):
    """Junta tudo em um texto só."""
    valores = achatar(argumentos)

    erro = primeiro_erro(valores)
    if erro is not None:
        return erro

    return "".join(como_texto(valor) for valor in valores)


@registrar("MAIUSCULA", minimo=1, maximo=1)
def maiuscula(valor):
    """Tudo em caixa alta."""
    return _texto_ou_erro(valor, str.upper)


@registrar("MINUSCULA", minimo=1, maximo=1)
def minuscula(valor):
    """Tudo em caixa baixa."""
    return _texto_ou_erro(valor, str.lower)


@registrar("PRI.MAIUSCULA", minimo=1, maximo=1)
def primeira_maiuscula(valor):
    """Primeira letra de cada palavra em caixa alta."""
    return _texto_ou_erro(valor, str.title)


@registrar("ARRUMAR", minimo=1, maximo=1)
def arrumar(valor):
    """Tira os espaços das pontas e reduz os do meio a um só."""
    return _texto_ou_erro(valor, lambda t: " ".join(t.split()))


@registrar("NUM.CARACT", minimo=1, maximo=1)
def num_caract(valor):
    """Quantidade de caracteres."""
    atual = escalar(valor)
    if eh_erro(atual):
        return atual
    return float(len(como_texto(atual)))


@registrar("ESQUERDA", minimo=1, maximo=2)
def esquerda(valor, quantidade=1):
    """Os primeiros caracteres."""
    return _recortar(valor, quantidade, do_inicio=True)


@registrar("DIREITA", minimo=1, maximo=2)
def direita(valor, quantidade=1):
    """Os últimos caracteres."""
    return _recortar(valor, quantidade, do_inicio=False)


@registrar("EXT.TEXTO", minimo=3, maximo=3)
def ext_texto(valor, inicio, quantidade):
    """Um pedaço do texto, contando a partir de 1."""
    atual = escalar(valor)
    if eh_erro(atual):
        return atual

    i = como_numero(inicio)
    if eh_erro(i):
        return i

    n = como_numero(quantidade)
    if eh_erro(n):
        return n

    if i < 1 or n < 0:
        return VALOR

    corpo = como_texto(atual)
    comeco = int(i) - 1
    return corpo[comeco : comeco + int(n)]


@registrar("LOCALIZAR", minimo=2, maximo=3)
def localizar(procurado, dentro, inicio=1):
    """Posição do texto procurado, contando de 1. Ignora a caixa."""
    from ..valores import NAO_DISPONIVEL

    alvo = escalar(procurado)
    corpo = escalar(dentro)

    if eh_erro(alvo):
        return alvo
    if eh_erro(corpo):
        return corpo

    i = como_numero(inicio)
    if eh_erro(i):
        return i
    if i < 1:
        return VALOR

    posicao = como_texto(corpo).casefold().find(como_texto(alvo).casefold(), int(i) - 1)
    return NAO_DISPONIVEL if posicao < 0 else float(posicao + 1)


@registrar("SUBSTITUIR", minimo=3, maximo=3)
def substituir(valor, antigo, novo):
    """Troca todas as ocorrências de um trecho por outro."""
    partes = [escalar(valor), escalar(antigo), escalar(novo)]

    erro = primeiro_erro(partes)
    if erro is not None:
        return erro

    corpo, de, para = (como_texto(parte) for parte in partes)
    return corpo.replace(de, para) if de else corpo


@registrar("REPT", minimo=2, maximo=2)
def repetir(valor, vezes):
    """Repete o texto o número de vezes informado."""
    atual = escalar(valor)
    if eh_erro(atual):
        return atual

    n = como_numero(vezes)
    if eh_erro(n):
        return n
    if n < 0:
        return VALOR

    return como_texto(atual) * int(n)


@registrar("VALOR", minimo=1, maximo=1)
def valor_numerico(valor):
    """Converte texto em número."""
    atual = escalar(valor)
    if eh_erro(atual):
        return atual
    return numero(atual)


@registrar("TEXTO", minimo=1, maximo=1)
def para_texto(valor):
    """Converte o valor em texto do jeito que ele apareceria na célula."""
    atual = escalar(valor)
    if eh_erro(atual):
        return atual
    return como_texto(atual)


def _texto_ou_erro(valor, transformar):
    atual = escalar(valor)
    if eh_erro(atual):
        return atual
    return transformar(como_texto(atual))


def _recortar(valor, quantidade, do_inicio: bool):
    atual = escalar(valor)
    if eh_erro(atual):
        return atual

    n = como_numero(quantidade)
    if eh_erro(n):
        return n
    if n < 0:
        return VALOR

    corpo = como_texto(atual)
    corte = int(n)

    if corte == 0:
        return ""

    return corpo[:corte] if do_inicio else corpo[-corte:]
