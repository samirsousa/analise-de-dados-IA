"""Módulo de Treinamento do Modelo de Previsão de Churn.

Gera dados sintéticos com padrões realistas de clientes de telecom/SaaS,
constrói um pipeline de pré-processamento e classificação com Scikit-Learn,
avalia a performance do modelo e persiste o artefato final para produção.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def generate_synthetic_data(
    n_samples: int = 2500, random_state: int = 42
) -> pd.DataFrame:
    """Gera um conjunto de dados sintético e consistente de comportamento de clientes.

    Regras de negócio simuladas para probabilidade de churn:
    - Menor tempo de contrato e maior idade aumentam o risco.
    - Alto volume de chamados de suporte técnico é forte preditor de insatisfação.
    - Uso mensal elevado reduz a probabilidade de cancelamento (maior engajamento).

    Args:
        n_samples: Quantidade de instâncias a serem geradas (padrão: 2500).
        random_state: Semente para reprodutibilidade estocástica.

    Returns:
        pd.DataFrame: DataFrame contendo as features e a coluna alvo 'churn'.
    """
    rng = np.random.default_rng(seed=random_state)

    # 1. Idade do cliente (distribuição entre 18 e 75 anos)
    idade = rng.integers(18, 76, size=n_samples)

    # 2. Tempo de contrato em meses (1 a 72 meses)
    tempo_contrato = rng.integers(1, 73, size=n_samples)

    # 3. Uso mensal do serviço (horas ou gigabytes consumidos, de 10 a 500)
    uso_mensal = np.round(rng.uniform(10.0, 500.0, size=n_samples), 2)

    # 4. Chamados abertos no suporte técnico (0 a 10 chamados)
    # Distribuição com cauda mais pesada para 0 a 3 chamados
    chamados_suporte = rng.choice(
        np.arange(0, 11),
        size=n_samples,
        p=[0.30, 0.25, 0.15, 0.10, 0.08, 0.05, 0.03, 0.02, 0.01, 0.005, 0.005],
    )

    # Construção de um score linear ponderado (Log-Odds) com ruído gaussiano
    # coeficientes calibrados para simular comportamento mercadológico
    log_odds = (
        -1.50
        + 0.025 * (idade - 40)
        - 0.055 * (tempo_contrato - 24)
        - 0.004 * (uso_mensal - 200)
        + 0.550 * chamados_suporte
        + rng.normal(0, 0.5, size=n_samples)
    )

    # Função Sigmóide para converter log_odds em probabilidade real
    probabilidade_churn = 1.0 / (1.0 + np.exp(-log_odds))

    # Binarização estocástica com base na probabilidade
    churn = (rng.uniform(0, 1, size=n_samples) < probabilidade_churn).astype(int)

    df = pd.DataFrame(
        {
            "idade": idade,
            "tempo_contrato": tempo_contrato,
            "uso_mensal": uso_mensal,
            "chamados_suporte": chamados_suporte,
            "churn": churn,
        }
    )

    return df


def build_and_train_pipeline(
    X_train: pd.DataFrame, y_train: pd.Series
) -> Pipeline:
    """Cria e ajusta um pipeline de Machine Learning (Scaler + RandomForest).

    Args:
        X_train: Matriz de features de treino.
        y_train: Vetor alvo de treino.

    Returns:
        Pipeline: Pipeline Scikit-Learn treinado e calibrado.
    """
    pipeline = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=120,
                    max_depth=7,
                    min_samples_split=6,
                    random_state=42,
                    class_weight="balanced",
                    n_jobs=-1,
                ),
            ),
        ]
    )

    pipeline.fit(X_train, y_train)
    return pipeline


def evaluate_model(
    pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series
) -> Dict[str, float]:
    """Avalia o modelo nas partições de teste e imprime métricas detalhadas.

    Args:
        pipeline: Pipeline treinado.
        X_test: Dados de teste.
        y_test: Rótulos reais de teste.

    Returns:
        Dict[str, float]: Dicionário com os indicadores de performance calculados.
    """
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred, zero_division=0))
    rec = float(recall_score(y_test, y_pred, zero_division=0))
    f1 = float(f1_score(y_test, y_pred, zero_division=0))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    cm = confusion_matrix(y_test, y_pred)

    print("=" * 70)
    print("🎯 RELATÓRIO DE AVALIAÇÃO DO MODELO DE CHURN")
    print("=" * 70)
    print(f"• Acurácia Global : {acc * 100:.2f}%")
    print(f"• F1-Score        : {f1 * 100:.2f}%")
    print(f"• Precisão        : {prec * 100:.2f}%")
    print(f"• Recall (Revoc.) : {rec * 100:.2f}%")
    print(f"• ROC AUC         : {roc_auc * 100:.2f}%")
    print("-" * 70)
    print("📊 Matriz de Confusão:")
    print(f"   [Verdadeiros Negativos (Fiel)]: {cm[0, 0]:4d} | [Falsos Positivos]: {cm[0, 1]:4d}")
    print(f"   [Falsos Negativos]:            {cm[1, 0]:4d} | [Verdadeiros Positivos (Churn)]: {cm[1, 1]:4d}")
    print("-" * 70)
    print("📋 Relatório Detalhado de Classificação:")
    print(classification_report(y_test, y_pred, target_names=["Fiel (0)", "Churn (1)"]))
    print("=" * 70)

    # Exibição da importância das features
    rf_model: RandomForestClassifier = pipeline.named_steps["classifier"]
    feature_names = list(X_test.columns)
    importances = rf_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]

    print("🔍 Importância Relativa das Features no Modelo:")
    for rank, idx in enumerate(sorted_idx, start=1):
        print(f"   {rank}. {feature_names[idx]:<18}: {importances[idx] * 100:.2f}%")
    print("=" * 70)

    return {
        "accuracy": acc,
        "f1_score": f1,
        "precision": prec,
        "recall": rec,
        "roc_auc": roc_auc,
    }


def train_and_export_model(
    output_dir: Path | str | None = None,
) -> Tuple[Pipeline, Dict[str, float]]:
    """Fluxo orquestrado de ponta a ponta: geração de dados, treino, avaliação e salvamento.

    Args:
        output_dir: Diretório onde o modelo e o dataset serão salvos.

    Returns:
        Tuple[Pipeline, Dict[str, float]]: Pipeline treinado e dicionário de métricas.
    """
    if output_dir is None:
        target_dir = Path(__file__).resolve().parent
    else:
        target_dir = Path(output_dir)

    target_dir.mkdir(parents=True, exist_ok=True)
    model_path = target_dir / "churn_model.joblib"
    csv_path = target_dir / "synthetic_customer_data.csv"

    print("⚙️  Gerando base sintética de clientes (2.500 registros)...")
    df = generate_synthetic_data(n_samples=2500, random_state=42)
    df.to_csv(csv_path, index=False)
    print(f"💾 Dataset sintético salvo em: {csv_path.name} (Taxa base de Churn: {df['churn'].mean() * 100:.1f}%)")

    features = ["idade", "tempo_contrato", "uso_mensal", "chamados_suporte"]
    X = df[features]
    y = df["churn"]

    # Divisão treino/teste estratificada
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("🤖 Treinando Pipeline de Classificação (StandardScaler + RandomForest)...")
    pipeline = build_and_train_pipeline(X_train, y_train)

    # Avaliação
    metrics = evaluate_model(pipeline, X_test, y_test)

    # Persistência do artefato
    joblib.dump(pipeline, model_path)
    print(f"📦 Modelo treinado exportado com sucesso para: {model_path.name}")
    print("=" * 70)

    return pipeline, metrics


if __name__ == "__main__":
    train_and_export_model()
