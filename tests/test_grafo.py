from planilha.grafo import Grafo


def chave(texto):
    from planilha.referencia import Referencia

    return Referencia.de(texto).chave


def test_registra_as_duas_direcoes():
    grafo = Grafo()
    grafo.definir(chave("B1"), [chave("A1"), chave("A2")])

    assert grafo.le(chave("B1")) == {chave("A1"), chave("A2")}
    assert grafo.lido_por(chave("A1")) == {chave("B1")}


def test_redefinir_troca_as_ligacoes():
    grafo = Grafo()
    grafo.definir(chave("B1"), [chave("A1")])
    grafo.definir(chave("B1"), [chave("A2")])

    assert grafo.lido_por(chave("A1")) == set()
    assert grafo.lido_por(chave("A2")) == {chave("B1")}


def test_remover_apaga_as_ligacoes_de_saida():
    grafo = Grafo()
    grafo.definir(chave("B1"), [chave("A1")])
    grafo.remover(chave("B1"))

    assert grafo.le(chave("B1")) == set()
    assert grafo.lido_por(chave("A1")) == set()


def test_dependentes_percorre_a_cadeia_inteira():
    grafo = Grafo()
    grafo.definir(chave("B1"), [chave("A1")])
    grafo.definir(chave("C1"), [chave("B1")])
    grafo.definir(chave("D1"), [chave("C1")])

    assert grafo.dependentes([chave("A1")]) == {chave("B1"), chave("C1"), chave("D1")}


def test_quem_ninguem_le_nao_tem_dependente():
    assert Grafo().dependentes([chave("A1")]) == set()


def test_a_ordem_de_recalculo_respeita_as_dependencias():
    grafo = Grafo()
    grafo.definir(chave("B1"), [chave("A1")])
    grafo.definir(chave("C1"), [chave("B1")])

    ordem, em_ciclo = grafo.ordem_de_recalculo([chave("A1")])

    assert em_ciclo == set()
    assert ordem.index(chave("A1")) < ordem.index(chave("B1")) < ordem.index(chave("C1"))


def test_a_ordem_inclui_a_propria_celula_alterada():
    grafo = Grafo()
    ordem, _ = grafo.ordem_de_recalculo([chave("A1")])

    assert ordem == [chave("A1")]


def test_uma_celula_que_alimenta_duas_sai_antes_das_duas():
    grafo = Grafo()
    grafo.definir(chave("B1"), [chave("A1")])
    grafo.definir(chave("C1"), [chave("A1")])
    grafo.definir(chave("D1"), [chave("B1"), chave("C1")])

    ordem, _ = grafo.ordem_de_recalculo([chave("A1")])

    assert ordem[0] == chave("A1")
    assert ordem[-1] == chave("D1")


def test_ciclo_de_duas_celulas_e_detectado():
    grafo = Grafo()
    grafo.definir(chave("A1"), [chave("B1")])
    grafo.definir(chave("B1"), [chave("A1")])

    ordem, em_ciclo = grafo.ordem_de_recalculo([chave("A1")])

    assert ordem == []
    assert em_ciclo == {chave("A1"), chave("B1")}


def test_celula_que_se_referencia_e_ciclo():
    grafo = Grafo()
    grafo.definir(chave("A1"), [chave("A1")])

    _, em_ciclo = grafo.ordem_de_recalculo([chave("A1")])

    assert em_ciclo == {chave("A1")}


def test_quem_depende_de_um_ciclo_tambem_fica_preso():
    grafo = Grafo()
    grafo.definir(chave("A1"), [chave("B1")])
    grafo.definir(chave("B1"), [chave("A1")])
    grafo.definir(chave("C1"), [chave("A1")])

    _, em_ciclo = grafo.ordem_de_recalculo([chave("A1")])

    assert chave("C1") in em_ciclo


def test_mostra_o_caminho_do_ciclo():
    grafo = Grafo()
    grafo.definir(chave("A1"), [chave("B1")])
    grafo.definir(chave("B1"), [chave("C1")])
    grafo.definir(chave("C1"), [chave("A1")])

    caminho = grafo.ciclo_de(chave("A1"))

    assert caminho[0] == caminho[-1] == chave("A1")
    assert len(caminho) == 4


def test_sem_ciclo_o_caminho_e_nulo():
    grafo = Grafo()
    grafo.definir(chave("B1"), [chave("A1")])

    assert grafo.ciclo_de(chave("B1")) is None


def test_o_tamanho_conta_as_celulas_com_dependencia():
    grafo = Grafo()
    grafo.definir(chave("B1"), [chave("A1")])
    grafo.definir(chave("C1"), [chave("A1")])

    assert len(grafo) == 2
