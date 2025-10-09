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


def get_df_anuncios_by_property(property):
    return con.sql(f"""
    select
        {property},
        count(distinct Identificador) as Anúncios
    from
        anuncios
    left join
        {property} using(Identificador)
    where
        {property} is not null
    group by
        {property}
    order by
        Anúncios desc
    """).pl()


def get_df_veiculacoes_by_property(property):
    return con.sql(f"""
    select
        {property},
        count(distinct ano_edicao ||Identificador) as Veiculações
    from
        veiculacoes
    left join
        {property} using(Identificador)
    where
        {property} is not null
    group by
        {property}
    order by
        Veiculações desc
    """).pl()


def df_to_histogram(df, x_col, y_col, color_col=None, title=None):
    df = df.to_pandas()
    df["percent"] = df[y_col] / df[y_col].sum()

    if color_col:
        color = alt.Color(shorthand=color_col).scale(range=color_scale)
    else:
        color = alt.Color(value=color_scale[0])

    bars = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(shorthand=f"{x_col}:N", axis=alt.Axis(labelAngle=0)),
            y=alt.Y(shorthand=f"{y_col}"),
            color=color,
        )
    ).properties(title=title if title else f"{y_col} por {x_col.lower()}")

    text = (
        alt.Chart(data=df)
        .mark_text(dy=-8)
        .encode(
            x=f"{x_col}:N",
            y=f"{y_col}:Q",
            text=alt.Text(shorthand="percent:Q", format=".0%"),
        )
    )

    return bars + text


def df_to_histogram_count_by_x(df, x_col, x_title, y_title):
    base = (
        alt.Chart(df)
        .transform_aggregate(count="count()", groupby=[x_col])
        .transform_joinaggregate(total="sum(count)")
        .transform_calculate(percent="round(datum.count / datum.total * 100, 1) + '%'")
    ).properties(title=f"{y_title} por {x_title.lower()}")

    bars = base.mark_bar().encode(
        x=alt.X(f"{x_col}:N", title=x_title, sort="x", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("count:Q", title=y_title),
        color=alt.Color(value=color_scale[0]),
    )

    text = base.mark_text(dy=-6, fontSize=11).encode(
        x=alt.X(f"{x_col}:N", sort="x"), y="count:Q", text="percent:N"
    )

    return bars + text


def property_to_histogram_by_anuncios(
    property: str,
    title: str | None = None,
    show_percentage: bool | None = True,
    invert_axis: bool | None = None,
    top_k=None,
    is_sum=True,
):
    total_anuncios = con.sql(
        """select count(distinct Identificador) from anuncios"""
    ).pl()[0, 0]

    if show_percentage is None:
        show_percentage = True

    x = alt.X(property, title="", sort="-x" if invert_axis else "-y")
    y = alt.Y("Anúncios", title="Anúncios")

    dx, dy = 0, -10

    if invert_axis:
        x, y = y, x
        dx, dy = 15, dx

    df_property = get_df_anuncios_by_property(property)

    # total_anuncios = df_property.select(pl.col("Anúncios").sum()).to_numpy()[0][0]
    df_property = df_property.with_columns(
        (pl.col("Anúncios") / total_anuncios * 100).alias("percent_full")
    )
    if top_k:
        df_property = df_property.top_k(k=top_k, by="Anúncios")

    df_property = df_property.with_columns(
        (pl.col("percent_full").round(2).cast(pl.Utf8) + "%").alias("percent_full_str"),
        (pl.col("percent_full").round(0).cast(pl.Int32).cast(pl.Utf8) + "%").alias(
            "percent_str"
        ),
    )

    chart = (
        alt.Chart(df_property.to_pandas())
        .mark_bar()
        .encode(
            x=x,
            y=y,
            color=alt.Color(value=color_scale[1]),
            tooltip=[
                alt.Tooltip(property, title=property),
                alt.Tooltip("Anúncios", title="Anúncios"),
                alt.Tooltip("percent_full_str", title="Percentual"),
            ],
        )
        .properties(title=title if title else property)
    )

    text = (
        alt.Chart(df_property)
        .mark_text(dx=dx, dy=dy, color="black", fontSize=12)
        .encode(x=x, y=y, text=alt.Text("percent_str"))
    )
    chart = st.altair_chart(chart + text) if show_percentage else st.altair_chart(chart)
    return chart


def property_to_histogram_by_veiculacoes(
    property: str,
    title: str | None = None,
    show_percentage: bool | None = True,
    invert_axis: bool | None = None,
    top_k=None,
    is_sum=True,
):
    total_anuncios = con.sql("""select count(*) from veiculacoes""").pl()[0, 0]

    if show_percentage is None:
        show_percentage = True

    x = alt.X(property, title="", sort="-x" if invert_axis else "-y")
    y = alt.Y("Veiculações", title="Veiculações")

    dx, dy = 0, -10

    if invert_axis:
        x, y = y, x
        dx, dy = 15, dx

    df_property = get_df_veiculacoes_by_property(property)

    # total_anuncios = df_property.select(pl.col("Anúncios").sum()).to_numpy()[0][0]
    df_property = df_property.with_columns(
        (pl.col("Veiculações") / total_anuncios * 100).alias("percent_full")
    )

    df_property = df_property.with_columns(
        (pl.col("percent_full").round(2).cast(pl.Utf8) + "%").alias("percent_full_str"),
        (pl.col("percent_full").round(0).cast(pl.Int32).cast(pl.Utf8) + "%").alias(
            "percent_str"
        ),
    )
    if top_k:
        df_property = df_property.top_k(k=top_k, by="Veiculações")

    chart = (
        alt.Chart(df_property.to_pandas())
        .mark_bar()
        .encode(
            x=x,
            y=y,
            color=alt.Color(value=color_scale[1]),
            tooltip=[
                alt.Tooltip(property, title=property),
                alt.Tooltip("Veiculações", title="Veiculações"),
                alt.Tooltip("percent_full_str", title="Percentual"),
            ],
        )
        .properties(title=title if title else property)
    )

    text = (
        alt.Chart(df_property)
        .mark_text(dx=dx, dy=dy, color="black", fontSize=12)
        .encode(x=x, y=y, text=alt.Text("percent_str"))
    )
    chart = st.altair_chart(chart + text) if show_percentage else st.altair_chart(chart)
    return chart


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


def st_dataframe_from_property(property: str, property_title=None, height=260):
    property_title: str = property_title if property_title else property
    df = (
        con.sql(f"""
    select
        {property} as '{property_title}',
        count(distinct Identificador) as Anúncios,
        count(distinct ano_edicao ||Identificador) as Veiculações,
        count(distinct Identificador) * count(distinct ano_edicao ||Identificador) as Prevalência

    from
        {property}
    left join
        veiculacoes using(Identificador)
    left join
        anuncios using(Identificador)
    group by
        {property}
    order by
        Prevalência desc
    """)
        .pl()
        .with_columns(
            (pl.col("Prevalência") * 100 / pl.col("Prevalência").max()).alias(
                "Prevalência"
            )
        )
    )
    st_df = st.dataframe(
        df,
        hide_index=True,
        height=height,
        column_config={
            "Anúncios": st.column_config.ProgressColumn(
                format="%d", max_value=df["Anúncios"].max()
            ),
            "Veiculações": st.column_config.ProgressColumn(
                format="%d", max_value=df["Veiculações"].max()
            ),
            "Prevalência": st.column_config.ProgressColumn(
                format="%.0f %%",
                max_value=df["Prevalência"].max(),
                help="Produto entre Anúncios e Veiculações",
            ),
        },
    )

    return st_df


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
        count(distinct ano_edicao || Identificador) as Veiculações,
        group_concat(distinct Orientação) as 'Orientações',
        group_concat(distinct doenca_mencionada) as Moléstias,
        group_concat(Orientação) as 'Orientações Detalhadas',
        Identificador,
    from
        veiculacoes
    left join
        anuncios using(Identificador)
    left join
        doenca_mencionada using(Identificador)
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
        count(distinct
            case when doenca_mencionada = 'Ausente' then null
            else doenca_mencionada
            end
        ) as molestias
    from
        anuncios
    left join
        doenca_mencionada using(Identificador)
    group by
        Identificador
""").pl()

df_ailments_per_ad = con.sql("""
    select
        doenca_mencionada as Moléstia,
        count(distinct Identificador) as Anúncios,
        count(distinct ano_edicao) as Veiculações,
        count(distinct Identificador) * count(distinct ano_edicao) as Prevalência
    from
        doenca_mencionada
    left join
        veiculacoes using(Identificador)
    group by
        doenca_mencionada
    order by
        Anúncios desc
""").pl()


tab_main, tab_dicourse, tab_graphics, tab_extras, tab_links = st.tabs(
    ["Geral", "Discurso", "Gráfico", "Extras", "Links"]
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
        .mark_circle(size=120)
        .encode(
            x=alt.X("ano_edicao").title("Edição"),
            y=alt.Y("anuncios").title("Contagem Anúncios"),
            color=alt.Color("ano:N").scale(range=color_scale),
        )
        .properties(title="Veiculação por Edição")
    )
    st.altair_chart(ads_per_edition, use_container_width=True)

    df = con.sql("""
            with quantidade_paginas as (
                select
                    max(Página) as total_paginas
                from
                    veiculacoes
                group by
                    ano_edicao
            )
            select
                total_paginas as 'Total de Páginas',
                count(*) as Edições
            from
                quantidade_paginas
            group by
                total_paginas
        """).pl()
    st.altair_chart(df_to_histogram(df, "Total de Páginas", "Edições"))

    ads_per_page_year = alt.Chart(df_ad_edition_page).mark_bar().transform_aggregate(
        count="count()", groupby=["Ano", "Página"]
    ).encode(
        x=alt.X("Página:N").axis(labelAngle=0),
        y=alt.Y("sum(count):Q", title="Veiculações"),
        color=alt.Color("Ano:N").scale(range=color_scale),
    ).properties(title="Veiculações por página") + alt.Chart(
        df_ad_edition_page
    ).transform_aggregate(count="count()", groupby=["Ano", "Página"]).mark_text(
        align="center",
        baseline="middle",
        dy=-10,  # adjust vertical position of the text
    ).encode(
        x=alt.X("Página:N"), y=alt.Y("sum(count):Q"), text=alt.Text("sum(count):Q")
    )
    _ = st.altair_chart(ads_per_page_year, use_container_width=True)

with tab_dicourse:
    _ = st.altair_chart(
        df_to_histogram_count_by_x(
            df_ailments_count_per_ad, "molestias", "Contagem de moléstias", "Anúncios"
        )
    )

    _ = st_dataframe_from_property("doenca_mencionada", "Moléstia mencionada")

    ailments_per_ad = (
        alt.Chart(df_ailments_per_ad)
        .mark_circle(size=200)
        .encode(
            x=alt.X("Anúncios"),
            y=alt.Y("Veiculações"),
            text="Moléstia",
            tooltip=["Moléstia", "Anúncios", "Veiculações"],
            color=alt.Color(
                "Moléstia", scale=alt.Scale(range=color_scale), legend=None
            ),
        )
    ).properties(title="Moléstias por veiculações e anúncios")
    _ = st.altair_chart(ailments_per_ad)

    df_top_ailments = df_ailments_per_ad.top_k(100, by="Prevalência")
    base = alt.Chart(df_top_ailments).encode(
        x=alt.X("Moléstia:N", sort=alt.SortField(field="Anúncios", order="descending"))
    )
    bar1 = base.mark_bar(color=color_scale[1]).encode(
        y=alt.Y("Anúncios:Q").axis(titleColor=color_scale[1], orient="left"),
        tooltip=["Moléstia", "Anúncios", "Veiculações"],
    )
    bar2 = base.mark_bar(color=color_scale[3]).encode(
        y=alt.Y("Veiculações:Q").axis(titleColor=color_scale[3], orient="right"),
        tooltip=["Moléstia", "Anúncios", "Veiculações"],
    )
    final_chart = (
        alt.layer(bar2, bar1).resolve_scale(y="independent").configure_mark(opacity=0.6)
    ).properties(title="Moéstias por veiculações e anúncios")

    _ = st.altair_chart(final_chart)

    _ = property_to_histogram_by_anuncios(
        "primeiras_palavras_do_anuncio",
        "Primeiras palavras do anúncio",
        True,
        False,
        top_k=10,
    )

    _ = st_dataframe_from_property(
        "primeiras_palavras_do_anuncio", "Primeiras palavras", height=195
    )

    df = con.sql("""
        with autorizacoes as (
        select
            Identificador,
            case
                when autorizacoes = 'Ausente' then 'Ausente'
                when autorizacoes = 'Governo Imperial' then 'Governo Imperial'
                when autorizacoes = 'Pharmacopéa official da França' then 'Pharmacopéa official da França'
                when autorizacoes = 'Academia de Medicina de Paris' then 'Academia de Medicina de Paris'
                else 'Exma. Junta Central de Hygiene'
            end as Autoridade,
            case
                when autorizacoes = 'Ausente' then 'Ausente'
                else 'Presente'
            end as Autorização
        from
            autorizacoes
        )
        select
            Autoridade,
            Autorização,
            count(distinct Identificador) as Anúncios,
        from anuncios
        left join
            autorizacoes using(Identificador)
        group by
            Autorização, Autoridade
    """)
    x_col = "Autorização"
    y_col = "Anúncios"
    color_col = "Autoridade"
    _ = st.altair_chart(
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X(f"{x_col}:N", axis=alt.Axis(labelAngle=0)),
            y=alt.X(f"{y_col}"),
            color=alt.Color(color_col, scale=alt.Scale(range=color_scale[1:])),
        )
        .properties(title="Menção à autorização")
    )

    _ = property_to_histogram_by_anuncios(
        "palavra_chave_efeito", "Palavras chave de efeito", True, False, 10
    )
    _ = st_dataframe_from_property(
        "palavra_chave_efeito", "Palavras-chave de efeito", height=195
    )

    _ = property_to_histogram_by_anuncios(
        "palavras_chave_produto", "Palavras chave de produto", True, False, 10
    )
    _ = st_dataframe_from_property(
        "palavras_chave_produto", "Palavra-chave produto", height=195
    )
    discourse_analysis = [
        ["discursos_de_autoridade", "Discursos de autoridade", "True", "True", 10],
        ["publico_mencionado", "Público mencionado", True, True, None],
        # ["origem", "Origem", True, False],
    ]

    for prop in discourse_analysis:
        column, title, show_percentage, invert_axis, top_k = (prop + [None] * 5)[:5]
        _ = property_to_histogram_by_anuncios(
            column, title, show_percentage, invert_axis, top_k
        )

    _ = property_to_histogram_by_anuncios(
        "mencoes_a_lugares", "Menções a Lugares", True, False, 10
    )
    _ = st_dataframe_from_property("mencoes_a_lugares", "Lugar mencionado", height=250)


with tab_graphics:
    df = con.sql("""
    select
        "Quantidade de variações tipográficas (aprox.)" as 'Quantidade de variações tipográficas',
        count(distinct Identificador) as Anúncios,
    from
        anuncios
    group by
        "Quantidade de variações tipográficas (aprox.)"
    """).pl()
    _ = st.altair_chart(
        df_to_histogram(df, "Quantidade de variações tipográficas", "Anúncios")
    )
    graphical_analysis = [
        ["informacoes_indicativas", "Informações indicativas"],
        ["detalhamento_do_efeito", "Detalhamento do efeito"],
        ["detalhamento_forma_de_uso", "Detalhamento da forma de uso"],
        ["variacao_typeface", "Variação de typeface"],
        ["variacao_tipografica", "Variação tipográfica", True, True],
        ["alinhamento", "Alinhamento"],
        ["diagramacao", "Diagramação", True, True],
        ["hieraquia_da_informacao", "Hierarquia da informação", True, True],
        ["elementos_de_composicao", "Elementos de composição"],
        ["sinal_visual_de_autoridade", "Sinal visual de autoridade"],
    ]
    for prop in graphical_analysis:
        column, title, show_percentage, invert_axis = (prop + [None] * 4)[:4]
        _ = property_to_histogram_by_anuncios(
            column, title, show_percentage, invert_axis
        )

    df = con.sql("""
    with presenca_imagem as (
    select
        case
            when tipificacao_da_imagem_aprox = 'Ausente' then 'Ausente'
            else 'Presente'
        end as 'Presença de imagem',
        Identificador
    from tipificacao_da_imagem_aprox
    )
    select
        "Presença de imagem",
        count(distinct Identificador) as Anúncios
    from
        presenca_imagem
    group by
        "Presença de imagem"
    """).pl()
    _ = st.altair_chart(df_to_histogram(df, "Presença de imagem", "Anúncios"))
    _ = st_dataframe_from_property(
        "tipificacao_da_imagem_aprox", "Tipificação da imagem"
    )


with tab_extras:
    _ = st_dataframe_from_property("tipo_de_produto", "Tipo de produto")
    _ = st_dataframe_from_property("substancias", "Substância")
    _ = st_dataframe_from_property("responsavel_tecnico", "Responsável técnico")

with tab_links:
    st.markdown(
        "[🗃️ Ficha de catálogo](https://docs.google.com/spreadsheets/d/1Be14RT5XPDtsarD1-NpYpkqV5BgyXIQQFt36iCaCsY4/edit?usp=sharing)"
    )
    st.markdown(
        "[🗃️ Ficha de análise](https://www.notion.so/262d075ca712800887f6fe4774477031?v=262d075ca71280cd90c6000c052909ba)"
    )
    st.markdown(
        "[🖼️ Anúncios](https://drive.google.com/drive/folders/1HyZi_paov0iWure1DvHzdd5A1TtI0gqu)"
    )
    st.markdown(
        "[📰 Mudanças do Monitor Campista](https://docs.google.com/spreadsheets/d/133VMhrcGgJwl1AdXv2b-15_sC6qv8KWMBMDfvWqBwiw/edit?usp=sharing)"
    )
    st.markdown(
        "[📰 Jornais de Campos dos Goytacazes](https://docs.google.com/spreadsheets/d/1FcaQgNfmki29YI9Jb6SX3lyNIrBZ-2GsxCZX21ZYHQE/edit?usp=sharing)"
    )
