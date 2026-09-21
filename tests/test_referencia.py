import pytest

from planilha.referencia import (
    Intervalo,
    Referencia,
    ReferenciaInvalida,
    coluna_para_letras,
    letras_para_coluna,
)


@pytest.mark.parametrize(
    "letras, numero",
    [("A", 1), ("B", 2), ("Z", 26), ("AA", 27), ("AB", 28), ("AZ", 52), ("BA", 53), ("ZZ", 702), ("AAA", 703)],
)
def test_converte_letras_em_numero_de_coluna(letras, numero):
    assert letras_para_coluna(letras) == numero
    assert coluna_para_letras(numero) == letras


def test_a_conversao_de_coluna_e_reversivel():
    for coluna in range(1, 1000):
        assert letras_para_coluna(coluna_para_letras(coluna)) == coluna


def test_letras_minusculas_valem_igual():
    assert letras_para_coluna("ab") == 28


@pytest.mark.parametrize("entrada", ["", "A1", "1"])
def test_coluna_invalida_reclama(entrada):
    with pytest.raises(ReferenciaInvalida):
        letras_para_coluna(entrada)


def test_coluna_zero_reclama():
    with pytest.raises(ReferenciaInvalida):
        coluna_para_letras(0)


def test_le_referencia_simples():
    referencia = Referencia.de("C7")

    assert referencia.coluna == 3
    assert referencia.linha == 7
    assert not referencia.linha_fixa
    assert not referencia.coluna_fixa
    assert str(referencia) == "C7"


@pytest.mark.parametrize(
    "texto, coluna_fixa, linha_fixa",
    [("A1", False, False), ("$A1", True, False), ("A$1", False, True), ("$A$1", True, True)],
)
def test_le_os_cifroes(texto, coluna_fixa, linha_fixa):
    referencia = Referencia.de(texto)

    assert referencia.coluna_fixa is coluna_fixa
    assert referencia.linha_fixa is linha_fixa
    assert str(referencia) == texto


def test_aceita_minusculas_e_espacos():
    assert Referencia.de("  b12 ") == Referencia.de("B12")


@pytest.mark.parametrize("texto", ["", "A", "1", "A0", "1A", "A1B", "AAAA1", "$", "A$", "A1:B2"])
def test_referencia_invalida_reclama(texto):
    with pytest.raises(ReferenciaInvalida):
        Referencia.de(texto)


def test_a_chave_ignora_os_cifroes():
    assert Referencia.de("$B$3").chave == Referencia.de("B3").chave


def test_sem_travas_remove_os_cifroes():
    assert Referencia.de("$B$3").sem_travas() == Referencia.de("B3")


def test_desloca_respeitando_o_que_esta_travado():
    assert str(Referencia.de("B2").deslocada(1, 1)) == "C3"
    assert str(Referencia.de("$B2").deslocada(1, 1)) == "$B3"
    assert str(Referencia.de("B$2").deslocada(1, 1)) == "C$2"
    assert str(Referencia.de("$B$2").deslocada(5, 5)) == "$B$2"


def test_deslocar_para_fora_da_planilha_reclama():
    with pytest.raises(ReferenciaInvalida):
        Referencia.de("A1").deslocada(-1, 0)


def test_referencias_sao_ordenaveis():
    assert sorted([Referencia.de("B1"), Referencia.de("A2"), Referencia.de("A1")])[0] == Referencia.de("A1")


def test_le_intervalo():
    intervalo = Intervalo.de("A1:C3")

    assert intervalo.linhas == 3
    assert intervalo.colunas == 3
    assert len(intervalo) == 9
    assert str(intervalo) == "A1:C3"


def test_intervalo_normaliza_cantos_invertidos():
    assert Intervalo.de("C3:A1") == Intervalo.de("A1:C3")


def test_intervalo_percorre_da_esquerda_para_a_direita():
    percorrido = [str(referencia) for referencia in Intervalo.de("A1:B2").celulas()]

    assert percorrido == ["A1", "B1", "A2", "B2"]


def test_intervalo_sabe_o_que_esta_dentro():
    intervalo = Intervalo.de("B2:D4")

    assert intervalo.contem(Referencia.de("C3"))
    assert not intervalo.contem(Referencia.de("A1"))
    assert not intervalo.contem(Referencia.de("E3"))


def test_intervalo_de_uma_celula_so():
    assert len(Intervalo.de("A1:A1")) == 1


@pytest.mark.parametrize("texto", ["A1", "A1:B2:C3", "A1:", ":B2"])
def test_intervalo_invalido_reclama(texto):
    with pytest.raises(ReferenciaInvalida):
        Intervalo.de(texto)
