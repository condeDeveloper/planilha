"""Importação e exportação em CSV.

Na exportação dá para escolher entre gravar o que foi digitado — fórmulas e
tudo — ou o resultado do cálculo. O primeiro modo serve de formato de arquivo,
o segundo serve para entregar o número pronto para outro sistema.
"""

from __future__ import annotations

import csv
import io
from pathlib import Path

from .planilha import Planilha
from .referencia import Referencia
from .valores import VAZIO
from .valores import texto as como_texto


def importar_texto(conteudo: str, delimitador: str = ";") -> Planilha:
    """Monta uma planilha a partir de um CSV em memória."""
    planilha = Planilha()
    leitor = csv.reader(io.StringIO(conteudo), delimiter=delimitador)

    for numero_da_linha, linha in enumerate(leitor, start=1):
        for numero_da_coluna, campo in enumerate(linha, start=1):
            if campo.strip() == "":
                continue
            planilha.definir(Referencia(numero_da_linha, numero_da_coluna), campo)

    return planilha


def importar(caminho: str | Path, delimitador: str = ";", codificacao: str = "utf-8") -> Planilha:
    """Monta uma planilha a partir de um arquivo CSV."""
    return importar_texto(Path(caminho).read_text(encoding=codificacao), delimitador)


def exportar_texto(planilha: Planilha, delimitador: str = ";", formulas: bool = False) -> str:
    """Devolve o CSV da planilha, com os valores ou com as fórmulas."""
    linhas, colunas = planilha.dimensoes

    saida = io.StringIO()
    escritor = csv.writer(saida, delimiter=delimitador, lineterminator="\n")

    for linha in range(1, linhas + 1):
        campos = []
        for coluna in range(1, colunas + 1):
            referencia = Referencia(linha, coluna)
            if formulas:
                campos.append(_entrada(planilha, referencia))
            else:
                campos.append(planilha.texto(referencia))
        escritor.writerow(campos)

    return saida.getvalue()


def exportar(
    planilha: Planilha,
    caminho: str | Path,
    delimitador: str = ";",
    formulas: bool = False,
    codificacao: str = "utf-8",
) -> None:
    """Grava o CSV da planilha em um arquivo."""
    Path(caminho).write_text(
        exportar_texto(planilha, delimitador, formulas),
        encoding=codificacao,
        newline="",
    )


def _entrada(planilha: Planilha, referencia: Referencia) -> str:
    bruta = planilha.entrada(referencia)
    return "" if bruta is VAZIO else como_texto(bruta)
