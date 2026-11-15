"""Customer Segmentation RFM - Segmentação Estratégica de Clientes via K-Means.

Módulo em Python (Pandas e Scikit-Learn) que simula o histórico transacional de e-commerce,
calcula as métricas de Recência, Frequência e Valor Monetário (RFM), aplica pré-processamento
com transformação logarítmica e padronização, e agrupa a base de clientes em clusters
estratégicos utilizando o algoritmo K-Means.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class RFMClusterProfile:
    """Perfil consolidado de um cluster estratégico de clientes."""

    cluster_id: int
    segment_name: str
    customer_count: int
    customer_share_pct: float
    avg_recency_days: float
    avg_frequency_orders: float
    avg_monetary_val: float
    total_revenue: float
    revenue_share_pct: float
    strategic_action: str


class CustomerSegmentationRFM:
    """Motor de análise RFM e clusterização não-supervisionada de clientes."""

    def __init__(self, n_clusters: int = 4, random_state: int = 42) -> None:
        """Inicializa o motor com quantidade de clusters e semente.

        Args:
            n_clusters: Número de clusters a serem criados (default: 4).
            random_state: Semente para reprodutibilidade dos centróides do K-Means.
        """
        self.n_clusters = n_clusters
        self.random_state = random_state
        self.orders_df: pd.DataFrame = pd.DataFrame()
        self.rfm_df: pd.DataFrame = pd.DataFrame()
        self.kmeans_model: KMeans | None = None
        self.scaler = StandardScaler()

    def generate_synthetic_orders(
        self, n_customers: int = 400, n_orders: int = 2200, ref_date: str = "2026-11-15"
    ) -> pd.DataFrame:
        """Gera histórico realista de transações de e-commerce ao longo de 12 meses.

        Args:
            n_customers: Total de clientes únicos simulados.
            n_orders: Volume total de pedidos transacionados.
            ref_date: Data de corte para o cálculo de recência (AAAA-MM-DD).

        Returns:
            pd.DataFrame: Tabela de pedidos sintéticos.
        """
        rng = np.random.default_rng(seed=self.random_state)
        reference_dt = datetime.strptime(ref_date, "%Y-%m-%d")

        # Define 4 perfis arquetípicos de clientes para garantir heterogeneidade natural
        customer_ids = [f"CUST-{1000 + i}" for i in range(1, n_customers + 1)]
        records: List[Dict[str, object]] = []

        n_vip = int(n_customers * 0.15)
        n_loyal = int(n_customers * 0.35)
        n_new = int(n_customers * 0.20)
        n_at_risk = n_customers - (n_vip + n_loyal + n_new)

        cust_archetypes = (
            [("VIP", c) for c in customer_ids[:n_vip]]
            + [("Loyal", c) for c in customer_ids[n_vip : n_vip + n_loyal]]
            + [("New", c) for c in customer_ids[n_vip + n_loyal : n_vip + n_loyal + n_new]]
            + [("AtRisk", c) for c in customer_ids[n_vip + n_loyal + n_new :]]
        )

        order_counter = 10001
        for arch, cid in cust_archetypes:
            if arch == "VIP":
                num_orders = int(rng.integers(7, 16))
                for _ in range(num_orders):
                    days_ago = int(rng.integers(1, 15))
                    dt = reference_dt - timedelta(days=days_ago)
                    val = float(np.round(rng.uniform(450.0, 2200.0), 2))
                    records.append({
                        "order_id": f"ORD-{order_counter}",
                        "customer_id": cid,
                        "order_date": dt.strftime("%Y-%m-%d"),
                        "order_value": val,
                    })
                    order_counter += 1

            elif arch == "Loyal":
                num_orders = int(rng.integers(4, 9))
                for _ in range(num_orders):
                    days_ago = int(rng.integers(10, 60))
                    dt = reference_dt - timedelta(days=days_ago)
                    val = float(np.round(rng.uniform(180.0, 750.0), 2))
                    records.append({
                        "order_id": f"ORD-{order_counter}",
                        "customer_id": cid,
                        "order_date": dt.strftime("%Y-%m-%d"),
                        "order_value": val,
                    })
                    order_counter += 1

            elif arch == "New":
                num_orders = int(rng.integers(1, 3))
                for _ in range(num_orders):
                    days_ago = int(rng.integers(1, 20))
                    dt = reference_dt - timedelta(days=days_ago)
                    val = float(np.round(rng.uniform(120.0, 600.0), 2))
                    records.append({
                        "order_id": f"ORD-{order_counter}",
                        "customer_id": cid,
                        "order_date": dt.strftime("%Y-%m-%d"),
                        "order_value": val,
                    })
                    order_counter += 1

            else:  # AtRisk / Dormentes
                num_orders = int(rng.integers(1, 5))
                for _ in range(num_orders):
                    days_ago = int(rng.integers(100, 350))
                    dt = reference_dt - timedelta(days=days_ago)
                    val = float(np.round(rng.uniform(90.0, 480.0), 2))
                    records.append({
                        "order_id": f"ORD-{order_counter}",
                        "customer_id": cid,
                        "order_date": dt.strftime("%Y-%m-%d"),
                        "order_value": val,
                    })
                    order_counter += 1

        df = pd.DataFrame(records)
        df["order_date"] = pd.to_datetime(df["order_date"])
        self.orders_df = df
        return self.orders_df

    def compute_rfm_metrics(self, ref_date: str = "2026-11-15") -> pd.DataFrame:
        """Calcula as métricas clássicas de Recência, Frequência e Valor Monetário.

        Args:
            ref_date: Data de corte temporal.

        Returns:
            pd.DataFrame: Tabela de clientes com colunas R, F e M calculadas.
        """
        if self.orders_df.empty:
            self.generate_synthetic_orders(ref_date=ref_date)

        ref_dt = pd.to_datetime(ref_date)

        rfm = (
            self.orders_df.groupby("customer_id")
            .agg(
                data_ultima_compra=("order_date", "max"),
                frequencia=("order_id", "nunique"),
                monetario=("order_value", "sum"),
            )
            .reset_index()
        )

        # Recência em dias = Data de Referência - Data do Último Pedido
        rfm["recencia"] = (ref_dt - rfm["data_ultima_compra"]).dt.days
        rfm["ticket_medio"] = (rfm["monetario"] / rfm["frequencia"]).round(2)
        rfm["monetario"] = rfm["monetario"].round(2)

        self.rfm_df = rfm
        return self.rfm_df

    def fit_clusters(self) -> pd.DataFrame:
        """Aplica transformação de escala e ajusta o K-Means para segmentação."""
        if self.rfm_df.empty:
            self.compute_rfm_metrics()

        # 1. Transformação logarítmica para atenuar assimetria positiva de cauda longa (skewness)
        rfm_log = pd.DataFrame({
            "recencia_log": np.log1p(self.rfm_df["recencia"]),
            "frequencia_log": np.log1p(self.rfm_df["frequencia"]),
            "monetario_log": np.log1p(self.rfm_df["monetario"]),
        })

        # 2. Padronização (StandardScaler: Média 0, Desvio Padrão 1)
        X_scaled = self.scaler.fit_transform(rfm_log)

        # 3. Treinamento do K-Means
        self.kmeans_model = KMeans(
            n_clusters=self.n_clusters,
            init="k-means++",
            n_init=10,
            max_iter=300,
            random_state=self.random_state,
        )
        cluster_labels = self.kmeans_model.fit_predict(X_scaled)
        self.rfm_df["cluster_raw"] = cluster_labels

        # 4. Rotulação semântica inteligente dos clusters avaliando os centróides reais
        cluster_stats = self.rfm_df.groupby("cluster_raw").agg({
            "recencia": "mean",
            "frequencia": "mean",
            "monetario": "mean",
        })

        segment_names_map: Dict[int, str] = {}
        for cid, row in cluster_stats.iterrows():
            r = row["recencia"]
            f = row["frequencia"]
            m = row["monetario"]

            if r >= 90.0:
                segment_names_map[int(cid)] = "⚠️ Clientes em Risco / Dormentes"
            elif m >= 6000.0 and f >= 8.0:
                segment_names_map[int(cid)] = "⭐ Clientes VIP (Campeões)"
            elif f >= 3.5:
                segment_names_map[int(cid)] = "💎 Clientes Fiéis (Recorrentes)"
            else:
                segment_names_map[int(cid)] = "🌱 Clientes Novos / Recentes"

        self.rfm_df["segmento"] = self.rfm_df["cluster_raw"].map(segment_names_map)
        return self.rfm_df

    def get_cluster_profiles(self) -> List[RFMClusterProfile]:
        """Extrai os perfis analíticos e ações estratégicas de cada cluster."""
        if "segmento" not in self.rfm_df.columns:
            self.fit_clusters()

        total_customers = len(self.rfm_df)
        total_rev = float(self.rfm_df["monetario"].sum())

        strategic_playbook = {
            "⭐ Clientes VIP (Campeões)": (
                "Tratamento exclusivo (Concierge/White-Glove), programas de fidelidade premium, "
                "acesso antecipado a lançamentos e recompensas personalizadas."
            ),
            "💎 Clientes Fiéis (Recorrentes)": (
                "Campanhas de Cross-Selling e Up-Selling de itens complementares, ofertas de combos "
                "e incentivos para aumentar o ticket médio por pedido."
            ),
            "🌱 Clientes Novos / Recentes": (
                "Comunicação de onboarding com guias de uso, cupons de incentivo para 2ª compra "
                "em até 20 dias e pesquisas curtas de satisfação pós-primeiro pedido."
            ),
            "⚠️ Clientes em Risco / Dormentes": (
                "Campanhas agressivas de Win-back (reativação) com descontos exclusivos de retorno, "
                "pesquisas para identificar motivos de abandono e canais de suporte ativo."
            ),
        }

        profiles: List[RFMClusterProfile] = []
        grouped = self.rfm_df.groupby(["cluster_raw", "segmento"]).agg(
            count=("customer_id", "count"),
            avg_r=("recencia", "mean"),
            avg_f=("frequencia", "mean"),
            avg_m=("monetario", "mean"),
            sum_m=("monetario", "sum"),
        ).reset_index()

        # Ordena pelo maior volume de receita total
        grouped = grouped.sort_values(by="sum_m", ascending=False)

        for _, row in grouped.iterrows():
            c_name = str(row["segmento"])
            cnt = int(row["count"])
            revenue = float(row["sum_m"])
            profiles.append(
                RFMClusterProfile(
                    cluster_id=int(row["cluster_raw"]),
                    segment_name=c_name,
                    customer_count=cnt,
                    customer_share_pct=round((cnt / total_customers) * 100, 1),
                    avg_recency_days=round(float(row["avg_r"]), 1),
                    avg_frequency_orders=round(float(row["avg_f"]), 1),
                    avg_monetary_val=round(float(row["avg_m"]), 2),
                    total_revenue=round(revenue, 2),
                    revenue_share_pct=round((revenue / total_rev) * 100, 1),
                    strategic_action=strategic_playbook.get(c_name, "Ações direcionadas por canal."),
                )
            )

        return profiles

    def print_terminal_summary(self) -> None:
        """Exibe no terminal o resumo executivo alinhado e o plano de ação estratégico."""
        profiles = self.get_cluster_profiles()
        total_cust = len(self.rfm_df)
        total_rev = float(self.rfm_df["monetario"].sum())
        avg_rec = float(self.rfm_df["recencia"].mean())
        avg_freq = float(self.rfm_df["frequencia"].mean())

        print("\n" + "=" * 95)
        print("🎯 RELATÓRIO EXECUTIVO - SEGMENTAÇÃO DE CLIENTES VIA RFM & K-MEANS")
        print("=" * 95)
        print(f"• Base Total de Clientes Analisada : {total_cust} clientes únicos")
        print(f"• Faturamento Total Auditado       : R$ {total_rev:,.2f}")
        print(f"• Recência Média da Base          : {avg_rec:.1f} dias")
        print(f"• Frequência Média de Compras     : {avg_freq:.1f} pedidos por cliente")
        print(f"• Algoritmo de Agrupamento         : K-Means (k={self.n_clusters} clusters com K-Means++)")
        print("-" * 95)
        print("📊 MATRIZ COMPARATIVA DE CLUSTERS ESTRATÉGICOS:")
        print("-" * 95)

        header = (
            f"{'Segmento Estratégico':<32} | {'Clientes':<12} | "
            f"{'Recência':<11} | {'Frequência':<12} | {'Ticket Médio':<14} | {'Share Rec.'}"
        )
        print(header)
        print("-" * 95)

        for p in profiles:
            cli_str = f"{p.customer_count} ({p.customer_share_pct:.1f}%)"
            rec_str = f"{p.avg_recency_days:.0f} dias"
            freq_str = f"{p.avg_frequency_orders:.1f} ped."
            ticket_str = f"R$ {p.avg_monetary_val:,.2f}"
            share_str = f"{p.revenue_share_pct:>5.1f}%"
            print(
                f"{p.segment_name:<32} | {cli_str:<12} | {rec_str:<11} | "
                f"{freq_str:<12} | {ticket_str:<14} | {share_str}"
            )

        print("=" * 95)
        print("💡 PLAYBOOK DE MARKETING & AÇÕES ESTRATÉGICAS RECOMENDADAS:")
        print("=" * 95)

        for idx, p in enumerate(profiles, start=1):
            print(f"{idx}. {p.segment_name} -> Faturamento: R$ {p.total_revenue:,.2f} ({p.revenue_share_pct:.1f}%)")
            print(f"   ▶ Ação Recomendada: {p.strategic_action}\n")

        print("=" * 95 + "\n")


def main() -> None:
    """Ponto de entrada do script de análise RFM."""
    base_dir = Path(__file__).resolve().parent

    print("🚀 INICIANDO CUSTOMER SEGMENTATION RFM...")
    print(f"📁 Diretório de Trabalho: {base_dir.name}\n")

    engine = CustomerSegmentationRFM(n_clusters=4, random_state=42)

    # 1. Simulação de histórico de pedidos
    engine.generate_synthetic_orders(n_customers=400, n_orders=2200, ref_date="2026-11-15")

    # 2. Cálculo das métricas RFM
    engine.compute_rfm_metrics(ref_date="2026-11-15")

    # 3. Treinamento e ajuste dos clusters K-Means
    engine.fit_clusters()

    # 4. Impressão do relatório executivo no terminal
    engine.print_terminal_summary()

    # 5. Exportação da base segmentada para CSV
    output_csv = base_dir / "clientes_segmentados_rfm.csv"
    engine.rfm_df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"💾 Base de clientes segmentada salva em: {output_csv.name}")

    output_orders = base_dir / "historico_pedidos_simulado.csv"
    engine.orders_df.to_csv(output_orders, index=False, encoding="utf-8")
    print(f"💾 Histórico de pedidos exportado para: {output_orders.name}")
    print("=" * 95)


if __name__ == "__main__":
    main()
