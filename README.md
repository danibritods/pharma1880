# Anúncios Farmaceuticos no Monitor Campista entre 1880 e 1884

Projeto de análise e visualização de dados coletados na [monografia](https://drive.google.com/file/d/1AHOyU2x0TVYfhFXA_pLwzK_rOqaVCOMR/view) de [Dóris Peres](https://www.behance.net/drisperes1).


## Organização do Projeto
```
monitor_campista_analytics/
├── .gitignore
├── README.md
├── pyproject.toml
├── LICENSE
├── main.py
│
├── data/
│   ├── 01_bonze/
│   │   ├── notion_ficha_analise.csv
│   │   └── sheets_ficha_registro_veiculacoes.csv
│   ├── 02_silver/
│   └── 03_gold/
│       └── monitor_campista_pharma_ads_1880_1884.db
│
├── notebooks/
│   ├── 01_cleaning.ipynb
│   ├── 02_analysis.ipynb
│   └── 03_visualization.ipynb
│
└── src/
    └── monitor_campista/
        ├── __init__.py
        ├── data_processing.py
        └── dashboard.py
```

## Tutorial

Este projeto usa o Jupyter Lab para exploração e desenvolvimento inicial. Para iniciá-lo, execute o seguinte comando:
```bash
uv run jupyter lab
```

Para a visualização final utilizamos um dashboard construído com Streamlit. Para iniciá-lo, executo o seguinte comando:
```bash
uv run streamlit run src/monitor_campista/dashboard.py
```

## Ferramentas utilizadas

* [uv](https://docs.astral.sh/uv/) -
* [Jupyter Lab](https://jupyter.org/install) -
* [Polars](https://pola.rs/) -
* [DuckDB](https://duckdb.org/) -
* [Streamlit](https://streamlit.io/) -
* [SQLite](https://sqlite.org/index.html) -


## Licença

 [MIT](LICENSE)

## Créditos

Esse documento foi inspirado no [template para um bom README.md](https://gist.github.com/PurpleBooth/109311bb0361f32d87a2)
