"""Linha de comando: abre um CSV, calcula e mostra o resultado.

Sem argumento de arquivo, entra em modo interativo — o jeito mais rápido de
experimentar uma fórmula sem escrever código.
"""

from __future__ import annotations

import argparse
import sys

from . import csv_io, funcoes
from .planilha import Planilha
from .referencia import ReferenciaInvalida
from .valores import texto as como_texto


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada do comando ``planilha``."""
    analisador = argparse.ArgumentParser(
        prog="planilha",
        description="Motor de planilha: calcula fórmulas de um CSV ou de um prompt interativo.",
    )
    analisador.add_argument("arquivo", nargs="?", help="CSV de entrada; sem ele, abre o modo interativo")
    analisador.add_argument("-d", "--delimitador", default=";", help="delimitador do CSV (padrão: ';')")
    analisador.add_argument("-s", "--saida", help="grava o resultado neste arquivo em vez de mostrar na tela")
    analisador.add_argument("--formulas", action="store_true", help="exporta as fórmulas em vez dos valores")
    analisador.add_argument("--funcoes", action="store_true", help="lista as funções disponíveis e sai")

    opcoes = analisador.parse_args(argv)

    if opcoes.funcoes:
        print("\n".join(funcoes.nomes()))
        return 0

    if opcoes.arquivo is None:
        return interativo()

    try:
        tabela = csv_io.importar(opcoes.arquivo, opcoes.delimitador)
    except OSError as erro:
        print(f"Não consegui ler o arquivo: {erro}", file=sys.stderr)
        return 1

    resultado = csv_io.exportar_texto(tabela, opcoes.delimitador, opcoes.formulas)

    if opcoes.saida:
        csv_io.exportar(tabela, opcoes.saida, opcoes.delimitador, opcoes.formulas)
    else:
        print(resultado, end="")

    return 0


def interativo(entrada=None, saida=None) -> int:
    """Laço ``célula = fórmula`` até o usuário sair."""
    ler = entrada or (lambda: input("planilha> "))
    escrever = saida or print

    tabela = Planilha()
    escrever("Digite 'A1 = 10' para escrever e 'A1' para consultar. 'sair' encerra.")

    while True:
        try:
            linha = ler()
        except (EOFError, KeyboardInterrupt):
            escrever("")
            return 0

        if linha is None:
            return 0

        comando = linha.strip()
        if not comando:
            continue
        if comando.lower() in ("sair", "exit", "quit"):
            return 0

        escrever(executar(tabela, comando))


def executar(tabela: Planilha, comando: str) -> str:
    """Interpreta uma linha do modo interativo e devolve o que mostrar."""
    if "=" in comando and not comando.lstrip().startswith("="):
        alvo, _, conteudo = comando.partition("=")
        alvo = alvo.strip()
        conteudo = conteudo.strip()

        # "A1 = SOMA(B1:B3)" é atribuição de fórmula; "A1 = 10" é valor.
        if not conteudo.startswith("=") and _parece_formula(conteudo):
            conteudo = "=" + conteudo

        try:
            tabela.definir(alvo, conteudo)
        except ReferenciaInvalida as erro:
            return str(erro)

        return f"{alvo} = {tabela.texto(alvo)}"

    try:
        return f"{comando} = {tabela.texto(comando)}"
    except ReferenciaInvalida as erro:
        return str(erro)


def _parece_formula(conteudo: str) -> bool:
    return any(caractere in conteudo for caractere in "()+*/^&:") or _tem_nome_de_funcao(conteudo)


def _tem_nome_de_funcao(conteudo: str) -> bool:
    return conteudo.split("(")[0].strip().upper() in funcoes.BIBLIOTECA


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
