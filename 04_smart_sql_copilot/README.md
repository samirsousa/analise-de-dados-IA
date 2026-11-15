# 04 Smart SQL Copilot: Assistente Interativo de Texto para SQL com Streamlit e SQLite

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **04_smart_sql_copilot** é um assistente analítico interativo (*Text-to-SQL Copilot*) desenvolvido em Python com **Streamlit** e banco de dados relacional **SQLite**. 

Projetado para democratizar o acesso a dados para times de negócios, gestores e analistas de BI, o aplicativo permite digitar dúvidas analíticas em linguagem natural (ex: *"Qual o produto mais caro?"*, *"Faturamento total por categoria"*, *"Distribuição regional de vendas"*), convertendo-as em **consultas SQL otimizadas**, executando-as em milissegundos e exibindo os resultados em tabelas dinâmicas e visualizações gráficas.

---

## 🏛️ Arquitetura da Solução

```
+--------------------------------------------------------------------------+
|                       INTERFACE INTERATIVA (STREAMLIT)                  |
+--------------------------------------------------------------------------+
|  [KPIs Rápidos: Total Produtos | Valor Estoque | Transações | Faturamento]|
|                                                                          |
|  [Input do Usuário: "Faturamento total por categoria"]                   |
|  ou Botões de Atalho com Perguntas Frequentes                            |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                      MOTOR TEXT-TO-SQL (COPILOT ENGINE)                  |
+--------------------------------------------------------------------------+
|  - Normalização fonética e remoção de acentos                            |
|  - Mapeamento semântico de entidades, filtros, junções (JOIN) e agregações|
|  - Geração da query SQL relacional otimizada                             |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                       BANCO RELACIONAL (SQLITE LOCAL)                    |
+--------------------------------------------------------------------------+
|  Tabela 'produtos' (id, nome, categoria, preco, estoque, avaliacao)      |
|  Tabela 'vendas'   (id, produto_id, data_venda, quantidade, canal, regiao)|
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                       APRESENTAÇÃO ANALÍTICA (STREAMLIT)                 |
+--------------------------------------------------------------------------+
|  - Exibição do Código SQL com Syntax Highlighting                        |
|  - Tabela Interativa de Resultados (`st.dataframe`)                      |
|  - Gráfico de Barras Automático (`st.bar_chart`)                         |
|  - Métricas de Latência de Execução (ms) e Registros Afetados            |
+--------------------------------------------------------------------------+
```

---

## 📚 Esquema Relacional das Tabelas

### 1. Tabela `produtos`
| Coluna | Tipo | Descrição |
| :--- | :---: | :--- |
| `id` | `INTEGER` | Identificador único primário (PK). |
| `nome` | `TEXT` | Descrição comercial do produto. |
| `categoria` | `TEXT` | Categoria de mercado (Informática, Eletrônicos, Móveis, Acessórios). |
| `preco` | `REAL` | Preço unitário de venda em Reais (R$). |
| `estoque` | `INTEGER` | Saldo físico atual em estoque. |
| `avaliacao` | `REAL` | Nota média de satisfação do cliente (1.0 a 5.0). |

### 2. Tabela `vendas`
| Coluna | Tipo | Descrição |
| :--- | :---: | :--- |
| `id` | `INTEGER` | Identificador único do pedido (PK). |
| `produto_id` | `INTEGER` | Chave estrangeira referenciando `produtos(id)` (FK). |
| `data_venda` | `TEXT` | Data da transação (AAAA-MM-DD). |
| `quantidade` | `INTEGER` | Quantidade de unidades vendidas. |
| `canal` | `TEXT` | Canal de venda (`E-commerce`, `Loja Física`, `Marketplace`). |
| `regiao` | `TEXT` | Região do comprador (`Sudeste`, `Sul`, `Nordeste`, etc.). |

---

## 💡 Exemplos de Perguntas Analíticas Suportadas

1. **"Qual o produto mais caro?"**
   ```sql
   SELECT nome, categoria, preco, estoque, avaliacao 
   FROM produtos 
   ORDER BY preco DESC 
   LIMIT 1;
   ```
2. **"Faturamento total por categoria"**
   ```sql
   SELECT 
       p.categoria,
       COUNT(v.id) AS total_pedidos,
       SUM(v.quantidade) AS total_unidades_vendidas,
       ROUND(SUM(v.quantidade * p.preco), 2) AS faturamento_total
   FROM vendas v
   JOIN produtos p ON v.produto_id = p.id
   GROUP BY p.categoria
   ORDER BY faturamento_total DESC;
   ```
3. **"Quais produtos têm estoque crítico (< 20 unid.)?"**
   ```sql
   SELECT nome, categoria, estoque, preco 
   FROM produtos 
   WHERE estoque < 20 
   ORDER BY estoque ASC;
   ```
4. **"Distribuição de vendas por região"**
   ```sql
   SELECT 
       v.regiao,
       COUNT(v.id) AS numero_pedidos,
       SUM(v.quantidade) AS unidades_vendidas,
       ROUND(SUM(v.quantidade * p.preco), 2) AS receita_total
   FROM vendas v
   JOIN produtos p ON v.produto_id = p.id
   GROUP BY v.regiao
   ORDER BY receita_total DESC;
   ```
5. **"Top 5 produtos mais bem avaliados"**
   ```sql
   SELECT nome, categoria, avaliacao, preco, estoque 
   FROM produtos 
   ORDER BY avaliacao DESC, preco DESC 
   LIMIT 5;
   ```

---

## 📂 Estrutura do Repositório

```text
04_smart_sql_copilot/
├── copilot_app.py     # Aplicação completa em Streamlit e motor de tradução Text-to-SQL
├── requirements.txt   # Dependências do projeto (streamlit, pandas)
├── .gitignore         # Regras de exclusão do Git
└── README.md          # Documentação técnica e guia de execução
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Clonagem e Instalação
Navegue até a pasta do projeto e instale as dependências:
```bash
cd "04_smart_sql_copilot"
pip install -r requirements.txt
```

### 3. Execução da Aplicação com Streamlit
Inicie a aplicação com o comando:
```bash
streamlit run copilot_app.py
```

O aplicativo abrirá automaticamente no seu navegador padrão no endereço:
👉 **`http://localhost:8501`**

---

## 🖥️ Recursos da Interface

- **Aba 1: 💬 Copilot (Text-to-SQL):** Caixa de texto livre para perguntas, botões de atalho rápido na barra lateral, código SQL formatado, tempo de execução e gráficos interativos.
- **Aba 2: 📑 Dicionário & Tabelas:** Inspeção em tempo real das tabelas completas `produtos` e `vendas`.
- **Aba 3: 💻 Terminal SQL Livre:** Console para analistas experientes testarem consultas SQL manuais diretamente na base.

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
