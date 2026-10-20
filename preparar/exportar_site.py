"""Exporta os resultados do DuckDB para o JSON da página estática.

Os microdados são um retrato fixo do ano, então o JSON entra no git e a
página não depende de baixar os 550 MB do INEP para ser publicada.
"""

import json
import sys
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parent.parent
PROVAS = {
    "nota_mt": "Matemática", "nota_cn": "Ciências da Natureza", "nota_lc": "Linguagens",
    "nota_ch": "Ciências Humanas", "nota_redacao": "Redação",
}


def linhas(con, sql):
    rel = con.sql(sql)
    return [dict(zip(rel.columns, r)) for r in rel.fetchall()]


def main(ano):
    con = duckdb.connect(str(RAIZ / "dados" / "enem.duckdb"), read_only=True)
    provas = []
    for coluna, nome in PROVAS.items():
        provas += linhas(con, f"""
            with total as (select avg({coluna}) as media, var_pop({coluna}) as variancia, count(*) as n from participantes),
            faixas as (select faixa_renda, count(*) as n, avg({coluna}) as media from participantes group by 1)
            select '{nome}' as prova,
                   round(max(f.media) filter (where f.faixa_renda = 'Q') - max(f.media) filter (where f.faixa_renda = 'A'), 1) as diferenca,
                   round(100 * sum(f.n * power(f.media - t.media, 2)) / (t.n * t.variancia), 1) as pct_variancia_renda
            from faixas f cross join total t group by t.n, t.variancia""")
    dados = {
        "ano": ano,
        "resumo": linhas(con, "select * from resumo")[0],
        "concluintes": con.sql("select count(*) from participantes where tipo_escola is not null").fetchone()[0],
        "variancia": linhas(con, "select * from variancia_explicada"),
        "renda": linhas(con, "select faixa_renda, descricao, participantes, nota_media, p25, mediana, p75 from nota_por_renda order by faixa_renda"),
        "renda_escola": linhas(con, "select faixa_renda, tipo_escola, participantes, nota_media from nota_por_renda_escola order by 1, 2"),
        "uf": linhas(con, "select uf, participantes, nota_media, media_publica, media_privada, diferenca_privada_publica from ranking_uf order by diferenca_privada_publica desc"),
        "provas": sorted(provas, key=lambda p: -p["pct_variancia_renda"]),
    }
    saida = RAIZ / "site" / "data" / "enem.json"
    saida.write_text(json.dumps(dados, ensure_ascii=False, separators=(",", ":")))
    print(f"{saida.name}: {saida.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 2023)
