# planilha

Motor de planilha em Python puro, sem dependência nenhuma. Lexer e parser de
fórmulas escritos do zero, grafo de dependências entre células e recálculo
topológico incremental — mexer em `B2` só refaz `B2` e quem lê `B2`, na ordem
certa.

```python
>>> from planilha import Planilha
>>> p = Planilha()
>>> p.definir("A1", 10)
10.0
>>> p.definir("A2", 32)
32.0
>>> p.definir("B1", "=SOMA(A1:A2)*2")
84.0
>>> p.definir("A1", 20)
20.0
>>> p.valor("B1")
104.0
```

## Por que existe

Todo mundo usa planilha e quase ninguém sabe o que acontece entre digitar
`=SOMA(A1:A10)` e o número aparecer. São três problemas empilhados: ler a
fórmula, descobrir em que ordem calcular as células e perceber quando essa
ordem não existe. O terceiro é o mais interessante — a referência circular não
é um caso especial escondido no código, é simplesmente o que sobra quando a
ordenação topológica não consegue emitir todos os nós.

## O que ele entende

| Recurso | Exemplo |
| --- | --- |
| Aritmética | `=1+2*3-4/2`, `=2^10`, `=-5`, `=50%` |
| Comparação | `=A1>=10`, `=A1<>B1`, `="a"="A"` |
| Concatenação | `=A1&" - "&B1` |
| Referências | `A1`, `$A$1`, `A$1`, `$A1` |
| Intervalos | `=SOMA(A1:C10)` |
| Texto e erros literais | `="oi"`, `=#N/D` |
| Funções aninhadas | `=SE(SOMA(A1:A3)>10;"alto";"baixo")` |

O separador de argumentos é o ponto e vírgula, como no Excel em português, o que
libera a vírgula para ser decimal: `=ARRED(1,005;2)` funciona, e dá `1,01` — o
arredondamento passa pela representação decimal justamente para não errar esse
caso.

A precedência segue a do Excel, inclusive na parte que costuma surpreender: o
sinal de menos une mais forte que a potência, então `=-2^2` vale **4**.

## Funções

**Matemática** — `SOMA`, `PRODUTO`, `ABS`, `SINAL`, `ARRED`, `TRUNCAR`, `INT`,
`MOD`, `POTÊNCIA`, `RAIZ`, `SOMASE`, `SOMARPRODUTO`

**Estatística** — `MÉDIA`, `MEDIANA`, `MÍNIMO`, `MÁXIMO`, `MAIOR`, `MENOR`,
`CONT.NUM`, `CONT.VALORES`, `CONT.VAZIO`, `CONT.SE`, `DESVPAD`, `VAR`

**Lógica** — `SE`, `SES`, `E`, `OU`, `NÃO`, `SEERRO`, `ÉERRO`, `ÉNÚM`,
`ÉTEXTO`, `ÉCÉL.VAZIA`, `VERDADEIRO`, `FALSO`

**Texto** — `CONCATENAR`, `MAIÚSCULA`, `MINÚSCULA`, `PRI.MAIÚSCULA`, `ARRUMAR`,
`NUM.CARACT`, `ESQUERDA`, `DIREITA`, `EXT.TEXTO`, `LOCALIZAR`, `SUBSTITUIR`,
`REPT`, `VALOR`, `TEXTO`

**Busca** — `PROCV`, `PROCH`, `CORRESP`, `ÍNDICE`, `ESCOLHER`, `LINHAS`,
`COLUNAS`

Os nomes valem com e sem acento, porque ninguém quer digitar `MÁXIMO` com crase
no meio de um script. `planilha --funcoes` lista todos.

## Erros

Erro não é exceção: é um valor, que se propaga por quem depende dele e pode ser
capturado com `SEERRO`.

| Código | Quando aparece |
| --- | --- |
| `#DIV/0!` | divisão por zero |
| `#VALOR!` | tipo incompatível, ou fórmula que não compila |
| `#NOME?` | função desconhecida |
| `#REF!` | posição fora do intervalo |
| `#NÚM!` | resultado numérico impossível, como `RAIZ(-1)` |
| `#N/D` | `PROCV` que não encontrou |
| `#CIRC!` | referência circular |

No caso da circular, dá para ver o caminho inteiro em vez de só o código:

```python
>>> p.definir("A1", "=B1"); p.definir("B1", "=C1"); p.definir("C1", "=A1")
>>> p.valor("A1")
Erro(codigo='#CIRC!', detalhe='referência circular')
>>> p.ciclo("A1")
['A1', 'B1', 'C1', 'A1']
```

## Linha de comando

```bash
planilha tabela.csv                 # calcula e imprime os valores
planilha tabela.csv --formulas      # imprime as fórmulas de volta
planilha tabela.csv -s saida.csv    # grava o resultado
planilha -d , tabela.csv            # outro delimitador
planilha                            # modo interativo
planilha --funcoes                  # lista as funções
```

No modo interativo, `A1 = 10` escreve e `A1` consulta:

```
planilha> A1 = 10
A1 = 10
planilha> A2 = 32
A2 = 32
planilha> A3 = SOMA(A1:A2)
A3 = 42
planilha> A1 = 20
A1 = 20
planilha> A3
A3 = 52
```

O CSV serve como formato de arquivo: exportar com `--formulas` e importar de
volta devolve a mesma planilha, fórmulas e tudo.

## Estrutura

```
planilha/valores.py     tipos de célula, erros e coerção entre eles
planilha/referencia.py  A1, $A$1 e intervalos; conversão coluna ↔ letras
planilha/lexer.py       fórmula → tokens
planilha/sintaxe.py     nós da árvore e varredura de dependências
planilha/parser.py      tokens → árvore, com a precedência do Excel
planilha/avaliador.py   árvore → valor, contra uma fonte de células
planilha/funcoes/       biblioteca, um módulo por família
planilha/grafo.py       dependências, ordem de recálculo e ciclos
planilha/planilha.py    a grade, o recálculo incremental e o histórico
planilha/csv_io.py      importação e exportação
planilha/__main__.py    linha de comando e modo interativo
```

O avaliador não conhece a planilha — ele recebe uma função que sabe ler uma
célula. É o que permite testá-lo com um dicionário e, na planilha de verdade,
plugar o recálculo com detecção de ciclo.

## Rodando

```bash
pip install -e ".[dev]"
pytest
```

294 testes, sem dependência de runtime. Python 3.10 ou mais novo.

## Limites conhecidos

- Uma planilha só: não há abas nem referência entre arquivos.
- Fórmula matricial de verdade (`CTRL+SHIFT+ENTER`) não existe; intervalo só
  vale como argumento de função.
- Sem formatação, sem datas e sem funções financeiras.
- `SOMASE` e `CONT.SE` aceitam critério com operador e texto, mas não curinga
  (`*`, `?`).

## Licença

MIT.
