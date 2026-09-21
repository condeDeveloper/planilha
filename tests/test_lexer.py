import pytest

from planilha.lexer import ErroDeSintaxe, Tipo, tokenizar


def tipos(formula):
    return [token.tipo for token in tokenizar(formula)][:-1]


def textos(formula):
    return [token.texto for token in tokenizar(formula)][:-1]


def test_a_lista_termina_com_o_token_de_fim():
    assert tokenizar("1")[-1].tipo is Tipo.FIM


def test_ignora_o_igual_inicial():
    assert textos("=1+2") == ["1", "+", "2"]


def test_ignora_espacos():
    assert textos("  1   +  2 ") == ["1", "+", "2"]


def test_le_numero_com_ponto_ou_virgula():
    assert textos("1.5") == ["1.5"]
    assert textos("1,5") == ["1.5"]


def test_le_notacao_cientifica():
    assert textos("2E3") == ["2E3"]
    assert textos("1.5e-3") == ["1.5e-3"]


def test_nao_confunde_numero_com_referencia_colada():
    # "2E" não é notação científica; o E precisa de dígitos depois.
    assert tipos("2+E3") == [Tipo.NUMERO, Tipo.OPERADOR, Tipo.REFERENCIA]


def test_le_texto_entre_aspas():
    assert textos('"oi"') == ["oi"]


def test_aspas_duplicadas_viram_uma_so():
    assert textos('"diz ""oi"""') == ['diz "oi"']


def test_texto_sem_fechar_reclama():
    with pytest.raises(ErroDeSintaxe):
        tokenizar('"sem fim')


def test_distingue_referencia_de_nome():
    assert tipos("A1") == [Tipo.REFERENCIA]
    assert tipos("SOMA") == [Tipo.NOME]


def test_le_referencia_com_cifrao():
    assert tipos("$A$1") == [Tipo.REFERENCIA]


def test_le_nome_de_funcao_com_ponto():
    assert textos("CONT.SE(A1:A2;1)")[0] == "CONT.SE"


def test_le_operadores_de_dois_caracteres():
    assert textos("1<=2") == ["1", "<=", "2"]
    assert textos("1<>2") == ["1", "<>", "2"]
    assert textos("1>=2") == ["1", ">=", "2"]


def test_le_os_sinais_de_pontuacao():
    assert tipos("F(A1:B2;3)%") == [
        Tipo.NOME,
        Tipo.ABRE,
        Tipo.REFERENCIA,
        Tipo.DOIS_PONTOS,
        Tipo.REFERENCIA,
        Tipo.SEPARADOR,
        Tipo.NUMERO,
        Tipo.FECHA,
        Tipo.PERCENTUAL,
    ]


def test_le_erro_escrito_na_formula():
    assert tipos("#N/D") == [Tipo.ERRO]
    assert textos("#DIV/0!") == ["#DIV/0!"]


def test_erro_desconhecido_reclama():
    with pytest.raises(ErroDeSintaxe):
        tokenizar("#QUALQUER")


def test_caractere_estranho_reclama():
    with pytest.raises(ErroDeSintaxe) as capturado:
        tokenizar("1 ~ 2")

    assert capturado.value.posicao == 2


def test_formula_vazia_so_tem_o_fim():
    tokens = tokenizar("")

    assert len(tokens) == 1
    assert tokens[0].tipo is Tipo.FIM
