"""Financial Anomaly Detector - Detecção de Fraudes e Transações Suspeitas.

Módulo em Python (Pandas e Scikit-Learn) que simula fluxos transacionais bancários,
injeta anomalias deliberadas e utiliza o algoritmo não-supervisionado Isolation Forest
para identificar, isolar e classificar o risco de transações atípicas.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class AnomalyAuditSummary:
    """Consolida as métricas da auditoria transacional."""

    total_transactions: int
    anomalies_detected: int
    anomaly_rate_pct: float
    total_anomalous_volume: float
    highest_risk_txn_id: str
    highest_risk_value: float


class FinancialAnomalyDetector:
    """Motor de detecção de fraudes e transações financeiras anômalas."""

    def __init__(self, contamination: float = 0.035, random_state: int = 42) -> None:
        """Inicializa o detector com taxa estimada de contaminação e semente.

        Args:
            contamination: Proporção esperada de anomalias no conjunto de dados (default: 3.5%).
            random_state: Semente para reprodutibilidade dos splits da árvore.
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=150,
            max_samples="auto",
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.df: pd.DataFrame = pd.DataFrame()
        self.feature_columns: List[str] = [
            "valor",
            "hora_dia",
            "is_madrugada",
            "distancia_origem_km",
        ]

    def generate_synthetic_transactions(
        self, n_normal: int = 970, n_anomalies: int = 30
    ) -> pd.DataFrame:
        """Gera um fluxo de transações contendo operações legítimas e outliers intencionais.

        Args:
            n_normal: Número de transações bancárias normais e corriqueiras.
            n_anomalies: Número de transações atípicas/fraudulentas injetadas.

        Returns:
            pd.DataFrame: Conjunto transacional estruturado.
        """
        rng = np.random.default_rng(seed=self.random_state)
        records: List[Dict[str, object]] = []
        base_time = datetime(2026, 11, 1, 0, 0, 0)

        # ----------------------------------------------------------------------
        # 1. TRANSAÇÕES NORMAIS (Comportamento Típico de Clientes)
        # ----------------------------------------------------------------------
        cidades_padrao = ["São Paulo", "Rio de Janeiro", "Curitiba", "Belo Horizonte", "Porto Alegre"]
        categorias_normais = ["Supermercado", "Alimentação", "Farmácia", "Combustível", "Streaming"]

        for i in range(1, n_normal + 1):
            txn_id = f"TXN-{1000 + i}"
            # Horários predominantemente comerciais (07h às 22h)
            hora = int(rng.choice(np.arange(7, 23), p=[0.03, 0.05, 0.08, 0.10, 0.10, 0.10, 0.08, 0.08, 0.08, 0.08, 0.08, 0.05, 0.04, 0.03, 0.01, 0.01]))
            minuto = int(rng.integers(0, 60))
            delta_dias = int(rng.integers(0, 15))
            dt = base_time + timedelta(days=delta_dias, hours=hora, minutes=minuto)

            # Valores típicos (R$ 15,00 a R$ 450,00 com média em R$ 120,00)
            valor = float(np.round(rng.exponential(scale=95.0) + 15.0, 2))
            if valor > 1200.0:
                valor = 480.0  # Limita cauda normal

            cidade = str(rng.choice(cidades_padrao))
            distancia_km = float(np.round(rng.uniform(0.5, 45.0), 1))
            categoria = str(rng.choice(categorias_normais))

            records.append({
                "transaction_id": txn_id,
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "hora_dia": hora,
                "is_madrugada": 1 if hora < 6 else 0,
                "valor": valor,
                "localidade": cidade,
                "distancia_origem_km": distancia_km,
                "categoria": categoria,
                "is_synthetic_outlier": 0,
                "anomaly_type": "Legítima",
            })

        # ----------------------------------------------------------------------
        # 2. OUTLIERS DELIBERADOS (Cenários Críticos de Fraude e Anomalia)
        # ----------------------------------------------------------------------
        outlier_scenarios = [
            # Cenário A: Pix de valor exorbitante na madrugada
            {"val_range": (15000.0, 48000.0), "hora_range": (1, 4), "dist_range": (10.0, 80.0), "cat": "Transferência Pix Imediata", "desc": "Alto valor em horário de madrugada (Madrugada/Pix)", "loc": "São Paulo"},
            # Cenário B: Compra de luxo com salto brusco em joalheria
            {"val_range": (28000.0, 65000.0), "hora_range": (14, 19), "dist_range": (5.0, 50.0), "cat": "Joalheria & Artigos de Luxo", "desc": "Ticket ultra elevado fora do perfil de consumo", "loc": "Rio de Janeiro"},
            # Cenário C: Transação remota / internacional repentina
            {"val_range": (8500.0, 29000.0), "hora_range": (2, 5), "dist_range": (2500.0, 9500.0), "cat": "Serviços Digitais Internacionais", "desc": "Disparidade geográfica extrema (Distância > 2500km)", "loc": "Kyiv / Ilhas Cayman"},
            # Cenário D: Saque em espécie atípico em caixa eletrônico
            {"val_range": (7000.0, 15000.0), "hora_range": (3, 5), "dist_range": (250.0, 800.0), "cat": "Saque em Espécie 24h", "desc": "Saque de alto valor na madrugada em local distante", "loc": "Fronteira Seca"},
        ]

        for j in range(1, n_anomalies + 1):
            txn_id = f"TXN-OUT-{2000 + j}"
            scen = rng.choice(outlier_scenarios)
            hora = int(rng.integers(scen["hora_range"][0], scen["hora_range"][1] + 1))
            minuto = int(rng.integers(0, 60))
            delta_dias = int(rng.integers(0, 15))
            dt = base_time + timedelta(days=delta_dias, hours=hora, minutes=minuto)

            valor = float(np.round(rng.uniform(scen["val_range"][0], scen["val_range"][1]), 2))
            distancia_km = float(np.round(rng.uniform(scen["dist_range"][0], scen["dist_range"][1]), 1))

            records.append({
                "transaction_id": txn_id,
                "timestamp": dt.strftime("%Y-%m-%d %H:%M:%S"),
                "hora_dia": hora,
                "is_madrugada": 1 if hora < 6 else 0,
                "valor": valor,
                "localidade": scen["loc"],
                "distancia_origem_km": distancia_km,
                "categoria": scen["cat"],
                "is_synthetic_outlier": 1,
                "anomaly_type": scen["desc"],
            })

        df = pd.DataFrame(records)
        # Embaralha as linhas para simular fluxo cronológico realista
        self.df = df.sample(frac=1.0, random_state=self.random_state).reset_index(drop=True)
        return self.df

    def train_and_detect(self) -> pd.DataFrame:
        """Treina o Isolation Forest e pontua a probabilidade de anomalia."""
        if self.df.empty:
            self.generate_synthetic_transactions()

        # Extração e pré-processamento das features numéricas
        X = self.df[self.feature_columns].copy()

        # Treinamento do Isolation Forest
        self.model.fit(X)

        # 1. Anomaly Score bruto do Scikit-Learn:
        # Valores negativos indicam anomalias severas; valores positivos indicam registros normais
        raw_scores = self.model.decision_function(X)

        # 2. Predição binária: -1 = Anomalia, 1 = Normal
        predictions = self.model.predict(X)

        self.df["raw_anomaly_score"] = raw_scores
        # Converte para uma métrica legível de Risco (0 a 100)
        # Quanto mais negativo o raw_score, mais próximo de 100% de risco
        min_s, max_s = raw_scores.min(), raw_scores.max()
        risk_score = 100.0 * (1.0 - (raw_scores - min_s) / (max_s - min_s + 1e-9))
        self.df["risk_score"] = np.round(risk_score, 1)

        self.df["is_anomaly"] = (predictions == -1).astype(int)

        # Classificação do nível de severidade
        def classify_risk(row: pd.Series) -> str:
            if row["is_anomaly"] == 1:
                if row["risk_score"] >= 80.0 or row["valor"] >= 15000.0:
                    return "CRÍTICO"
                elif row["risk_score"] >= 65.0:
                    return "ALTO"
                else:
                    return "MÉDIO"
            return "NORMAL"

        self.df["risk_level"] = self.df.apply(classify_risk, axis=1)

        # Diagnóstico analítico do motivo da suspeita
        def generate_suspicion_reason(row: pd.Series) -> str:
            if row["is_anomaly"] == 0:
                return "Transação dentro dos padrões usuais de consumo."
            reasons = []
            if row["valor"] >= 5000.0:
                reasons.append(f"Valor atípico (R$ {row['valor']:,.2f})")
            if row["is_madrugada"] == 1:
                reasons.append(f"Horário de risco ({row['hora_dia']:02d}h)")
            if row["distancia_origem_km"] > 500.0:
                reasons.append(f"Localidade distante ({row['distancia_origem_km']:.0f}km)")
            if not reasons:
                reasons.append("Padrão multidimensional divergente do cluster usual")
            return " + ".join(reasons)

        self.df["motivo_suspeita"] = self.df.apply(generate_suspicion_reason, axis=1)

        return self.df

    def get_audit_summary(self) -> AnomalyAuditSummary:
        """Gera o sumário executivo dos resultados da detecção."""
        total = len(self.df)
        anomalies_df = self.df[self.df["is_anomaly"] == 1]
        count_anomalies = len(anomalies_df)
        pct = (count_anomalies / total) * 100.0 if total > 0 else 0.0
        total_vol = float(anomalies_df["valor"].sum())

        if not anomalies_df.empty:
            highest_risk = anomalies_df.sort_values(by="risk_score", ascending=False).iloc[0]
            max_id = str(highest_risk["transaction_id"])
            max_val = float(highest_risk["valor"])
        else:
            max_id, max_val = "N/A", 0.0

        return AnomalyAuditSummary(
            total_transactions=total,
            anomalies_detected=count_anomalies,
            anomaly_rate_pct=round(pct, 2),
            total_anomalous_volume=round(total_vol, 2),
            highest_risk_txn_id=max_id,
            highest_risk_value=max_val,
        )

    def print_terminal_report(self, top_n: int = 10) -> None:
        """Imprime no terminal um relatório estruturado e corporativo das transações suspeitas."""
        summary = self.get_audit_summary()
        anomalies_df = self.df[self.df["is_anomaly"] == 1].sort_values(
            by=["risk_score", "valor"], ascending=[False, False]
        )

        print("\n" + "=" * 105)
        print("🚨 RELATÓRIO DE AUDITORIA TRANSACIONAL - DETECÇÃO DE FRAUDES E ANOMALIAS")
        print("=" * 105)
        print(f"• Total de Transações Auditadas   : {summary.total_transactions:,}")
        print(f"• Transações Suspeitas Isoladas   : {summary.anomalies_detected} ocorrências ({summary.anomaly_rate_pct:.1f}% do fluxo)")
        print(f"• Volume Financeiro sob Risco     : R$ {summary.total_anomalous_volume:,.2f}")
        print(f"• Transação de Maior Risco        : {summary.highest_risk_txn_id} (Valor: R$ {summary.highest_risk_value:,.2f})")
        print(f"• Modelo Utilizado                : Isolation Forest (Contaminação Calibrada: {self.contamination * 100:.1f}%)")
        print("-" * 105)
        print(f"📋 TOP {min(top_n, len(anomalies_df))} TRANSAÇÕES SUSPEITAS IDENTIFICADAS PELO MODELO:")
        print("-" * 105)

        # Cabeçalho da tabela
        header = (
            f"{'ID Transação':<13} | {'Data/Hora':<19} | {'Valor (R$)':<12} | "
            f"{'Risco':<8} | {'Score':<6} | {'Categoria / Motivo do Alerta'}"
        )
        print(header)
        print("-" * 105)

        for _, row in anomalies_df.head(top_n).iterrows():
            badge = "🔴" if row["risk_level"] == "CRÍTICO" else "🟠" if row["risk_level"] == "ALTO" else "🟡"
            valor_fmt = f"R$ {row['valor']:>9,.2f}"
            score_fmt = f"{row['risk_score']:>5.1f}"
            print(
                f"{row['transaction_id']:<13} | {row['timestamp']:<19} | {valor_fmt} | "
                f"{badge} {row['risk_level']:<6} | {score_fmt} | {row['categoria']} -> {row['motivo_suspeita']}"
            )

        print("=" * 105)
        print("💡 PLANO DE AÇÃO IMEDIATO PARA COMPLIANCE & SEGURANÇA BANCÁRIA:")
        print("   1. BLOQUEIO PREVENTIVO: Suspender liquidação das transações marcadas com Risco CRÍTICO.")
        print("   2. ETAPA STEP-UP DE AUTENTICAÇÃO: Solicitar validação biométrica/MFA para transferências de madrugada.")
        print("   3. NOTIFICAÇÃO PUSH: Enviar alerta urgente para o cliente confirmar a legitimidade da compra.")
        print("=" * 105 + "\n")


def main() -> None:
    """Execução principal do detector de anomalias financeiras."""
    base_dir = Path(__file__).resolve().parent

    print("🚀 INICIANDO FINANCIAL ANOMALY DETECTOR...")
    print(f"📁 Diretório de Execução: {base_dir.name}")

    detector = FinancialAnomalyDetector(contamination=0.035, random_state=42)

    # 1. Geração de base sintética com outliers intencionais
    detector.generate_synthetic_transactions(n_normal=970, n_anomalies=30)

    # 2. Treinamento e Isolamento não supervisionado
    detector.train_and_detect()

    # 3. Exibição do relatório no terminal
    detector.print_terminal_report(top_n=10)

    # 4. Exportação das transações suspeitas e base completa
    output_anomalies_file = base_dir / "transacoes_suspeitas_detectadas.csv"
    anomalies_only = detector.df[detector.df["is_anomaly"] == 1].sort_values(
        by="risk_score", ascending=False
    )
    anomalies_only.to_csv(output_anomalies_file, index=False, encoding="utf-8")
    print(f"💾 Transações suspeitas salvas para auditoria em: {output_anomalies_file.name}")

    output_full_file = base_dir / "historico_transacoes_completo.csv"
    detector.df.to_csv(output_full_file, index=False, encoding="utf-8")
    print(f"💾 Base consolidada com scores exportada para: {output_full_file.name}")
    print("=" * 105)


if __name__ == "__main__":
    main()
