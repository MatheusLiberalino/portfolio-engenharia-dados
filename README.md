# Portfolio de Engenharia de Dados

Este repositorio reune projetos praticos de Engenharia de Dados, com foco em pipelines, modelagem, qualidade, orquestracao e consumo analitico.

## Projetos

| Projeto | Descricao | Stack |
| --- | --- | --- |
| [Pipeline de Vendas: ELT, Data Warehouse, dbt, Airflow e Dashboard](projeto-01-pipeline-vendas/) | Pipeline completo de vendas com geracao de dados, ingestao, staging, Data Warehouse dimensional, testes, dbt, Airflow e dashboard em Streamlit. | Python, SQL, PostgreSQL, SQLite, dbt, Airflow, Streamlit, Docker |

## Projeto em Destaque

### Pipeline de Vendas

O primeiro projeto simula uma operacao de vendas de ponta a ponta:

```text
CSV raw
-> Python ingestion
-> PostgreSQL staging
-> dbt transformations
-> Data Warehouse dimensional
-> Data quality checks
-> Airflow orchestration
-> Streamlit dashboard
```

Ele demonstra:

- construcao de pipeline ELT;
- organizacao em camadas raw, staging e analytics;
- modelagem dimensional com tabela fato e dimensoes;
- testes de qualidade em Python e dbt;
- orquestracao com Airflow;
- dashboard para consumo dos dados.

Acesse o projeto:

[projeto-01-pipeline-vendas](projeto-01-pipeline-vendas/)

## Objetivo do Portfolio

Demonstrar habilidades praticas em Engenharia de Dados por meio de projetos reproduziveis, documentados e organizados para avaliacao tecnica.

## Proximos Projetos Planejados

- Data Lake com PySpark e Parquet.
- Pipeline de streaming com Kafka.
- Monitoramento de qualidade de dados.
- Projeto com dados em nuvem.
