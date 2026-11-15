# 03 NLP Sentiment Pulse: Processamento em Lote de Feedbacks e Análise de Sentimento

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NLP](https://img.shields.io/badge/NLP-Sentiment%20Analysis-orange?style=for-the-badge)](https://en.wikipedia.org/wiki/Sentiment_analysis)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **03_nlp_sentiment_pulse** é um motor autônomo de Processamento de Linguagem Natural (**NLP - Natural Language Processing**) projetado para processar em lote avaliações de clientes (*customer reviews*), classificar a polaridade de sentimentos (**Positivo, Neutro ou Negativo**) e diagnosticar automaticamente os principais **pontos de dor operacionais (pain points)** enfrentados pelos consumidores.

O projeto foi construído para ser **100% autossuficiente e offline**, sem exigir downloads pesados de modelos externos ou chamadas pagas de APIs, tornando-o ideal para pipelines de auditoria de qualidade, esteiras de BI e monitoramento contínuo de Customer Experience (**CX**).

---

## 🧠 Arquitetura do Motor de NLP

O pipeline emprega uma abordagem léxico-contextual calibrada para a língua portuguesa, estruturada nas seguintes etapas:

```
[Lista de Reviews Não-Estruturados]
                 │
                 ▼
  [Normalização & Limpeza Textual]
  - Remoção de pontuações e caracteres especiais
  - Tratamento de exceções morfológicas (ex: 'sem fio')
                 │
                 ▼
  [Análise Contextual & Polaridade]
  - Avaliação de termos do léxico positivo e negativo
  - Janela deslizante de negação (ex: 'não gostei', 'não recomendo')
  - Multiplicadores de intensidade (ex: 'muito', 'extremamente')
                 │
                 ▼
  [Classificação & Diagnóstico de Dores]
  - Determinação da classe: Positivo / Neutro / Negativo
  - Classificação temática de ofensores (Logística, Qualidade, Suporte)
                 │
                 ▼
  [Consolidação Executiva & Exportação]
  - Cálculo de Satisfação (CSAT), Neutros e Insatisfação
  - Net Sentiment Score (NSS = % Positivos - % Negativos)
  - Exportação automática para CSV e Markdown
```

---

## 🏷️ Categorias de Pontos de Dor Monitoradas

O motor analisa padrões linguísticos recorrentes em avaliações com atrito para mapear quatro grandes ofensores:

| Macro-Área de Dor | Gatilhos Linguísticos Monitorados | Impacto no Negócio |
| :--- | :--- | :--- |
| **Defeito & Baixa Qualidade** | `defeito`, `quebrado`, `danificado`, `estragado`, `frágil`, `trava`, `chiado`, `arranhado` | Reclamações de garantia, trocas e estornos. |
| **Logística & Atrasos de Entrega** | `atraso`, `demorou`, `prazo`, `entrega`, `transportadora`, `não chegou` | Cancelamento de compras e aumento de tickets de SAC. |
| **Mau Atendimento & Suporte Técnico** | `suporte`, `atendente`, `descaso`, `sem resposta`, `sac`, `grosseiro` | Degradação direta de reputação de marca e NPS. |
| **Cobrança, Preço ou Reembolso** | `reembolso`, `estorno`, `caro`, `cobrança`, `devolução` | Atrito financeiro e chargebacks. |

---

## 📂 Estrutura do Repositório

```text
03_nlp_sentiment_pulse/
├── sentiment_analyzer.py         # Script principal de processamento em lote e relatório
├── sentiment_analysis_results.csv# Base tabular exportada com scores e classificações
├── sentiment_summary.md          # Resumo executivo exportado em Markdown
├── requirements.txt              # Dependências do projeto (Pandas)
├── .gitignore                    # Regras de exclusão do Git
└── README.md                     # Documentação do projeto
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Clonagem e Instalação
```bash
git clone https://github.com/seu-usuario/03_nlp_sentiment_pulse.git
cd 03_nlp_sentiment_pulse

pip install -r requirements.txt
```
*Ou instalação direta do Pandas:*
```bash
pip install pandas
```

### 3. Execução do Analisador
```bash
python sentiment_analyzer.py
```

---

## 📊 Exemplo da Saída Executiva no Terminal

Ao executar o script, o console exibe a amostra categorizada e o relatório executivo estruturado:

```text
======================================================================
📊 RELATÓRIO EXECUTIVO - NLP SENTIMENT PULSE
======================================================================
• Total de Avaliações Processadas : 20
• Taxa de Satisfação (Positivos)  : 50.0% (10 avaliações)
• Avaliações Neutras / Indiferentes: 15.0% (3 avaliações)
• Taxa de Insatisfação (Negativos): 35.0% (7 avaliações)
• Net Sentiment Score (NSS)       : +15.0 pts (Escala de -100 a +100)
----------------------------------------------------------------------
🔍 DISTRIBUIÇÃO DE SENTIMENTOS POR CATEGORIA DE PRODUTO:
----------------------------------------------------------------------
   Acessórios     -> Positivos:  40.0% | Neutros:   0.0% | Negativos:  60.0%
   Eletrônicos    -> Positivos:  40.0% | Neutros:  20.0% | Negativos:  40.0%
   Informática    -> Positivos:  50.0% | Neutros:  16.7% | Negativos:  33.3%
   Móveis         -> Positivos:  75.0% | Neutros:  25.0% | Negativos:   0.0%
----------------------------------------------------------------------
⚠️  PRINCIPAIS PONTOS DE DOR IDENTIFICADOS (OFENSORES OPERACIONAIS):
----------------------------------------------------------------------
   1. Defeito & Baixa Qualidade do Produto   ->  5 ocorrências (25.0% do total de reviews)
   2. Logística & Atrasos de Entrega         ->  2 ocorrências (10.0% do total de reviews)
   3. Mau Atendimento & Suporte Técnico      ->  1 ocorrências (5.0% do total de reviews)
----------------------------------------------------------------------
💡 RECOMENDAÇÕES ESTRATÉGICAS DE CUSTOMER EXPERIENCE (CX):
----------------------------------------------------------------------
   1. QUALIDADE & TESTES: Reforçar controle de qualidade de componentes e
      periféricos sensíveis (telas e placas) para evitar produtos danificados.
   2. LOGÍSTICA & SLA: Alinhar SLAs com transportadoras para mitigar atrasos
      e fornecer código de rastreamento com notificações ativas via WhatsApp/SMS.
   3. CAPACITAÇÃO DO SAC: Treinar equipe de suporte técnico para tratamento
      ágil e resolutivo de reclamações, evitando sensação de descaso.
======================================================================
```

---

## 📈 Integração com Novos Dados

Para analisar novos reviews programaticamente a partir de outra aplicação ou pipeline:

```python
from sentiment_analyzer import SentimentPulseAnalyzer

analyzer = SentimentPulseAnalyzer()

meus_reviews = [
    {
        "id": "REV-101",
        "customer": "João Silva",
        "category": "Eletrônicos",
        "text": "Produto maravilhoso, entrega super rápida e atendimento excelente!"
    }
]

df = analyzer.process_batch(meus_reviews)
print(df[["review_id", "sentiment", "score", "pain_point"]])
```

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
