from planilha import csv_io
from planilha.planilha import Planilha

CONTEUDO = "\n".join(
    [
        "produto;qtd;preco;total",
        "caneta;10;2,5;=B2*C2",
        "caderno;3;15;=B3*C3",
        ";;;=SOMA(D2:D3)",
    ]
)


def test_importa_e_calcula():
    p = csv_io.importar_texto(CONTEUDO)

    assert p.valor("A2") == "caneta"
    assert p.valor("B2") == 10.0
    assert p.valor("D2") == 25.0
    assert p.valor("D4") == 70.0


def test_campos_vazios_nao_viram_celula():
    p = csv_io.importar_texto(CONTEUDO)

    assert "A4" not in p


def test_importa_com_outro_delimitador():
    p = csv_io.importar_texto("a,b\n1,2", delimitador=",")

    assert p.valor("B2") == 2.0


def test_exporta_os_valores_calculados():
    p = csv_io.importar_texto(CONTEUDO)

    linhas = csv_io.exportar_texto(p).strip().split("\n")

    assert linhas[1] == "caneta;10;2.5;25"
    assert linhas[3] == ";;;70"


def test_exporta_as_formulas():
    p = csv_io.importar_texto(CONTEUDO)

    linhas = csv_io.exportar_texto(p, formulas=True).strip().split("\n")

    assert linhas[1].endswith("=B2*C2")


def test_a_ida_e_volta_preserva_as_formulas():
    original = csv_io.importar_texto(CONTEUDO)

    devolta = csv_io.importar_texto(csv_io.exportar_texto(original, formulas=True))

    assert devolta.formula("D4") == "=SOMA(D2:D3)"
    assert devolta.valor("D4") == 70.0


def test_exporta_planilha_vazia():
    assert csv_io.exportar_texto(Planilha()) == ""


def test_grava_e_le_arquivo(tmp_path):
    caminho = tmp_path / "tabela.csv"
    caminho.write_text(CONTEUDO, encoding="utf-8")

    p = csv_io.importar(caminho)

    assert p.valor("D4") == 70.0

    saida = tmp_path / "saida.csv"
    csv_io.exportar(p, saida)

    assert "70" in saida.read_text(encoding="utf-8")
