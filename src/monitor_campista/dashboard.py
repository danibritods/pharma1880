import streamlit as st
import duckdb
import polars as pl

# def progress_bar_col(col):


st.set_page_config(page_title="Monitor Campista", layout="centered")
st.title("Monitor Campista")

# # ----- trivial data -----
# df_pl = pl.DataFrame({"greeting": ["Hello", "Hola", "Ciao"], "count": [1, 2, 3]})
# st.write("Polars frame:", df_pl)


con = duckdb.connect("data/03_gold/monitor_campista_pharma_ads_1880_1884.duckdb", True)


df_anuncios = con.sql("""
    select
        Identificador,
        image_url,
        count(*) as Veiculações,
        "Produto ofertado (título completo)"
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


st.dataframe(
    df_anuncios,
    use_container_width=True,
    column_config={
        "Veiculações": st.column_config.ProgressColumn(format="%d"),
        "image_url": st.column_config.ImageColumn(),
    },
)

tables = pl.read_database("SELECT name FROM sqlite_master WHERE type='table';", con)

table_name = st.selectbox("Pick a table:", tables["name"].to_list())
df_pl = pl.read_database(f"SELECT * FROM {table_name}", con)

kpi1, kpi2 = st.columns(2)
with kpi1:
    st.metric("Total rows", f"{df_pl.height:,}")
with kpi2:
    numeric_cols = [c for c, dtype in df_pl.schema.items() if dtype.is_numeric()]
    if numeric_cols:
        st.metric("Sum of first numeric", f"{df_pl[numeric_cols[0]].sum():,.0f}")
