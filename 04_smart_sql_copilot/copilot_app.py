"""Smart SQL Copilot - Assistente de Conversão de Texto para SQL com Streamlit e SQLite.

Permite a usuários de negócio e analistas consultar bases de dados relacionais
utilizando perguntas em linguagem natural, convertendo intenções analíticas em
consultas SQL otimizadas, executando-as em SQLite local e apresentando métricas,
tabelas interativas e gráficos de visualização.
"""

from __future__ import annotations

import re
import sqlite3
import time
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import streamlit as st


# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA STREAMLIT
# ==============================================================================
st.set_page_config(
    page_title="Smart SQL Copilot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==============================================================================
# GERENCIAMENTO E POVOAMENTO DO BANCO DE DADOS SQLITE
# ==============================================================================
@st.cache_resource
def get_database_connection() -> sqlite3.Connection:
    """Cria e mantém a conexão com o banco SQLite em memória."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    init_sample_database(conn)
    return conn


def init_sample_database(conn: sqlite3.Connection) -> None:
    """Cria o esquema relacional e popula as tabelas de exemplo."""
    cursor = conn.cursor()

    # Tabela 1: Produtos
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL,
            avaliacao REAL NOT NULL
        );
        """
    )

    # Tabela 2: Vendas
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            data_venda TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            canal TEXT NOT NULL,
            regiao TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        );
        """
    )

    # Inserção de dados dos produtos
    produtos_data = [
        ("Notebook Gamer Dell G15", "Informática", 5499.00, 18, 4.8),
        ("Notebook Ultra Asus Zenbook", "Informática", 4890.00, 12, 4.7),
        ("SSD NVMe 1TB Kingston", "Informática", 320.00, 85, 4.9),
        ("Memória RAM DDR4 16GB", "Informática", 195.00, 64, 4.6),
        ("Placa de Vídeo RTX 4060", "Informática", 2399.00, 9, 4.9),
        ("Monitor UltraWide 29 LG", "Eletrônicos", 1299.90, 24, 4.5),
        ("Headset Gamer HyperX Cloud", "Eletrônicos", 420.00, 35, 4.6),
        ("Smartwatch Galaxy Watch", "Eletrônicos", 1250.00, 15, 4.4),
        ("Caixa de Som JBL Flip 6", "Eletrônicos", 650.00, 42, 4.7),
        ("Headphone Sony WH-1000XM5", "Eletrônicos", 2190.00, 8, 4.9),
        ("Cadeira Ergonômica Pro", "Móveis", 1150.00, 14, 4.6),
        ("Mesa Regulagem de Altura", "Móveis", 1890.00, 11, 4.8),
        ("Gaveteiro Volante 3 Gavetas", "Móveis", 420.00, 22, 4.2),
        ("Mouse Sem Fio MX Master", "Acessórios", 450.00, 50, 4.9),
        ("Teclado Mecânico Keychron", "Acessórios", 580.00, 28, 4.7),
        ("Webcam Full HD Logitech", "Acessórios", 389.00, 31, 4.5),
        ("Hub USB-C 7 em 1 Baseus", "Acessórios", 175.00, 60, 4.3),
        ("Suporte Articulado Monitor", "Acessórios", 189.90, 40, 4.4),
    ]

    cursor.executemany(
        """
        INSERT INTO produtos (nome, categoria, preco, estoque, avaliacao)
        VALUES (?, ?, ?, ?, ?);
        """,
        produtos_data,
    )

    # Inserção de dados de vendas
    vendas_data = [
        (1, "2026-01-05", 2, "E-commerce", "Sudeste"),
        (2, "2026-01-08", 1, "Marketplace", "Sul"),
        (3, "2026-01-12", 5, "E-commerce", "Sudeste"),
        (4, "2026-01-15", 4, "Loja Física", "Nordeste"),
        (5, "2026-01-18", 1, "E-commerce", "Sudeste"),
        (6, "2026-01-22", 3, "Marketplace", "Centro-Oeste"),
        (7, "2026-01-26", 2, "E-commerce", "Sul"),
        (8, "2026-01-30", 1, "Loja Física", "Norte"),
        (9, "2026-02-03", 4, "Marketplace", "Sudeste"),
        (10, "2026-02-07", 1, "E-commerce", "Sul"),
        (11, "2026-02-11", 2, "Loja Física", "Nordeste"),
        (12, "2026-02-14", 2, "E-commerce", "Sudeste"),
        (13, "2026-02-18", 3, "Marketplace", "Centro-Oeste"),
        (14, "2026-02-22", 6, "E-commerce", "Sudeste"),
        (15, "2026-02-25", 2, "Loja Física", "Sul"),
        (16, "2026-03-01", 3, "E-commerce", "Nordeste"),
        (17, "2026-03-05", 5, "Marketplace", "Norte"),
        (18, "2026-03-09", 4, "E-commerce", "Sudeste"),
        (1, "2026-03-12", 1, "Loja Física", "Sul"),
        (6, "2026-03-15", 2, "E-commerce", "Sudeste"),
    ]

    cursor.executemany(
        """
        INSERT INTO vendas (produto_id, data_venda, quantidade, canal, regiao)
        VALUES (?, ?, ?, ?, ?);
        """,
        vendas_data,
    )

    conn.commit()


# ==============================================================================
# MOTOR DE CONVERSÃO TEXT-TO-SQL
# ==============================================================================
class TextToSQLCopilot:
    """Motor heurístico e de mapeamento de intenções em linguagem natural para SQL."""

    @staticmethod
    def _normalize(text: str) -> str:
        """Normaliza caracteres, acentos e espaços."""
        text = text.lower().strip()
        replacements = {
            "á": "a", "à": "a", "ã": "a", "â": "a",
            "é": "e", "ê": "e",
            "í": "i",
            "ó": "o", "ô": "o", "õ": "o",
            "ú": "u",
            "ç": "c",
        }
        for orig, sub in replacements.items():
            text = text.replace(orig, sub)
        return text

    def translate_to_sql(self, user_prompt: str) -> Tuple[str, str]:
        """Converte uma pergunta analítica em linguagem natural em consulta SQL.

        Args:
            user_prompt: Pergunta digitada pelo usuário.

        Returns:
            Tuple[str, str]: (Query SQL gerada, Explicação da intenção detectada).
        """
        norm = self._normalize(user_prompt)

        # 1. Produto mais caro
        if any(kw in norm for kw in ["mais caro", "maior preco", "maior valor"]):
            sql = """
SELECT nome, categoria, preco, estoque, avaliacao 
FROM produtos 
ORDER BY preco DESC 
LIMIT 1;
""".strip()
            desc = "Busca o item com o maior preço unitário cadastrado na tabela de produtos."
            return sql, desc

        # 2. Produto mais barato
        if any(kw in norm for kw in ["mais barato", "menor preco", "menor valor"]):
            sql = """
SELECT nome, categoria, preco, estoque, avaliacao 
FROM produtos 
ORDER BY preco ASC 
LIMIT 1;
""".strip()
            desc = "Busca o item de menor custo unitário cadastrado."
            return sql, desc

        # 3. Top N produtos mais bem avaliados
        if any(kw in norm for kw in ["mais bem avaliado", "melhor avalia", "maior nota", "ranking avalia"]):
            sql = """
SELECT nome, categoria, avaliacao, preco, estoque 
FROM produtos 
ORDER BY avaliacao DESC, preco DESC 
LIMIT 5;
""".strip()
            desc = "Lista os 5 produtos com as maiores notas médias de avaliação dos clientes."
            return sql, desc

        # 4. Estoque crítico ou menor que X
        if any(kw in norm for kw in ["estoque baixo", "estoque critico", "menor estoque", "pouco estoque", "estoque menor"]):
            sql = """
SELECT nome, categoria, estoque, preco 
FROM produtos 
WHERE estoque < 20 
ORDER BY estoque ASC;
""".strip()
            desc = "Filtra produtos com estoque crítico (menos de 20 unidades em estoque)."
            return sql, desc

        # 5. Faturamento total por categoria (Join vendas e produtos)
        if any(kw in norm for kw in ["faturamento por categoria", "receita por categoria", "vendas por categoria", "faturamento total"]):
            sql = """
SELECT 
    p.categoria,
    COUNT(v.id) AS total_pedidos,
    SUM(v.quantidade) AS total_unidades_vendidas,
    ROUND(SUM(v.quantidade * p.preco), 2) AS faturamento_total
FROM vendas v
JOIN produtos p ON v.produto_id = p.id
GROUP BY p.categoria
ORDER BY faturamento_total DESC;
""".strip()
            desc = "Cruza as tabelas de vendas e produtos para calcular o faturamento consolidado por categoria."
            return sql, desc

        # 6. Distribuição de vendas por região
        if any(kw in norm for kw in ["por regiao", "distribuicao regional", "vendas por regiao", "faturamento por regiao"]):
            sql = """
SELECT 
    v.regiao,
    COUNT(v.id) AS numero_pedidos,
    SUM(v.quantidade) AS unidades_vendidas,
    ROUND(SUM(v.quantidade * p.preco), 2) AS receita_total,
    ROUND(AVG(v.quantidade * p.preco), 2) AS ticket_medio_regiao
FROM vendas v
JOIN produtos p ON v.produto_id = p.id
GROUP BY v.regiao
ORDER BY receita_total DESC;
""".strip()
            desc = "Agrupa as vendas realizadas por região geográfica e computa a receita total e o ticket médio."
            return sql, desc

        # 7. Vendas por canal (E-commerce, Loja Física, Marketplace)
        if any(kw in norm for kw in ["canal", "canais"]):
            sql = """
SELECT 
    v.canal,
    COUNT(v.id) AS total_transacoes,
    SUM(v.quantidade) AS unidades_comercializadas,
    ROUND(SUM(v.quantidade * p.preco), 2) AS faturamento_canal
FROM vendas v
JOIN produtos p ON v.produto_id = p.id
GROUP BY v.canal
ORDER BY faturamento_canal DESC;
""".strip()
            desc = "Segmenta as métricas de vendas e receita pelos canais de distribuição (E-commerce, Loja Física, Marketplace)."
            return sql, desc

        # 8. Média de preço por categoria / Contagem de produtos por categoria
        if any(kw in norm for kw in ["preco medio", "media de preco", "produtos por categoria", "quantos produtos"]):
            sql = """
SELECT 
    categoria,
    COUNT(*) AS total_produtos,
    ROUND(AVG(preco), 2) AS preco_medio,
    ROUND(MIN(preco), 2) AS preco_minimo,
    ROUND(MAX(preco), 2) AS preco_maximo,
    SUM(estoque) AS estoque_total
FROM produtos
GROUP BY categoria
ORDER BY preco_medio DESC;
""".strip()
            desc = "Agrupa produtos por categoria calculando contagem, preço médio e limites de valores."
            return sql, desc

        # 9. Produtos de Informática
        if "informatica" in norm:
            sql = """
SELECT nome, categoria, preco, estoque, avaliacao 
FROM produtos 
WHERE categoria = 'Informática' 
ORDER BY preco DESC;
""".strip()
            desc = "Filtra todos os itens pertencentes à categoria 'Informática'."
            return sql, desc

        # 10. Produtos de Eletrônicos
        if "eletronico" in norm or "eletronicos" in norm:
            sql = """
SELECT nome, categoria, preco, estoque, avaliacao 
FROM produtos 
WHERE categoria = 'Eletrônicos' 
ORDER BY preco DESC;
""".strip()
            desc = "Filtra todos os itens pertencentes à categoria 'Eletrônicos'."
            return sql, desc

        # 11. Produtos de Móveis
        if "moveis" in norm or "movel" in norm:
            sql = """
SELECT nome, categoria, preco, estoque, avaliacao 
FROM produtos 
WHERE categoria = 'Móveis' 
ORDER BY preco DESC;
""".strip()
            desc = "Filtra todos os itens pertencentes à categoria 'Móveis'."
            return sql, desc

        # 12. Produtos de Acessórios
        if "acessorio" in norm or "acessorios" in norm:
            sql = """
SELECT nome, categoria, preco, estoque, avaliacao 
FROM produtos 
WHERE categoria = 'Acessórios' 
ORDER BY preco DESC;
""".strip()
            desc = "Filtra todos os itens pertencentes à categoria 'Acessórios'."
            return sql, desc

        # 13. Preços acima de um valor padrão (ex: 1000 reais)
        if any(kw in norm for kw in ["acima de", "maior que", "mais de"]):
            # Tenta capturar valor numérico digitado pelo usuário
            match = re.search(r"\b(\d+)\b", norm)
            threshold = int(match.group(1)) if match else 1000
            sql = f"""
SELECT nome, categoria, preco, estoque, avaliacao 
FROM produtos 
WHERE preco >= {threshold} 
ORDER BY preco DESC;
""".strip()
            desc = f"Filtra produtos com preço unitário igual ou superior a R$ {threshold:.2f}."
            return sql, desc

        # Fallback genérico: Visão geral de catálogo
        sql = """
SELECT nome, categoria, preco, estoque, avaliacao 
FROM produtos 
ORDER BY preco DESC 
LIMIT 10;
""".strip()
        desc = (
            "Não foi possível isolar um filtro específico. "
            "Exibindo os 10 principais produtos ordenados por preço."
        )
        return sql, desc


# ==============================================================================
# INTERFACE PRINCIPAL DO STREAMLIT
# ==============================================================================
def main() -> None:
    conn = get_database_connection()
    copilot = TextToSQLCopilot()

    # Barra Lateral
    with st.sidebar:
        st.title("🤖 Smart SQL Copilot")
        st.markdown(
            "Assistente generativo para **conversão de linguagem natural em consultas SQL** "
            "com execução analítica em tempo real."
        )
        st.divider()

        st.subheader("💡 Perguntas Rápidas (Exemplos)")
        exemplos = [
            "Qual o produto mais caro?",
            "Faturamento total por categoria",
            "Quais produtos têm estoque crítico (< 20 unid.)?",
            "Distribuição de vendas por região",
            "Top 5 produtos mais bem avaliados",
            "Qual o preço médio por categoria?",
            "Vendas por canal de distribuição",
            "Quais os produtos da categoria Informática?",
        ]

        # Botões de clique rápido que preenchem a pergunta na sessão
        for ex in exemplos:
            if st.button(f"👉 {ex}", use_container_width=True):
                st.session_state["user_query_input"] = ex

        st.divider()
        st.info("📦 **Base de Dados:** SQLite em memória\n\n📊 **Tabelas:** `produtos`, `vendas`")

    # Cabeçalho Principal
    st.markdown("## 🧠 Smart SQL Copilot: Text-to-SQL Assistant")
    st.caption("Digite sua pergunta de negócios em português para gerar e rodar a consulta SQL instantaneamente.")

    # KPI Summary Cards no Topo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        total_prod = pd.read_sql_query("SELECT COUNT(*) as c FROM produtos", conn).iloc[0]["c"]
        st.metric("Total de Produtos", f"{total_prod} itens")
    with col2:
        val_estoque = pd.read_sql_query("SELECT SUM(preco * estoque) as v FROM produtos", conn).iloc[0]["v"]
        st.metric("Valor do Estoque", f"R$ {val_estoque:,.2f}")
    with col3:
        total_vendas = pd.read_sql_query("SELECT COUNT(*) as c FROM vendas", conn).iloc[0]["c"]
        st.metric("Total de Transações", f"{total_vendas} ordens")
    with col4:
        fat_total = pd.read_sql_query(
            "SELECT SUM(v.quantidade * p.preco) as f FROM vendas v JOIN produtos p ON v.produto_id = p.id",
            conn,
        ).iloc[0]["f"]
        st.metric("Receita Consolidada", f"R$ {fat_total:,.2f}")

    st.write("")

    # Abas da Aplicação
    tab_chat, tab_schema, tab_custom_sql = st.tabs(
        ["💬 Copilot (Text-to-SQL)", "📑 Dicionário & Tabelas", "💻 Terminal SQL Livre"]
    )

    # --------------------------------------------------------------------------
    # ABA 1: COPILOT TEXT-TO-SQL
    # --------------------------------------------------------------------------
    with tab_chat:
        st.markdown("### Faça sua pergunta analítica:")

        # Campo de entrada de texto
        default_val = st.session_state.get("user_query_input", "Qual o produto mais caro?")
        user_prompt = st.text_input(
            "Digite uma pergunta em linguagem natural:",
            value=default_val,
            placeholder="Ex: Qual o produto mais caro? / Faturamento por categoria...",
            label_visibility="collapsed",
        )

        btn_run = st.button("🚀 Gerar e Executar Consulta SQL", type="primary")

        if user_prompt and (btn_run or "user_query_input" in st.session_state):
            # Tradução e Execução
            sql_query, explanation = copilot.translate_to_sql(user_prompt)

            start_time = time.perf_counter()
            try:
                df_result = pd.read_sql_query(sql_query, conn)
                duration_ms = (time.perf_counter() - start_time) * 1000
                exec_success = True
            except Exception as e:
                exec_success = False
                error_msg = str(e)

            st.markdown("---")
            col_sql, col_info = st.columns([2, 1])

            with col_sql:
                st.markdown("#### 📝 Código SQL Gerado")
                st.code(sql_query, language="sql")

            with col_info:
                st.markdown("#### 🎯 Intenção Detectada")
                st.info(explanation)
                if exec_success:
                    st.success(f"⏱️ **Tempo de Execução:** {duration_ms:.2f} ms | **Linhas:** {len(df_result)}")

            st.markdown("#### 📊 Resultado da Consulta")
            if exec_success:
                if df_result.empty:
                    st.warning("A consulta não retornou nenhum registro com os filtros aplicados.")
                else:
                    st.dataframe(df_result, use_container_width=True, hide_index=True)

                    # Gráfico Dinâmico Automático
                    if len(df_result) > 1 and df_result.shape[1] >= 2:
                        cols = df_result.columns
                        numeric_cols = df_result.select_dtypes(include=["number"]).columns
                        text_cols = [c for c in cols if c not in numeric_cols]

                        if len(text_cols) > 0 and len(numeric_cols) > 0:
                            st.markdown("##### 📈 Visualização Gráfica")
                            chart_df = df_result.set_index(text_cols[0])[numeric_cols[0]]
                            st.bar_chart(chart_df)
            else:
                st.error(f"Erro na execução da consulta: {error_msg}")

    # --------------------------------------------------------------------------
    # ABA 2: SCHEMA E TABELAS BRUTAS
    # --------------------------------------------------------------------------
    with tab_schema:
        st.markdown("### 📚 Estrutura do Banco de Dados Relacional")

        col_schema1, col_schema2 = st.columns(2)
        with col_schema1:
            st.markdown("#### 🛒 Tabela `produtos`")
            df_prod_full = pd.read_sql_query("SELECT * FROM produtos", conn)
            st.dataframe(df_prod_full, use_container_width=True, hide_index=True)

        with col_schema2:
            st.markdown("#### 📦 Tabela `vendas`")
            df_vendas_full = pd.read_sql_query("SELECT * FROM vendas", conn)
            st.dataframe(df_vendas_full, use_container_width=True, hide_index=True)

    # --------------------------------------------------------------------------
    # ABA 3: CONSOLE SQL LIVRE
    # --------------------------------------------------------------------------
    with tab_custom_sql:
        st.markdown("### 💻 Console SQL Customizado (Modo Avançado)")
        st.caption("Escreva e execute consultas SQL livres diretamente no banco SQLite.")

        custom_sql = st.text_area(
            "Digite sua instrução SQL:",
            value="SELECT categoria, AVG(preco) AS preco_medio, COUNT(*) AS qtd FROM produtos GROUP BY categoria;",
            height=120,
        )

        if st.button("Executar SQL Customizado", type="secondary"):
            try:
                t0 = time.perf_counter()
                df_custom = pd.read_sql_query(custom_sql, conn)
                dt = (time.perf_counter() - t0) * 1000
                st.success(f"Consulta executada com sucesso em {dt:.2f} ms ({len(df_custom)} registros)")
                st.dataframe(df_custom, use_container_width=True, hide_index=True)
            except Exception as e:
                st.error(f"Erro de sintaxe ou execução SQL: {e}")


if __name__ == "__main__":
    main()
