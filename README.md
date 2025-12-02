Avaliação de Desempenho do CoinMarketCap
Modelagem com Teoria das Filas (M/M/1 e M/M/c) e Streamlit

Este projeto consiste em um protótipo interativo desenvolvido para a disciplina de Modelagem e Simulação de Sistemas Computacionais, com o objetivo de analisar o desempenho de um sistema inspirado no CoinMarketCap, aplicando Teoria das Filas e explorando dados reais de volume negociado em criptomoedas.

A aplicação foi construída utilizando Python + Streamlit e implementa os modelos de filas M/M/1 e M/M/c, além de gerar métricas e gráficos comparativos a partir de datasets reais.

FUNCIONALIDADES
1. Banner visual com tema Bitcoin
2. Simulações teóricas de filas M/M/1 e M/M/c
3. Upload de Dataset para análise real
4. Visualização gráfica com matplotlib

ESTRUTURA DO PROJETO
/
├── app.py
├── README.md
└── data/

MODELOS IMPLEMENTADOS
- M/M/1 (λ, μ)
- M/M/c (λ, μ, c, Erlang C)

DATASET
historical_daily_volume_reduzido.csv
(date, volume_24h_total)

COMO EXECUTAR
1. pip install streamlit pandas matplotlib
2. streamlit run app.py
3. acessar http://localhost:8501


OBJETIVO ACADÊMICO
Demonstração prática de modelagem, análise de desempenho, visualização gráfica e uso da teoria das filas aplicada a sistemas web.

AUTOR
leandro Queiroz, Irismar Neris
Bacharelado em Ciência da Computação - Modelagem e Simulação de Sistemas Computacionais - UFRPE 2025.2	

