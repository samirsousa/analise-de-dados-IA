# 07 RAG Document Copilot: Q&A Inteligente sobre Manuais e Contratos com Busca Vetorial Local

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3%2B-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![RAG Architecture](https://img.shields.io/badge/RAG-Local%20Vector%20Search-blueviolet?style=for-the-badge)](#)
[![Status](https://img.shields.io/badge/Status-Produção%20Pronto-success?style=for-the-badge)](#)
[![Licença](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](#)

---

## 📌 Visão Geral do Projeto

O **07_rag_document_copilot** é um assistente conversacional corporativo baseado na arquitetura **RAG (Retrieval-Augmented Generation - Geração Aumentada por Recuperação)** desenvolvido com **Streamlit** e motor de **busca vetorial 100% local e offline**.

O sistema permite a operadores, advogados e engenheiros realizarem perguntas em linguagem natural sobre contratos corporativos complexos e manuais de engenharia, recuperando os trechos exatos (*chunks*) por proximidade semântica (vetores TF-IDF e Similaridade de Cosseno), exibindo respostas fundamentadas (*grounded*) e citando páginas, cláusulas e níveis de confiança estatística.

---

## 🏛️ Arquitetura do Pipeline RAG Local

```
+--------------------------------------------------------------------------+
|                     BASE DE DOCUMENTOS TÉCNICOS                          |
|  - Contrato de Prestação de Serviços Cloud & SaaS (SLA, Multas, LGPD)     |
|  - Manual Técnico de Operação de Servidores v2.4 (Rescue Mode, Backups)   |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                    FRAGMENTAÇÃO & INDEXAÇÃO VETORIAL                     |
|  - Segmentação em Chunks com Metadados (Documento, Seção, Página)        |
|  - Vetorização Esparsa N-Gram (TF-IDF com normalização de stopwords)     |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                         CONSULTA EM LINGUAGEM NATURAL                    |
|  Usuário: "Qual a multa por rescisão antecipada do contrato?"            |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                       MOTOR DE BUSCA VETORIAL (RETRIEVAL)                |
|  - Cálculo da Similaridade de Cosseno da Query contra todos os Chunks    |
|  - Ranqueamento dos Top-K fragmentos com maior aderência vetorial        |
+--------------------------------------------------------------------------+
                                     │
                                     ▼
+--------------------------------------------------------------------------+
|                   RESPOSTA FUNDAMENTADA & INTERFACE CHAT                 |
|  - Síntese analítica da cláusula / procedimento                          |
|  - Caixa expansível com o texto original, página e score de similaridade |
+--------------------------------------------------------------------------+
```

---

## 📚 Base de Conhecimento Indexada

O copilot já possui incorporado um acervo técnico simulado de alta fidelidade:

1. **Contrato de Prestação de Serviços Cloud & SaaS:**
   - **Cláusula 2.1:** SLA garantido de 99,95% de disponibilidade e tabela de créditos compensatórios.
   - **Cláusula 4.4:** Janelas de manutenção programada (domingos, 02h às 06h, aviso prévio de 72h).
   - **Cláusula 5.3:** Rescisão antecipada, aviso prévio de 30 dias e multa de 20% sobre parcelas remanescentes.
   - **Cláusula 8.2:** Dever de sigilo, conformidade com a LGPD e vigência de confidencialidade por 5 anos pós-término.

2. **Manual Técnico de Operação de Servidores Cloud v2.4:**
   - **Seção 3.2:** Procedimento passo a passo para inicialização em modo de recuperação (*Rescue Mode*).
   - **Seção 4.1:** Política de snapshots a cada 4 horas, RPO de 4h, RTO de 45 min e retenção de 30 dias.
   - **Seção 5.3:** Diagnóstico de falha de firewall, regras do UFW e liberação de portas críticas (22/443).
   - **Seção 6.2:** Escalonamento vertical de vCPU/RAM, suporte a *Hot-Plug* e rotina de desligamento seguro.

---

## 📂 Estrutura do Repositório

```text
07_rag_document_copilot/
├── copilot_ui.py      # Aplicação completa em Streamlit com o motor RAG vetorial
├── requirements.txt   # Dependências do projeto (streamlit, scikit-learn, pandas, numpy)
├── .gitignore         # Regras de exclusão do Git
└── README.md          # Documentação técnica e guia de execução
```

---

## ⚡ Instalação e Execução

### 1. Pré-requisitos
- Python 3.10 ou superior instalado.

### 2. Clonagem e Instalação
Acesse a pasta do projeto e instale as bibliotecas:
```bash
cd "07_rag_document_copilot"
pip install -r requirements.txt
```

### 3. Execução da Interface Streamlit
Inicie a aplicação com o comando:
```bash
streamlit run copilot_ui.py
```

O aplicativo abrirá automaticamente no navegador em:
👉 **`http://localhost:8501`**

---

## 💡 Exemplos de Perguntas e Respostas Fundamentadas

### Pergunta 1:
> *"Qual a multa contratual em caso de rescisão imotivada antes do primeiro ano?"*

**Resposta do Copilot:**
> Com base na análise documental do **Contrato de Prestação de Serviços Cloud & SaaS** (*Cláusula 5.3 - Rescisão Antecipada e Multa Contratual*, pág. 7):
> *"Qualquer das partes poderá rescindir o presente contrato mediante aviso prévio por escrito com antecedência mínima de 30 dias. Em caso de rescisão imotivada por iniciativa da CONTRATANTE antes de completados os primeiros 12 meses de vigência, será aplicada multa rescisória compensatória equivalente a 20% do valor total das parcelas remanescentes..."*
>
> **Evidência Vetorial:** Score de Similaridade: `0.3171` (Confiança Alta).

---

### Pergunta 2:
> *"Como devo proceder caso o servidor não inicialize após falha no kernel?"*

**Resposta do Copilot:**
> Com base na análise documental do **Manual Técnico de Operação de Servidores Cloud v2.4** (*Seção 3.2 - Procedimento de Boot em Modo de Recuperação (Rescue Mode)*, pág. 14):
> *"O operador deve acessar o painel de controle do datacenter, selecionar o host afetado e acionar a opção 'Ativar Rescue Mode'. Em seguida, conecte-se via console serial VNC e execute: `mount /dev/sda1 /mnt && chroot /mnt` para reparar os pacotes do sistema."*
>
> **Evidência Vetorial:** Score de Similaridade: `0.3296` (Confiança Alta).

---

## ⚙️ Controles da Barra Lateral

- **Botões de Atalho:** Clique em perguntas frequentes prontas para testar o sistema instantaneamente sem precisar digitar.
- **Top-K Slider:** Controle quantos trechos recuperados devem ser avaliados (1 a 4 fragmentos).
- **Limiar de Similaridade:** Ajuste fino da sensibilidade mínima do cosseno para filtrar ruídos ou perguntas fora de contexto.
- **Inspetor de Conhecimento:** Visualização direta de todas as cláusulas e páginas indexadas.

---

## 📄 Licença
Distribuído sob a licença **MIT**. Consulte o arquivo de licença para mais detalhes.
