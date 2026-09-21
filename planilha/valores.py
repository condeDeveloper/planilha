"""Os tipos que uma célula pode guardar e os erros que uma fórmula devolve.

Uma planilha não levanta exceção quando a conta dá errado: ela devolve um valor
de erro, que se propaga por quem depende dela. Tratar o erro como um valor de
primeira classe é o que permite que ``=SEERRO(A1/B1; 0)`` funcione.
"""

from __future__ import annotations

from dataclasses import dataclass

#: Valor de uma célula vazia.
VAZIO = None


@dataclass(frozen=True, slots=True)
class Erro:
    """Um erro de fórmula, identificado pelo código que aparece na célula."""

    codigo: str
    detalhe: str = ""

    def __str__(self) -> str:
        return self.codigo

    def __bool__(self) -> bool:
        # Um erro nunca é verdadeiro em um teste lógico; quem quiser tratá-lo
        # precisa usar SEERRO ou ÉERRO, e não deixar passar por acidente.
        return False


DIV_ZERO = Erro("#DIV/0!", "divisão por zero")
VALOR = Erro("#VALOR!", "tipo de valor incompatível")
NOME = Erro("#NOME?", "função ou nome desconhecido")
REF = Erro("#REF!", "referência inválida")
NUM = Erro("#NUM!", "resultado numérico impossível")
NAO_DISPONIVEL = Erro("#N/D", "valor não encontrado")
CIRCULAR = Erro("#CIRC!", "referência circular")

#: Todos os códigos de erro reconhecidos.
CODIGOS = (
    DIV_ZERO.codigo,
    VALOR.codigo,
    NOME.codigo,
    REF.codigo,
    NUM.codigo,
    NAO_DISPONIVEL.codigo,
    CIRCULAR.codigo,
)


def eh_erro(valor: object) -> bool:
    """Indica se o valor é um erro de fórmula."""
    return isinstance(valor, Erro)


def eh_numero(valor: object) -> bool:
    """Indica se o valor conta como número. Booleano não conta."""
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


def numero(valor: object) -> float | Erro:
    """Converte o valor para número seguindo a coerção da planilha.

    Vazio vira zero, booleano vira 1 ou 0, e texto só é aceito se for mesmo um
    número escrito — inclusive com vírgula decimal, que é como se digita aqui.
    """
    if valor is VAZIO:
        return 0.0
    if isinstance(valor, Erro):
        return valor
    if isinstance(valor, bool):
        return 1.0 if valor else 0.0
    if eh_numero(valor):
        return float(valor)
    if isinstance(valor, str):
        texto = valor.strip().replace(".", "").replace(",", ".") if _tem_virgula(valor) else valor.strip()
        try:
            return float(texto)
        except ValueError:
            return VALOR
    return VALOR


def texto(valor: object) -> str:
    """Converte o valor para texto do jeito que apareceria na célula."""
    if valor is VAZIO:
        return ""
    if isinstance(valor, Erro):
        return valor.codigo
    if isinstance(valor, bool):
        return "VERDADEIRO" if valor else "FALSO"
    if eh_numero(valor):
        return formatar_numero(valor)
    return str(valor)


def logico(valor: object) -> bool | Erro:
    """Converte o valor para booleano seguindo a coerção da planilha."""
    if isinstance(valor, Erro):
        return valor
    if isinstance(valor, bool):
        return valor
    if valor is VAZIO:
        return False
    if eh_numero(valor):
        return valor != 0
    if isinstance(valor, str):
        limpo = valor.strip().upper()
        if limpo in ("VERDADEIRO", "TRUE"):
            return True
        if limpo in ("FALSO", "FALSE"):
            return False
    return VALOR


def formatar_numero(valor: float) -> str:
    """Mostra o número sem o ``.0`` inútil dos inteiros."""
    arredondado = round(float(valor), 10)
    if arredondado == int(arredondado):
        return str(int(arredondado))
    return repr(arredondado)


def _tem_virgula(valor: str) -> bool:
    return "," in valor
