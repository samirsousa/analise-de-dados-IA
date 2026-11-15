# 09 Customer Segmentation RFM: Segmentação Estratégica de Clientes com K-Means

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **09_customer_segmentation_rfm** é uma solução completa de inteligência de CRM e Ciência de Dados aplicada a e-commerce para **segmentação comportamental e clustering de clientes**.

Combinando o modelo clássico de **RFM (Recência, Frequência e Valor Monetário)** com o algoritmo de aprendizado não-supervisionado **K-Means**, o projeto divide a base de consumidores em grupos homogêneos e acionáveis, permitindo desenhar réguas de comunicação personalizadas, otimizar orçamentos de mídia de retenção e maximizar o *Customer Lifetime Value* (LTV).

---

## 📐 Metodologia de Clusterização Aplicada

O agrupamento é estruturado em quatro etapas rigorosas de Ciência de Dados:

```
[Histórico Transacional: 2.200 Pedidos de E-commerce]
                          │
                          ▼
        [Engenharia de Atributos RFM por Cliente]
        - Recência (R): Dias desde o último pedido (menor = melhor)
        - Frequência (F): Total de pedidos únicos realizados
        - Valor Monetário (M): Gasto acumulado em Reais (R$)
                          │
                          ▼
       [Tratamento de Assimetria & Padronização]
        - Transformação Logarítmica: log(1 + x) para mitigar caudas longas (skewness)
        - Normalização Z-Score (StandardScaler): Média 0, Desvio Padrão 1
                          │
                          ▼
            [Agrupamento K-Means (k=4)]
        - Inicialização K-Means++ para convergência estável dos centróides
        - Otimização da inércia e atribuição de partições
                          │
                          ▼
      [Interpretação Semântica & Playbook Estratégico]
        - Mapeamento analítico de centróides para personas de negócios
        - Exportação da base rotulada em CSV e relatório executivo
```

---

## 👥 Matriz de Clusters Estratégicos

| Cluster / Segmento | Perfil Comportamental RFM | Representatividade na Base | Share de Receita (%) |
| :--- | :--- | :---: | :---: |
| **⭐ Clientes VIP (Campeões)** | Recência imediata (2 dias), frequência altíssima (~11 pedidos) e ticket de alto valor. | **15,0%** dos clientes | **63,2%** da receita total |
| **💎 Clientes Fiéis (Recorrentes)** | Recência recente (~17 dias), compras frequentes (~6 pedidos) e ticket sólido. | **35,0%** dos clientes | **28,0%** da receita total |
| **⚠️ Clientes em Risco (Dormentes)** | Recência crítica (~186 dias sem compras), clientes com histórico passado abandonado. | **30,0%** dos clientes | **5,8%** da receita total |
| **🌱 Clientes Novos / Recentes** | Recência recente (~9 dias), ticket inicial e frequência baixa (~1 a 2 pedidos). | **20,0%** dos clientes | **3,0%** da receita total |

---

## 💡 Playbook de Ações Estratégicas de Marketing

1. **⭐ Clientes VIP (Campeões):**
   - *Ação:* Atendimento prioritário (*Concierge*), programa de recompensas exclusivas, convites para testes beta de novos produtos e presentes comemorativos.
2. **💎 Clientes Fiéis (Recorrentes):**
   - *Ação:* Campanhas de *Cross-Selling* e *Up-Selling* recomendando produtos complementares aos já adquiridos, além de planos de assinatura ou frete grátis fixo.
3. **⚠️ Clientes em Risco / Dormentes:**
   - *Ação:* Réguas de reativação (*Win-back*) por e-mail e WhatsApp com cupons de retorno expressivo, pesquisas para entender motivos do abandono e ofertas de produtos renovados.
4. **🌱 Clientes Novos / Recentes:**
   - *Ação:* Régua de boas-vindas (*onboarding*) com guias de uso, cupom para 2ª compra válido por 15 dias e pesquisa rápida de satisfação com o primeiro pedido.

---

## 📂 Estrutura do Repositório

```text
09_customer_segmentation_rfm/
├── rfm_analysis.py               # Script com gerador, cálculo RFM, K-Means e relatório
├── clientes_segmentados_rfm.csv  # Base tratada com cada cliente mapeado ao seu cluster
├── historico_pedidos_simulado.csv# Histórico transacional completo de pedidos
├── requirements.txt              # Dependências do projeto (scikit-learn, pandas, numpy)
├── .gitignore                    # Regras de exclusão do Git
└── README.md                     # Documentação técnica e estratégica
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Clonagem e Instalação
Acesse a pasta do projeto e instale as dependências:
```bash
cd "09_customer_segmentation_rfm"
pip install -r requirements.txt
```

### 3. Execução da Análise RFM
Execute o script diretamente no terminal:
```bash
python rfm_analysis.py
```

---

## 📊 Exemplo da Saída no Terminal

```text
===============================================================================================
🎯 RELATÓRIO EXECUTIVO - SEGMENTAÇÃO DE CLIENTES VIA RFM & K-MEANS
===============================================================================================
• Base Total de Clientes Analisada : 400 clientes únicos
• Faturamento Total Auditado       : R$ 1,406,215.70
• Recência Média da Base          : 63.9 dias
• Frequência Média de Compras     : 4.8 pedidos por cliente
• Algoritmo de Agrupamento         : K-Means (k=4 clusters com K-Means++)
-----------------------------------------------------------------------------------------------
📊 MATRIZ COMPARATIVA DE CLUSTERS ESTRATÉGICOS:
-----------------------------------------------------------------------------------------------
Segmento Estratégico             | Clientes     | Recência    | Frequência   | Ticket Médio   | Share Rec.
-----------------------------------------------------------------------------------------------
⭐ Clientes VIP (Campeões)        | 60 (15.0%)   | 2 dias      | 11.0 ped.    | R$ 14,816.59   |  63.2%
💎 Clientes Fiéis (Recorrentes)   | 140 (35.0%)  | 17 dias     | 6.0 ped.     | R$ 2,809.87    |  28.0%
⚠️ Clientes em Risco / Dormentes | 120 (30.0%)  | 186 dias    | 2.4 ped.     | R$ 681.12      |   5.8%
🌱 Clientes Novos / Recentes      | 80 (20.0%)   | 9 dias      | 1.5 ped.     | R$ 526.29      |   3.0%
===============================================================================================
💡 PLAYBOOK DE MARKETING & AÇÕES ESTRATÉGICAS RECOMENDADAS:
===============================================================================================
1. ⭐ Clientes VIP (Campeões) -> Faturamento: R$ 888,995.44 (63.2%)
   ▶ Ação Recomendada: Tratamento exclusivo (Concierge/White-Glove), programas de fidelidade premium, acesso antecipado a lançamentos e recompensas personalizadas.

2. 💎 Clientes Fiéis (Recorrentes) -> Faturamento: R$ 393,382.02 (28.0%)
   ▶ Ação Recomendada: Campanhas de Cross-Selling e Up-Selling de itens complementares, ofertas de combos e incentivos para aumentar o ticket médio por pedido.

3. ⚠️ Clientes em Risco / Dormentes -> Faturamento: R$ 81,734.99 (5.8%)
   ▶ Ação Recomendada: Campanhas agressivas de Win-back (reativação) com descontos exclusivos de retorno, pesquisas para identificar motivos de abandono e canais de suporte ativo.

4. 🌱 Clientes Novos / Recentes -> Faturamento: R$ 42,103.25 (3.0%)
   ▶ Ação Recomendada: Comunicação de onboarding com guias de uso, cupons de incentivo para 2ª compra em até 20 dias e pesquisas curtas de satisfação pós-primeiro pedido.
===============================================================================================
```

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
