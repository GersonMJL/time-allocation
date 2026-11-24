"""Redesenha as figuras de tempo a partir dos resumos já gravados, sem Jupyter e sem rodar os algoritmos.

Lê `resumo_benchmark.csv` e `resumo_densa.csv` de --pasta e grava `figura_benchmark_tempos.png` e
`figura_densa_tempos.png` em --saida (padrão: a mesma pasta). O código de desenho é o mesmo do notebook
`comparacao_alocacao_horarios.ipynb` (`_fmt_br`, `_painel_tempos` e a primeira figura de
`desenhar_figuras_separadas`).

Uso:
    python redesenhar_figuras_tempo.py [--pasta resultados] [--saida PASTA]
"""
import argparse
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd

FIGURAS = (('resumo_benchmark.csv', 'figura_benchmark_tempos.png'),
           ('resumo_densa.csv', 'figura_densa_tempos.png'))


def _fmt_br(valor, casas=0):
    """Número no padrão brasileiro: 5101.3 -> '5.101'; 0.112 (casas=3) -> '0,112'."""
    texto = f'{valor:,.{casas}f}'
    return texto.replace(',', '§').replace('.', ',').replace('§', '.')


def _painel_tempos(ax, resumo, titulo):
    """Tempo da VNS (K) como múltiplo do tempo do guloso, em escala linear.
    Barras: mediana; hastes: intervalo interquartil (Q1 e Q3 da VNS divididos pela mediana do guloso)."""
    base = resumo[resumo['orcamento'] == 'K'].reset_index(drop=True)
    guloso = base['guloso_tempo_mediana_s']
    x = np.arange(len(base))
    largura = 0.36
    series = [
        ('VNS (K), tempo total', 'vns_tempo',
         dict(color='#2f6fdb', edgecolor='#2f6fdb')),
        ('VNS (K), até a primeira solução viável', 'vns_ate_viavel',
         dict(color='white', edgecolor='#2f6fdb', hatch='///')),
    ]
    topo = np.nanmax([base[f'{p}_q3_s'] / guloso for _, p, _ in series])
    for j, (rotulo, prefixo, estilo) in enumerate(series):
        mediana = (base[f'{prefixo}_mediana_s'] / guloso).to_numpy()
        q1 = (base[f'{prefixo}_q1_s'] / guloso).to_numpy()
        q3 = (base[f'{prefixo}_q3_s'] / guloso).to_numpy()
        xs = x + (j - 0.5) * largura
        ok = ~np.isnan(mediana)
        ax.bar(xs[ok], mediana[ok], largura, label=rotulo, linewidth=1.2, **estilo)
        ax.errorbar(xs[ok], mediana[ok], yerr=np.clip([mediana[ok] - q1[ok], q3[ok] - mediana[ok]], 0, None),
                    fmt='none', ecolor='#333333', capsize=3, linewidth=1)
        for xi, m, sup in zip(xs, mediana, q3):
            if np.isnan(m):
                ax.text(xi, topo * 0.02, 'sem\nexecução\nviável', ha='center', va='bottom',
                        fontsize=7, color='#555555')
            else:
                ax.text(xi, (sup if not np.isnan(sup) else m) + topo * 0.015, f'{_fmt_br(m)}×',
                        ha='center', va='bottom', fontsize=8)
    ax.set_xlim(-0.6, len(base) - 0.4)
    ax.set_ylim(0, topo * 1.15)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: _fmt_br(v)))
    ax.set(xticks=x, xticklabels=base['turmas'].astype(int), title=titulo,
           xlabel='Número de turmas', ylabel='Vezes o tempo do guloso (escala linear)')
    ax.grid(axis='x', visible=False)
    return (f'Guloso = 1× (mediana de {_fmt_br(guloso.min() * 1e3, 3)} a '
            f'{_fmt_br(guloso.max() * 1e3, 3)} ms por chamada). '
            'Barras: mediana; hastes: intervalo interquartil da VNS.')


def desenhar_figura_tempos(resumo, caminho):
    """Mesma figura de tempos que `desenhar_figuras_separadas` grava no notebook."""
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    nota = _painel_tempos(ax, resumo, 'Tempo da VNS em relação ao guloso')
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=2, frameon=False, fontsize=8)
    fig.tight_layout()
    fig.text(0.5, -0.03, nota, ha='center', fontsize=7.5, color='#555555')
    fig.savefig(caminho, dpi=200, bbox_inches='tight')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description='Redesenha as figuras de tempo a partir de resumo_benchmark.csv e resumo_densa.csv.')
    parser.add_argument('--pasta', default='resultados', help='pasta com os CSVs de resumo (padrão: resultados)')
    parser.add_argument('--saida', default=None, help='pasta onde gravar as figuras (padrão: a mesma de --pasta)')
    args = parser.parse_args()
    saida = args.saida or args.pasta
    os.makedirs(saida, exist_ok=True)
    for arquivo_resumo, arquivo_figura in FIGURAS:
        resumo = pd.read_csv(os.path.join(args.pasta, arquivo_resumo))
        caminho = os.path.join(saida, arquivo_figura)
        desenhar_figura_tempos(resumo, caminho)
        print('Gravado:', caminho)


if __name__ == '__main__':
    main()
