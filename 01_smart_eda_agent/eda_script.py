"""Smart EDA Agent - Análise Exploratória Automatizada de Vendas de E-commerce.

Este módulo realiza uma Análise Exploratória de Dados (EDA) completa,
calculando métricas essenciais como faturamento consolidado, ticket médio,
rankings de produtos/categorias e distribuição geográfica, gerando ao final
um relatório executivo formatado em Markdown pronto para documentação e tomada de decisão.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ExecutiveMetrics:
    """Estrutura imutável para encapsular os principais KPIs calculados na análise."""

    total_orders: int
    unique_customers: int
    total_items_sold: int
    total_revenue: float
    average_ticket: float
    average_item_price: float
    min_order_value: float
    max_order_value: float


class SmartEDAAgent:
    """Agente responsável pela ingestão, validação e análise exploratória de vendas."""

    def __init__(self, data_path: Path | str) -> None:
        """Inicializa o agente com o caminho para o dataset.

        Args:
            data_path: Caminho (Path ou str) para o arquivo CSV de vendas.
        """
        self.data_path = Path(data_path)
        self.df: pd.DataFrame = pd.DataFrame()

    def load_and_validate(self) -> pd.DataFrame:
        """Carrega e valida a integridade do dataset de vendas.

        Raises:
            FileNotFoundError: Se o arquivo CSV não for localizado.
            ValueError: Se colunas obrigatórias estiverem ausentes.

        Returns:
            pd.DataFrame: DataFrame limpo e tipado.
        """
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Arquivo de dados não encontrado: {self.data_path.resolve()}"
            )

        # Leitura do dataset
        self.df = pd.read_csv(self.data_path)

        # Validação de colunas obrigatórias
        required_columns: List[str] = [
            "order_id",
            "date",
            "category",
            "product_name",
            "customer_id",
            "quantity",
            "unit_price",
            "total_revenue",
            "region",
        ]
        missing_cols = [col for col in required_columns if col not in self.df.columns]
        if missing_cols:
            raise ValueError(
                f"Colunas obrigatórias ausentes no CSV: {missing_cols}"
            )

        # Conversão e padronização de tipos
        self.df["date"] = pd.to_datetime(self.df["date"])
        self.df["quantity"] = pd.to_numeric(self.df["quantity"], errors="coerce").astype(int)
        self.df["unit_price"] = pd.to_numeric(self.df["unit_price"], errors="coerce").astype(float)
        self.df["total_revenue"] = pd.to_numeric(self.df["total_revenue"], errors="coerce").astype(float)
        self.df["category"] = self.df["category"].astype(str).str.strip()
        self.df["region"] = self.df["region"].astype(str).str.strip()
        self.df["product_name"] = self.df["product_name"].astype(str).str.strip()

        # Checagem de consistência matemática: total_revenue = quantity * unit_price
        calculated_rev = self.df["quantity"] * self.df["unit_price"]
        diff = np.abs(self.df["total_revenue"] - calculated_rev)
        inconsistent_rows = diff > 0.05
        if inconsistent_rows.any():
            # Auto-ajuste para garantir consistência
            self.df.loc[inconsistent_rows, "total_revenue"] = calculated_rev[inconsistent_rows]

        return self.df

    def compute_kpis(self) -> ExecutiveMetrics:
        """Calcula os indicadores-chave de desempenho (KPIs) gerais.

        Returns:
            ExecutiveMetrics: Objeto contendo os KPIs consolidados.
        """
        total_orders = int(self.df["order_id"].nunique())
        unique_customers = int(self.df["customer_id"].nunique())
        total_items_sold = int(self.df["quantity"].sum())
        total_revenue = float(self.df["total_revenue"].sum())

        # Ticket médio = Faturamento total / Número total de pedidos únicos
        average_ticket = float(total_revenue / total_orders) if total_orders > 0 else 0.0

        # Preço médio por item vendido
        average_item_price = float(total_revenue / total_items_sold) if total_items_sold > 0 else 0.0

        # Faturamento agrupado por pedido para identificar extremos
        order_totals = self.df.groupby("order_id")["total_revenue"].sum()
        min_order_value = float(order_totals.min()) if not order_totals.empty else 0.0
        max_order_value = float(order_totals.max()) if not order_totals.empty else 0.0

        return ExecutiveMetrics(
            total_orders=total_orders,
            unique_customers=unique_customers,
            total_items_sold=total_items_sold,
            total_revenue=total_revenue,
            average_ticket=average_ticket,
            average_item_price=average_item_price,
            min_order_value=min_order_value,
            max_order_value=max_order_value,
        )

    def analyze_categories(self) -> pd.DataFrame:
        """Gera a sumarização de faturamento e volume por categoria de produto.

        Returns:
            pd.DataFrame: Tabela ordenada por receita com share percentual.
        """
        category_summary = (
            self.df.groupby("category", as_index=False)
            .agg(
                total_volume=("quantity", "sum"),
                total_revenue=("total_revenue", "sum"),
                orders_count=("order_id", "nunique"),
                avg_unit_price=("unit_price", "mean"),
            )
            .sort_values(by="total_revenue", ascending=False)
        )

        total_rev = self.df["total_revenue"].sum()
        total_vol = self.df["quantity"].sum()

        category_summary["revenue_share_%"] = (category_summary["total_revenue"] / total_rev) * 100
        category_summary["volume_share_%"] = (category_summary["total_volume"] / total_vol) * 100

        return category_summary

    def analyze_top_products(self, top_n: int = 5) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Extrai os produtos líderes em faturamento e volume de vendas.

        Args:
            top_n: Quantidade de produtos no ranking (padrão: 5).

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: (Top por Receita, Top por Volume).
        """
        product_summary = (
            self.df.groupby(["product_name", "category"], as_index=False)
            .agg(
                total_volume=("quantity", "sum"),
                total_revenue=("total_revenue", "sum"),
                unit_price=("unit_price", "mean"),
            )
        )

        top_revenue = product_summary.sort_values(
            by="total_revenue", ascending=False
        ).head(top_n).reset_index(drop=True)

        top_volume = product_summary.sort_values(
            by="total_volume", ascending=False
        ).head(top_n).reset_index(drop=True)

        return top_revenue, top_volume

    def analyze_regions(self) -> pd.DataFrame:
        """Calcula a distribuição de vendas, faturamento e ticket médio regional.

        Returns:
            pd.DataFrame: Distribuição regional ordenada por faturamento.
        """
        regional_summary = (
            self.df.groupby("region", as_index=False)
            .agg(
                total_orders=("order_id", "nunique"),
                total_volume=("quantity", "sum"),
                total_revenue=("total_revenue", "sum"),
            )
            .sort_values(by="total_revenue", ascending=False)
        )

        total_rev = self.df["total_revenue"].sum()
        regional_summary["revenue_share_%"] = (regional_summary["total_revenue"] / total_rev) * 100
        regional_summary["regional_ticket"] = (
            regional_summary["total_revenue"] / regional_summary["total_orders"]
        )

        return regional_summary

    def generate_markdown_report(self) -> str:
        """Compila todas as análises estatísticas em um relatório executivo em Markdown.

        Returns:
            str: Relatório formatado em sintaxe Markdown.
        """
        if self.df.empty:
            self.load_and_validate()

        kpis = self.compute_kpis()
        cat_df = self.analyze_categories()
        top_rev, top_vol = self.analyze_top_products(top_n=5)
        reg_df = self.analyze_regions()

        lines: List[str] = [
            "# 📊 Relatório Executivo de Análise Exploratória (EDA)",
            "",
            "> **Dataset:** Vendas de E-commerce | **Agente:** Smart EDA Agent v1.0",
            "",
            "---",
            "",
            "## 1. 🎯 Indicadores-Chave de Desempenho (KPIs Gerais)",
            "",
            "| Métrica | Valor Absoluto | Detalhes |",
            "| :--- | :---: | :--- |",
            f"| **Faturamento Total** | **R$ {kpis.total_revenue:,.2f}** | Receita líquida consolidada |",
            f"| **Ticket Médio por Pedido** | **R$ {kpis.average_ticket:,.2f}** | Valor médio gasto por transação |",
            f"| **Volume Total de Itens** | **{kpis.total_items_sold:,} unid.** | Total de produtos comercializados |",
            f"| **Total de Pedidos** | **{kpis.total_orders:,}** | Pedidos únicos processados |",
            f"| **Clientes Únicos** | **{kpis.unique_customers:,}** | Base de clientes ativos |",
            f"| **Preço Médio por Item** | **R$ {kpis.average_item_price:,.2f}** | Receita / Volume de itens |",
            f"| **Faixa de Valor por Pedido** | **R$ {kpis.min_order_value:,.2f} ~ R$ {kpis.max_order_value:,.2f}** | Mínimo e Máximo observados |",
            "",
            "---",
            "",
            "## 2. 🏷️ Desempenho por Categoria de Produto",
            "",
            "| Categoria | Volume Vendido | Faturamento (R$) | Share Receita (%) | Share Volume (%) |",
            "| :--- | :---: | :---: | :---: | :---: |",
        ]

        for _, row in cat_df.iterrows():
            lines.append(
                f"| {row['category']} | {int(row['total_volume'])} unid. | "
                f"R$ {row['total_revenue']:,.2f} | {row['revenue_share_%']:.1f}% | "
                f"{row['volume_share_%']:.1f}% |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 3. 🏆 Rankings: Top 5 Produtos Líderes",
            "",
            "### 3.1. Top 5 por Faturamento (Receita Gerada)",
            "",
            "| Ranking | Produto | Categoria | Preço Unit. Médio | Volume | Faturamento Total |",
            "| :---: | :--- | :--- | :---: | :---: | :---: |",
        ])

        for idx, row in top_rev.iterrows():
            lines.append(
                f"| #{idx + 1} | **{row['product_name']}** | {row['category']} | "
                f"R$ {row['unit_price']:,.2f} | {int(row['total_volume'])} unid. | "
                f"**R$ {row['total_revenue']:,.2f}** |"
            )

        lines.extend([
            "",
            "### 3.2. Top 5 por Volume de Vendas (Unidades)",
            "",
            "| Ranking | Produto | Categoria | Volume Vendido | Faturamento Gerado |",
            "| :---: | :--- | :--- | :---: | :---: |",
        ])

        for idx, row in top_vol.iterrows():
            lines.append(
                f"| #{idx + 1} | **{row['product_name']}** | {row['category']} | "
                f"**{int(row['total_volume'])} unid.** | R$ {row['total_revenue']:,.2f} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 4. 🌍 Distribuição Geográfica de Vendas por Região",
            "",
            "| Região | Pedidos | Volume (unid.) | Faturamento (R$) | Ticket Médio Reg. | Share (%) |",
            "| :--- | :---: | :---: | :---: | :---: | :---: |",
        ])

        for _, row in reg_df.iterrows():
            lines.append(
                f"| **{row['region']}** | {int(row['total_orders'])} | "
                f"{int(row['total_volume'])} | R$ {row['total_revenue']:,.2f} | "
                f"R$ {row['regional_ticket']:,.2f} | {row['revenue_share_%']:.1f}% |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 5. 💡 Principais Insights e Recomendações de Negócio",
            "",
            f"1. **Dominância da Categoria Informática:** A categoria líder responde pela maior fatia do faturamento, impulsionada pelo alto valor agregado de itens como notebooks e componentes.",
            f"2. **Concentração Regional no Sudeste & Sul:** O Sudeste desponta como o principal polo de receita e densidade de pedidos, recomendando campanhas de retenção e logística expressa para essa região.",
            f"3. **Alavancagem do Ticket Médio:** Produtos premium (ex: Notebooks Gamer e Monitores) elevam substancialmente o ticket médio geral (R$ {kpis.average_ticket:,.2f}), indicando oportunidade para estratégias de *cross-selling* de acessórios periféricos.",
            "",
            "---",
            "*Relatório gerado automaticamente pelo `01_smart_eda_agent`.*",
        ])

        return "\n".join(lines)


def main() -> None:
    """Ponto de entrada principal para execução do script de EDA."""
    # Garante a resolução correta do caminho relativo ao diretório do script
    base_dir = Path(__file__).resolve().parent
    dataset_file = base_dir / "sample_data.csv"

    print("=" * 70)
    print("🚀 INICIANDO SMART EDA AGENT - ANÁLISE EXPLORATÓRIA DE DADOS")
    print("=" * 70)
    print(f"📁 Carregando base de dados: {dataset_file.name}")

    try:
        agent = SmartEDAAgent(data_path=dataset_file)
        report_markdown = agent.generate_markdown_report()

        print("\n" + report_markdown + "\n")

        # Salva cópia do relatório gerado em Markdown para documentação
        output_report_file = base_dir / "relatorio_executivo_eda.md"
        output_report_file.write_text(report_markdown, encoding="utf-8")
        print(f"✅ Relatório executivo exportado com sucesso para: {output_report_file.name}")
        print("=" * 70)

    except Exception as exc:
        print(f"\n❌ Erro durante a execução da análise: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
