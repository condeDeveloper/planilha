import pytest

from planilha import sintaxe
from planilha.lexer import ErroDeSintaxe
from planilha.parser import analisar
from planilha.valores import NAO_DISPONIVEL


def test_le_literal_numerico():
    assert analisar("=42") == sintaxe.Numero(42.0)


def test_le_literal_de_texto():
    assert analisar('="oi"') == sintaxe.Texto("oi")


def test_le_booleanos():
    assert analisar("=VERDADEIRO") == sintaxe.Booleano(True)
    assert analisar("=falso") == sintaxe.Booleano(False)


def test_le_erro_literal():
    assert analisar("=#N/D") == sintaxe.ErroLiteral(NAO_DISPONIVEL)


def test_le_referencia_e_intervalo():
    assert isinstance(analisar("=A1"), sintaxe.Celula)
    assert isinstance(analisar("=A1:B2"), sintaxe.Faixa)


def test_multiplicacao_vem_antes_da_soma():
    arvore = analisar("=1+2*3")

    assert arvore.operador == "+"
    assert arvore.direita.operador == "*"


def test_parenteses_mudam_a_ordem():
    arvore = analisar("=(1+2)*3")

    assert arvore.operador == "*"
    assert arvore.esquerda.operador == "+"


def test_soma_e_subtracao_associam_para_a_esquerda():
    arvore = analisar("=1-2-3")

    assert arvore.esquerda.operador == "-"
    assert arvore.direita == sintaxe.Numero(3.0)


def test_potencia_associa_para_a_direita():
    arvore = analisar("=2^3^2")

    assert arvore.operador == "^"
    assert arvore.direita.operador == "^"


def test_o_sinal_une_mais_forte_que_a_potencia():
    # Como no Excel: -2^2 é (-2)^2, e dá 4.
    arvore = analisar("=-2^2")

    assert arvore.operador == "^"
    assert isinstance(arvore.esquerda, sintaxe.Unario)


def test_concatenacao_vem_depois_da_soma():
    arvore = analisar('=1+2&"x"')

    assert arvore.operador == "&"
    assert arvore.esquerda.operador == "+"


def test_comparacao_e_a_de_menor_precedencia():
    arvore = analisar("=1+2>3")

    assert arvore.operador == ">"
    assert arvore.esquerda.operador == "+"


def test_percentual_e_sufixo():
    assert analisar("=50%") == sintaxe.Percentual(sintaxe.Numero(50.0))


def test_le_chamada_de_funcao():
    arvore = analisar("=SOMA(A1;2)")

    assert arvore == sintaxe.Chamada("SOMA", (sintaxe.Celula(analisar("=A1").referencia), sintaxe.Numero(2.0)))


def test_o_nome_da_funcao_vira_caixa_alta():
    assert analisar("=soma(1)").nome == "SOMA"


def test_funcao_sem_argumentos():
    assert analisar("=VERDADEIRO()") == sintaxe.Chamada("VERDADEIRO", ())


def test_funcoes_aninhadas():
    arvore = analisar("=SE(SOMA(A1:A3)>10;1;0)")

    assert arvore.nome == "SE"
    assert len(arvore.argumentos) == 3


@pytest.mark.parametrize("formula", ["=", "=1+", "=(1", "=1)", "=SOMA(1;", "=;", "=A1:", "=*2"])
def test_formula_malformada_reclama(formula):
    with pytest.raises(ErroDeSintaxe):
        analisar(formula)


def test_nome_desconhecido_solto_reclama():
    with pytest.raises(ErroDeSintaxe):
        analisar("=banana")


def test_sobra_no_fim_reclama():
    with pytest.raises(ErroDeSintaxe):
        analisar("=1 2")


def test_lista_as_dependencias_de_uma_celula():
    arvore = analisar("=A1+SOMA(B1:B3)*C1")

    nomes = sorted(str(referencia) for referencia in sintaxe.dependencias(arvore))

    assert nomes == ["A1", "B1", "B2", "B3", "C1"]


def test_formula_sem_referencia_nao_tem_dependencia():
    assert list(sintaxe.dependencias(analisar("=1+2"))) == []


def test_o_cifrao_nao_muda_a_dependencia():
    assert [str(r) for r in sintaxe.dependencias(analisar("=$A$1"))] == ["A1"]
