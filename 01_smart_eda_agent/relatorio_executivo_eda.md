# 📊 Relatório Executivo de Análise Exploratória (EDA)

> **Dataset:** Vendas de E-commerce | **Agente:** Smart EDA Agent v1.0

---

## 1. 🎯 Indicadores-Chave de Desempenho (KPIs Gerais)

| Métrica | Valor Absoluto | Detalhes |
| :--- | :---: | :--- |
| **Faturamento Total** | **R$ 42,500.50** | Receita líquida consolidada |
| **Ticket Médio por Pedido** | **R$ 1,700.02** | Valor médio gasto por transação |
| **Volume Total de Itens** | **41 unid.** | Total de produtos comercializados |
| **Total de Pedidos** | **25** | Pedidos únicos processados |
| **Clientes Únicos** | **25** | Base de clientes ativos |
| **Preço Médio por Item** | **R$ 1,036.60** | Receita / Volume de itens |
| **Faixa de Valor por Pedido** | **R$ 379.80 ~ R$ 5,499.00** | Mínimo e Máximo observados |

---

## 2. 🏷️ Desempenho por Categoria de Produto

| Categoria | Volume Vendido | Faturamento (R$) | Share Receita (%) | Share Volume (%) |
| :--- | :---: | :---: | :---: | :---: |
| Informática | 13 unid. | R$ 20,667.00 | 48.6% | 31.7% |
| Eletrônicos | 9 unid. | R$ 9,479.70 | 22.3% | 22.0% |
| Móveis | 6 unid. | R$ 7,650.00 | 18.0% | 14.6% |
| Acessórios | 13 unid. | R$ 4,703.80 | 11.1% | 31.7% |

---

## 3. 🏆 Rankings: Top 5 Produtos Líderes

### 3.1. Top 5 por Faturamento (Receita Gerada)

| Ranking | Produto | Categoria | Preço Unit. Médio | Volume | Faturamento Total |
| :---: | :--- | :--- | :---: | :---: | :---: |
| #1 | **Notebook Gamer Dell G15** | Informática | R$ 5,499.00 | 2 unid. | **R$ 10,998.00** |
| #2 | **Notebook Ultra Asus Zenbook** | Informática | R$ 4,890.00 | 1 unid. | **R$ 4,890.00** |
| #3 | **Monitor UltraWide 29 LG** | Eletrônicos | R$ 1,299.90 | 3 unid. | **R$ 3,899.70** |
| #4 | **Mesa com Regulagem de Altura** | Móveis | R$ 1,890.00 | 2 unid. | **R$ 3,780.00** |
| #5 | **Cadeira Ergonômica Pro** | Móveis | R$ 1,150.00 | 3 unid. | **R$ 3,450.00** |

### 3.2. Top 5 por Volume de Vendas (Unidades)

| Ranking | Produto | Categoria | Volume Vendido | Faturamento Gerado |
| :---: | :--- | :--- | :---: | :---: |
| #1 | **SSD NVMe 1TB Kingston** | Informática | **5 unid.** | R$ 1,600.00 |
| #2 | **Mouse Sem Fio Logitech MX Master** | Acessórios | **5 unid.** | R$ 2,250.00 |
| #3 | **Memória RAM DDR4 16GB Corsair** | Informática | **4 unid.** | R$ 780.00 |
| #4 | **Cadeira Ergonômica Pro** | Móveis | **3 unid.** | R$ 3,450.00 |
| #5 | **Monitor UltraWide 29 LG** | Eletrônicos | **3 unid.** | R$ 3,899.70 |

---

## 4. 🌍 Distribuição Geográfica de Vendas por Região

| Região | Pedidos | Volume (unid.) | Faturamento (R$) | Ticket Médio Reg. | Share (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Sudeste** | 10 | 15 | R$ 21,566.90 | R$ 2,156.69 | 50.7% |
| **Sul** | 5 | 8 | R$ 9,808.80 | R$ 1,961.76 | 23.1% |
| **Centro-Oeste** | 3 | 4 | R$ 5,069.80 | R$ 1,689.93 | 11.9% |
| **Nordeste** | 5 | 10 | R$ 4,280.00 | R$ 856.00 | 10.1% |
| **Norte** | 2 | 4 | R$ 1,775.00 | R$ 887.50 | 4.2% |

---

## 5. 💡 Principais Insights e Recomendações de Negócio

1. **Dominância da Categoria Informática:** A categoria líder responde pela maior fatia do faturamento, impulsionada pelo alto valor agregado de itens como notebooks e componentes.
2. **Concentração Regional no Sudeste & Sul:** O Sudeste desponta como o principal polo de receita e densidade de pedidos, recomendando campanhas de retenção e logística expressa para essa região.
3. **Alavancagem do Ticket Médio:** Produtos premium (ex: Notebooks Gamer e Monitores) elevam substancialmente o ticket médio geral (R$ 1,700.02), indicando oportunidade para estratégias de *cross-selling* de acessórios periféricos.

---
*Relatório gerado automaticamente pelo `01_smart_eda_agent`.*