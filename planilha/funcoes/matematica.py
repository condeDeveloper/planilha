"""Funções matemáticas."""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from ..matriz import Matriz
from ..valores import DIV_ZERO, NUM, VALOR, eh_erro, eh_numero
from .base import achatar, como_numero, numeros, primeiro_erro, registrar
from .criterio import interpretar


@registrar("SOMA", minimo=1)
def soma(*argumentos):
    """Soma tudo o que for número."""
    valores = numeros(argumentos)
    return valores if eh_erro(valores) else math.fsum(valores)


@registrar("PRODUTO", minimo=1)
def produto(*argumentos):
    """Multiplica tudo o que for número."""
    valores = numeros(argumentos)
    if eh_erro(valores):
        return valores

    resultado = 1.0
    for valor in valores:
        resultado *= valor
    return resultado


@registrar("ABS", minimo=1, maximo=1)
def absoluto(valor):
    """Valor absoluto."""
    n = como_numero(valor)
    return n if eh_erro(n) else abs(n)


@registrar("SINAL", minimo=1, maximo=1)
def sinal(valor):
    """-1, 0 ou 1, conforme o sinal."""
    n = como_numero(valor)
    if eh_erro(n):
        return n
    return float((n > 0) - (n < 0))


@registrar("ARRED", minimo=1, maximo=2)
def arredondar(valor, casas=0):
    """Arredonda para o número de casas informado, meio para cima."""
    n = como_numero(valor)
    if eh_erro(n):
        return n

    c = como_numero(casas)
    if eh_erro(c):
        return c

    # round() do Python arredonda o meio para o par, e fazer a conta em ponto
    # flutuante erra casos como ARRED(1,005; 2), porque 1,005 não existe exato
    # em binário. Passar pela representação decimal resolve os dois problemas.
    casa = Decimal(1).scaleb(-int(c))

    try:
        return float(Decimal(repr(n)).quantize(casa, rounding=ROUND_HALF_UP))
    except InvalidOperation:
        return NUM


@registrar("TRUNCAR", minimo=1, maximo=2)
def truncar(valor, casas=0):
    """Corta as casas decimais sem arredondar."""
    n = como_numero(valor)
    if eh_erro(n):
        return n

    c = como_numero(casas)
    if eh_erro(c):
        return c

    fator = 10 ** int(c)
    return math.trunc(n * fator) / fator


@registrar("INT", minimo=1, maximo=1)
def inteiro(valor):
    """Maior inteiro menor ou igual ao valor."""
    n = como_numero(valor)
    return n if eh_erro(n) else float(math.floor(n))


@registrar("MOD", minimo=2, maximo=2)
def resto(dividendo, divisor):
    """Resto da divisão, com o sinal do divisor."""
    a = como_numero(dividendo)
    if eh_erro(a):
        return a

    b = como_numero(divisor)
    if eh_erro(b):
        return b

    if b == 0:
        return DIV_ZERO

    # O resto da planilha tem o sinal do divisor, que é justamente o que o
    # operador % do Python faz com números de ponto flutuante.
    return a % b


@registrar("POTENCIA", minimo=2, maximo=2)
def potencia(base, expoente):
    """Base elevada ao expoente."""
    a = como_numero(base)
    if eh_erro(a):
        return a

    b = como_numero(expoente)
    if eh_erro(b):
        return b

    try:
        resultado = a**b
    except (OverflowError, ZeroDivisionError):
        return NUM

    if isinstance(resultado, complex):
        return NUM

    return float(resultado)


@registrar("RAIZ", minimo=1, maximo=1)
def raiz(valor):
    """Raiz quadrada. Número negativo devolve #NUM!."""
    n = como_numero(valor)
    if eh_erro(n):
        return n
    if n < 0:
        return NUM
    return math.sqrt(n)


@registrar("SOMASE", minimo=2, maximo=3)
def somase(intervalo, criterio, intervalo_soma=None):
    """Soma as células que atendem ao critério.

    Quando o terceiro argumento existe, o teste é feito no primeiro intervalo e
    a soma no segundo, posição a posição.
    """
    if not isinstance(intervalo, Matriz):
        return VALOR

    teste = interpretar(criterio)
    if eh_erro(teste):
        return teste

    origem = intervalo.valores()
    alvo = intervalo_soma.valores() if isinstance(intervalo_soma, Matriz) else origem

    erro = primeiro_erro(origem) or primeiro_erro(alvo)
    if erro is not None:
        return erro

    total = 0.0
    for posicao, valor in enumerate(origem):
        if posicao < len(alvo) and teste(valor) and eh_numero(alvo[posicao]):
            total += float(alvo[posicao])

    return total


@registrar("SOMARPRODUTO", minimo=1)
def somarproduto(*argumentos):
    """Soma dos produtos posição a posição."""
    colunas = []
    for argumento in argumentos:
        valores = argumento.valores() if isinstance(argumento, Matriz) else achatar([argumento])
        colunas.append(valores)

    if len({len(coluna) for coluna in colunas}) > 1:
        return VALOR

    erro = primeiro_erro(achatar(colunas))
    if erro is not None:
        return erro

    total = 0.0
    for posicao in range(len(colunas[0])):
        produto_da_linha = 1.0
        for coluna in colunas:
            valor = coluna[posicao]
            produto_da_linha *= float(valor) if eh_numero(valor) else 0.0
        total += produto_da_linha

    return total
