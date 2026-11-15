# 08 Sales Forecasting Engine: Modelagem Preditiva de Séries Temporais e Visualização com Plotly

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Plotly](https://img.shields.io/badge/Plotly-6.0%2B-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/python/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **08_sales_forecasting_engine** é um pipeline corporativo em Python de **modelagem preditiva de séries temporais financeiras e de faturamento**, desenvolvido com **Pandas**, **NumPy** e **Plotly**.

Projetado para diretores financeiros (CFOs), analistas de FP&A e equipes de planejamento comercial, o motor realiza a suavização de dados através de **médias móveis de curto e médio prazo (3 e 6 meses)**, decompõe a sazonalidade e a tendência de crescimento do negócio, e projeta os próximos 12 meses de receita acompanhados de um **intervalo de confiança estatística de 95%**, exportando um **dashboard interativo em HTML independente**.

---

## 📈 Metodologia de Modelagem e Séries Temporais

A modelagem temporal é decomposta em 4 etapas quantitativas:

```
[Histórico Mensal: 36 Meses de Vendas]
                  │
                  ▼
  [Suavização por Médias Móveis]
  - MM 3 Meses: Filtra ruídos rápidos e identifica inflexão de curto prazo
  - MM 6 Meses: Captura o vetor estrutural e estabilidade de médio prazo
                  │
                  ▼
  [Decomposição Clássica: Tendência + Sazonalidade]
  - Ajuste de Tendência Linear via Mínimos Quadrados Ordinários (OLS)
  - Fatores sazonais empíricos (S_m = Faturamento / Tendência)
                  │
                  ▼
  [Extrapolação Preditiva + Intervalo de Incerteza (95%)]
  - Y_hat = Tendência(t) * Fator_Sazonal(mês)
  - Faixa de Confiança: Y_hat ± 1.96 * Desvio_Padrão_Residual * sqrt(1 + h/N)
                  │
                  ▼
  [Exportação do Gráfico Interativo Plotly (HTML) + Tabela Terminal]
```

---

## 🌟 Recursos do Gráfico Interativo (`sales_forecast_interactive.html`)

O arquivo gerado em HTML é totalmente autossuficiente (não depende de servidores ativos e pode ser enviado por e-mail ou hospedado no GitHub Pages) e traz:

- **Série Histórica Realizada:** Linha contínua azul realçando os 36 meses históricos consolidados.
- **Médias Móveis Configuráveis:** Curvas em tracejado para visualização de tendência (3M em âmbar e 6M em violeta).
- **Projeção Futura (Forecast):** Linha verde esmeralda com marcadores pontuais em diamante demarcando os 12 meses projetados.
- **Faixa de Incerteza (Intervalo de Confiança 95%):** Sombreado translúcido verde delimitando o cenário pessimista (limite inferior) e otimista (limite superior).
- **Controles de Zoom e Range Slider:** Seletor de período rápido (*Últimos 12M*, *Últimos 24M*, *Ver Tudo*) e barra deslizante temporal no rodapé.
- **Hover Card Unificado:** Exibe valores monetários formatados em Real (`R$ 450.656,04`) ao passar o cursor sobre qualquer mês.

---

## 📂 Estrutura do Repositório

```text
08_sales_forecasting_engine/
├── forecast_model.py              # Script principal de modelagem estatística e exportação
├── sales_forecast_interactive.html# Gráfico executivo interativo em HTML (Plotly)
├── sales_timeseries_dataset.csv   # Base consolidada com histórico, médias móveis e projeção
├── requirements.txt               # Dependências do projeto (pandas, numpy, plotly)
├── .gitignore                     # Regras de exclusão do Git
└── README.md                      # Documentação técnica e metodológica
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Clonagem e Instalação
Acesse a pasta do projeto e instale as dependências:
```bash
cd "08_sales_forecasting_engine"
pip install -r requirements.txt
```

### 3. Execução do Modelo
Execute o script diretamente no terminal:
```bash
python forecast_model.py
```

### 4. Visualização do Dashboard
Abra o arquivo [`sales_forecast_interactive.html`](sales_forecast_interactive.html) diretamente com qualquer navegador web (Chrome, Edge, Firefox).

---

## 📊 Exemplo da Saída Estatística no Terminal

```text
==========================================================================================
📊 RELATÓRIO ESTATÍSTICO DE PROJEÇÃO DE VENDAS (SALES FORECAST)
==========================================================================================
• Histórico Analisado             : 36 meses (Base consolidada)
• Faturamento Total Histórico     : R$ 8,974,249.94
• Média Mensal Histórica          : R$ 249,284.72
• Último Faturamento Real         : R$ 409,776.43
------------------------------------------------------------------------------------------
• Horizonte de Previsão           : 12 meses futuros
• Faturamento Total Projetado     : R$ 4,260,087.85
• Média Mensal Projetada          : R$ 355,007.32
• Taxa de Crescimento Projetada   : +21.81% (vs últimos 12 meses)
==========================================================================================

🗓️ TABELA DE PROJEÇÃO MENSAL DETALHADA COM INTERVALO DE CONFIANÇA (95%):
------------------------------------------------------------------------------------------
Mês/Ano    | Previsão Central (R$)  | Limite Inferior (R$)   | Limite Superior (R$)  
------------------------------------------------------------------------------------------
Jan/2027   | R$         290,033.58 | R$         225,056.91 | R$         355,010.25
Feb/2027   | R$         284,875.70 | R$         219,026.82 | R$         350,724.58
Mar/2027   | R$         327,621.31 | R$         260,911.62 | R$         394,331.00
Apr/2027   | R$         332,110.29 | R$         264,550.77 | R$         399,669.82
May/2027   | R$         344,266.05 | R$         275,867.24 | R$         412,664.86
Jun/2027   | R$         334,693.89 | R$         265,465.98 | R$         403,921.80
Jul/2027   | R$         353,899.17 | R$         283,851.96 | R$         423,946.38
Aug/2027   | R$         351,537.47 | R$         280,680.44 | R$         422,394.49
Sep/2027   | R$         347,886.46 | R$         276,228.76 | R$         419,544.16
Oct/2027   | R$         357,341.27 | R$         284,891.75 | R$         429,790.80
Nov/2027   | R$         450,656.04 | R$         377,423.26 | R$         523,888.82
Dec/2027   | R$         485,166.62 | R$         411,158.87 | R$         559,174.38
==========================================================================================
```

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
