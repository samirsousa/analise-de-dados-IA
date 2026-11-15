"""Módulo de Processamento e Análise de Sentimento de Avaliações de Clientes.

Realiza processamento em lote (batch) de reviews em linguagem natural,
classificando polaridade (Positivo, Neutro, Negativo), calculando índice de
satisfação do cliente (CSAT/NPS simplificado) e identificando automaticamente
os principais pontos de dor (pain points) operacionais.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd


@dataclass
class ReviewRecord:
    """Representação estruturada de uma avaliação de cliente."""

    review_id: str
    customer_name: str
    product_category: str
    text: str
    sentiment: str = "Neutro"
    score: float = 0.0
    detected_pain_point: Optional[str] = None


class SentimentPulseAnalyzer:
    """Motor léxico e contextual de análise de sentimento para reviews em português."""

    def __init__(self) -> None:
        # Léxico refinado de termos positivos e pesos
        self.positive_lexicon: Dict[str, float] = {
            "excelente": 2.2,
            "perfeito": 2.2,
            "perfeita": 2.2,
            "otimo": 2.0,
            "ótimo": 2.0,
            "otima": 2.0,
            "ótima": 2.0,
            "maravilhoso": 2.0,
            "maravilhosa": 2.0,
            "incrivel": 1.9,
            "incrível": 1.9,
            "adorei": 1.8,
            "amei": 1.8,
            "gostei": 1.4,
            "bom": 1.2,
            "boa": 1.2,
            "recomendo": 1.7,
            "qualidade": 1.5,
            "rapido": 1.4,
            "rápido": 1.4,
            "rapida": 1.4,
            "rápida": 1.4,
            "pontual": 1.4,
            "satisfeito": 1.6,
            "satisfeita": 1.6,
            "eficiente": 1.5,
            "top": 1.3,
            "impecavel": 2.0,
            "impecável": 2.0,
            "surpreendeu": 1.6,
            "facil": 1.2,
            "fácil": 1.2,
            "resistente": 1.4,
            "confortavel": 1.5,
            "confortável": 1.5,
            "bonito": 1.2,
            "bonita": 1.2,
            "lindo": 1.3,
            "linda": 1.3,
            "aprovado": 1.5,
            "aprovada": 1.5,
            "parabens": 1.6,
            "parabéns": 1.6,
            "potente": 1.4,
            "pratico": 1.3,
            "prático": 1.3,
            "melhor": 1.8,
        }

        # Léxico refinado de termos negativos e pesos
        self.negative_lexicon: Dict[str, float] = {
            "pessimo": -2.2,
            "péssimo": -2.2,
            "pessima": -2.2,
            "péssima": -2.2,
            "horrivel": -2.2,
            "horrível": -2.2,
            "ruim": -1.6,
            "defeito": -2.0,
            "quebrado": -2.2,
            "quebrada": -2.2,
            "quebrou": -2.0,
            "atraso": -1.8,
            "atrasou": -1.8,
            "demorou": -1.5,
            "demorado": -1.4,
            "demorada": -1.4,
            "lento": -1.4,
            "lenta": -1.4,
            "danificado": -2.0,
            "danificada": -2.0,
            "estragado": -2.0,
            "estragada": -2.0,
            "decepcao": -2.0,
            "decepção": -2.0,
            "frustrado": -1.8,
            "frustrada": -1.8,
            "arrependido": -1.7,
            "arrependida": -1.7,
            "trava": -1.6,
            "travando": -1.6,
            "inutil": -1.8,
            "inútil": -1.8,
            "grosseiro": -1.8,
            "descaso": -2.2,
            "vergonha": -2.0,
            "fragil": -1.5,
            "frágil": -1.5,
            "falha": -1.7,
            "falhou": -1.7,
            "fraco": -1.4,
            "fraca": -1.4,
            "caro": -1.3,
            "chiado": -1.4,
            "dificil": -1.2,
            "difícil": -1.2,
            "arranhado": -1.5,
            "arranhada": -1.5,
        }

        # Modificadores de contexto (inversores estritos de polaridade)
        self.negation_tokens: Set[str] = {
            "nao",
            "não",
            "nunca",
            "jamais",
            "nem",
            "tampouco",
        }

        # Intensificadores de magnitude
        self.intensifiers: Dict[str, float] = {
            "muito": 1.6,
            "bastante": 1.4,
            "extremamente": 1.9,
            "super": 1.6,
            "demais": 1.4,
            "completamente": 1.7,
            "totalmente": 1.7,
        }

        # Categorização analítica de Pontos de Dor (Pain Points)
        self.pain_point_categories: Dict[str, List[str]] = {
            "Logística & Atrasos de Entrega": [
                "atraso",
                "atrasou",
                "demorou",
                "demorado",
                "prazo",
                "entrega",
                "transportadora",
                "extravio",
                "nao chegou",
                "não chegou",
            ],
            "Defeito & Baixa Qualidade do Produto": [
                "defeito",
                "quebrado",
                "quebrada",
                "quebrou",
                "danificado",
                "estragado",
                "frágil",
                "fragil",
                "trava",
                "falhou",
                "falha",
                "chiado",
                "arranhada",
                "arranhado",
            ],
            "Mau Atendimento & Suporte Técnico": [
                "suporte",
                "atendente",
                "atendimento",
                "descaso",
                "grosseiro",
                "sem resposta",
                "sac",
                "chat",
                "lento e não",
            ],
            "Cobrança, Preço ou Reembolso": [
                "reembolso",
                "estorno",
                "caro",
                "cobrança",
                "devolucao",
                "devolução",
                "preço",
            ],
        }

    def _clean_text(self, text: str) -> str:
        """Limpa e normaliza o texto removendo pontuações e padronizando minúsculas."""
        # Substitui qualquer caractere não alfanumérico por espaço
        normalized = re.sub(r"[^\w\sáéíóúàâêôãõçÁÉÍÓÚÀÂÊÔÃÕÇ]", " ", text.lower())
        # Trata expressões de exceção (ex: "sem fio" não deve inverter polaridade)
        normalized = normalized.replace("sem fio", "wireless_feature")
        return normalized

    def analyze_text(self, text: str) -> Tuple[str, float, Optional[str]]:
        """Avalia a polaridade e identifica se há ponto de dor em um review.

        Args:
            text: Conteúdo textual da avaliação.

        Returns:
            Tuple[str, float, Optional[str]]: (Sentimento, Score Normalizado, Ponto de Dor Identificado).
        """
        cleaned = self._clean_text(text)
        words = cleaned.split()

        total_score = 0.0
        negate_window = 0
        current_multiplier = 1.0

        for word in words:
            # Verifica se a palavra é um intensificador
            if word in self.intensifiers:
                current_multiplier = self.intensifiers[word]
                continue

            # Verifica se é token de negação estrito
            if word in self.negation_tokens:
                negate_window = 2  # Aplica inversão para até as próximas 2 palavras
                continue

            # Avalia termos positivos
            if word in self.positive_lexicon:
                val = self.positive_lexicon[word] * current_multiplier
                if negate_window > 0:
                    total_score -= val * 1.2  # Inversão com penalidade
                    negate_window = 0
                else:
                    total_score += val
                current_multiplier = 1.0
                continue

            # Avalia termos negativos
            if word in self.negative_lexicon:
                val = abs(self.negative_lexicon[word]) * current_multiplier
                if negate_window > 0:
                    total_score += val * 0.8  # Negação de termo negativo (ex: "não quebrou")
                    negate_window = 0
                else:
                    total_score -= val
                current_multiplier = 1.0
                continue

            # Palavra neutra decrementa a janela de negação
            if negate_window > 0:
                negate_window -= 1

        # Classificação estrita com limiares equilibrados
        if total_score >= 1.0:
            sentiment = "Positivo"
        elif total_score <= -1.0:
            sentiment = "Negativo"
        else:
            sentiment = "Neutro"

        # Identificação de Pontos de Dor (apenas para avaliações não-positivas)
        detected_pain = None
        if sentiment in ("Negativo", "Neutro"):
            for category, triggers in self.pain_point_categories.items():
                for trigger in triggers:
                    if trigger in cleaned:
                        detected_pain = category
                        break
                if detected_pain:
                    break

        return sentiment, round(total_score, 2), detected_pain

    def process_batch(self, reviews: List[Dict[str, str]]) -> pd.DataFrame:
        """Processa em lote uma coleção de reviews e consolida em DataFrame.

        Args:
            reviews: Lista de dicionários contendo os dados dos clientes e textos.

        Returns:
            pd.DataFrame: DataFrame contendo a classificação de cada review.
        """
        records: List[Dict[str, object]] = []

        for item in reviews:
            sentiment, score, pain_point = self.analyze_text(item["text"])
            records.append(
                {
                    "review_id": item["id"],
                    "customer": item["customer"],
                    "category": item["category"],
                    "text": item["text"],
                    "sentiment": sentiment,
                    "score": score,
                    "pain_point": pain_point,
                }
            )

        return pd.DataFrame(records)


def get_sample_reviews() -> List[Dict[str, str]]:
    """Fornece um conjunto embutido e realista de 20 avaliações de clientes."""
    return [
        {
            "id": "REV-001",
            "customer": "Mariana Souza",
            "category": "Informática",
            "text": "O notebook gamer é simplesmente excelente e muito rápido! Superou todas as minhas expectativas, recomendo demais.",
        },
        {
            "id": "REV-002",
            "customer": "Carlos Alberto",
            "category": "Eletrônicos",
            "text": "Péssima experiência! O produto chegou com a tela quebrada e com defeito grave. Solicito estorno imediato.",
        },
        {
            "id": "REV-003",
            "customer": "Fernanda Lima",
            "category": "Móveis",
            "text": "A cadeira ergonômica é boa e confortável, porém o manual de montagem é um pouco confuso. No geral, ok.",
        },
        {
            "id": "REV-004",
            "customer": "Rodrigo Mendes",
            "category": "Acessórios",
            "text": "O mouse sem fio é ótimo, bateria dura bastante e acabamento impecável. Chegou antes do prazo!",
        },
        {
            "id": "REV-005",
            "customer": "Juliana Castro",
            "category": "Informática",
            "text": "Horrível! Grande atraso na entrega, demorou mais de 25 dias e a transportadora não atualizava o rastreio.",
        },
        {
            "id": "REV-006",
            "customer": "Lucas Ferreira",
            "category": "Eletrônicos",
            "text": "O monitor atende ao básico para trabalhar com planilhas. Nada de extraordinário, produto mediano.",
        },
        {
            "id": "REV-007",
            "customer": "Patrícia Alves",
            "category": "Acessórios",
            "text": "Não recomendo! O teclado mecânico não funcionou direito, fica dando falha de tecla e o suporte técnico teve descaso total.",
        },
        {
            "id": "REV-008",
            "customer": "Bruno Martins",
            "category": "Móveis",
            "text": "Mesa com regulagem de altura perfeita! Muito resistente, bonita e de altíssima qualidade. Parabéns à loja!",
        },
        {
            "id": "REV-009",
            "customer": "Camila Ribeiro",
            "category": "Informática",
            "text": "SSD rápido, entrega pontual e bem embalado. Tudo 100% conforme o anúncio.",
        },
        {
            "id": "REV-010",
            "customer": "Eduardo Santos",
            "category": "Eletrônicos",
            "text": "O fone de ouvido é caro pelo que entrega. O cancelamento de ruído é fraco e não gostei do acabamento.",
        },
        {
            "id": "REV-011",
            "customer": "Beatriz Rocha",
            "category": "Acessórios",
            "text": "Hub USB muito prático e compacto. Funcionou de primeira no meu Macbook, compra aprovada.",
        },
        {
            "id": "REV-012",
            "customer": "Gabriel Nogueira",
            "category": "Informática",
            "text": "A placa de vídeo esquenta muito e trava em jogos pesados. Estou bastante frustrado com o defeito.",
        },
        {
            "id": "REV-013",
            "customer": "Aline Moreira",
            "category": "Móveis",
            "text": "Gaveteiro bonito, mas a fechadura veio arranhada. Como não interfere no uso diário, decidi não pedir devolução.",
        },
        {
            "id": "REV-014",
            "customer": "Rafael Vieira",
            "category": "Eletrônicos",
            "text": "Som da caixa bluetooth potente e bateria duradoura! Adorei a qualidade sonora e a facilidade de conexão.",
        },
        {
            "id": "REV-015",
            "customer": "Tatiane Cunha",
            "category": "Acessórios",
            "text": "Suporte articulado rígido e difícil de ajustar. Atendimento do SAC foi lento e não resolveu minha dúvida.",
        },
        {
            "id": "REV-016",
            "customer": "Marcelo Dias",
            "category": "Informática",
            "text": "Memória RAM instalada e reconhecida com perfeição. Desempenho do computador melhorou muito.",
        },
        {
            "id": "REV-017",
            "customer": "Vanessa Barbosa",
            "category": "Eletrônicos",
            "text": "Smartwatch bonito, porém as notificações demoram para sincronizar. Funciona razoavelmente bem.",
        },
        {
            "id": "REV-018",
            "customer": "Felipe Cardoso",
            "category": "Móveis",
            "text": "Cadeira confortável, entrega rápida e ótimo custo-benefício. Recomendo para quem trabalha em home office.",
        },
        {
            "id": "REV-019",
            "customer": "Isabela Pires",
            "category": "Acessórios",
            "text": "Câmera webcam com imagem de baixa resolução e chiado no microfone. Decepção pelo valor cobrado.",
        },
        {
            "id": "REV-020",
            "customer": "Thiago Borges",
            "category": "Informática",
            "text": "Notebook ultra leve e bateria excelente. Melhor compra do ano, qualidade impecável!",
        },
    ]


def format_executive_report(df: pd.DataFrame) -> str:
    """Gera um relatório executivo consolidado com métricas de satisfação e pontos de dor."""
    total_reviews = len(df)
    sentiment_counts = df["sentiment"].value_counts()

    pos_count = int(sentiment_counts.get("Positivo", 0))
    neu_count = int(sentiment_counts.get("Neutro", 0))
    neg_count = int(sentiment_counts.get("Negativo", 0))

    pos_pct = (pos_count / total_reviews) * 100
    neu_pct = (neu_count / total_reviews) * 100
    neg_pct = (neg_count / total_reviews) * 100

    # Net Sentiment Score (Índice Líquido de Sentimento: % Positivos - % Negativos)
    net_sentiment_score = pos_pct - neg_pct

    # Extração e ranking dos pontos de dor
    pain_points = df[df["pain_point"].notna()]["pain_point"].value_counts()

    lines: List[str] = [
        "======================================================================",
        "📊 RELATÓRIO EXECUTIVO - NLP SENTIMENT PULSE",
        "======================================================================",
        f"• Total de Avaliações Processadas : {total_reviews}",
        f"• Taxa de Satisfação (Positivos)  : {pos_pct:.1f}% ({pos_count} avaliações)",
        f"• Avaliações Neutras / Indiferentes: {neu_pct:.1f}% ({neu_count} avaliações)",
        f"• Taxa de Insatisfação (Negativos): {neg_pct:.1f}% ({neg_count} avaliações)",
        f"• Net Sentiment Score (NSS)       : {net_sentiment_score:+.1f} pts (Escala de -100 a +100)",
        "----------------------------------------------------------------------",
        "🔍 DISTRIBUIÇÃO DE SENTIMENTOS POR CATEGORIA DE PRODUTO:",
        "----------------------------------------------------------------------",
    ]

    pivot = pd.crosstab(
        df["category"], df["sentiment"], normalize="index"
    ) * 100

    for cat, row in pivot.iterrows():
        p = row.get("Positivo", 0.0)
        n = row.get("Neutro", 0.0)
        neg = row.get("Negativo", 0.0)
        lines.append(
            f"   {cat:<14} -> Positivos: {p:5.1f}% | Neutros: {n:5.1f}% | Negativos: {neg:5.1f}%"
        )

    lines.extend([
        "----------------------------------------------------------------------",
        "⚠️  PRINCIPAIS PONTOS DE DOR IDENTIFICADOS (OFENSORES OPERACIONAIS):",
        "----------------------------------------------------------------------",
    ])

    if not pain_points.empty:
        for idx, (pain, count) in enumerate(pain_points.items(), start=1):
            pct = (count / total_reviews) * 100
            lines.append(
                f"   {idx}. {pain:<38} -> {count:2d} ocorrências ({pct:.1f}% do total de reviews)"
            )
    else:
        lines.append("   Nenhum ponto de dor crítico detectado na amostra.")

    lines.extend([
        "----------------------------------------------------------------------",
        "💡 RECOMENDAÇÕES ESTRATÉGICAS DE CUSTOMER EXPERIENCE (CX):",
        "----------------------------------------------------------------------",
        "   1. QUALIDADE & TESTES: Reforçar controle de qualidade de componentes e",
        "      periféricos sensíveis (telas e placas) para evitar produtos danificados.",
        "   2. LOGÍSTICA & SLA: Alinhar SLAs com transportadoras para mitigar atrasos",
        "      e fornecer código de rastreamento com notificações ativas via WhatsApp/SMS.",
        "   3. CAPACITAÇÃO DO SAC: Treinar equipe de suporte técnico para tratamento",
        "      ágil e resolutivo de reclamações, evitando sensação de descaso.",
        "======================================================================",
    ])

    return "\n".join(lines)


def main() -> None:
    """Execução principal do analisador de sentimentos."""
    base_dir = Path(__file__).resolve().parent

    print("=" * 70)
    print("🚀 INICIANDO NLP SENTIMENT PULSE - PROCESSAMENTO EM LOTE DE REVIEWS")
    print("=" * 70)
    print(f"📁 Diretório de Trabalho: {base_dir.name}\n")

    analyzer = SentimentPulseAnalyzer()
    raw_reviews = get_sample_reviews()

    print(f"⚙️  Processando {len(raw_reviews)} avaliações de clientes...")
    df_results = analyzer.process_batch(raw_reviews)

    # Exibe amostra das avaliações classificadas no terminal
    print("\n📋 AMOSTRA DE REVIEWS PROCESSADOS (PRIMEIROS 5 REGISTROS):")
    for _, row in df_results.head(5).iterrows():
        icon = (
            "🟢"
            if row["sentiment"] == "Positivo"
            else "🔴"
            if row["sentiment"] == "Negativo"
            else "🟡"
        )
        print(
            f"   [{row['review_id']}] {icon} {row['sentiment']:<8} (Score: {row['score']:+4.1f}) "
            f"| {row['customer']:<16} | \"{row['text'][:65]}...\""
        )

    # Gera e exibe o relatório executivo estruturado
    report_text = format_executive_report(df_results)
    print("\n" + report_text + "\n")

    # Exporta tabela consolidada em CSV e Markdown para auditoria
    csv_output = base_dir / "sentiment_analysis_results.csv"
    df_results.to_csv(csv_output, index=False, encoding="utf-8")
    print(f"💾 Resultados tabulares salvos em: {csv_output.name}")

    report_output = base_dir / "sentiment_summary.md"
    report_output.write_text(report_text, encoding="utf-8")
    print(f"📄 Resumo executivo exportado para: {report_output.name}")
    print("=" * 70)


if __name__ == "__main__":
    main()
