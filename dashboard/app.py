from pathlib import Path

import duckdb
import plotly.express as px
import streamlit as st

BANCO = Path(__file__).resolve().parent.parent / "dados" / "enem.duckdb"

st.set_page_config(page_title="ENEM 2023: renda, escola e nota", layout="wide")


@st.cache_data
def consultar(sql):
    with duckdb.connect(str(BANCO), read_only=True) as con:
        return con.execute(sql).df()


st.title("ENEM 2023: renda familiar, tipo de escola e nota")
st.caption("Microdados do INEP. Participantes presentes nos dois dias, com redação válida.")

resumo = consultar("select * from resumo").iloc[0]
variancia = consultar("select * from variancia_explicada").set_index("fator")["pct_variancia_explicada"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Participantes analisados", f"{int(resumo.participantes):,}".replace(",", "."))
c2.metric("Nota média geral", f"{resumo.nota_media_geral:.1f}")
c3.metric("Variância explicada pela renda", f"{variancia['Renda familiar']:.1f}%")
c4.metric("Renda + escola juntas", f"{variancia['Renda + escola']:.1f}%")

st.subheader("Nota média por faixa de renda e tipo de escola")
renda_escola = consultar("select * from nota_por_renda_escola")
fig = px.line(
    renda_escola,
    x="descricao",
    y="nota_media",
    color="tipo_escola",
    markers=True,
    labels={"descricao": "Renda familiar mensal", "nota_media": "Nota média", "tipo_escola": "Escola"},
)
fig.update_xaxes(tickangle=-45)
st.plotly_chart(fig, width="stretch")

st.subheader("Distribuição da nota por faixa de renda")
renda = consultar("select * from nota_por_renda")
fig = px.bar(
    renda,
    x="descricao",
    y="mediana",
    error_y=renda["p75"] - renda["mediana"],
    error_y_minus=renda["mediana"] - renda["p25"],
    labels={"descricao": "Renda familiar mensal", "mediana": "Mediana (barras: p25 a p75)"},
)
fig.update_xaxes(tickangle=-45)
st.plotly_chart(fig, width="stretch")

st.subheader("Ranking por UF")
uf = consultar("select * from ranking_uf")
col_a, col_b = st.columns(2)
col_a.plotly_chart(
    px.bar(uf.sort_values("nota_media"), x="nota_media", y="uf", orientation="h",
           labels={"nota_media": "Nota média", "uf": "UF"}, height=700),
    width="stretch",
)
col_b.plotly_chart(
    px.bar(uf.sort_values("diferenca_privada_publica"), x="diferenca_privada_publica", y="uf",
           orientation="h", labels={"diferenca_privada_publica": "Privada menos pública (pontos)", "uf": "UF"},
           height=700),
    width="stretch",
)
st.dataframe(uf, hide_index=True, width="stretch")
