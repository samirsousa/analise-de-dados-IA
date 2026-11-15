# 10 AI Executive Reporter: Gerador Automatizado de Briefings e Relatórios Corporativos em Markdown

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Markdown](https://img.shields.io/badge/Output-Standard%20Markdown-083fa1?style=for-the-badge&logo=markdown&logoColor=white)](https://www.markdownguide.org/)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Standard%20Library-green?style=for-the-badge)](#)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **10_ai_executive_reporter** é um motor autônomo em Python de **geração dinâmica de relatórios executivos em Markdown (*Executive Briefings*)**, projetado para consolidar dados de múltiplos silos corporativos (ERP, CRM, Billing) em uma síntese de alto nível para tomada de decisão de C-Levels (CEO, CFO, CRO) e Conselhos de Administração.

O projeto é **100% autossuficiente e utiliza exclusivamente a biblioteca padrão do Python**, garantindo execução instantânea e compatibilidade com esteiras CI/CD, crons diárias/mensais de relatórios e webhooks de automação.

---

## 🏛️ Dimensões Analíticas Consolidadas

```
+--------------------------------------------------------------------------+
|                        FONTES DE DADOS ESTRUTURADAS                      |
+--------------------------------------------------------------------------+
|  [Financeiro]      Faturamento Líquido, Metas, Margem Bruta, ARR         |
|  [Comercial]       Leads, Oportunidades (SQL), Deals Fechados, Conversão |
|  [Unit Economics]  CAC, LTV, Relação LTV/CAC, Payback, Churn, NRR        |
|  [Unidades de Neg.]Performance por Produto, Atingimento e Crescimento    |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                    MOTOR EXECUTIVO (REPORTER ENGINE)                     |
+--------------------------------------------------------------------------+
|  - Cálculo automatizado de MoM (Month-over-Month) e Run-Rate anualizado  |
|  - Avaliação de conformidade com benchmarks de mercado e orçamentos      |
|  - Atribuição de status executivo visual (🟢, 🟡, 🔴)                    |
|  - Formulação de recomendações estratégicas e planos de ação             |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                        SAÍDA EXECUTIVA MULTICANAL                        |
+--------------------------------------------------------------------------+
|  - Exibição renderizada diretamente no terminal                          |
|  - Gravação automática em 'executive_briefing.md'                        |
+--------------------------------------------------------------------------+
```

---

## 📊 Indicadores e Métricas Chave Computadas

| Categoria | Indicador Chave | Fórmula / Definição | Benchmark Típico |
| :--- | :--- | :--- | :---: |
| **Financeiro** | **Crescimento MoM** | $\frac{\text{Receita Atual} - \text{Receita Anterior}}{\text{Receita Anterior}} \times 100$ | $> +10\%$ ao mês |
| **Financeiro** | **ARR Projetado** | $\text{Receita Recorrente Mensal} \times 12$ | Expansão de Run-Rate |
| **Comercial** | **Conversão Global** | $\frac{\text{Contratos Fechados}}{\text{Total de Leads}} \times 100$ | $2.5\% \sim 4.5\%$ |
| **Comercial** | **Conversão SQL** | $\frac{\text{Contratos Fechados}}{\text{SQLs Qualificados}} \times 100$ | $> 15.0\%$ |
| **Sustentabilidade**| **LTV / CAC** | $\frac{\text{Lifetime Value}}{\text{Custo de Aquisição de Clientes}}$ | $> 3.0\times$ (Saudável) |
| **Retenção** | **Net Revenue Retention** | Faturamento da base existente pós-expansões e churn | $> 110\%$ |

---

## 📂 Estrutura do Repositório

```text
10_ai_executive_reporter/
├── reporter.py            # Script principal orientado a objetos com dataclasses
├── executive_briefing.md  # Relatório executivo gerado dinamicamente em Markdown
├── requirements.txt       # Arquivo de dependências (Python Standard Library)
├── .gitignore             # Regras de exclusão do Git
└── README.md              # Documentação de apresentação corporativa
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.
- Nenhuma dependência externa pesada necessária.

### 2. Execução Direta
Navegue até a pasta do projeto e execute:
```bash
cd "10_ai_executive_reporter"
python reporter.py
```

O relatório será impresso no terminal e gravado simultaneamente em [`executive_briefing.md`](executive_briefing.md).

---

## 📑 Exemplo do Relatório Executivo Gerado

```markdown
# 📑 Executive Performance Briefing: Enterprise Cloud & Analytics S.A.
> Período de Referência: Outubro / 2026 | Status Global: 🟢 FORTE EXPANSÃO

## 1. 🎯 Executive Scorecard (Resumo em Alto Nível)
| Indicador Chave (KPI) | Resultado Atual | Meta Mensal | Crescimento MoM | Status Executivo |
| :--- | :---: | :---: | :---: | :---: |
| **Faturamento Líquido** | **R$ 1,854,200.00** | R$ 1,750,000.00 | **+14.56%** | 🟢 Superou Meta (106.0%) |
| **ARR Anualizado (Run-Rate)** | **R$ 22,250,400.00** | R$ 21,000,000.00 | +14.56% | 🟢 Ritmo Acelerado |
| **Margem Bruta Operacional** | **72.4%** | 70.0% | +2.4 p.p. | 🟢 Rentabilidade Saudável |
| **Taxa de Conversão Global** | **3.69%** | 3.20% | +0.49 p.p. | 🟢 Alta Eficiência |
| **Relação LTV / CAC** | **4.89x** | 3.00x | +0.6x | 🟢 Unidades Econômicas Excelentes |
| **Churn Mensal de Receita** | **1.45%** | < 2.00% | -0.3 p.p. | 🟢 Retenção Controlada |

## 2. 💰 Performance Financeira & Tração de Receita
- **Receita Realizada:** R$ 1,854,200.00 (+14.56% MoM).
- **Atingimento Orçamentário:** 106.0% da meta planejada.
```

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
