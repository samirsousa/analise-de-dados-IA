# 02 Churn Predict Engine: Motor de Inferência e Machine Learning para Retenção de Clientes

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **02_churn_predict_engine** é uma solução completa de Machine Learning para detecção preventiva de **Churn (cancelamento voluntário de clientes)** em empresas de base recorrente (SaaS, Telecomunicações e Serviços Financeiros).

O projeto é **100% autossuficiente e desacoplado**, compreendendo desde a geração sintética e calibração de dados transacionais, treinamento e validação estatística de modelos supervisionados (Random Forest com balanceamento de classes), até a disponibilização de uma **API REST assíncrona de baixa latência em FastAPI**, pronta para integração com CRMs e ferramentas de Customer Success.

---

## 🏛️ Arquitetura do Sistema

```
+-------------------------------------------------------------------------+
|                          PIPELINE DE MACHINE LEARNING                    |
+-------------------------------------------------------------------------+
|                                                                         |
|  [Gerador Sintético]                                                    |
|  (Idade, Contrato, Uso, Suporte)                                        |
|              │                                                          |
|              ▼                                                          |
|  [Divisão Estratificada Treino/Teste (80/20)]                           |
|              │                                                          |
|              ▼                                                          |
|  [Pipeline Scikit-Learn: StandardScaler + Balanced RandomForest]        |
|              │                                                          |
|              ▼                                                          |
|  [Avaliação de Métricas (F1: 66%, Recall: 78%, ROC-AUC: 82%)]           |
|              │                                                          |
|              ▼                                                          |
|  [Serialização Joblib: churn_model.joblib]                              |
|                                                                         |
+-------------------------------------------------------------------------+
                                │
                                ▼
+-------------------------------------------------------------------------+
|                           API REST EM FASTAPI                           |
+-------------------------------------------------------------------------+
|                                                                         |
|  [POST /predict] <── JSON Payload (Idade, Contrato, Uso, Suporte)       |
|              │                                                          |
|              ▼                                                          |
|  [Validação Pydantic v2]                                                |
|              │                                                          |
|              ▼                                                          |
|  [Inferência Preditiva em Tempo Real + Matriz de Risco]                 |
|              │                                                          |
|              ▼                                                          |
|  [JSON Response: Probabilidade, Classificação e Ação Recomendada]       |
|                                                                         |
+-------------------------------------------------------------------------+
```

---

## 📊 Dicionário de Variáveis e Features

| Feature | Tipo | Descrição | Impacto no Modelo |
| :--- | :---: | :--- | :--- |
| `tempo_contrato` | `int` | Meses de contrato ativo (1 a 120 meses). | **Maior impacto (38,6%)**: clientes novos têm maior propensão à evasão. |
| `chamados_suporte` | `int` | Quantidade de chamados ao suporte técnico. | **Alto impacto (29,4%)**: reflete atrito e insatisfação operacional. |
| `uso_mensal` | `float` | Horas de uso ou GB consumidos no mês. | **Moderado (17,2%)**: maior engajamento reduz o risco de cancelamento. |
| `idade` | `int` | Idade do titular do contrato (18 a 100 anos). | **Moderado (14,7%)**: perfis com diferentes sensibilidades a preço. |
| **`churn`** *(Alvo)* | `int` | `0` = Cliente Fiel (Retido) \| `1` = Churn (Cancelamento). | Variável dependente binária. |

---

## 📈 Métricas de Performance do Modelo

Avaliadas em conjunto de teste independente (500 amostras estratificadas não vistas):

- **ROC-AUC Score:** `82.42%` (Excelente discriminação entre classes)
- **Recall (Sensibilidade para Churn):** `77.71%` *(Prioridade de negócio: minimizar falsos negativos)*
- **F1-Score:** `66.12%`
- **Acurácia Global:** `75.00%`

---

## 📂 Estrutura do Repositório

```text
02_churn_predict_engine/
├── model_train.py             # Script de geração de dados, treino, validação e exportação
├── app.py                     # API REST em FastAPI com schemas Pydantic e inferência
├── churn_model.joblib         # Artefato serializado do modelo treinado
├── synthetic_customer_data.csv# Dataset sintético com 2.500 instâncias para auditoria
├── requirements.txt           # Dependências fixadas do projeto
├── .gitignore                 # Arquivos e pastas ignorados no Git
└── README.md                  # Documentação técnica e operacional
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Clonagem e Instalação de Dependências
```bash
git clone https://github.com/seu-usuario/02_churn_predict_engine.git
cd 02_churn_predict_engine

pip install -r requirements.txt
```

### 3. Treinar o Modelo de Machine Learning
Para gerar a base sintética e treinar o modelo do zero:
```bash
python model_train.py
```
*Saída esperada: resumo estatístico no terminal e geração dos arquivos `churn_model.joblib` e `synthetic_customer_data.csv`.*

### 4. Inicializar a API FastAPI
Inicie o servidor de inferência:
```bash
python app.py
```
*Ou via uvicorn CLI:*
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

O servidor estará disponível em:
- **API Base:** `http://127.0.0.1:8000`
- **Swagger UI Interativo:** `http://127.0.0.1:8000/docs`
- **Redoc UI:** `http://127.0.0.1:8000/redoc`

---

## 🧪 Exemplos de Requisição e Resposta

### Exemplo 1: Cliente em Risco Crítico de Churn (Pouco tempo de casa e muitos chamados)

#### Requisição (`cURL`):
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "idade": 55,
       "tempo_contrato": 3,
       "uso_mensal": 45.0,
       "chamados_suporte": 5
     }'
```

#### Resposta (`JSON`):
```json
{
  "churn_prediction": 1,
  "churn_label": "Churn (Risco de Cancelamento)",
  "churn_probability": 0.9144,
  "churn_probability_pct": "91.44%",
  "risk_level": "Crítico",
  "retention_action": "Perda quase certa. Ofertar desconto de retenção, suporte prioritário imediato e plano de fidelização."
}
```

---

### Exemplo 2: Cliente Fiel / Retido (Longo tempo de contrato e alto engajamento)

#### Requisição (`cURL`):
```bash
curl -X POST "http://127.0.0.1:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{
       "idade": 28,
       "tempo_contrato": 36,
       "uso_mensal": 380.0,
       "chamados_suporte": 0
     }'
```

#### Resposta (`JSON`):
```json
{
  "churn_prediction": 0,
  "churn_label": "Fiel (Retido)",
  "churn_probability": 0.0418,
  "churn_probability_pct": "4.18%",
  "risk_level": "Baixo",
  "retention_action": "Cliente satisfeito e engajado. Manter rotina padrão de comunicação e pós-venda."
}
```

---

### Exemplo de Consumo via Python (`requests`)

```python
import requests

url = "http://127.0.0.1:8000/predict"
payload = {
    "idade": 42,
    "tempo_contrato": 8,
    "uso_mensal": 120.0,
    "chamados_suporte": 3
}

response = requests.post(url, json=payload)
data = response.json()

print(f"Probabilidade de Churn: {data['churn_probability_pct']}")
print(f"Nível de Risco: {data['risk_level']}")
print(f"Ação Recomendada: {data['retention_action']}")
```

---

## 🛡️ Autossuficiência Garantida
Se o comando `python app.py` for executado antes de `python model_train.py`, o módulo de inicialização (`lifespan`) detectará automaticamente a ausência de `churn_model.joblib`, treinará o modelo em tempo de execução e servirá as requisições sem erros ou intervenção manual.

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
