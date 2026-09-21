import pytest

from planilha import Planilha
from planilha.referencia import Referencia, ReferenciaInvalida
from planilha.valores import CIRCULAR, DIV_ZERO, VALOR, VAZIO


def test_guarda_e_devolve_um_numero():
    p = Planilha()
    p.definir("A1", 42)

    assert p.valor("A1") == 42.0


def test_texto_que_e_numero_vira_numero():
    p = Planilha()
    p.definir("A1", "42")
    p.definir("A2", "1,5")

    assert p.valor("A1") == 42.0
    assert p.valor("A2") == 1.5


def test_texto_que_nao_e_numero_continua_texto():
    p = Planilha()
    p.definir("A1", "banana")

    assert p.valor("A1") == "banana"


def test_verdadeiro_e_falso_digitados_viram_booleano():
    p = Planilha()
    p.definir("A1", "VERDADEIRO")

    assert p.valor("A1") is True


def test_celula_nunca_escrita_esta_vazia():
    assert Planilha().valor("Z99") is VAZIO


def test_calcula_uma_formula():
    p = Planilha()
    p.definir("A1", 10)
    p.definir("A2", 32)
    p.definir("B1", "=A1+A2")

    assert p.valor("B1") == 42.0


def test_recalcula_quem_depende_da_celula_alterada():
    p = Planilha()
    p.definir("A1", 10)
    p.definir("B1", "=A1*2")
    p.definir("C1", "=B1+1")

    p.definir("A1", 100)

    assert p.valor("B1") == 200.0
    assert p.valor("C1") == 201.0


def test_recalcula_uma_cadeia_longa():
    p = Planilha()
    p.definir("A1", 1)
    for linha in range(2, 20):
        p.definir(f"A{linha}", f"=A{linha - 1}+1")

    p.definir("A1", 100)

    assert p.valor("A19") == 118.0


def test_a_formula_fica_disponivel_separada_do_valor():
    p = Planilha()
    p.definir("A1", 2)
    p.definir("B1", "=A1*3")

    assert p.formula("B1") == "=A1*3"
    assert p.valor("B1") == 6.0
    assert p.formula("A1") is None


def test_a_entrada_original_e_preservada():
    p = Planilha()
    p.definir("A1", "=1+1")

    assert p.entrada("A1") == "=1+1"


def test_limpar_apaga_e_recalcula_os_dependentes():
    p = Planilha()
    p.definir("A1", 10)
    p.definir("B1", "=A1+5")

    p.limpar("A1")

    assert p.valor("A1") is VAZIO
    assert p.valor("B1") == 5.0


def test_definir_vazio_equivale_a_limpar():
    p = Planilha()
    p.definir("A1", 10)
    p.definir("A1", "")

    assert p.valor("A1") is VAZIO
    assert "A1" not in p


def test_referencia_circular_direta():
    p = Planilha()
    p.definir("A1", "=A1+1")

    assert p.valor("A1") == CIRCULAR


def test_referencia_circular_indireta():
    p = Planilha()
    p.definir("A1", "=B1")
    p.definir("B1", "=A1")

    assert p.valor("A1") == CIRCULAR
    assert p.valor("B1") == CIRCULAR


def test_mostra_o_caminho_da_referencia_circular():
    p = Planilha()
    p.definir("A1", "=B1")
    p.definir("B1", "=C1")
    p.definir("C1", "=A1")

    assert p.ciclo("A1") == ["A1", "B1", "C1", "A1"]


def test_sem_ciclo_nao_ha_caminho():
    p = Planilha()
    p.definir("A1", 1)

    assert p.ciclo("A1") is None


def test_desfazer_o_ciclo_devolve_o_valor():
    p = Planilha()
    p.definir("A1", "=B1")
    p.definir("B1", "=A1")
    p.definir("B1", 7)

    assert p.valor("B1") == 7.0
    assert p.valor("A1") == 7.0


def test_formula_malformada_vira_erro_de_valor():
    p = Planilha()
    p.definir("A1", "=1+")

    assert p.valor("A1") == VALOR
    assert p.formula("A1") == "=1+"


def test_a_formula_malformada_continua_errada_apos_recalculo():
    p = Planilha()
    p.definir("A1", "=1+")
    p.definir("B1", 1)

    assert p.valor("A1") == VALOR


def test_o_erro_se_propaga_para_os_dependentes():
    p = Planilha()
    p.definir("A1", 0)
    p.definir("B1", "=1/A1")
    p.definir("C1", "=B1+1")

    assert p.valor("C1") == DIV_ZERO


def test_aceita_referencia_em_vez_de_texto():
    p = Planilha()
    p.definir(Referencia.de("A1"), 5)

    assert p.valor(Referencia.de("A1")) == 5.0


def test_definir_varias_de_uma_vez():
    p = Planilha()
    p.definir_varias({"A1": 1, "A2": 2, "A3": "=A1+A2"})

    assert p.valor("A3") == 3.0


def test_le_um_intervalo():
    p = Planilha()
    p.definir_varias({"A1": 1, "B1": 2, "A2": 3, "B2": 4})

    assert p.intervalo("A1:B2") == [1.0, 2.0, 3.0, 4.0]


def test_texto_da_celula_sai_formatado():
    p = Planilha()
    p.definir("A1", 4)
    p.definir("A2", "=A1/0")

    assert p.texto("A1") == "4"
    assert p.texto("A2") == "#DIV/0!"


def test_numero_da_celula_converte():
    p = Planilha()
    p.definir("A1", "7")

    assert p.numero("A1") == 7.0


def test_tamanho_e_pertencimento():
    p = Planilha()
    p.definir_varias({"A1": 1, "B2": 2})

    assert len(p) == 2
    assert "A1" in p
    assert "C3" not in p
    assert 42 not in p


def test_lista_as_celulas_preenchidas_em_ordem():
    p = Planilha()
    p.definir_varias({"B2": 1, "A1": 2, "A2": 3})

    assert [str(referencia) for referencia in p.preenchidas] == ["A1", "A2", "B2"]


def test_dimensoes():
    p = Planilha()

    assert p.dimensoes == (0, 0)

    p.definir("C5", 1)
    assert p.dimensoes == (5, 3)


def test_referencia_invalida_reclama():
    with pytest.raises(ReferenciaInvalida):
        Planilha().definir("banana", 1)


def test_o_cifrao_nao_muda_o_resultado():
    p = Planilha()
    p.definir("A1", 10)
    p.definir("B1", "=$A$1*2")

    assert p.valor("B1") == 20.0


def test_exemplo_de_ponta_a_ponta():
    p = Planilha()
    p.definir_varias(
        {
            "A1": "Produto", "B1": "Qtd", "C1": "Preço", "D1": "Total",
            "A2": "caneta", "B2": 10, "C2": 2.5, "D2": "=B2*C2",
            "A3": "caderno", "B3": 3, "C3": 15, "D3": "=B3*C3",
            "A4": "mochila", "B4": 1, "C4": 90, "D4": "=B4*C4",
            "D5": "=SOMA(D2:D4)",
            "D6": "=D5*0,1",
            "D7": "=D5-D6",
        }
    )

    assert p.valor("D5") == 160.0
    assert p.valor("D6") == pytest.approx(16.0)
    assert p.valor("D7") == pytest.approx(144.0)

    p.definir("B2", 20)

    assert p.valor("D5") == 185.0
    assert p.valor("D7") == pytest.approx(166.5)
