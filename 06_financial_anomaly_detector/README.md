# 06 Financial Anomaly Detector: Detecção Não-Supervisionada de Fraudes com Isolation Forest

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **06_financial_anomaly_detector** é um sistema inteligente de auditoria e segurança bancária desenvolvido em Python para **identificação e isolamento de transações atípicas ou fraudulentas** em fluxos de pagamentos de alta volumetria.

Utilizando o algoritmo de aprendizado não-supervisionado **Isolation Forest (Floresta de Isolamento)**, o projeto é capaz de detectar anomalias sem a necessidade de rótulos prévios de fraude, identificando pontos isolados no espaço multidimensional de atributos como:
- Valores transacionais desproporcionais;
- Horários atípicos (ex: transferências Pix de alto valor na madrugada);
- Padrões geográficos discrepantes (ex: IP/localidade remota com mais de 2.500 km da residência habitual do cliente);
- Tipologias de consumo com saltos bruscos em joalherias ou saques vultosos em terminais 24h.

---

## 🧠 Como Funciona o Algoritmo Isolation Forest?

Diferente de métodos tradicionais que mapeiam primeiro o perfil "normal" do cliente (como distâncias euclidianas ou densidade), o **Isolation Forest** baseia-se em um princípio matemático contra-intuitivo e eficiente:

```
                  [Espaço Amostral Multidimensional]
                                   │
              ┌────────────────────┴────────────────────┐
              ▼                                         ▼
   [Partição Aleatória (Split)]              [Partição Aleatória (Split)]
              │                                         │
              ▼                                         ▼
  {Ponto Anômalo Isolado!}                   [Sub-árvores Profundas...]
   (Poucos splits necessários:               (Muitos splits necessários
    caminho curto na árvore)                  para isolar pontos normais)
```

1. **Facilidade de Isolamento:** Instâncias anômalas possuem valores extremos e esparsos, exigindo **poucas divisões recursivas (árvores rasas)** para serem completamente separadas dos demais dados.
2. **Normalidade Agrupada:** Pontos legítimos concentram-se em clusters densos e demandam um caminho muito mais profundo na árvore para serem isolados.
3. **Escala de Risco:** Quanto menor o comprimento médio do caminho percorrido nas árvores da floresta, maior o índice de anomalia (*Anomaly Score*).

---

## 📊 Engenharia de Atributos (Features Utilizadas)

| Feature | Tipo | Descrição Técnica | Fator de Risco Analisado |
| :--- | :---: | :--- | :--- |
| `valor` | `float` | Valor monetário nominal da transação (R$). | Transações desproporcionais ao ticket médio da conta. |
| `hora_dia` | `int` | Hora de autorização do pagamento (0 a 23h). | Concentração atípica fora do horário comercial. |
| `is_madrugada` | `int` | Flag binária indicadora de janela de risco (00h às 06h). | Janela historicamente crítica para golpes e sequestros relâmpago. |
| `distancia_origem_km`| `float` | Distância geográfica em relação ao endereço cadastral. | Compras remotas e anomalias de geolocalização. |

---

## 📂 Estrutura do Repositório

```text
06_financial_anomaly_detector/
├── anomaly_detector.py                  # Script principal com gerador, modelo e relatório
├── transacoes_suspeitas_detectadas.csv  # Base exportada apenas com as transações anômalas
├── historico_transacoes_completo.csv    # Base total com 1.000 registros e scores de risco
├── requirements.txt                     # Dependências fixadas (scikit-learn, pandas, numpy)
├── .gitignore                           # Regras de exclusão do Git
└── README.md                            # Documentação técnica de execução
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Clonagem e Instalação de Dependências
Acesse a pasta do projeto e instale as bibliotecas necessárias:
```bash
cd "06_financial_anomaly_detector"
pip install -r requirements.txt
```

### 3. Execução do Detector
Execute o script diretamente no terminal:
```bash
python anomaly_detector.py
```

---

## 🚨 Exemplo do Relatório de Auditoria no Terminal

Ao rodar o script, o modelo avalia o fluxo de 1.000 operações e gera o seguinte painel executivo:

```text
=========================================================================================================
🚨 RELATÓRIO DE AUDITORIA TRANSACIONAL - DETECÇÃO DE FRAUDES E ANOMALIAS
=========================================================================================================
• Total de Transações Auditadas   : 1,000
• Transações Suspeitas Isoladas   : 35 ocorrências (3.5% do fluxo)
• Volume Financeiro sob Risco     : R$ 869,800.40
• Transação de Maior Risco        : TXN-OUT-2004 (Valor: R$ 12,187.67)
• Modelo Utilizado                : Isolation Forest (Contaminação Calibrada: 3.5%)
---------------------------------------------------------------------------------------------------------
📋 TOP 10 TRANSAÇÕES SUSPEITAS IDENTIFICADAS PELO MODELO:
---------------------------------------------------------------------------------------------------------
ID Transação  | Data/Hora           | Valor (R$)   | Risco    | Score  | Categoria / Motivo do Alerta
---------------------------------------------------------------------------------------------------------
TXN-OUT-2004  | 2026-11-05 03:37:00 | R$ 12,187.67 | 🔴 CRÍTICO | 100.0 | Serviços Digitais Internacionais -> Valor atípico (R$ 12,187.67) + Horário de risco (03h) + Localidade distante (8649km)
TXN-OUT-2010  | 2026-11-06 03:11:00 | R$ 12,930.30 | 🔴 CRÍTICO |  98.2 | Serviços Digitais Internacionais -> Valor atípico (R$ 12,930.30) + Horário de risco (03h) + Localidade distante (5895km)
TXN-OUT-2012  | 2026-11-04 05:16:00 | R$ 21,436.08 | 🔴 CRÍTICO |  96.6 | Serviços Digitais Internacionais -> Valor atípico (R$ 21,436.08) + Horário de risco (05h) + Localidade distante (3576km)
TXN-OUT-2003  | 2026-11-08 01:59:00 | R$ 44,330.00 | 🔴 CRÍTICO |  90.3 | Transferência Pix Imediata -> Valor atípico (R$ 44,330.00) + Horário de risco (01h)
TXN-OUT-2023  | 2026-11-04 02:30:00 | R$ 41,792.09 | 🔴 CRÍTICO |  87.9 | Transferência Pix Imediata -> Valor atípico (R$ 41,792.09) + Horário de risco (02h)
TXN-OUT-2030  | 2026-11-07 03:39:00 | R$ 13,192.19 | 🔴 CRÍTICO |  84.9 | Saque em Espécie 24h -> Valor atípico (R$ 13,192.19) + Horário de risco (03h) + Localidade distante (608km)
=========================================================================================================
💡 PLANO DE AÇÃO IMEDIATO PARA COMPLIANCE & SEGURANÇA BANCÁRIA:
   1. BLOQUEIO PREVENTIVO: Suspender liquidação das transações marcadas com Risco CRÍTICO.
   2. ETAPA STEP-UP DE AUTENTICAÇÃO: Solicitar validação biométrica/MFA para transferências de madrugada.
   3. NOTIFICAÇÃO PUSH: Enviar alerta urgente para o cliente confirmar a legitimidade da compra.
=========================================================================================================
```

---

## 💾 Exportação e Auditoria Externa

O script gera dois arquivos CSV prontos para consumo por esteiras de Compliance e ferramentas de SIEM:
- **`transacoes_suspeitas_detectadas.csv`**: Contém apenas as transações flagradas como anômalas, ranqueadas por nível de severidade e risco.
- **`historico_transacoes_completo.csv`**: Histórico integral com os respectivos *Anomaly Scores* normalizados de 0 a 100 para auditoria contábil.

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
