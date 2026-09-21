from planilha.__main__ import executar, interativo, main
from planilha.planilha import Planilha

CONTEUDO = "a;b;soma\n1;2;=A2+B2\n"


def test_calcula_um_arquivo_e_mostra_na_tela(tmp_path, capsys):
    caminho = tmp_path / "entrada.csv"
    caminho.write_text(CONTEUDO, encoding="utf-8")

    assert main([str(caminho)]) == 0
    assert "3" in capsys.readouterr().out


def test_grava_o_resultado_em_arquivo(tmp_path):
    entrada = tmp_path / "entrada.csv"
    entrada.write_text(CONTEUDO, encoding="utf-8")
    saida = tmp_path / "saida.csv"

    assert main([str(entrada), "-s", str(saida)]) == 0
    assert "3" in saida.read_text(encoding="utf-8")


def test_exporta_as_formulas(tmp_path, capsys):
    caminho = tmp_path / "entrada.csv"
    caminho.write_text(CONTEUDO, encoding="utf-8")

    main([str(caminho), "--formulas"])

    assert "=A2+B2" in capsys.readouterr().out


def test_arquivo_inexistente_devolve_codigo_de_erro(tmp_path, capsys):
    assert main([str(tmp_path / "nao-existe.csv")]) == 1
    assert "não consegui" in capsys.readouterr().err.lower()


def test_lista_as_funcoes(capsys):
    assert main(["--funcoes"]) == 0
    assert "SOMA" in capsys.readouterr().out


def test_atribui_um_valor_no_modo_interativo():
    tabela = Planilha()

    assert executar(tabela, "A1 = 10") == "A1 = 10"
    assert tabela.valor("A1") == 10.0


def test_atribui_uma_formula_sem_precisar_do_igual():
    tabela = Planilha()
    executar(tabela, "A1 = 10")
    executar(tabela, "A2 = 32")

    assert executar(tabela, "A3 = SOMA(A1:A2)") == "A3 = 42"


def test_atribui_uma_formula_com_o_igual():
    tabela = Planilha()
    executar(tabela, "A1 = 2")

    assert executar(tabela, "A2 = =A1*3") == "A2 = 6"


def test_consulta_uma_celula():
    tabela = Planilha()
    executar(tabela, "A1 = 7")

    assert executar(tabela, "A1") == "A1 = 7"


def test_referencia_invalida_devolve_a_mensagem():
    assert "inválida" in executar(Planilha(), "banana").lower()


def test_o_laco_interativo_encerra_com_sair():
    linhas = iter(["A1 = 5", "A1", "sair"])
    saida = []

    assert interativo(entrada=lambda: next(linhas), saida=saida.append) == 0
    assert "A1 = 5" in saida


def test_o_laco_interativo_encerra_no_fim_da_entrada():
    def ler():
        raise EOFError

    assert interativo(entrada=ler, saida=lambda _: None) == 0


def test_o_laco_interativo_ignora_linha_em_branco():
    linhas = iter(["", "   ", "sair"])

    assert interativo(entrada=lambda: next(linhas), saida=lambda _: None) == 0
