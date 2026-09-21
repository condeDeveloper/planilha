"""Referências de célula no estilo A1, com suporte a cifrão e a intervalos.

A coluna é um número escrito em base 26 sem zero — A, B, ... Z, AA, AB — o que
torna a conversão um pouco menos óbvia do que parece: não existe o dígito zero,
então cada passo precisa descontar um.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_CELULA = re.compile(r"^(\$?)([A-Z]{1,3})(\$?)([1-9][0-9]{0,6})$")

#: Maior coluna aceita, equivalente a ZZZ.
MAX_COLUNA = 18277

#: Maior linha aceita.
MAX_LINHA = 1_048_576


class ReferenciaInvalida(ValueError):
    """A referência não está no formato A1."""


def letras_para_coluna(letras: str) -> int:
    """Converte ``A`` em 1, ``Z`` em 26, ``AA`` em 27."""
    if not letras or not letras.isalpha():
        raise ReferenciaInvalida(f"Coluna inválida: {letras!r}.")

    numero = 0
    for letra in letras.upper():
        numero = numero * 26 + (ord(letra) - ord("A") + 1)
    return numero


def coluna_para_letras(coluna: int) -> str:
    """Converte 1 em ``A``, 27 em ``AA``."""
    if coluna < 1:
        raise ReferenciaInvalida(f"Coluna inválida: {coluna}.")

    letras = ""
    while coluna > 0:
        coluna, resto = divmod(coluna - 1, 26)
        letras = chr(ord("A") + resto) + letras
    return letras


@dataclass(frozen=True, slots=True, order=True)
class Referencia:
    """Uma célula, com a informação de quais eixos estão travados por cifrão."""

    linha: int
    coluna: int
    linha_fixa: bool = False
    coluna_fixa: bool = False

    @staticmethod
    def de(texto: str) -> "Referencia":
        """Interpreta ``A1``, ``$A1``, ``A$1`` ou ``$A$1``."""
        casou = _CELULA.match(texto.strip().upper())
        if not casou:
            raise ReferenciaInvalida(f"Referência inválida: {texto!r}.")

        cifrao_coluna, letras, cifrao_linha, digitos = casou.groups()
        coluna = letras_para_coluna(letras)
        linha = int(digitos)

        if coluna > MAX_COLUNA or linha > MAX_LINHA:
            raise ReferenciaInvalida(f"Referência fora da planilha: {texto!r}.")

        return Referencia(linha, coluna, bool(cifrao_linha), bool(cifrao_coluna))

    @property
    def chave(self) -> tuple[int, int]:
        """Par linha/coluna, que é o que identifica a célula de fato."""
        return (self.linha, self.coluna)

    def sem_travas(self) -> "Referencia":
        """A mesma célula, ignorando os cifrões."""
        return Referencia(self.linha, self.coluna)

    def deslocada(self, linhas: int, colunas: int) -> "Referencia":
        """Move a referência, respeitando os eixos travados por cifrão."""
        linha = self.linha if self.linha_fixa else self.linha + linhas
        coluna = self.coluna if self.coluna_fixa else self.coluna + colunas

        if linha < 1 or coluna < 1:
            raise ReferenciaInvalida("O deslocamento saiu da planilha.")

        return Referencia(linha, coluna, self.linha_fixa, self.coluna_fixa)

    def __str__(self) -> str:
        cifrao_coluna = "$" if self.coluna_fixa else ""
        cifrao_linha = "$" if self.linha_fixa else ""
        return f"{cifrao_coluna}{coluna_para_letras(self.coluna)}{cifrao_linha}{self.linha}"


@dataclass(frozen=True, slots=True)
class Intervalo:
    """Um retângulo de células, como ``A1:C3``."""

    inicio: Referencia
    fim: Referencia

    @staticmethod
    def de(texto: str) -> "Intervalo":
        """Interpreta ``A1:C3``, normalizando os cantos se vierem invertidos."""
        partes = texto.strip().split(":")
        if len(partes) != 2:
            raise ReferenciaInvalida(f"Intervalo inválido: {texto!r}.")

        return Intervalo.entre(Referencia.de(partes[0]), Referencia.de(partes[1]))

    @staticmethod
    def entre(uma: Referencia, outra: Referencia) -> "Intervalo":
        """Monta o intervalo a partir de dois cantos quaisquer."""
        inicio = Referencia(
            min(uma.linha, outra.linha),
            min(uma.coluna, outra.coluna),
            uma.linha_fixa,
            uma.coluna_fixa,
        )
        fim = Referencia(
            max(uma.linha, outra.linha),
            max(uma.coluna, outra.coluna),
            outra.linha_fixa,
            outra.coluna_fixa,
        )
        return Intervalo(inicio, fim)

    @property
    def linhas(self) -> int:
        """Quantidade de linhas do retângulo."""
        return self.fim.linha - self.inicio.linha + 1

    @property
    def colunas(self) -> int:
        """Quantidade de colunas do retângulo."""
        return self.fim.coluna - self.inicio.coluna + 1

    def __len__(self) -> int:
        return self.linhas * self.colunas

    def celulas(self):
        """Percorre as células da esquerda para a direita, linha a linha."""
        for linha in range(self.inicio.linha, self.fim.linha + 1):
            for coluna in range(self.inicio.coluna, self.fim.coluna + 1):
                yield Referencia(linha, coluna)

    def contem(self, referencia: Referencia) -> bool:
        """Indica se a célula está dentro do retângulo."""
        return (
            self.inicio.linha <= referencia.linha <= self.fim.linha
            and self.inicio.coluna <= referencia.coluna <= self.fim.coluna
        )

    def __str__(self) -> str:
        return f"{self.inicio}:{self.fim}"
