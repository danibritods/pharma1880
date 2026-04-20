"""
Pipeline de dados: Bronze → Silver → Gold.

Extrai os CSVs brutos (Bronze), aplica limpeza e padronização em memória (Silver),
e grava as 27 tabelas normalizadas em DuckDB e SQLite (Gold).

Uso:
    uv run update-data
"""

import polars as pl
import duckdb
from pathlib import Path


# ---------------------------------------------------------------------------
# Constantes: schema das fichas
# ---------------------------------------------------------------------------

SCHEMA_ANALYSIS = [
    # a. Identificação do objeto
    "Identificador",
    "ID",
    "Link",
    "Produto ofertado (título completo)",
    "Primeiras palavras do anúncio",
    "Doença mencionada",
    "Tipo de produto",
    "Substâncias",
    "Extras",
    # b. Identificação do contexto
    "Informações indicativas",
    "Menções a lugares",
    "Origem",
    "Preço",
    "Responsável técnico",
    "Comercialização",
    "Depósito",
    "Produção",
    # c. Identificação do discurso
    "Palavra-chave efeito",
    "Palavras-chave produto",
    "Discursos de autoridade",
    "Público mencionado",
    "Detalhamento do efeito",
    "Detalhamento forma de uso",
    "Autorizações",
    "Observações",
    # d. Identificação gráfica
    "Sinal visual de autoridade",
    "Quantidade de variações tipográficas (aprox.)",
    "Variação typeface",
    "Variação tipográfica",
    "Alinhamento",
    "Diagramação",
    "Hieraquia da informação",
    "Tipificação da imagem (aprox.)",
    "Elementos de composição",
    #
    "Original (primeira aparição)",
    "Derivados",
    "Status",
    "Dúvidas",
]

MULTI_SELECT_COLUMNS = [
    "Primeiras palavras do anúncio",
    "Doença mencionada",
    "Tipo de produto",
    "Substâncias",
    "Extras",
    # b. Identificação do contexto
    "Informações indicativas",
    "Menções a lugares",
    "Origem",
    "Responsável técnico",
    # c. Identificação do discurso
    "Palavra-chave efeito",
    "Palavras-chave produto",
    "Discursos de autoridade",
    "Público mencionado",
    "Detalhamento do efeito",
    "Detalhamento forma de uso",
    "Autorizações",
    # d. Identificação gráfica
    "Sinal visual de autoridade",
    "Variação typeface",
    "Variação tipográfica",
    "Alinhamento",
    "Diagramação",
    "Hieraquia da informação",
    "Tipificação da imagem (aprox.)",
    "Elementos de composição",
]

SCHEMA_INSERTIONS = [
    "Anúncio",
    "Ano",
    "Edição",
    "Página",
    "Coluna(s) ocupadas",
    "Número de Colunas",
    "Orientação",
]

SINGLE_VALUE_COLUMNS = [
    col for col in SCHEMA_ANALYSIS if col not in MULTI_SELECT_COLUMNS
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clean_text(text: str) -> str:
    """Remove acentos e caracteres especiais para gerar chaves de banco seguras."""
    translation_table = str.maketrans(" -çõãóéíâáú", "__coaoeiaau", "().")
    return text.lower().translate(translation_table)


# ---------------------------------------------------------------------------
# Silver: leitura e limpeza em memória
# ---------------------------------------------------------------------------

def load_analysis(bronze_dir: Path) -> pl.DataFrame:
    """Carrega e limpa a ficha de análise (Notion CSV)."""
    raw = pl.read_csv(bronze_dir / "notion_ficha_analise.csv")
    return (
        raw
        .select([
            pl.col(c).str.split(", ").alias(c) if c in MULTI_SELECT_COLUMNS else pl.col(c)
            for c in SCHEMA_ANALYSIS
        ])
        .filter(pl.col("Status").is_in(["Finalizado", "Revisado"]))
    )


def load_insertions(bronze_dir: Path) -> pl.DataFrame:
    """Carrega e limpa a ficha de registro de veiculações (Google Sheets CSV)."""
    raw = pl.read_csv(bronze_dir / "sheets_ficha_registro_veiculacoes.csv")
    return (
        raw
        .select(SCHEMA_INSERTIONS)
        .filter(pl.col("Anúncio").is_not_null())
        .rename({"Anúncio": "Identificador"})
        .with_columns(
            pl.format(
                "{}_{}",
                pl.col("Ano"),
                pl.col("Edição").cast(pl.Utf8).str.zfill(3),
            ).alias("ano_edicao")
        )
    )


# ---------------------------------------------------------------------------
# Gold: modelagem dimensional
# ---------------------------------------------------------------------------

def build_tables(
    ad_analysis: pl.DataFrame,
    ad_insertions: pl.DataFrame,
) -> dict[str, pl.DataFrame]:
    """
    Constrói o dicionário com todas as tabelas do banco:
      - 24 tabelas dimensionais (uma por coluna multi-select)
      - tabela fato `anuncios` (colunas de valor único)
      - tabela fato `veiculacoes`
      - tabela auxiliar `original`
    """
    # 24 tabelas dimensionais: explode cada coluna multi-select
    tables = {
        clean_text(col): (
            ad_analysis
            .select(["Identificador", col])
            .explode(col)
            .unique()
            .drop_nulls()
            .rename({col: clean_text(col)})
        )
        for col in MULTI_SELECT_COLUMNS
    }

    # Tabela fato: anúncios (colunas single-value + image_url derivada)
    tables["anuncios"] = ad_analysis.select(SINGLE_VALUE_COLUMNS).with_columns(
        (
            pl.lit("https://drive.google.com/thumbnail?id=")
            + pl.col("Link").str.extract(r"([-\w]{25,})")
            + pl.lit("&sz=w1920")
        ).alias("image_url")
    )

    # Tabela auxiliar: relação original ↔ derivado
    tables["original"] = (
        ad_analysis
        .select(["Identificador", "Original (primeira aparição)"])
        .unique()
        .drop_nulls()
        .with_columns(
            pl.col("Original (primeira aparição)").str.split(" ").list.get(0)
        )
    )

    # Tabela fato: veiculações
    tables["veiculacoes"] = ad_insertions

    return tables


# ---------------------------------------------------------------------------
# Gold: escrita nos bancos
# ---------------------------------------------------------------------------

DB_NAME = "monitor_campista_pharma_ads_1880_1884"


def write_sqlite(tables: dict[str, pl.DataFrame], gold_dir: Path) -> Path:
    """Grava todas as tabelas no banco SQLite (recria do zero)."""
    db_path = gold_dir / f"{DB_NAME}.db"
    db_path.unlink(missing_ok=True)
    connection_string = f"sqlite:///{db_path.resolve()}"

    for table_name, df in tables.items():
        df.write_database(
            table_name=table_name,
            connection=connection_string,
            if_table_exists="replace",
            engine="adbc",
        )
    return db_path


def write_duckdb(tables: dict[str, pl.DataFrame], gold_dir: Path) -> Path:
    """Grava todas as tabelas no banco DuckDB (recria do zero)."""
    db_path = gold_dir / f"{DB_NAME}.duckdb"
    db_path.unlink(missing_ok=True)
    con = duckdb.connect(str(db_path))

    for table_name, df in tables.items():
        con.register("tmp_arrow", df.to_arrow())
        con.execute(
            f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM tmp_arrow"
        )

    con.close()
    return db_path


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def main():
    """Entry point: executa o pipeline Bronze → Silver → Gold."""
    project_root = Path(__file__).resolve().parents[2]
    bronze_dir = project_root / "data" / "01_bronze"
    gold_dir = project_root / "data" / "03_gold"

    gold_dir.mkdir(parents=True, exist_ok=True)

    print("Pipeline de dados — Monitor Campista (1880–1884)")
    print("=" * 52)

    # Silver
    print("\nSilver: carregando e limpando dados em memória...")
    ad_analysis = load_analysis(bronze_dir)
    print(f"   Ficha de análise: {ad_analysis.height} anúncios distintos")

    ad_insertions = load_insertions(bronze_dir)
    print(f"   Ficha de registro: {ad_insertions.height} veiculações")

    # Gold
    print("\nGold: construindo modelagem dimensional...")
    tables = build_tables(ad_analysis, ad_insertions)
    print(f"   {len(tables)} tabelas geradas")

    print("\nGravando bancos...")
    sqlite_path = write_sqlite(tables, gold_dir)
    print(f"   SQLite:  {sqlite_path.relative_to(project_root)}")

    duckdb_path = write_duckdb(tables, gold_dir)
    print(f"   DuckDB:  {duckdb_path.relative_to(project_root)}")

    print("\nPipeline concluído com sucesso!")


if __name__ == "__main__":
    main()
