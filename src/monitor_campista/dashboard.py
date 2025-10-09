import streamlit as st
import altair as alt
import polars as pl
import tomllib
import duckdb
from pathlib import Path

with open(Path("src/monitor_campista/.streamlit/config.toml"), "rb") as f:
    config = tomllib.load(f)

page_title = "Anúncios de Fármacos Monitor Campista (1880-1884)"
title = "Entre tônicos e depurativos: a memória gráfica nos anúncios de fármacos do Monitor Campista <small>(1880-1884)</small>"

st.set_page_config(page_title=page_title, layout="centered", page_icon="📰")

st.markdown(f"<h1 style='font-size: 28px;'>{title}</h1>", unsafe_allow_html=True)

color_scale = config["theme"]["colorScale"]
con = duckdb.connect("data/03_gold/monitor_campista_pharma_ads_1880_1884.duckdb", True)

def custom_metric(label: str, value) -> None:
    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding-bottom:1.4rem;">
            <div style="
                font-size:2.2rem;
                line-height:1.1;">
                {value}
            </div>
            <div style="
                font-size:0.85rem;
                color:#6b7281;
                margin-top:-0.25rem;">
                {label}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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

total_unique_producs = con.query("""
    select
        count(distinct Identificador)
    from
        anuncios
    where
        "Original (primeira aparição)" is null
    """).pl()[0, 0]

total_placements = con.query("""
                        select
                            count(*)
                        from
                            veiculacoes
                        """).pl()[0, 0]

df_substances = con.query("""
    select
        substancias as Substâncias,
        count(distinct Identificador) as Anúncios
    from
        substancias
    left join
        anuncios using(Identificador)
    group by
        substancias
    order by
        Anúncios desc
    """).pl()

df_pharmacists = con.query("""
    select
        responsavel_tecnico as Farmacêutico,
        count(distinct Identificador) as Anúncios
    from
        responsavel_tecnico
    left join
        anuncios using(Identificador)
    group by
        responsavel_tecnico
    order by
        Anúncios desc
                        """).pl()

df_product_types = con.query("""
    select
        tipo_de_produto as 'Tipo de Produto',
        count(distinct Identificador) as Anúncios
    from
        tipo_de_produto
    left join
        anuncios using(Identificador)
    group by
        tipo_de_produto
    order by
        Anúncios desc
                        """).pl()

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

df_disease_count_per_ad = con.query("""
select
    Ano,
    ano_edicao,

from veiculacoes
""").pl()

df_ailments_count_per_ad = con.sql("""
    select
        Identificador as anuncio,
        count(distinct doenca_mencionada) as doencas
    from
        doenca_mencionada
    group by
        Identificador
""").pl()

df_ailments_per_ad = con.sql("""
    select
        doenca_mencionada as Doença,
        count(distinct Identificador) as Anúncios,
        count(distinct ano_edicao) as Veiculações
    from
        doenca_mencionada
    left join
        veiculacoes using(Identificador)
    group by
        doenca_mencionada
    order by
        Anúncios desc
""").pl()


tab_main, tab_dicourse, tab_graphics, tab_extras = st.tabs(
    ["Geral", "Discurso", "Gráfico", "Extras"]
)


with tab_main:
    col1, col2, col3 = st.columns(3)
    with col1:
        custom_metric("Edições", total_editions)
    with col2:
        custom_metric("Veiculações", total_placements)
    with col3:
        custom_metric("Anúncios Fármacos", total_ads)

    with col1:
        custom_metric("Anúncios Analisados", total_ads_single_products)
    with col2:
        custom_metric("Produtos", total_unique_producs)
    with col3:
        custom_metric("Tipos de Produto", df_product_types["Tipo de Produto"].count())

    with col1:
        custom_metric("Moléstias", df_ailments_per_ad["Moléstia"].unique().count())
    with col2:
        custom_metric("Substâncias", df_substances["Substâncias"].count())
    with col3:
        custom_metric("Farmacéuticos", df_pharmacists["Farmacêutico"].count())

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
    .transform_aggregate(count="count()", groupby=["Ano", "Página"])
    .encode(
        x=alt.X("Página:N").axis(labelAngle=0),
        y=alt.Y("sum(count):Q", title="Veiculações"),
        color=alt.Color("Ano:N").scale(range=color_scale),
    )
    .properties(title="Veiculações por página")
)
_ = st.altair_chart(ads_per_page_year, use_container_width=True)

ailments_per_ad_hist = (
    alt.Chart(df_ailments_count_per_ad)
    .mark_bar()
    .encode(
        x=alt.X("doencas:N", title="Contagem doenças mencionadas", sort="x").axis(
            labelAngle=0
        ),
        y=alt.Y("count()", title="Anúncios"),
        color=alt.Color(value=color_scale[0]),
    )
    .properties(title="Doenças Mencionadas por anúncios")
)
_ = st.altair_chart(ailments_per_ad_hist)


_ = st.dataframe(
    df_ailments_per_ad,
    column_config={
        "Anúncios": st.column_config.ProgressColumn(
            format="%d", max_value=df_ailments_per_ad["Anúncios"].max()
        ),
        "Veiculações": st.column_config.ProgressColumn(
            format="%d", max_value=df_ailments_per_ad["Veiculações"].max()
        ),
    },
)

ailments_per_ad = (
    alt.Chart(df_ailments_per_ad)
    .mark_circle(size=200)
    .encode(
        x=alt.X("Anúncios"),
        y=alt.Y("Veiculações"),
        text="Doença",
        tooltip=["Doença", "Anúncios", "Veiculações"],
        color=alt.Color("Doença", scale=alt.Scale(range=color_scale)),
    )
)
_ = st.altair_chart(ailments_per_ad)

df_top_ailments = df_ailments_per_ad.top_k(90, by="Veiculações")
base = alt.Chart(df_top_ailments).encode(
    x=alt.X("Doença:N", sort=alt.SortField(field="Veiculações", order="descending"))
)
bar1 = base.mark_bar(color=color_scale[1]).encode(
    y=alt.Y("Anúncios:Q").axis(titleColor=color_scale[1])
)
bar2 = base.mark_bar(color=color_scale[3]).encode(
    y=alt.Y("Veiculações:Q").axis(titleColor=color_scale[3])
)
final_chart = (
    alt.layer(bar2, bar1).resolve_scale(y="independent").configure_mark(opacity=0.6)
)

_ = st.altair_chart(final_chart)
