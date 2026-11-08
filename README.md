# Alocação de horários universitários: heurística gulosa vs. VNS

Código do TCC *Heurística gulosa e Busca em Vizinhança Variável na alocação de horários universitários: um estudo em instâncias sintéticas*.

O problema é modelado como coloração de grafos: cada turma é um vértice, turmas que compartilham professor ou grupo de alunos são adjacentes e cada cor é um horário. O notebook compara o **guloso por grau**, o **DSATUR** (referência) e a **VNS (Busca em Vizinhança Variável)** em duas famílias de instâncias sintéticas (benchmark e família densa).

Todo o experimento está em um único arquivo, [`comparacao_alocacao_horarios.ipynb`](comparacao_alocacao_horarios.ipynb). Todos os resultados do trabalho saem de uma única execução dele, do início ao fim.

## Estrutura

```
.
├── comparacao_alocacao_horarios.ipynb   # geração das instâncias, algoritmos, experimentos e figuras
├── requirements.txt                     # versões exatas usadas no TCC
└── resultados/                          # tabelas (.csv), figuras (.png) e ambiente.json
```

## Requisitos

- Python **3.12** (os resultados do TCC foram gerados com 3.12.13)
- `numpy 2.5.3`, `pandas 3.0.6`, `matplotlib 3.11.2` (fixados em `requirements.txt`)
- Jupyter, para executar o notebook (o código usa `display()` e não roda como script Python comum)
- `git`, `lscpu` e `free` são usados apenas para registrar o ambiente em `ambiente.json`; na falta deles, os campos ficam vazios e o restante funciona normalmente

## Instalação

```bash
git clone <url-do-repositorio>
cd new_reservations

python3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install jupyterlab nbconvert ipykernel
```

## Execução

### Opção 1: interface do Jupyter

```bash
jupyter lab comparacao_alocacao_horarios.ipynb
```

Selecione o kernel do `.venv` e use **Kernel → Restart Kernel and Run All Cells**. Não execute células fora de ordem: as funções e os parâmetros definidos no início são usados pelas seções seguintes.

### Opção 2: linha de comando (sem interface)

```bash
jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=-1 \
    comparacao_alocacao_horarios.ipynb
```

`timeout=-1` desativa o limite de tempo por célula, necessário porque as células da VNS levam vários minutos. Para preservar o notebook original, troque `--inplace` por `--output execucao.ipynb`.

### Tempo de execução

A execução completa que gerou os resultados do repositório levou cerca de **40 minutos** em um AMD Ryzen 5 5600G (início e fim registrados em `resultados/ambiente.json`). Quase todo esse tempo vai para a VNS:

- seção 7, benchmark: 15 instâncias × 40 rodadas (600 rodadas);
- seção 8, família densa: seleção das instâncias + 15 instâncias × 20 rodadas (300 rodadas, mais caras por serem grafos mais densos).

O código roda em um único núcleo.

## Resultados gerados

Os arquivos são gravados em `resultados/` e sobrescrevem os existentes:

| Arquivo | Conteúdo | Uso no TCC |
|---|---|---|
| `instancias.csv` | Características dos grafos do exemplo e do benchmark, com ω(G) exato | Tabela 2 |
| `exemplo_120.csv` | Exemplo ilustrativo de 120 turmas | Seção 5.2 |
| `construtivos.csv` | Guloso e DSATUR por instância: horários, ω(G), tempo | Tabelas 2 e 3 |
| `rodadas_vns.csv` | Cada rodada da VNS (K e K + 1) | Tabelas 3 a 5 |
| `resumo_benchmark.csv` | Agregados por tamanho e orçamento de cores | Tabelas 3 e 5, Figuras 1 e 2 |
| `figura_benchmark_tempos.png` | Tempos no benchmark (escala log.) | Figura 1 |
| `figura_benchmark_viabilidade.png` | Taxa de viabilidade da VNS no benchmark | Figura 2 |
| `candidatas_densa.csv` | Todas as candidatas examinadas na família densa | Seção 5 |
| `instancias_densa.csv` | Características das instâncias densas selecionadas | Tabela da família densa |
| `construtivos_densa.csv`, `rodadas_vns_densa.csv`, `resumo_densa.csv` | O mesmo que no benchmark, com K e K − 1 | Seção 5 |
| `figura_densa_tempos.png` | Tempos na família densa (escala log.) | Figura 3 |
| `figura_densa_viabilidade.png` | Taxa de viabilidade da VNS na família densa | Figura 4 |
| `ambiente.json` | Commit, versões das bibliotecas e hardware | Seção 4.4 |

`guloso_tempos.csv` e `teste_folga_cores.csv` são de uma versão anterior do experimento e não são mais gerados pelo notebook.

## O que é reproduzível

- **Exatamente reproduzível**: instâncias, ω(G), número de horários e conflitos de cada método, e todas as rodadas da VNS (conflitos, horários, iterações). Toda a aleatoriedade vem de `numpy.random.default_rng` com sementes fixas:
  - benchmark: `42 + n + 1000·i`, com `n ∈ {60, 100, 140}` e `i = 0, …, 4`;
  - família densa: candidata `j` usa `5000 + n + 1000·j`;
  - rodada `r` da VNS usa a semente da instância `+ r`.

  Use as mesmas versões de `requirements.txt`: outra versão do NumPy pode mudar a sequência de números gerados.
- **Dependente da máquina**: tempos absolutos (`tempo_s`, `tempo_ate_viavel_s` etc.). Em outro hardware os valores mudam; as razões entre métodos e as conclusões qualitativas devem se manter.

## Parâmetros

Os parâmetros do experimento ficam na célula da **seção 0 (Configuração)** do notebook: tamanhos das instâncias, número de instâncias por tamanho, rodadas, iterações e `k_max` da VNS, limite de passos da busca local, configurações do `timeit` e da família densa. Para um teste rápido, reduza `RODADAS_VNS`, `RODADAS_VNS_DENSA` e `TAMANHOS`; para reproduzir o TCC, mantenha os valores do repositório.

## Rastreabilidade

A seção 9 grava em `ambiente.json` o hash do commit atual (`git rev-parse HEAD`). Faça o commit de qualquer alteração no notebook **antes** de executá-lo, para que o hash identifique o código que gerou os resultados.
