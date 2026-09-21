"""Grafo de dependências entre células.

É o que faz a planilha não recalcular tudo a cada digitação: mexer em B2 só
obriga a refazer B2 e quem lê B2, direta ou indiretamente, e nessa ordem. O
mesmo grafo entrega de graça a detecção de referência circular — o que sobra
sem ordem topológica está num ciclo.
"""

from __future__ import annotations

from collections import deque

#: Uma célula no grafo é identificada pelo par linha/coluna.
Chave = tuple[int, int]


class Grafo:
    """Quem lê quem, nas duas direções."""

    __slots__ = ("_le", "_lido_por")

    def __init__(self) -> None:
        self._le: dict[Chave, set[Chave]] = {}
        self._lido_por: dict[Chave, set[Chave]] = {}

    def definir(self, celula: Chave, dependencias) -> None:
        """Declara de quais células esta passa a depender."""
        self.remover(celula)

        # O argumento pode ser um gerador, e ele é percorrido mais de uma vez
        # aqui embaixo. A célula que aparece entre as próprias dependências
        # continua no conjunto de propósito: é um ciclo de tamanho um, e o
        # recálculo precisa enxergá-lo como tal.
        self._le[celula] = set(dependencias)

        for dependencia in self._le[celula]:
            self._lido_por.setdefault(dependencia, set()).add(celula)

    def remover(self, celula: Chave) -> None:
        """Tira as ligações que saem desta célula."""
        for dependencia in self._le.pop(celula, ()):
            leitores = self._lido_por.get(dependencia)
            if leitores is not None:
                leitores.discard(celula)
                if not leitores:
                    del self._lido_por[dependencia]

    def le(self, celula: Chave) -> frozenset[Chave]:
        """Células lidas diretamente por esta."""
        return frozenset(self._le.get(celula, ()))

    def lido_por(self, celula: Chave) -> frozenset[Chave]:
        """Células que leem esta diretamente."""
        return frozenset(self._lido_por.get(celula, ()))

    def dependentes(self, celulas) -> set[Chave]:
        """Todas as células afetadas por uma mudança nas informadas."""
        alcancadas: set[Chave] = set()
        fila = deque(celulas)

        while fila:
            atual = fila.popleft()
            for leitor in self._lido_por.get(atual, ()):
                if leitor not in alcancadas:
                    alcancadas.add(leitor)
                    fila.append(leitor)

        return alcancadas

    def ordem_de_recalculo(self, alteradas) -> tuple[list[Chave], set[Chave]]:
        """Ordem em que recalcular, e o que ficou preso em ciclo.

        Roda um Kahn sobre o subgrafo afetado. O que não sai da fila está em um
        ciclo, ou depende de alguém que está.
        """
        alvos = set(alteradas)
        afetadas = alvos | self.dependentes(alvos)

        pendentes: dict[Chave, int] = {}
        for celula in afetadas:
            pendentes[celula] = sum(1 for lida in self._le.get(celula, ()) if lida in afetadas)

        fila = deque(sorted(celula for celula, grau in pendentes.items() if grau == 0))
        ordem: list[Chave] = []

        while fila:
            atual = fila.popleft()
            ordem.append(atual)

            for leitor in sorted(self._lido_por.get(atual, ())):
                if leitor not in pendentes:
                    continue
                pendentes[leitor] -= 1
                if pendentes[leitor] == 0:
                    fila.append(leitor)

        em_ciclo = afetadas - set(ordem)
        return ordem, em_ciclo

    def ciclo_de(self, celula: Chave) -> list[Chave] | None:
        """Um caminho que sai da célula e volta nela, se existir.

        Serve para a mensagem de erro: dizer "#CIRC!" ajuda pouco, mostrar
        ``B2 → C3 → B2`` resolve o problema de quem está olhando.
        """
        caminho: list[Chave] = []
        visitando: set[Chave] = set()

        def descer(atual: Chave) -> list[Chave] | None:
            if atual in visitando:
                inicio = caminho.index(atual)
                return caminho[inicio:] + [atual]

            visitando.add(atual)
            caminho.append(atual)

            for lida in sorted(self._le.get(atual, ())):
                encontrado = descer(lida)
                if encontrado is not None:
                    return encontrado

            caminho.pop()
            visitando.discard(atual)
            return None

        return descer(celula)

    def __len__(self) -> int:
        return len(self._le)
