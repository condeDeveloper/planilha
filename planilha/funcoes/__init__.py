"""Biblioteca de funções da planilha.

Importar os módulos aqui é o que popula o registro: cada um deles decora as
suas funções com ``registrar`` no momento da importação.
"""

from __future__ import annotations

from . import busca, estatistica, logica, matematica, texto  # noqa: F401
from .base import BIBLIOTECA, ILIMITADO, Funcao, apelidar, registrar

# Os nomes com acento são os que aparecem no Excel em português; os sem acento
# ficam valendo porque é o que a maioria das pessoas digita.
apelidar("ÉERRO", "EERRO")
apelidar("ÉNÚM", "ENUM")
apelidar("ÉTEXTO", "ETEXTO")
apelidar("ÉCÉL.VAZIA", "EVAZIO")
apelidar("MÁXIMO", "MAXIMO")
apelidar("MÍNIMO", "MINIMO")
apelidar("MÁX", "MAXIMO")
apelidar("MÍN", "MINIMO")
apelidar("MAX", "MAXIMO")
apelidar("MIN", "MINIMO")
apelidar("MÉDIA", "MEDIA")
apelidar("POTÊNCIA", "POTENCIA")
apelidar("NÃO", "NAO")
apelidar("ÍNDICE", "INDICE")
apelidar("PRI.MAIÚSCULA", "PRI.MAIUSCULA")
apelidar("MAIÚSCULA", "MAIUSCULA")
apelidar("MINÚSCULA", "MINUSCULA")


def buscar(nome: str) -> Funcao | None:
    """Encontra a função pelo nome, ignorando a caixa."""
    return BIBLIOTECA.get(nome.upper())


def nomes() -> list[str]:
    """Todos os nomes registrados, em ordem alfabética."""
    return sorted(BIBLIOTECA)


__all__ = ["BIBLIOTECA", "ILIMITADO", "Funcao", "apelidar", "buscar", "nomes", "registrar"]
