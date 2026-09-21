"""Descida recursiva que transforma os tokens em uma árvore.

A precedência segue a do Excel, inclusive na parte que costuma surpreender: o
sinal de menos une mais forte que a potência, então ``-2^2`` vale 4 e não -4.
"""

from __future__ import annotations

from . import sintaxe
from .lexer import ErroDeSintaxe, Tipo, Token, tokenizar
from .referencia import Intervalo, Referencia, ReferenciaInvalida
from .valores import CIRCULAR, DIV_ZERO, NAO_DISPONIVEL, NOME, NUM, REF, VALOR

_COMPARADORES = ("=", "<>", "<", ">", "<=", ">=")

_ERROS = {
    DIV_ZERO.codigo: DIV_ZERO,
    VALOR.codigo: VALOR,
    NOME.codigo: NOME,
    REF.codigo: REF,
    NUM.codigo: NUM,
    NAO_DISPONIVEL.codigo: NAO_DISPONIVEL,
    CIRCULAR.codigo: CIRCULAR,
}


def analisar(formula: str) -> sintaxe.No:
    """Lê a fórmula inteira e devolve a raiz da árvore."""
    return _Parser(tokenizar(formula)).analisar()


class _Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.i = 0

    # --- controle ---------------------------------------------------------

    @property
    def atual(self) -> Token:
        return self.tokens[self.i]

    def avancar(self) -> Token:
        token = self.tokens[self.i]
        self.i += 1
        return token

    def aceitar(self, tipo: Tipo, texto: str | None = None) -> Token | None:
        token = self.atual
        if token.tipo is tipo and (texto is None or token.texto.upper() == texto):
            return self.avancar()
        return None

    def exigir(self, tipo: Tipo, descricao: str) -> Token:
        token = self.aceitar(tipo)
        if token is None:
            raise ErroDeSintaxe(f"Esperava {descricao}, veio {self.atual!s}", self.atual.posicao)
        return token

    # --- gramática --------------------------------------------------------

    def analisar(self) -> sintaxe.No:
        if self.atual.tipo is Tipo.FIM:
            raise ErroDeSintaxe("Fórmula vazia", 0)

        no = self.comparacao()

        if self.atual.tipo is not Tipo.FIM:
            raise ErroDeSintaxe(f"Sobrou {self.atual!s} no fim da fórmula", self.atual.posicao)

        return no

    def comparacao(self) -> sintaxe.No:
        no = self.concatenacao()

        while self.atual.tipo is Tipo.OPERADOR and self.atual.texto in _COMPARADORES:
            operador = self.avancar().texto
            no = sintaxe.Binario(operador, no, self.concatenacao())

        return no

    def concatenacao(self) -> sintaxe.No:
        no = self.aditiva()

        while self.atual.tipo is Tipo.OPERADOR and self.atual.texto == "&":
            self.avancar()
            no = sintaxe.Binario("&", no, self.aditiva())

        return no

    def aditiva(self) -> sintaxe.No:
        no = self.multiplicativa()

        while self.atual.tipo is Tipo.OPERADOR and self.atual.texto in "+-":
            operador = self.avancar().texto
            no = sintaxe.Binario(operador, no, self.multiplicativa())

        return no

    def multiplicativa(self) -> sintaxe.No:
        no = self.potencia()

        while self.atual.tipo is Tipo.OPERADOR and self.atual.texto in "*/":
            operador = self.avancar().texto
            no = sintaxe.Binario(operador, no, self.potencia())

        return no

    def potencia(self) -> sintaxe.No:
        no = self.unaria()

        if self.atual.tipo is Tipo.OPERADOR and self.atual.texto == "^":
            self.avancar()
            # À direita, para que 2^3^2 seja 2^(3^2).
            return sintaxe.Binario("^", no, self.potencia())

        return no

    def unaria(self) -> sintaxe.No:
        if self.atual.tipo is Tipo.OPERADOR and self.atual.texto in "+-":
            operador = self.avancar().texto
            return sintaxe.Unario(operador, self.unaria())

        return self.posfixa()

    def posfixa(self) -> sintaxe.No:
        no = self.primaria()

        while self.aceitar(Tipo.PERCENTUAL):
            no = sintaxe.Percentual(no)

        return no

    def primaria(self) -> sintaxe.No:
        token = self.atual

        if token.tipo is Tipo.NUMERO:
            self.avancar()
            return sintaxe.Numero(float(token.texto))

        if token.tipo is Tipo.TEXTO:
            self.avancar()
            return sintaxe.Texto(token.texto)

        if token.tipo is Tipo.ERRO:
            self.avancar()
            return sintaxe.ErroLiteral(_ERROS[token.texto.upper()])

        if token.tipo is Tipo.ABRE:
            self.avancar()
            no = self.comparacao()
            self.exigir(Tipo.FECHA, "')'")
            return no

        if token.tipo is Tipo.REFERENCIA:
            return self.referencia()

        if token.tipo is Tipo.NOME:
            return self.nome()

        raise ErroDeSintaxe(f"Não esperava {token!s} aqui", token.posicao)

    def referencia(self) -> sintaxe.No:
        inicio = Referencia.de(self.avancar().texto)

        if self.aceitar(Tipo.DOIS_PONTOS):
            fim_token = self.exigir(Tipo.REFERENCIA, "uma referência depois de ':'")
            return sintaxe.Faixa(Intervalo.entre(inicio, Referencia.de(fim_token.texto)))

        return sintaxe.Celula(inicio)

    def nome(self) -> sintaxe.No:
        token = self.avancar()
        nome = token.texto.upper()

        if self.aceitar(Tipo.ABRE):
            return sintaxe.Chamada(nome, self.argumentos())

        if nome in ("VERDADEIRO", "TRUE"):
            return sintaxe.Booleano(True)
        if nome in ("FALSO", "FALSE"):
            return sintaxe.Booleano(False)

        # Um nome solto que parece célula só chega aqui se estourou o limite da
        # planilha; qualquer outro é nome desconhecido mesmo.
        try:
            Referencia.de(nome)
        except ReferenciaInvalida:
            raise ErroDeSintaxe(f"Nome desconhecido: {token.texto}", token.posicao) from None

        raise ErroDeSintaxe(f"Referência fora da planilha: {token.texto}", token.posicao)

    def argumentos(self) -> tuple[sintaxe.No, ...]:
        if self.aceitar(Tipo.FECHA):
            return ()

        argumentos = [self.comparacao()]

        while self.aceitar(Tipo.SEPARADOR):
            argumentos.append(self.comparacao())

        self.exigir(Tipo.FECHA, "')'")
        return tuple(argumentos)
