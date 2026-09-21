"""Os nós da árvore de uma fórmula.

São só dados: quem sabe o que fazer com eles é o avaliador. Manter a árvore
burra permite reaproveitá-la para outras coisas além de calcular — listar as
dependências de uma célula, por exemplo, é só uma varredura.
"""

from __future__ import annotations

from dataclasses import dataclass

from .referencia import Intervalo, Referencia
from .valores import Erro


class No:
    """Raiz de todos os nós da árvore."""

    __slots__ = ()


@dataclass(frozen=True, slots=True)
class Numero(No):
    """Um literal numérico."""

    valor: float


@dataclass(frozen=True, slots=True)
class Texto(No):
    """Um literal de texto."""

    valor: str


@dataclass(frozen=True, slots=True)
class Booleano(No):
    """``VERDADEIRO`` ou ``FALSO``."""

    valor: bool


@dataclass(frozen=True, slots=True)
class ErroLiteral(No):
    """Um erro escrito na própria fórmula, como ``#N/D``."""

    valor: Erro


@dataclass(frozen=True, slots=True)
class Celula(No):
    """Uma referência a uma célula."""

    referencia: Referencia


@dataclass(frozen=True, slots=True)
class Faixa(No):
    """Uma referência a um intervalo retangular."""

    intervalo: Intervalo


@dataclass(frozen=True, slots=True)
class Unario(No):
    """Sinal aplicado a uma expressão."""

    operador: str
    operando: No


@dataclass(frozen=True, slots=True)
class Percentual(No):
    """Sufixo ``%``, que divide o valor por cem."""

    operando: No


@dataclass(frozen=True, slots=True)
class Binario(No):
    """Operação entre duas expressões."""

    operador: str
    esquerda: No
    direita: No


@dataclass(frozen=True, slots=True)
class Chamada(No):
    """Chamada de função, com o nome já em caixa alta."""

    nome: str
    argumentos: tuple[No, ...]


def dependencias(no: No):
    """Percorre a árvore devolvendo toda célula de que a fórmula depende.

    Um intervalo é expandido célula a célula, porque é assim que o grafo de
    dependências precisa enxergá-lo para saber o que recalcular.
    """
    if isinstance(no, Celula):
        yield no.referencia.sem_travas()
    elif isinstance(no, Faixa):
        yield from no.intervalo.celulas()
    elif isinstance(no, (Unario, Percentual)):
        yield from dependencias(no.operando)
    elif isinstance(no, Binario):
        yield from dependencias(no.esquerda)
        yield from dependencias(no.direita)
    elif isinstance(no, Chamada):
        for argumento in no.argumentos:
            yield from dependencias(argumento)
