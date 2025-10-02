import streamlit as st
import duckdb
import polars as pl

st.set_page_config(page_title="Monitor Campista", layout="centered")
st.title("Monitor Campista")


con = duckdb.connect("data/03_gold/monitor_campista_pharma_ads_1880_1884.duckdb", True)


df_anuncios = con.sql("""
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
# st.write("Anuncios:", df_anuncios)


_ = st.dataframe(
    df_anuncios,
    use_container_width=True,
    column_config={
        "Veiculações": st.column_config.ProgressColumn(format="%d"),
        "Anúncio": st.column_config.ImageColumn(),
    },
)
