# 01 Smart EDA Agent: Análise Exploratória e Inteligência de Negócios para E-commerce

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org/)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **01_smart_eda_agent** é um módulo autônomo e de alta performance desenvolvido em Python para realizar **Análise Exploratória de Dados (EDA - Exploratory Data Analysis)** e sintetizar inteligência acionável a partir de registros transacionais de e-commerce.

Projetado para engenheiros de dados, cientistas de dados e analistas de BI, o agente processa dados de vendas, valida integridade matemática, computa indicadores-chave de desempenho (**KPIs**) e entrega um **relatório executivo estruturado em Markdown**, pronto para consumo por tomadores de decisão, apresentações corporativas e pipelines automatizados de relatórios.

---

## 🚀 Principais Funcionalidades

- **Ingestão e Validação Automatizada:** Verificação de esquema, tipagem estrita com *Type Hints* e reconciliação da consistência matemática entre quantidade, preço unitário e faturamento.
- **KPIs Executivos Consolidados:**
  - Faturamento bruto e receita consolidada.
  - Ticket médio por transação e preço médio ponderado por item.
  - Métricas de amplitude e dispersão de valor por pedido.
- **Análise Multidimensional de Categorias e Produtos:**
  - Ranqueamento dos produtos líderes por faturamento (receita gerada) e por volume físico de vendas (unidades).
  - Cálculo de *Market Share* percentual relativo de receita e volume por categoria.
- **Distribuição Geográfica de Vendas:**
  - Quebra de desempenho e ticket médio regional (Sudeste, Sul, Nordeste, Centro-Oeste e Norte).
- **Exportação Multicanal:**
  - Saída estilizada e renderizada diretamente no terminal.
  - Gravação automática de arquivo `.md` consolidado para repositórios ou portais corporativos.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
| :--- | :--- |
| **Python 3.10+** | Linguagem base com recursos modernos de tipagem estática (`typing`, `dataclasses`, `pathlib`). |
| **Pandas** | Manipulação tabular de alta eficiência, agregações multidimensionais e agregações por janela. |
| **NumPy** | Operações vetorizadas e validação numérica de consistência estatística. |

---

## 📂 Estrutura do Repositório

```text
01_smart_eda_agent/
├── sample_data.csv             # Base de dados realista de vendas de e-commerce
├── eda_script.py               # Script principal orientado a objetos com tipagem estrita
├── relatorio_executivo_eda.md  # Relatório executivo gerado automaticamente em Markdown
├── requirements.txt            # Dependências do projeto
├── .gitignore                  # Arquivos ignorados pelo controle de versão Git
└── README.md                   # Documentação corporativa do projeto
```

---

## ⚙️ Instalação e Execução

### 1. Pré-requisitos
Certifique-se de possuir o Python 3.10 ou superior instalado em seu ambiente.

### 2. Clonagem do Repositório e Navegação
```bash
git clone https://github.com/seu-usuario/01_smart_eda_agent.git
cd 01_smart_eda_agent
```

### 3. Instalação das Dependências
Você pode instalar as bibliotecas necessárias diretamente via `requirements.txt`:
```bash
pip install -r requirements.txt
```
*Ou individualmente via pip:*
```bash
pip install pandas numpy
```

### 4. Execução da Análise
Execute o agente de análise diretamente:
```bash
python eda_script.py
```

---

## 📊 Exemplo do Relatório Executivo Gerado

Ao executar o script, o terminal exibe instantaneamente o relatório no padrão executivo abaixo:

```markdown
# 📊 Relatório Executivo de Análise Exploratória (EDA)
> Dataset: Vendas de E-commerce | Agente: Smart EDA Agent v1.0

## 1. 🎯 Indicadores-Chave de Desempenho (KPIs Gerais)
| Métrica | Valor Absoluto | Detalhes |
| :--- | :---: | :--- |
| **Faturamento Total** | **R$ 42,500.50** | Receita líquida consolidada |
| **Ticket Médio por Pedido** | **R$ 1,700.02** | Valor médio gasto por transação |
| **Volume Total de Itens** | **41 unid.** | Total de produtos comercializados |
| **Total de Pedidos** | **25** | Pedidos únicos processados |
| **Clientes Únicos** | **25** | Base de clientes ativos |
| **Preço Médio por Item** | **R$ 1,036.60** | Receita / Volume de itens |

## 2. 🏷️ Desempenho por Categoria de Produto
| Categoria | Volume Vendido | Faturamento (R$) | Share Receita (%) | Share Volume (%) |
| :--- | :---: | :---: | :---: | :---: |
| Informática | 13 unid. | R$ 20,667.00 | 48.6% | 31.7% |
| Eletrônicos | 9 unid. | R$ 9,479.70 | 22.3% | 22.0% |
| Móveis | 6 unid. | R$ 7,650.00 | 18.0% | 14.6% |
| Acessórios | 13 unid. | R$ 4,703.80 | 11.1% | 31.7% |
```

---

## 💡 Principais Insights e Recomendações Extraídas

1. **Concentração de Receita em Informática:** A categoria **Informática** é o motor de tração da receita da operação, concentrando **48,6% do faturamento total** devido ao alto valor unitário agregado dos notebooks e placas de vídeo.
2. **Dominância Logística e Comercial no Sudeste:** O **Sudeste** lidera tanto em receita líquida (**50,7% do share**) quanto em ticket médio (R$ 2.156,69), recomendando centros de distribuição avançados para redução de frete e prazos.
3. **Estratégia de Venda Cruzada (Cross-Selling):** A categoria de **Acessórios** tem expressivo volume unitário (31,7% do volume total vendido), porém menor ticket (11,1% da receita). Representa a oportunidade ideal para inclusão em *bundles* e combos promocionais no checkout dos eletrônicos e notebooks.

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais informações.
