"""Motor de planilha em Python puro.

Uso rápido:

    >>> from planilha import Planilha
    >>> p = Planilha()
    >>> p.definir("A1", 10)
    10.0
    >>> p.definir("A2", 32)
    32.0
    >>> p.definir("B1", "=SOMA(A1:A2)*2")
    84.0
    >>> p.definir("A1", 20)
    20.0
    >>> p.valor("B1")
    104.0
"""

from .csv_io import exportar, exportar_texto, importar, importar_texto
from .grafo import Grafo
from .lexer import ErroDeSintaxe
from .matriz import Matriz
from .parser import analisar
from .planilha import Celula, Planilha
from .referencia import Intervalo, Referencia, ReferenciaInvalida
from .valores import Erro

__version__ = "1.0.0"

__all__ = [
    "Celula",
    "Erro",
    "ErroDeSintaxe",
    "Grafo",
    "Intervalo",
    "Matriz",
    "Planilha",
    "Referencia",
    "ReferenciaInvalida",
    "analisar",
    "exportar",
    "exportar_texto",
    "importar",
    "importar_texto",
]
