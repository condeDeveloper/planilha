"""Infraestrutura da biblioteca de funções.

Cada função é registrada com a quantidade de argumentos que aceita, de modo que
a checagem de aridade fique num lugar só e nenhuma implementação precise repetir
a mesma validação.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..matriz import Matriz
from ..valores import VALOR, Erro, eh_erro, eh_numero, numero

#: Marca a função que aceita qualquer quantidade de argumentos.
ILIMITADO = -1


@dataclass(frozen=True, slots=True)
class Funcao:
    """Uma função da planilha, pronta para ser chamada pelo avaliador."""

    nome: str
    implementacao: Callable[..., object]
    minimo: int = 0
    maximo: int = ILIMITADO

    def aridade_ok(self, quantidade: int) -> bool:
        """Indica se a quantidade de argumentos é aceita."""
        if quantidade < self.minimo:
            return False
        return self.maximo == ILIMITADO or quantidade <= self.maximo


BIBLIOTECA: dict[str, Funcao] = {}


def registrar(nome: str, minimo: int = 0, maximo: int = ILIMITADO):
    """Decorador que põe a função na biblioteca sob o nome informado."""

    def decorar(implementacao: Callable[..., object]) -> Callable[..., object]:
        BIBLIOTECA[nome.upper()] = Funcao(nome.upper(), implementacao, minimo, maximo)
        return implementacao

    return decorar


def apelidar(nome: str, existente: str) -> None:
    """Registra outro nome para uma função já registrada."""
    original = BIBLIOTECA[existente.upper()]
    BIBLIOTECA[nome.upper()] = Funcao(nome.upper(), original.implementacao, original.minimo, original.maximo)


def achatar(argumentos) -> list[object]:
    """Junta todos os argumentos em uma lista, abrindo as matrizes."""
    valores: list[object] = []

    for argumento in argumentos:
        if isinstance(argumento, Matriz):
            valores.extend(argumento.valores())
        elif isinstance(argumento, (list, tuple)):
            valores.extend(argumento)
        else:
            valores.append(argumento)

    return valores


def primeiro_erro(valores) -> Erro | None:
    """Devolve o primeiro erro da sequência, se houver."""
    for valor in valores:
        if eh_erro(valor):
            return valor
    return None


def numeros(argumentos) -> list[float] | Erro:
    """Os números dos argumentos, ignorando texto e vazio como a planilha faz.

    Só o que já é número entra na conta. Texto que parece número não entra: é o
    comportamento do Excel para SOMA e MÉDIA, e evita que uma coluna importada
    de CSV mude de resultado dependendo de quem digitou.
    """
    valores = achatar(argumentos)

    erro = primeiro_erro(valores)
    if erro is not None:
        return erro

    return [float(valor) for valor in valores if eh_numero(valor)]


def escalar(valor: object) -> object:
    """Reduz uma matriz de um valor só ao próprio valor."""
    if isinstance(valor, Matriz):
        if len(valor) == 1:
            return valor.valores()[0]
        return VALOR
    return valor


def como_numero(valor: object) -> float | Erro:
    """Converte para número já desembrulhando matriz de um valor só."""
    return numero(escalar(valor))
