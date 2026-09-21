"""Quebra o texto de uma fórmula em tokens.

O separador de argumentos é o ponto e vírgula, como no Excel em português, o que
libera a vírgula para ser usada como separador decimal. Por conveniência o ponto
também é aceito como decimal, já que não há ambiguidade possível.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from .valores import CODIGOS


class Tipo(Enum):
    """Categoria de um token."""

    NUMERO = auto()
    TEXTO = auto()
    NOME = auto()
    REFERENCIA = auto()
    ERRO = auto()
    OPERADOR = auto()
    ABRE = auto()
    FECHA = auto()
    SEPARADOR = auto()
    DOIS_PONTOS = auto()
    PERCENTUAL = auto()
    FIM = auto()


@dataclass(frozen=True, slots=True)
class Token:
    """Um pedaço reconhecido da fórmula, com a posição para a mensagem de erro."""

    tipo: Tipo
    texto: str
    posicao: int

    def __str__(self) -> str:
        return self.texto or self.tipo.name


class ErroDeSintaxe(ValueError):
    """A fórmula não pôde ser lida ou montada."""

    def __init__(self, mensagem: str, posicao: int = -1) -> None:
        super().__init__(mensagem if posicao < 0 else f"{mensagem} (posição {posicao})")
        self.posicao = posicao


_OPERADORES_DUPLOS = ("<=", ">=", "<>")
_OPERADORES_SIMPLES = "+-*/^&=<>"


def tokenizar(formula: str) -> list[Token]:
    """Converte a fórmula em tokens, sem o ``=`` inicial."""
    texto = formula.lstrip()
    if texto.startswith("="):
        texto = texto[1:]

    tokens: list[Token] = []
    i = 0
    n = len(texto)

    while i < n:
        c = texto[i]

        if c.isspace():
            i += 1
            continue

        if c == '"':
            literal, i = _ler_texto(texto, i)
            tokens.append(Token(Tipo.TEXTO, literal, i))
            continue

        if c == "#":
            codigo, i = _ler_erro(texto, i)
            tokens.append(Token(Tipo.ERRO, codigo, i))
            continue

        if c.isdigit() or (c in ".," and i + 1 < n and texto[i + 1].isdigit()):
            numero, i = _ler_numero(texto, i)
            tokens.append(Token(Tipo.NUMERO, numero, i))
            continue

        if c.isalpha() or c in "_$":
            palavra, i = _ler_palavra(texto, i)
            tokens.append(Token(_classificar(palavra), palavra, i))
            continue

        if texto[i : i + 2] in _OPERADORES_DUPLOS:
            tokens.append(Token(Tipo.OPERADOR, texto[i : i + 2], i))
            i += 2
            continue

        if c in _OPERADORES_SIMPLES:
            tokens.append(Token(Tipo.OPERADOR, c, i))
            i += 1
            continue

        simples = {
            "(": Tipo.ABRE,
            ")": Tipo.FECHA,
            ";": Tipo.SEPARADOR,
            ":": Tipo.DOIS_PONTOS,
            "%": Tipo.PERCENTUAL,
        }

        if c in simples:
            tokens.append(Token(simples[c], c, i))
            i += 1
            continue

        raise ErroDeSintaxe(f"Caractere inesperado {c!r}", i)

    tokens.append(Token(Tipo.FIM, "", n))
    return tokens


def _ler_texto(texto: str, i: int) -> tuple[str, int]:
    inicio = i
    i += 1
    partes: list[str] = []

    while i < len(texto):
        if texto[i] == '"':
            # Aspas duplicadas dentro do literal viram uma aspa só, como no Excel.
            if i + 1 < len(texto) and texto[i + 1] == '"':
                partes.append('"')
                i += 2
                continue
            return "".join(partes), i + 1

        partes.append(texto[i])
        i += 1

    raise ErroDeSintaxe("Texto sem aspas de fechamento", inicio)


def _ler_erro(texto: str, i: int) -> tuple[str, int]:
    for codigo in CODIGOS:
        if texto.upper().startswith(codigo, i):
            return codigo, i + len(codigo)

    raise ErroDeSintaxe("Código de erro desconhecido", i)


def _ler_numero(texto: str, i: int) -> tuple[str, int]:
    inicio = i
    visto_separador = False

    while i < len(texto):
        c = texto[i]
        if c.isdigit():
            i += 1
        elif c in ".," and not visto_separador:
            visto_separador = True
            i += 1
        else:
            break

    bruto = texto[inicio:i]

    # A notação científica só é reconhecida quando tem dígito depois do sinal,
    # senão "2E" seria confundido com a célula E de uma linha qualquer.
    if i < len(texto) and texto[i] in "eE":
        j = i + 1
        if j < len(texto) and texto[j] in "+-":
            j += 1
        if j < len(texto) and texto[j].isdigit():
            while j < len(texto) and texto[j].isdigit():
                j += 1
            bruto = texto[inicio:j]
            i = j

    return bruto.replace(",", "."), i


def _ler_palavra(texto: str, i: int) -> tuple[str, int]:
    inicio = i
    while i < len(texto) and (texto[i].isalnum() or texto[i] in "_.$"):
        i += 1
    return texto[inicio:i], i


def _classificar(palavra: str) -> Tipo:
    from .referencia import Referencia, ReferenciaInvalida

    try:
        Referencia.de(palavra)
    except ReferenciaInvalida:
        return Tipo.NOME
    return Tipo.REFERENCIA
