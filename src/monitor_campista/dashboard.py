import streamlit as st
import altair as alt
import polars as pl
import tomllib
import duckdb
from pathlib import Path

# path = Path.cwd()
# print(path)
# for item in path.iterdir():
#     print(item.name)

# print("-------")
# with open("./src/monitor_campista/streamlit/config.toml", "rb") as f:
#     config = tomllib.load(f)
#
#
color_scale = [
    "#007F77",  # teal-700  – accent, starts the scale
    "#4385BE",  # blue-600
    "#8B7EC8",  # purple-600
    "#D83232",  # red-700
    "#BC6F00",  # orange-700
    "#6F6E69",  # gray-600  – neutral end-stop
]


con = duckdb.connect("data/03_gold/monitor_campista_pharma_ads_1880_1884.duckdb", True)


total_editions = con.query("""
                        select
                            count(distinct ano_edicao)
                        from
                            veiculacoes
                        """).pl()[0, 0]
total_ads = con.query("""
                        select
                            count(distinct Identificador)
                        from
                            veiculacoes
                        """).pl()[0, 0]
total_ads_single_products = con.query("""
                        select
                            count(distinct Identificador)
                        from
                            anuncios
                        """).pl()[0, 0]

df_ads = con.sql("""
    select
        image_url as 'Anúncio',
        "Produto ofertado (título completo)",
        count(*) as Veiculações,
        Identificador,
    from
        veiculacoes
    left join
        anuncios using(Identificador)
    group by
        Identificador,
        image_url,
        "Produto ofertado (título completo)"
    order by
        Veiculações desc
    """).pl()

df_ads_by_edition = con.sql("""
    select
        Ano as ano,
        ano_edicao,
        count(*) as anuncios,
        min(Página) as pagina_primeiro_anuncio,
        max(Página) as pagina_ultimo_anuncio,
    from veiculacoes
    group by
        ano,
        ano_edicao
    order by
        ano_edicao
    """).pl()

df_ads_by_page = con.sql("""
    select
        "Página",
        count(*) anuncios
    from veiculacoes
    group by
        "Página"
    order by
        "Página"
    """).pl()

df_ad_edition_page = con.query("""
select
    Ano,
    ano_edicao,
    Página
from veiculacoes
""").pl()


title = "Anúncios de Fármacos Monitor Campista (1880-1884)"
st.set_page_config(page_title=title, layout="centered")
st.title(title)

col1, col2, col3 = st.columns(3)
col1.metric("Edições", total_editions)
col2.metric("Anúncios Fármacos", total_ads)
col3.metric("Anúncios Analisados", total_ads_single_products)


ads = st.dataframe(
    df_ads,
    use_container_width=True,
    column_config={
        "Veiculações": st.column_config.ProgressColumn(format="%d"),
        "Anúncio": st.column_config.ImageColumn(),
    },
)


ads_per_edition = (
    alt.Chart(df_ads_by_edition)
    .mark_circle(size=60)
    .encode(
        x=alt.X("ano_edicao").title("Edição"),
        y=alt.Y("anuncios").title("Contagem Anúncios"),
        color=alt.Color("ano:N").scale(range=color_scale),
    )
    .properties(title="Anúncios por Edição")
)
st.altair_chart(ads_per_edition, use_container_width=True)


ads_per_page_year = (
    alt.Chart(df_ad_edition_page)
    .mark_bar()
    .encode(
        x=alt.X("Página:O", title="Página"),
        y=alt.Y("count():Q", stack="zero", title="Veiculações"),
        color="Ano:N",
    )
    .transform_aggregate(count="count()", groupby=["Ano", "Página"])
    .encode(
        x=alt.X("Página:N").axis(labelAngle=0),
        y=alt.Y("sum(count):Q", title="Veiculações"),
        color=alt.Color("Ano:N").scale(range=color_scale),
    )
    .properties(title="Veiculações por página")
)
st.altair_chart(ads_per_page_year, use_container_width=True)
