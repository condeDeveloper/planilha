import pytest

from planilha.valores import (
    DIV_ZERO,
    VALOR,
    VAZIO,
    Erro,
    eh_erro,
    eh_numero,
    formatar_numero,
    logico,
    numero,
    texto,
)


def test_o_erro_se_mostra_pelo_codigo():
    assert str(DIV_ZERO) == "#DIV/0!"
    assert eh_erro(DIV_ZERO)


def test_o_erro_nunca_e_verdadeiro():
    assert not DIV_ZERO


def test_erros_iguais_sao_iguais():
    assert Erro("#N/D") == Erro("#N/D")


def test_booleano_nao_conta_como_numero():
    assert eh_numero(1.5)
    assert eh_numero(3)
    assert not eh_numero(True)
    assert not eh_numero("3")


@pytest.mark.parametrize(
    "entrada, esperado",
    [(VAZIO, 0.0), (True, 1.0), (False, 0.0), (3, 3.0), (2.5, 2.5), ("7", 7.0), ("1,5", 1.5), ("1.234,56", 1234.56)],
)
def test_converte_para_numero(entrada, esperado):
    assert numero(entrada) == esperado


def test_texto_que_nao_e_numero_vira_erro():
    assert numero("banana") == VALOR


def test_erro_atravessa_a_conversao_para_numero():
    assert numero(DIV_ZERO) == DIV_ZERO


@pytest.mark.parametrize(
    "entrada, esperado",
    [(VAZIO, ""), (True, "VERDADEIRO"), (False, "FALSO"), (3.0, "3"), (2.5, "2.5"), ("oi", "oi"), (DIV_ZERO, "#DIV/0!")],
)
def test_converte_para_texto(entrada, esperado):
    assert texto(entrada) == esperado


@pytest.mark.parametrize(
    "entrada, esperado",
    [(True, True), (False, False), (VAZIO, False), (1, True), (0, False), ("VERDADEIRO", True), ("falso", False)],
)
def test_converte_para_logico(entrada, esperado):
    assert logico(entrada) is esperado


def test_texto_qualquer_nao_vira_logico():
    assert logico("talvez") == VALOR


def test_formata_numero_inteiro_sem_casas():
    assert formatar_numero(4.0) == "4"
    assert formatar_numero(-4.0) == "-4"


def test_formata_numero_com_casas():
    assert formatar_numero(4.25) == "4.25"


def test_formata_numero_aparando_o_lixo_do_ponto_flutuante():
    assert formatar_numero(0.1 + 0.2) == "0.3"
