import pytest

from planilha.avaliador import avaliar
from planilha.matriz import Matriz
from planilha.parser import analisar
from planilha.referencia import Referencia
from planilha.valores import DIV_ZERO, NOME, NUM, VALOR, VAZIO


def calcular(formula, celulas=None):
    valores = {}
    for onde, valor in (celulas or {}).items():
        valores[Referencia.de(onde).chave] = valor

    return avaliar(analisar(formula), lambda referencia: valores.get(referencia.chave, VAZIO))


@pytest.mark.parametrize(
    "formula, esperado",
    [
        ("=1+2", 3.0),
        ("=10-4", 6.0),
        ("=3*4", 12.0),
        ("=10/4", 2.5),
        ("=2^10", 1024.0),
        ("=-5", -5.0),
        ("=+5", 5.0),
        ("=50%", 0.5),
        ("=1+2*3-4/2", 5.0),
    ],
)
def test_aritmetica(formula, esperado):
    assert calcular(formula) == esperado


def test_divisao_por_zero_vira_erro():
    assert calcular("=1/0") == DIV_ZERO


def test_raiz_de_negativo_por_potencia_fracionaria_vira_erro():
    assert calcular("=(-8)^0.5") == NUM


def test_concatenacao():
    assert calcular('="oi"&" "&"mundo"') == "oi mundo"


def test_concatenacao_converte_numero():
    assert calcular('=1&"-"&2') == "1-2"


@pytest.mark.parametrize(
    "formula, esperado",
    [
        ("=1=1", True),
        ("=1<>1", False),
        ("=1<2", True),
        ("=2<=2", True),
        ("=3>2", True),
        ("=3>=4", False),
        ('="a"<"b"', True),
        ('="A"="a"', True),
    ],
)
def test_comparacoes(formula, esperado):
    assert calcular(formula) is esperado


def test_numero_vem_antes_de_texto_na_ordenacao():
    assert calcular('=1<"a"') is True


def test_le_o_valor_de_uma_celula():
    assert calcular("=A1*2", {"A1": 21.0}) == 42.0


def test_celula_vazia_vale_zero_na_conta():
    assert calcular("=A1+1") == 1.0


def test_intervalo_vira_matriz():
    resultado = calcular("=A1:B2", {"A1": 1.0, "B1": 2.0, "A2": 3.0, "B2": 4.0})

    assert isinstance(resultado, Matriz)
    assert resultado.valores() == [1.0, 2.0, 3.0, 4.0]


def test_matriz_de_um_valor_so_vale_pelo_valor():
    assert calcular("=A1:A1+1", {"A1": 4.0}) == 5.0


def test_matriz_maior_em_conta_escalar_vira_erro():
    assert calcular("=A1:A2+1", {"A1": 1.0, "A2": 2.0}) == VALOR


def test_erro_se_propaga_pela_conta():
    assert calcular("=A1+1", {"A1": DIV_ZERO}) == DIV_ZERO


def test_erro_escrito_na_formula_e_devolvido():
    assert calcular("=#N/D") .codigo == "#N/D"


def test_texto_em_conta_vira_erro_de_valor():
    assert calcular('="banana"+1') == VALOR


def test_texto_que_e_numero_entra_na_conta():
    assert calcular('="3"+1') == 4.0


def test_funcao_desconhecida_vira_erro_de_nome():
    assert calcular("=INEXISTENTE(1)") == NOME


def test_quantidade_errada_de_argumentos_vira_erro_de_valor():
    assert calcular("=ABS(1;2;3)") == VALOR


def test_chama_a_funcao_com_os_argumentos_avaliados():
    assert calcular("=SOMA(A1:A3)", {"A1": 1.0, "A2": 2.0, "A3": 3.0}) == 6.0


def test_o_resultado_inteiro_vira_float():
    assert isinstance(calcular("=1+1"), float)


def test_no_desconhecido_reclama():
    with pytest.raises(TypeError):
        avaliar(object(), lambda _: VAZIO)
