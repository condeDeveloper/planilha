"""O resultado de avaliar um intervalo: um retângulo de valores.

Guardar a forma do retângulo, e não só a lista de valores, é o que permite que
PROCV, ÍNDICE e CORRESP existam. As funções que só somam continuam tratando a
matriz como uma sequência qualquer.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Matriz:
    """Valores de um intervalo, linha a linha."""

    linhas_de_valores: tuple[tuple[object, ...], ...]

    @staticmethod
    def de(linhas) -> "Matriz":
        """Monta a matriz a partir de qualquer sequência de sequências."""
        return Matriz(tuple(tuple(linha) for linha in linhas))

    @staticmethod
    def de_lista(valores) -> "Matriz":
        """Monta uma matriz de uma coluna só."""
        return Matriz(tuple((valor,) for valor in valores))

    @property
    def linhas(self) -> int:
        """Quantidade de linhas."""
        return len(self.linhas_de_valores)

    @property
    def colunas(self) -> int:
        """Quantidade de colunas."""
        return len(self.linhas_de_valores[0]) if self.linhas_de_valores else 0

    def linha(self, indice: int) -> tuple[object, ...]:
        """Uma linha inteira, contando de 1."""
        return self.linhas_de_valores[indice - 1]

    def coluna(self, indice: int) -> tuple[object, ...]:
        """Uma coluna inteira, contando de 1."""
        return tuple(linha[indice - 1] for linha in self.linhas_de_valores)

    def em(self, linha: int, coluna: int) -> object:
        """Um valor pela posição, contando de 1."""
        return self.linhas_de_valores[linha - 1][coluna - 1]

    def __iter__(self):
        for linha in self.linhas_de_valores:
            yield from linha

    def __len__(self) -> int:
        return self.linhas * self.colunas

    def valores(self) -> list[object]:
        """Todos os valores em uma lista, da esquerda para a direita."""
        return list(self)
