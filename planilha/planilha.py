"""A planilha em si: células, fórmulas e recálculo.

Cada célula guarda o que foi digitado e o que aquilo virou. Ao mudar uma célula,
só ela e quem depende dela são recalculados, na ordem que o grafo dita.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import sintaxe
from .avaliador import avaliar
from .grafo import Chave, Grafo
from .lexer import ErroDeSintaxe
from .parser import analisar
from .referencia import Intervalo, Referencia
from .valores import CIRCULAR, VALOR, VAZIO, Erro, numero
from .valores import texto as como_texto


@dataclass(frozen=True, slots=True)
class Celula:
    """O conteúdo de uma célula: o que foi digitado e a árvore, se for fórmula."""

    entrada: object
    arvore: sintaxe.No | None = None

    @property
    def eh_formula(self) -> bool:
        """Indica se a entrada começa com ``=``."""
        return self.arvore is not None


class Planilha:
    """Uma grade de células com recálculo automático."""

    __slots__ = ("_celulas", "_valores", "_grafo")

    def __init__(self) -> None:
        self._celulas: dict[Chave, Celula] = {}
        self._valores: dict[Chave, object] = {}
        self._grafo = Grafo()

    # --- escrita ----------------------------------------------------------

    def definir(self, onde: str | Referencia, entrada: object) -> object:
        """Escreve em uma célula e devolve o valor calculado dela."""
        referencia = _referencia(onde)
        chave = referencia.chave

        if entrada is VAZIO or entrada == "":
            return self.limpar(referencia)

        arvore = None
        if isinstance(entrada, str) and entrada.lstrip().startswith("="):
            try:
                arvore = analisar(entrada)
            except ErroDeSintaxe:
                # Fórmula que não compila vira erro de valor na célula, como na
                # planilha de verdade, em vez de explodir na cara de quem
                # digitou. Guardar o erro como árvore mantém o texto original
                # visível e faz a célula continuar devolvendo #VALOR! em todo
                # recálculo seguinte.
                arvore = sintaxe.ErroLiteral(VALOR)

        self._celulas[chave] = Celula(_converter(entrada), arvore)
        self._grafo.definir(chave, (dependencia.chave for dependencia in sintaxe.dependencias(arvore)) if arvore else ())
        self._recalcular([chave])

        return self._valores.get(chave, VAZIO)

    def definir_varias(self, valores: dict) -> None:
        """Escreve várias células de uma vez."""
        for onde, entrada in valores.items():
            self.definir(onde, entrada)

    def limpar(self, onde: str | Referencia) -> object:
        """Apaga a célula e recalcula quem dependia dela."""
        referencia = _referencia(onde)
        chave = referencia.chave

        self._celulas.pop(chave, None)
        self._valores.pop(chave, None)
        self._grafo.definir(chave, ())
        self._recalcular([chave])
        self._grafo.remover(chave)

        return VAZIO

    # --- leitura ----------------------------------------------------------

    def valor(self, onde: str | Referencia) -> object:
        """Valor calculado de uma célula."""
        return self._valores.get(_referencia(onde).chave, VAZIO)

    def texto(self, onde: str | Referencia) -> str:
        """Valor da célula como ele apareceria na tela."""
        return como_texto(self.valor(onde))

    def numero(self, onde: str | Referencia) -> float | Erro:
        """Valor da célula convertido para número."""
        return numero(self.valor(onde))

    def entrada(self, onde: str | Referencia) -> object:
        """O que foi digitado na célula."""
        celula = self._celulas.get(_referencia(onde).chave)
        return celula.entrada if celula else VAZIO

    def formula(self, onde: str | Referencia) -> str | None:
        """A fórmula da célula, ou None se ela não for fórmula."""
        celula = self._celulas.get(_referencia(onde).chave)
        if celula is None or not celula.eh_formula:
            return None
        return str(celula.entrada)

    def intervalo(self, texto: str) -> list[object]:
        """Valores de um intervalo, da esquerda para a direita."""
        return [self.valor(referencia) for referencia in Intervalo.de(texto).celulas()]

    def ciclo(self, onde: str | Referencia) -> list[str] | None:
        """O caminho da referência circular que passa por esta célula."""
        caminho = self._grafo.ciclo_de(_referencia(onde).chave)
        if caminho is None:
            return None
        return [str(Referencia(linha, coluna)) for linha, coluna in caminho]

    @property
    def preenchidas(self) -> list[Referencia]:
        """Todas as células com conteúdo, em ordem de linha e coluna."""
        return [Referencia(linha, coluna) for linha, coluna in sorted(self._celulas)]

    @property
    def dimensoes(self) -> tuple[int, int]:
        """Linhas e colunas ocupadas, contando a partir de A1."""
        if not self._celulas:
            return (0, 0)
        linhas = max(linha for linha, _ in self._celulas)
        colunas = max(coluna for _, coluna in self._celulas)
        return (linhas, colunas)

    def __len__(self) -> int:
        return len(self._celulas)

    def __contains__(self, onde: object) -> bool:
        if not isinstance(onde, (str, Referencia)):
            return False
        return _referencia(onde).chave in self._celulas

    # --- recálculo --------------------------------------------------------

    def _recalcular(self, alteradas) -> None:
        ordem, em_ciclo = self._grafo.ordem_de_recalculo(alteradas)

        for chave in em_ciclo:
            self._valores[chave] = CIRCULAR

        for chave in ordem:
            celula = self._celulas.get(chave)

            if celula is None:
                self._valores.pop(chave, None)
            elif celula.arvore is None:
                self._valores[chave] = celula.entrada
            else:
                self._valores[chave] = avaliar(celula.arvore, self._ler)

    def _ler(self, referencia: Referencia) -> object:
        return self._valores.get(referencia.chave, VAZIO)


def _referencia(onde: str | Referencia) -> Referencia:
    return onde if isinstance(onde, Referencia) else Referencia.de(onde)


def _converter(entrada: object) -> object:
    """Texto digitado que é número vira número, como na planilha."""
    if not isinstance(entrada, str):
        return entrada

    limpo = entrada.strip()
    if limpo.startswith("="):
        return entrada

    if limpo.upper() in ("VERDADEIRO", "TRUE"):
        return True
    if limpo.upper() in ("FALSO", "FALSE"):
        return False

    convertido = numero(limpo)
    return entrada if isinstance(convertido, Erro) else convertido
