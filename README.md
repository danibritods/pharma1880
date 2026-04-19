# Anúncios Farmaceuticos no Monitor Campista entre 1880 e 1884


Projeto de análise e visualização dos dados coletados na monografia de [Dóris Peres](https://www.behance.net/drisperes1): 

[ENTRE TÔNICOS E DEPURATIVOS: A MEMÓRIA GRÁFICA NOS ANÚNCIOS DE FÁRMACOS DO MONITOR CAMPISTA (1880-1884)](https://bd.centro.iff.edu.br/jspui/handle/123456789/5158)

Fundado na cidade de Campos dos Goytacazes (RJ) em 1834 e ativo até 2009, o Monitor Campista é um dos jornais mais antigos e longevos do Brasil. Podemos encontrar em suas páginas todos os grandes acontecimentos ao longo desses três séculos de publicação. Uma janela única para observar o passado quando ele ainda era presente. Podemos, por exemplo, nos emocionar junto com o [povo na rua, bandas de música e estandartes comemorando a Lei Áurea](https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=030740&pagfis=16274).

Também podemos inferir como os eventos históricos foram apresentados e recebidos pela população local, com todas as nuances e camadas que um veículo jornalístico de determinada tendência, em uma determinada época, escrevendo para determinados leitores, pode oferecer.

Suas páginas testemunharam desde a [Declaração da Maioridade em 1840](https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=030740&pagfis=1813), a [chegada da iluminação elétrica na cidade em 1883](https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=030740&pagfis=9035), os ciclos econômicos do açúcar, do café e até o boom das commodities e a [crise do subprime em 2007](https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=030740&pagfis=104564) sobrevivendo às sucessivas rupturas institucionais e processos de redemocratização do Brasil.

Nesse sentido, a monografia escolheu focar em um recorte específico desse vasto acervo: os anúncios de fármacos veiculados entre 1880 e 1884. O início da década de 1880, por ser esse período de grandes transformações que culminaram na abolição da escravatura e na proclamação da República. Anúncios porque são a síntese visual de intenções, relações de comércio e discurso. Fármacos, em particular por capturarem aspectos de saúde e doença, desejos e medos, temas que atravessam todas as sociedades e épocas, mas que se manifestam de formas particulares em cada contexto histórico e social. 

Nesse sentido, foi construída uma [ficha de registro](https://docs.google.com/spreadsheets/d/1Be14RT5XPDtsarD1-NpYpkqV5BgyXIQQFt36iCaCsY4/edit?usp=sharing) para capturar cada veiculação de [cada anúncio](https://drive.google.com/drive/folders/1HyZi_paov0iWure1DvHzdd5A1TtI0gqu) de cada edição analisada. Finalizado o registro, cada anúncio **distinto** foi analisado em uma [ficha de análise](https://www.notion.so/262d075ca712800887f6fe4774477031?v=262d075ca71280cd90c6000c052909ba) com 35 propriedades como "Doenças mencionadas","Substâncias mencionadas","Palavras-chave de efeito","Discursos de autoridade", "Variação tipográfica", "Elementos de composição", etc. 

Finalmente, todos esses dados foram processados conforme a pipeline de dados implementada nesse projeto. Utilizei o [Jupyter Lab](https://jupyter.org/install) para exploração e desenvolvimento inicial, o [Polars](https://pola.rs/) para tratamento de dados, o [DuckDB](https://duckdb.org/) para armazenamento e consulta, e o [Streamlit](https://streamlit.io/) para visualização final.

Você pode acessar a visualização final [aqui](https://pharma1880.streamlit.app/), explorar os dados diretamente no [Notion (ficha de análise)](https://www.notion.so/262d075ca712800887f6fe4774477031?v=262d075ca71280cd90c6000c052909ba) ou [Google Sheets (ficha de registro)](https://docs.google.com/spreadsheets/d/1Be14RT5XPDtsarD1-NpYpkqV5BgyXIQQFt36iCaCsY4/edit?usp=sharing), baixar o banco de dados final [aqui](https://github.com/danibritods/pharma1880/raw/refs/heads/main/data/03_gold/monitor_campista_pharma_ads_1880_1884.db), ou executar o projeto localmente seguindo as instruções abaixo.

## Organização do Projeto
```
pharma1880/
├── .gitignore 
├── README.md
├── pyproject.toml
├── LICENSE
│
├── data/
│   ├── 01_bronze/
│   │   ├── notion_ficha_analise.csv
│   │   └── sheets_ficha_registro_veiculacoes.csv
│   ├── 02_silver/
│   └── 03_gold/
|       ├── monitor_campista_pharma_ads_1880_1884.duckdb 
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

O único pré-requisito desse é o [uv](https://docs.astral.sh/uv/getting-started/installation/), ele resolve todo o resto. 

Utilize o jupyter lab para explorar os dados, criar visuailzações, combinar tabelas, etc:
```bash
uv run jupyter lab
```

Utilize o streamlit para visualizar o dashboard com o resumo das principais visualizações construídas:
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
