# Anúncios Farmaceuticos no Monitor Campista entre 1880 e 1884

Projeto de análise e visualização dos dados coletados na [monografia](https://drive.google.com/file/d/1AHOyU2x0TVYfhFXA_pLwzK_rOqaVCOMR/view) de [Dóris Peres](https://www.behance.net/drisperes1):
- [ficha de registro](https://docs.google.com/spreadsheets/d/1Be14RT5XPDtsarD1-NpYpkqV5BgyXIQQFt36iCaCsY4/edit?usp=sharing) de todas veiculação de cada anúncio do corpus. 
- [ficha de análise](https://www.notion.so/262d075ca712800887f6fe4774477031?v=262d075ca71280cd90c6000c052909ba) com as 35 propriedades definidas para cada anúncio.
- [repositório de imagens](https://drive.google.com/drive/folders/1HyZi_paov0iWure1DvHzdd5A1TtI0gqu) dos anúncios.

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
