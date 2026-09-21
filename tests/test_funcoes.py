import pytest

from planilha import funcoes
from planilha.planilha import Planilha
from planilha.valores import DIV_ZERO, NAO_DISPONIVEL, NUM, REF, VALOR


@pytest.fixture()
def tabela():
    p = Planilha()
    p.definir_varias(
        {
            "A1": 10,
            "A2": 20,
            "A3": 30,
            "A4": "texto",
            "A5": 40,
            "B1": "maçã",
            "B2": "banana",
            "B3": "maçã",
            "B4": "uva",
            "B5": "banana",
        }
    )
    return p


def calcular(tabela, formula):
    tabela.definir("Z1", formula)
    return tabela.valor("Z1")


# --- matemática -----------------------------------------------------------


def test_soma_ignora_texto(tabela):
    assert calcular(tabela, "=SOMA(A1:A5)") == 100.0


def test_soma_aceita_varios_argumentos(tabela):
    assert calcular(tabela, "=SOMA(A1;A2;5)") == 35.0


def test_produto(tabela):
    assert calcular(tabela, "=PRODUTO(A1;A2)") == 200.0


@pytest.mark.parametrize(
    "formula, esperado",
    [
        ("=ABS(-3)", 3.0),
        ("=SINAL(-9)", -1.0),
        ("=SINAL(0)", 0.0),
        ("=INT(3.9)", 3.0),
        ("=INT(-3.1)", -4.0),
        ("=TRUNCAR(3.99)", 3.0),
        ("=TRUNCAR(3.456;2)", 3.45),
        ("=MOD(10;3)", 1.0),
        ("=MOD(-10;3)", 2.0),
        ("=POTENCIA(2;10)", 1024.0),
        ("=RAIZ(81)", 9.0),
    ],
)
def test_matematica(tabela, formula, esperado):
    assert calcular(tabela, formula) == pytest.approx(esperado)


def test_arred_arredonda_o_meio_para_longe_do_zero(tabela):
    assert calcular(tabela, "=ARRED(2.5;0)") == 3.0
    assert calcular(tabela, "=ARRED(-2.5;0)") == -3.0
    assert calcular(tabela, "=ARRED(1.005;2)") == 1.01


def test_mod_por_zero(tabela):
    assert calcular(tabela, "=MOD(1;0)") == DIV_ZERO


def test_raiz_de_negativo(tabela):
    assert calcular(tabela, "=RAIZ(-1)") == NUM


def test_somase_com_criterio_de_comparacao(tabela):
    assert calcular(tabela, '=SOMASE(A1:A5;">15")') == 90.0


def test_somase_com_intervalo_de_soma_separado(tabela):
    assert calcular(tabela, '=SOMASE(B1:B5;"maçã";A1:A5)') == 40.0


def test_somarproduto(tabela):
    tabela.definir_varias({"C1": 2, "C2": 3, "C3": 4})
    assert calcular(tabela, "=SOMARPRODUTO(A1:A3;C1:C3)") == 200.0


def test_somarproduto_com_tamanhos_diferentes(tabela):
    assert calcular(tabela, "=SOMARPRODUTO(A1:A3;A1:A2)") == VALOR


# --- estatística ----------------------------------------------------------


def test_media_ignora_texto(tabela):
    assert calcular(tabela, "=MEDIA(A1:A5)") == 25.0


def test_media_sem_numero_nenhum(tabela):
    assert calcular(tabela, "=MEDIA(B1:B2)") == DIV_ZERO


def test_mediana_com_quantidade_impar(tabela):
    assert calcular(tabela, "=MEDIANA(A1:A3)") == 20.0


def test_mediana_com_quantidade_par(tabela):
    assert calcular(tabela, "=MEDIANA(A1;A2)") == 15.0


def test_minimo_e_maximo(tabela):
    assert calcular(tabela, "=MÍNIMO(A1:A5)") == 10.0
    assert calcular(tabela, "=MÁXIMO(A1:A5)") == 40.0


def test_maior_e_menor(tabela):
    assert calcular(tabela, "=MAIOR(A1:A5;2)") == 30.0
    assert calcular(tabela, "=MENOR(A1:A5;2)") == 20.0


def test_maior_fora_da_faixa(tabela):
    assert calcular(tabela, "=MAIOR(A1:A5;99)") == NUM


def test_contagens(tabela):
    assert calcular(tabela, "=CONT.NUM(A1:A5)") == 4.0
    assert calcular(tabela, "=CONT.VALORES(A1:A5)") == 5.0
    assert calcular(tabela, "=CONT.VAZIO(A1:A10)") == 5.0


def test_cont_se(tabela):
    assert calcular(tabela, '=CONT.SE(B1:B5;"maçã")') == 2.0
    assert calcular(tabela, '=CONT.SE(A1:A5;">=20")') == 3.0


def test_desvio_padrao_e_variancia(tabela):
    assert calcular(tabela, "=VAR(A1;A2;A3)") == pytest.approx(100.0)
    assert calcular(tabela, "=DESVPAD(A1;A2;A3)") == pytest.approx(10.0)


def test_variancia_precisa_de_dois_valores(tabela):
    assert calcular(tabela, "=VAR(A1)") == DIV_ZERO


# --- lógica ---------------------------------------------------------------


def test_se(tabela):
    assert calcular(tabela, '=SE(A1>5;"grande";"pequeno")') == "grande"
    assert calcular(tabela, '=SE(A1>50;"grande";"pequeno")') == "pequeno"


def test_se_sem_o_terceiro_argumento(tabela):
    assert calcular(tabela, "=SE(A1>50;1)") is False


def test_ses(tabela):
    assert calcular(tabela, '=SES(A1>100;"muito";A1>5;"medio";VERDADEIRO;"pouco")') == "medio"


def test_ses_sem_nenhuma_verdadeira(tabela):
    assert calcular(tabela, '=SES(FALSO;"a";FALSO;"b")') == NAO_DISPONIVEL


def test_e_ou_nao(tabela):
    assert calcular(tabela, "=E(A1>5;A2>5)") is True
    assert calcular(tabela, "=E(A1>5;A2>50)") is False
    assert calcular(tabela, "=OU(A1>50;A2>5)") is True
    assert calcular(tabela, "=NÃO(A1>5)") is False


def test_seerro(tabela):
    assert calcular(tabela, '=SEERRO(1/0;"deu ruim")') == "deu ruim"
    assert calcular(tabela, '=SEERRO(10/2;"deu ruim")') == 5.0


def test_testes_de_tipo(tabela):
    assert calcular(tabela, "=ÉERRO(1/0)") is True
    assert calcular(tabela, "=ÉNÚM(A1)") is True
    assert calcular(tabela, "=ÉTEXTO(A4)") is True
    assert calcular(tabela, "=ÉCÉL.VAZIA(Y9)") is True


# --- texto ----------------------------------------------------------------


def test_concatenar(tabela):
    assert calcular(tabela, '=CONCATENAR(B1;" e ";B2)') == "maçã e banana"


def test_caixa(tabela):
    assert calcular(tabela, "=MAIÚSCULA(B2)") == "BANANA"
    assert calcular(tabela, '=MINÚSCULA("ABC")') == "abc"
    assert calcular(tabela, '=PRI.MAIÚSCULA("joão da silva")') == "João Da Silva"


def test_arrumar(tabela):
    assert calcular(tabela, '=ARRUMAR("  muito    espaço  ")') == "muito espaço"


def test_recortes(tabela):
    assert calcular(tabela, "=ESQUERDA(B2;3)") == "ban"
    assert calcular(tabela, "=DIREITA(B2;3)") == "ana"
    assert calcular(tabela, "=EXT.TEXTO(B2;2;3)") == "ana"
    assert calcular(tabela, "=NUM.CARACT(B2)") == 6.0


def test_recorte_de_zero_caracteres(tabela):
    assert calcular(tabela, "=ESQUERDA(B2;0)") == ""


def test_recorte_negativo(tabela):
    assert calcular(tabela, "=ESQUERDA(B2;-1)") == VALOR


def test_localizar(tabela):
    assert calcular(tabela, '=LOCALIZAR("nan";B2)') == 3.0
    assert calcular(tabela, '=LOCALIZAR("zzz";B2)') == NAO_DISPONIVEL


def test_substituir_e_repetir(tabela):
    assert calcular(tabela, '=SUBSTITUIR(B2;"a";"o")') == "bonono"
    assert calcular(tabela, '=REPT("ab";3)') == "ababab"


def test_valor_e_texto(tabela):
    assert calcular(tabela, '=VALOR("12,5")') == 12.5
    assert calcular(tabela, "=TEXTO(A1)") == "10"


# --- busca ----------------------------------------------------------------


@pytest.fixture()
def catalogo():
    p = Planilha()
    p.definir_varias(
        {
            "A1": "caneta", "B1": 3, "C1": "papelaria",
            "A2": "caderno", "B2": 15, "C2": "papelaria",
            "A3": "mochila", "B3": 90, "C3": "bolsas",
        }
    )
    return p


def test_procv_exato(catalogo):
    assert calcular(catalogo, '=PROCV("caderno";A1:C3;2;FALSO)') == 15.0
    assert calcular(catalogo, '=PROCV("caderno";A1:C3;3;FALSO)') == "papelaria"


def test_procv_nao_encontrado(catalogo):
    assert calcular(catalogo, '=PROCV("borracha";A1:C3;2;FALSO)') == NAO_DISPONIVEL


def test_procv_com_coluna_fora_da_tabela(catalogo):
    assert calcular(catalogo, '=PROCV("caneta";A1:C3;9;FALSO)') == REF


def test_procv_ignora_a_caixa(catalogo):
    assert calcular(catalogo, '=PROCV("CADERNO";A1:C3;2;FALSO)') == 15.0


def test_procv_aproximado():
    p = Planilha()
    p.definir_varias({"A1": 0, "B1": "E", "A2": 1000, "B2": "D", "A3": 5000, "B3": "C"})

    assert calcular(p, "=PROCV(2500;A1:B3;2;VERDADEIRO)") == "D"


def test_corresp_exato(catalogo):
    assert calcular(catalogo, '=CORRESP("mochila";A1:A3;0)') == 3.0


def test_corresp_nao_encontrado(catalogo):
    assert calcular(catalogo, '=CORRESP("nada";A1:A3;0)') == NAO_DISPONIVEL


def test_indice(catalogo):
    assert calcular(catalogo, "=ÍNDICE(A1:C3;2;2)") == 15.0


def test_indice_em_faixa_de_uma_coluna(catalogo):
    assert calcular(catalogo, "=ÍNDICE(A1:A3;3)") == "mochila"


def test_indice_fora_da_faixa(catalogo):
    assert calcular(catalogo, "=ÍNDICE(A1:C3;9;9)") == REF


def test_indice_com_corresp(catalogo):
    assert calcular(catalogo, '=ÍNDICE(B1:B3;CORRESP("mochila";A1:A3;0))') == 90.0


def test_proch():
    p = Planilha()
    p.definir_varias({"A1": "jan", "B1": "fev", "A2": 100, "B2": 200})

    assert calcular(p, '=PROCH("fev";A1:B2;2;FALSO)') == 200.0


def test_escolher(catalogo):
    assert calcular(catalogo, '=ESCOLHER(2;"a";"b";"c")') == "b"
    assert calcular(catalogo, '=ESCOLHER(9;"a")') == VALOR


def test_linhas_e_colunas(catalogo):
    assert calcular(catalogo, "=LINHAS(A1:C3)") == 3.0
    assert calcular(catalogo, "=COLUNAS(A1:C3)") == 3.0


# --- registro -------------------------------------------------------------


def test_a_biblioteca_encontra_ignorando_a_caixa():
    assert funcoes.buscar("soma") is funcoes.buscar("SOMA")


def test_funcao_inexistente_nao_e_encontrada():
    assert funcoes.buscar("XPTO") is None


def test_os_nomes_saem_ordenados():
    nomes = funcoes.nomes()

    assert nomes == sorted(nomes)
    assert "SOMA" in nomes


def test_os_apelidos_apontam_para_a_mesma_implementacao():
    assert funcoes.buscar("MÁXIMO").implementacao is funcoes.buscar("MAXIMO").implementacao


def test_a_aridade_e_conferida():
    soma = funcoes.buscar("SOMA")

    assert not soma.aridade_ok(0)
    assert soma.aridade_ok(1)
    assert soma.aridade_ok(50)
