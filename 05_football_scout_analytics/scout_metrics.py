"""Football Scout Analytics - Motor de Avaliação Estatística e Eficiência de Atletas.

Módulo analítico em Python (Pandas e NumPy) para ingestão de dados de desempenho esportivo,
normalização métrica por 90 minutos (P90), cálculo do índice composto 'Scout Score'
e ranqueamento de atletas de alto rendimento.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ScoutWeights:
    """Pesos relativos dos pilares para o cálculo do Scout Score composto."""

    weight_offensive: float = 0.35   # Impacto ofensivo: gols, assistências, finalizações no alvo
    weight_passing: float = 0.25     # Construção: passes certos P90 e precisão de passes
    weight_defensive: float = 0.25   # Combate defensivo: desarmes e interceptações P90
    weight_security: float = 0.15    # Confiabilidade: penalização ponderada de erros capitais


class FootballScoutEngine:
    """Motor estatístico de scouting para normalização e ranqueamento de atletas."""

    def __init__(self, data_path: Path | str, weights: ScoutWeights | None = None) -> None:
        """Inicializa o motor com o caminho do dataset e parâmetros de ponderação.

        Args:
            data_path: Caminho para o arquivo CSV com dados de atletas.
            weights: Pesos dos pilares do índice (padrão: ScoutWeights default).
        """
        self.data_path = Path(data_path)
        self.weights = weights or ScoutWeights()
        self.df: pd.DataFrame = pd.DataFrame()

    def load_data(self) -> pd.DataFrame:
        """Carrega e valida a consistência estrutural do dataset de jogadores."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset não encontrado em: {self.data_path.resolve()}")

        self.df = pd.read_csv(self.data_path)

        required_cols = [
            "player_id", "nome", "posicao", "clube", "partidas", "minutos_jogados",
            "passes_certos", "passes_tentados", "desarmes", "interceptacoes",
            "finalizacoes", "finalizacoes_no_alvo", "gols", "assistencias", "erros_capitais"
        ]
        missing = [col for col in required_cols if col not in self.df.columns]
        if missing:
            raise ValueError(f"Colunas obrigatórias ausentes no dataset: {missing}")

        return self.df

    @staticmethod
    def _min_max_scale(series: pd.Series) -> pd.Series:
        """Aplica escala Min-Max em uma série numérica normalizando-a de 0 a 100."""
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(50.0, index=series.index)
        return ((series - min_val) / (max_val - min_val)) * 100.0

    def compute_advanced_metrics(self) -> pd.DataFrame:
        """Computa métricas avançadas normalizadas por 90 minutos de jogo (P90) e pilares."""
        if self.df.empty:
            self.load_data()

        df = self.df.copy()

        # Fator de conversão para minutos jogados (P90)
        p90_factor = df["minutos_jogados"] / 90.0

        # 1. Pilar Construção e Passe
        df["passes_certos_p90"] = df["passes_certos"] / p90_factor
        df["precisao_passe_pct"] = (df["passes_certos"] / df["passes_tentados"].replace(0, 1)) * 100.0
        score_volume_passe = self._min_max_scale(df["passes_certos_p90"])
        score_precisao_passe = self._min_max_scale(df["precisao_passe_pct"])
        df["pilar_passe"] = (score_volume_passe * 0.6) + (score_precisao_passe * 0.4)

        # 2. Pilar Defensivo (Desarmes + Interceptações P90)
        df["acoes_defensivas_totais"] = df["desarmes"] + df["interceptacoes"]
        df["defesa_p90"] = df["acoes_defensivas_totais"] / p90_factor
        df["pilar_defesa"] = self._min_max_scale(df["defesa_p90"])

        # 3. Pilar Ofensivo (Índice de Ameaça e Gols Gerados P90)
        # Ponderação: Gols (3.0x), Assistências (2.0x), Finalizações no alvo (1.0x)
        df["producao_ofensiva"] = (
            (df["gols"] * 3.0)
            + (df["assistencias"] * 2.0)
            + (df["finalizacoes_no_alvo"] * 1.0)
        )
        df["ofensivo_p90"] = df["producao_ofensiva"] / p90_factor
        df["pilar_ataque"] = self._min_max_scale(df["ofensivo_p90"])

        # 4. Pilar de Confiabilidade / Segurança (Menos erros = maior nota)
        df["erros_p90"] = df["erros_capitais"] / p90_factor
        # Inversão: menor taxa de erro resulta em maior pontuação
        score_erros_invertido = 100.0 - self._min_max_scale(df["erros_p90"])
        df["pilar_seguranca"] = score_erros_invertido

        # 5. Índice Composto Final (Scout Score) de 0 a 100
        df["scout_score"] = (
            (df["pilar_ataque"] * self.weights.weight_offensive)
            + (df["pilar_passe"] * self.weights.weight_passing)
            + (df["pilar_defesa"] * self.weights.weight_defensive)
            + (df["pilar_seguranca"] * self.weights.weight_security)
        ).round(2)

        # Ordenação descendente pelo Scout Score
        df = df.sort_values(by="scout_score", ascending=False).reset_index(drop=True)
        df["ranking"] = df.index + 1

        self.df = df
        return self.df

    def get_top_athletes(self, top_n: int = 5) -> pd.DataFrame:
        """Retorna os Top N atletas ranqueados com as principais colunas analíticas."""
        if "scout_score" not in self.df.columns:
            self.compute_advanced_metrics()

        display_cols = [
            "ranking",
            "nome",
            "posicao",
            "clube",
            "partidas",
            "gols",
            "assistencias",
            "desarmes",
            "precisao_passe_pct",
            "scout_score",
        ]
        return self.df[display_cols].head(top_n)

    def print_top_ranking(self, top_n: int = 5) -> None:
        """Formata e imprime o ranking dos atletas no terminal com design limpo."""
        top_df = self.get_top_athletes(top_n=top_n)

        print("\n" + "=" * 90)
        print("🏆 FOOTBALL SCOUT ANALYTICS - TOP 5 ATLETAS MAIS EFICIENTES (SCOUT SCORE)")
        print("=" * 90)

        # Cabeçalho da tabela formatada
        header = (
            f"{'Rk':<4} | {'Atleta':<19} | {'Posição':<15} | {'Clube':<14} | "
            f"{'Part.':<5} | {'Gols':<4} | {'Ass.':<4} | {'Des.':<4} | {'Pass%':<6} | {'Scout Score':<11}"
        )
        print(header)
        print("-" * 90)

        for _, row in top_df.iterrows():
            pos_label = row["posicao"]
            rk_str = f"#{int(row['ranking'])}"
            line = (
                f"{rk_str:<4} | {row['nome']:<19} | {pos_label:<15} | {row['clube']:<14} | "
                f"{int(row['partidas']):<5} | {int(row['gols']):<4} | {int(row['assistencias']):<4} | "
                f"{int(row['desarmes']):<4} | {row['precisao_passe_pct']:>5.1f}% | "
                f"{row['scout_score']:>9.2f} pts"
            )
            print(line)

        print("=" * 90)

        # Destaque do Atleta MVP
        mvp = top_df.iloc[0]
        print(f"⭐ MVP DO SCOUTING: {mvp['nome']} ({mvp['clube']} - {mvp['posicao']})")
        print(
            f"   • Eficiência Global: {mvp['scout_score']:.2f}/100 | "
            f"Gols: {int(mvp['gols'])} | Assistências: {int(mvp['assistencias'])} | "
            f"Precisão de Passe: {mvp['precisao_passe_pct']:.1f}%"
        )
        print("=" * 90 + "\n")


def main() -> None:
    """Ponto de entrada do script de scouting esportivo."""
    base_dir = Path(__file__).resolve().parent
    dataset_path = base_dir / "sample_players.csv"

    print("🚀 INICIANDO ANÁLISE DE SCOUTING ESPORTIVO...")
    print(f"📁 Base de dados: {dataset_path.name}")

    try:
        engine = FootballScoutEngine(data_path=dataset_path)
        engine.compute_advanced_metrics()
        engine.print_top_ranking(top_n=5)

        # Exporta ranking completo com métricas avançadas
        output_csv = base_dir / "scout_ranking_completo.csv"
        engine.df.to_csv(output_csv, index=False, encoding="utf-8")
        print(f"✅ Relatório completo de scouting exportado para: {output_csv.name}")

    except Exception as exc:
        print(f"❌ Erro durante o processamento de scouting: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
