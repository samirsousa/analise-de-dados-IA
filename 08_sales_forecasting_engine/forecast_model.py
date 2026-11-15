"""Sales Forecasting Engine - Modelagem e Projeção de Séries Temporais de Vendas.

Módulo em Python utilizando Pandas, NumPy e Plotly para modelagem estatística de
séries temporais de faturamento corporativo, cálculo de médias móveis, decomposição
de sazonalidade, projeção com intervalos de confiança e geração de dashboards
interativos exportados em HTML.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go


@dataclass(frozen=True)
class ForecastKPIs:
    """Consolida os principais indicadores da série temporal e projeção."""

    historical_months: int
    total_historical_revenue: float
    avg_monthly_historical: float
    last_actual_revenue: float
    forecast_horizon_months: int
    total_projected_revenue: float
    avg_monthly_projected: float
    projected_growth_pct: float


class SalesForecastingEngine:
    """Motor de cálculo estatístico e projeção preditiva de séries temporais."""

    def __init__(self, random_state: int = 42) -> None:
        self.random_state = random_state
        self.historical_df: pd.DataFrame = pd.DataFrame()
        self.forecast_df: pd.DataFrame = pd.DataFrame()

    def generate_historical_sales(
        self, start_date: str = "2024-01-01", n_months: int = 36
    ) -> pd.DataFrame:
        """Gera histórico realista de vendas mensais com tendência, sazonalidade e ruído.

        Args:
            start_date: Data do primeiro mês no formato AAAA-MM-DD.
            n_months: Quantidade de meses históricos a serem gerados (default: 36).

        Returns:
            pd.DataFrame: Série temporal histórica estruturada.
        """
        rng = np.random.default_rng(seed=self.random_state)
        dates = pd.date_range(start=start_date, periods=n_months, freq="MS")

        base_revenue = 180_000.0   # Faturamento base inicial (R$ 180k)
        trend_slope = 3_200.0      # Crescimento linear médio de R$ 3.200/mês

        # Fatores sazonais mensais (12 meses): pico em Nov/Dez, queda sazonal em Jan/Fev
        seasonal_multipliers = {
            1: 0.90,   # Janeiro (ressaca pós-festas)
            2: 0.88,   # Fevereiro (mês curto/Carnaval)
            3: 0.98,   # Março
            4: 1.00,   # Abril
            5: 1.05,   # Maio (Dia das Mães)
            6: 1.02,   # Junho (Dia dos Namorados)
            7: 1.01,   # Julho
            8: 1.04,   # Agosto (Dia dos Pais)
            9: 1.02,   # Setembro
            10: 1.06,  # Outubro
            11: 1.25,  # Novembro (Black Friday)
            12: 1.35,  # Dezembro (Natal e compras de fim de ano)
        }

        revenues: List[float] = []

        for i, dt in enumerate(dates):
            # Componente de tendência
            trend = base_revenue + (trend_slope * i)
            # Componente de sazonalidade multiplicativa
            seasonality = seasonal_multipliers[dt.month]
            # Ruído estocástico gaussiano (~3% de volatilidade)
            noise = rng.normal(loc=0.0, scale=0.035)

            actual_val = trend * seasonality * (1.0 + noise)
            revenues.append(round(actual_val, 2))

        df = pd.DataFrame({
            "ds": dates,
            "faturamento_real": revenues,
            "mes_ano": dates.strftime("%b/%Y"),
        })

        # Cálculo de Médias Móveis para suavização
        df["media_movel_3m"] = df["faturamento_real"].rolling(window=3).mean().round(2)
        df["media_movel_6m"] = df["faturamento_real"].rolling(window=6).mean().round(2)
        df["crescimento_mom_%"] = df["faturamento_real"].pct_change().mul(100).round(2)

        self.historical_df = df
        return self.historical_df

    def compute_forecast(self, horizon_months: int = 12) -> pd.DataFrame:
        """Modela e projeta os próximos meses utilizando tendência linear e sazonalidade.

        Args:
            horizon_months: Quantidade de meses futuros a projetar (default: 12).

        Returns:
            pd.DataFrame: DataFrame contendo a projeção central e intervalos de confiança.
        """
        if self.historical_df.empty:
            self.generate_historical_sales()

        df_hist = self.historical_df.copy()
        n = len(df_hist)

        # 1. Ajuste de Tendência Linear via Mínimos Quadrados Ordinários (OLS)
        x = np.arange(n)
        y = df_hist["faturamento_real"].values
        slope, intercept = np.polyfit(x, y, deg=1)

        # Cálculo dos resíduos para estimação da variância e intervalo de confiança
        fitted_trend = intercept + slope * x
        residuals = y - fitted_trend
        residual_std = float(np.std(residuals))

        # 2. Decomposição de Fatores Sazonais Empíricos da Série
        df_hist["mes"] = df_hist["ds"].dt.month
        df_hist["trend"] = fitted_trend
        df_hist["seasonal_ratio"] = df_hist["faturamento_real"] / df_hist["trend"]
        monthly_seasonality = df_hist.groupby("mes")["seasonal_ratio"].mean().to_dict()

        # 3. Projeção para o Horizonte Futuro
        last_date = df_hist["ds"].iloc[-1]
        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1), periods=horizon_months, freq="MS"
        )

        future_x = np.arange(n, n + horizon_months)
        forecast_trend = intercept + slope * future_x

        projected_values: List[float] = []
        lower_bounds: List[float] = []
        upper_bounds: List[float] = []

        # Fator crítico para intervalo de confiança a 95% (Z = 1.96)
        z_score = 1.96

        for i, dt in enumerate(future_dates):
            seas_factor = monthly_seasonality.get(dt.month, 1.0)
            y_hat = forecast_trend[i] * seas_factor

            # Incerteza aumenta com o tempo (função da distância do horizonte h)
            h = i + 1
            uncertainty_std = residual_std * np.sqrt(1.0 + (h / n))

            lower_ci = max(0.0, y_hat - (z_score * uncertainty_std))
            upper_ci = y_hat + (z_score * uncertainty_std)

            projected_values.append(round(y_hat, 2))
            lower_bounds.append(round(lower_ci, 2))
            upper_bounds.append(round(upper_ci, 2))

        df_proj = pd.DataFrame({
            "ds": future_dates,
            "faturamento_projetado": projected_values,
            "limite_inferior_95": lower_bounds,
            "limite_superior_95": upper_bounds,
            "mes_ano": future_dates.strftime("%b/%Y"),
        })

        self.forecast_df = df_proj
        return self.forecast_df

    def get_summary_kpis(self) -> ForecastKPIs:
        """Sintetiza as principais métricas de desempenho histórico e projetado."""
        hist_total = float(self.historical_df["faturamento_real"].sum())
        hist_avg = float(self.historical_df["faturamento_real"].mean())
        last_val = float(self.historical_df["faturamento_real"].iloc[-1])

        proj_total = float(self.forecast_df["faturamento_projetado"].sum())
        proj_avg = float(self.forecast_df["faturamento_projetado"].mean())

        # Crescimento comparativo: média projetada vs média dos últimos 12 meses históricos
        last_12m_avg = float(self.historical_df["faturamento_real"].tail(12).mean())
        growth_pct = ((proj_avg - last_12m_avg) / last_12m_avg) * 100.0

        return ForecastKPIs(
            historical_months=len(self.historical_df),
            total_historical_revenue=round(hist_total, 2),
            avg_monthly_historical=round(hist_avg, 2),
            last_actual_revenue=round(last_val, 2),
            forecast_horizon_months=len(self.forecast_df),
            total_projected_revenue=round(proj_total, 2),
            avg_monthly_projected=round(proj_avg, 2),
            projected_growth_pct=round(growth_pct, 2),
        )

    def generate_interactive_chart(self, output_html_path: Path | str) -> Path:
        """Renderiza e salva um gráfico interativo completo em Plotly no formato HTML."""
        if self.historical_df.empty or self.forecast_df.empty:
            self.compute_forecast()

        df_hist = self.historical_df
        df_proj = self.forecast_df
        output_file = Path(output_html_path)

        fig = go.Figure()

        # 1. Faixa de Intervalo de Confiança 95% (Sombreado preenchido)
        # Limite Superior
        fig.add_trace(
            go.Scatter(
                x=df_proj["ds"],
                y=df_proj["limite_superior_95"],
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip",
                name="Limite Superior",
            )
        )
        # Limite Inferior preenchendo até o superior
        fig.add_trace(
            go.Scatter(
                x=df_proj["ds"],
                y=df_proj["limite_inferior_95"],
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(34, 197, 94, 0.15)",  # Verde suave translúcido
                showlegend=True,
                name="Intervalo de Confiança (95%)",
                hoverinfo="skip",
            )
        )

        # 2. Histórico de Vendas Reais
        fig.add_trace(
            go.Scatter(
                x=df_hist["ds"],
                y=df_hist["faturamento_real"],
                mode="lines+markers",
                name="Faturamento Realizado",
                line=dict(color="#2563EB", width=3),  # Azul royal
                marker=dict(size=6, color="#1D4ED8"),
                hovertemplate="<b>Data:</b> %{x|%b/%Y}<br><b>Faturamento Real:</b> R$ %{y:,.2f}<extra></extra>",
            )
        )

        # 3. Média Móvel 3 Meses (Curto Prazo)
        fig.add_trace(
            go.Scatter(
                x=df_hist["ds"],
                y=df_hist["media_movel_3m"],
                mode="lines",
                name="Média Móvel (3 Meses)",
                line=dict(color="#F59E0B", width=2, dash="dash"),  # Laranja
                hovertemplate="<b>MM 3M:</b> R$ %{y:,.2f}<extra></extra>",
            )
        )

        # 4. Média Móvel 6 Meses (Médio Prazo)
        fig.add_trace(
            go.Scatter(
                x=df_hist["ds"],
                y=df_hist["media_movel_6m"],
                mode="lines",
                name="Média Móvel (6 Meses)",
                line=dict(color="#8B5CF6", width=2, dash="dot"),  # Roxo
                hovertemplate="<b>MM 6M:</b> R$ %{y:,.2f}<extra></extra>",
            )
        )

        # Ponto de conexão entre o último histórico e o primeiro projetado
        conn_x = [df_hist["ds"].iloc[-1], df_proj["ds"].iloc[0]]
        conn_y = [df_hist["faturamento_real"].iloc[-1], df_proj["faturamento_projetado"].iloc[0]]
        fig.add_trace(
            go.Scatter(
                x=conn_x,
                y=conn_y,
                mode="lines",
                line=dict(color="#10B981", width=2, dash="dot"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        # 5. Linha de Projeção / Forecast
        fig.add_trace(
            go.Scatter(
                x=df_proj["ds"],
                y=df_proj["faturamento_projetado"],
                mode="lines+markers",
                name="Projeção (Forecast)",
                line=dict(color="#10B981", width=3, dash="dash"),  # Verde esmeralda
                marker=dict(size=7, color="#047857", symbol="diamond"),
                hovertemplate=(
                    "<b>Data Projetada:</b> %{x|%b/%Y}<br>"
                    "<b>Previsão:</b> R$ %{y:,.2f}<br>"
                    "<extra></extra>"
                ),
            )
        )

        # Linha vertical separadora entre histórico e previsão
        split_date = df_hist["ds"].iloc[-1]
        fig.add_vline(
            x=split_date,
            line_width=2,
            line_dash="dash",
            line_color="#64748B",
            annotation_text="Início da Projeção",
            annotation_position="top left",
        )

        # Configuração do Layout Executivo
        fig.update_layout(
            title=dict(
                text="📈 <b>Painel Executivo de Projeção de Vendas & Séries Temporais</b><br><sup>Histórico Consolidado (36 Meses) vs Projeção Futura com Intervalo de Confiança (95%)</sup>",
                font=dict(size=19, color="#0F172A"),
                x=0.02,
                y=0.96,
            ),
            template="plotly_white",
            hovermode="x unified",
            xaxis=dict(
                title="Período Mensal",
                showgrid=True,
                gridcolor="#F1F5F9",
                rangeselector=dict(
                    buttons=[
                        dict(count=12, label="Últimos 12M", step="month", stepmode="backward"),
                        dict(count=24, label="Últimos 24M", step="month", stepmode="backward"),
                        dict(step="all", label="Ver Tudo"),
                    ]
                ),
                rangeslider=dict(visible=True),
                type="date",
            ),
            yaxis=dict(
                title="Faturamento Mensal (R$)",
                showgrid=True,
                gridcolor="#F1F5F9",
                tickprefix="R$ ",
                tickformat=",.0f",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1.0,
                bgcolor="rgba(255, 255, 255, 0.8)",
            ),
            margin=dict(l=60, r=40, t=110, b=60),
            height=650,
        )

        fig.write_html(str(output_file))
        return output_file

    def print_terminal_summary(self) -> None:
        """Exibe resumo estatístico estruturado no terminal com tabelas alinhadas."""
        kpis = self.get_summary_kpis()

        print("\n" + "=" * 90)
        print("📊 RELATÓRIO ESTATÍSTICO DE PROJEÇÃO DE VENDAS (SALES FORECAST)")
        print("=" * 90)
        print(f"• Histórico Analisado             : {kpis.historical_months} meses (Base consolidada)")
        print(f"• Faturamento Total Histórico     : R$ {kpis.total_historical_revenue:,.2f}")
        print(f"• Média Mensal Histórica          : R$ {kpis.avg_monthly_historical:,.2f}")
        print(f"• Último Faturamento Real         : R$ {kpis.last_actual_revenue:,.2f}")
        print("-" * 90)
        print(f"• Horizonte de Previsão           : {kpis.forecast_horizon_months} meses futuros")
        print(f"• Faturamento Total Projetado     : R$ {kpis.total_projected_revenue:,.2f}")
        print(f"• Média Mensal Projetada          : R$ {kpis.avg_monthly_projected:,.2f}")
        print(f"• Taxa de Crescimento Projetada   : {kpis.projected_growth_pct:+.2f}% (vs últimos 12 meses)")
        print("=" * 90)

        print("\n🗓️ TABELA DE PROJEÇÃO MENSAL DETALHADA COM INTERVALO DE CONFIANÇA (95%):")
        print("-" * 90)
        header = f"{'Mês/Ano':<10} | {'Previsão Central (R$)':<22} | {'Limite Inferior (R$)':<22} | {'Limite Superior (R$)':<22}"
        print(header)
        print("-" * 90)

        for _, row in self.forecast_df.iterrows():
            print(
                f"{row['mes_ano']:<10} | R$ {row['faturamento_projetado']:>18,.2f} | "
                f"R$ {row['limite_inferior_95']:>18,.2f} | R$ {row['limite_superior_95']:>18,.2f}"
            )

        print("=" * 90 + "\n")


def main() -> None:
    """Execução principal do modelo de projeção de vendas."""
    base_dir = Path(__file__).resolve().parent

    print("🚀 INICIANDO SALES FORECASTING ENGINE...")
    print(f"📁 Diretório de Trabalho: {base_dir.name}\n")

    engine = SalesForecastingEngine(random_state=42)

    # 1. Geração de 36 meses históricos de vendas
    engine.generate_historical_sales(start_date="2024-01-01", n_months=36)

    # 2. Projeção dos próximos 12 meses
    engine.compute_forecast(horizon_months=12)

    # 3. Impressão do resumo estatístico no terminal
    engine.print_terminal_summary()

    # 4. Geração e salvamento do gráfico interativo Plotly em HTML
    chart_file = base_dir / "sales_forecast_interactive.html"
    engine.generate_interactive_chart(chart_file)
    print(f"🌐 Gráfico interativo salvo com sucesso em: {chart_file.name}")

    # 5. Exportação da base histórica e projetada em CSV
    output_csv = base_dir / "sales_timeseries_dataset.csv"
    combined_df = pd.concat(
        [
            engine.historical_df[["ds", "faturamento_real", "media_movel_3m", "media_movel_6m"]],
            engine.forecast_df[["ds", "faturamento_projetado", "limite_inferior_95", "limite_superior_95"]],
        ],
        axis=0,
        ignore_index=True,
    )
    combined_df.to_csv(output_csv, index=False, encoding="utf-8")
    print(f"💾 Base consolidada (histórico + forecast) salva em: {output_csv.name}")
    print("=" * 90)


if __name__ == "__main__":
    main()
