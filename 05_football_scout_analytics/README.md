# 05 Football Scout Analytics: Metodologia Estatística e Inteligência de Desempenho Esportivo

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Sports Analytics](https://img.shields.io/badge/Domain-Sports%20Analytics-green?style=for-the-badge)](#)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **05_football_scout_analytics** é uma solução em Python desenvolvida com **Pandas** e **NumPy** para inteligência esportiva, análise quantitativa de atletas e suporte a decisões de recrutamento (*scouting*) em clubes profissionais de futebol.

Diferente de abordagens superficiais baseadas apenas em contagem bruta de gols ou desarmes, o motor normaliza o tempo efetivo de jogo em base **Por 90 Minutos (P90)**, avalia a taxa de conversão qualitativa e sintetiza um índice composto de eficiência balanceado denominado **Scout Score (0 a 100)**.

---

## 📐 Metodologia Estatística do Scout Score

Para garantir comparabilidade justa entre atletas com minutagem e calendários distintos, a metodologia estatística é dividida em quatro fases:

### 1. Normalização Temporal Por 90 Minutos (P90)
Métricas brutas sofrem forte viés pelo número de jogos disputados. Cada indicador é convertido pelo fator de jogo completo:

$$\text{Métrica}_{P90} = \frac{\text{Métrica Bruta}}{\text{Minutos Jogados}} \times 90$$

---

### 2. Decomposição em 4 Pilares de Desempenho

| Pilar | Peso | Componentes e Fórmulas | Objetivo Tático |
| :--- | :---: | :--- | :--- |
| **⚔️ Ataque (Ofensivo)** | **35%** | $\text{Produção} = 3.0 \times \text{Gols} + 2.0 \times \text{Assists} + 1.0 \times \text{Chutes no Alvo}$ | Mede capacidade de decisão, finalização e criação direta de gols. |
| **🎯 Passe (Construção)** | **25%** | Média ponderada entre Volume $(\text{Passes Certos}_{P90})$ e Eficiência $(\frac{\text{Passes Certos}}{\text{Passes Tentados}} \times 100)$ | Avalia controle de jogo, retenção de posse e precisão de passes. |
| **🛡️ Defesa (Combate)** | **25%** | $\text{Ações Defensivas}_{P90} = (\text{Desarmes} + \text{Interceptações})_{P90}$ | Mede agressividade sem bola, desarme e leitura posicional de linha. |
| **⚠️ Segurança (Disciplina)** | **15%** | Inverso da taxa de erros capitais: $100 - \text{Scale}(\text{Erros Capitais}_{P90})$ | Penaliza perdas de bola perigosas e falhas defensivas críticas. |

---

### 3. Normalização por Escala Min-Max
Cada pilar é calibrado em escala contínua de 0 a 100 pontos:

$$S_{\text{pilar}} = \left( \frac{X - \min(X)}{\max(X) - \min(X)} \right) \times 100$$

---

### 4. Fórmula Consolidada do Scout Score
O **Scout Score** final de cada atleta é determinado pela combinação linear ponderada:

$$\text{Scout Score} = (0.35 \times S_{\text{ataque}}) + (0.25 \times S_{\text{passe}}) + (0.25 \times S_{\text{defesa}}) + (0.15 \times S_{\text{seguranca}})$$

---

## 📂 Estrutura do Repositório

```text
05_football_scout_analytics/
├── sample_players.csv         # Dataset simulado com estatísticas de 16 atletas de elite
├── scout_metrics.py           # Script principal com a lógica matemática e exibição
├── scout_ranking_completo.csv # Tabela exportada com todas as métricas P90 e pilares
├── requirements.txt           # Dependências do projeto (pandas, numpy)
├── .gitignore                 # Regras de exclusão do Git
└── README.md                  # Documentação com a metodologia estatística
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Clonagem e Instalação
Acesse a pasta do projeto e instale as bibliotecas:
```bash
cd "05_football_scout_analytics"
pip install -r requirements.txt
```

### 3. Execução do Script de Scouting
Execute a rotina analítica diretamente no terminal:
```bash
python scout_metrics.py
```

---

## 📊 Exemplo da Saída no Terminal (Top 5 Ranking)

```text
==========================================================================================
🏆 FOOTBALL SCOUT ANALYTICS - TOP 5 ATLETAS MAIS EFICIENTES (SCOUT SCORE)
==========================================================================================
Rk   | Atleta              | Posição         | Clube          | Part. | Gols | Ass. | Des. | Pass%  | Scout Score
------------------------------------------------------------------------------------------
#1   | Thiago Alcantara    | Meio-Campista   | Athletico-PR   | 29    | 6    | 12   | 81   |  92.1% |     69.66 pts
#2   | Lucas Silveira      | Meio-Campista   | Flamengo       | 28    | 7    | 11   | 74   |  91.6% |     65.90 pts
#3   | Gustavo Gomez       | Zagueiro        | Santos         | 30    | 4    | 1    | 91   |  91.7% |     63.69 pts
#4   | Rodrigo Caetano     | Meio-Campista   | Internacional  | 25    | 5    | 9    | 65   |  90.9% |     63.69 pts
#5   | Vinícius Lima       | Meio-Campista   | Corinthians    | 24    | 8    | 7    | 58   |  89.9% |     62.62 pts
==========================================================================================
⭐ MVP DO SCOUTING: Thiago Alcantara (Athletico-PR - Meio-Campista)
   • Eficiência Global: 69.66/100 | Gols: 6 | Assistências: 12 | Precisão de Passe: 92.1%
==========================================================================================
```

---

## 🔍 Interpretação Tática dos Resultados

1. **Predomínio dos Meio-Campistas Modernos (Box-to-Box):** Atletas como Thiago Alcantara e Lucas Silveira lideram o ranking por entregarem notas altas de forma consistente nos pilares de criação (passes precisos > 91%), combate (mais de 70 desarmes) e chegada à área adversária (gols e assistências combinados).
2. **Impacto Defensivo Puro:** O zagueiro Gustavo Gomez alcança a 3ª posição graças a números expressivos em volume de desarmes (91), alta precisão na saída de bola (91.7%) e baixa incidência de erros capitais.
3. **Exportação para BI:** O arquivo gerado [`scout_ranking_completo.csv`](scout_ranking_completo.csv) contém todas as notas abertas por pilar para alimentar dashboards no Power BI, Tableau ou Streamlit.

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
