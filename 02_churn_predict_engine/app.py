"""API REST de Inferência para Previsão de Churn em Tempo Real.

Desenvolvida em FastAPI, fornece endpoints para validação, verificação de integridade
e predição da probabilidade de cancelamento de clientes utilizando o modelo de Machine Learning.
"""

from __future__ import annotations

import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# Adiciona o diretório local ao sys.path para importação modular
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

try:
    from model_train import train_and_export_model
except ImportError:
    train_and_export_model = None  # type: ignore

MODEL_PATH = CURRENT_DIR / "churn_model.joblib"
loaded_pipeline: Any = None


def get_model():
    """Carrega o pipeline preditivo em memória ou o treina automaticamente caso ausente."""
    global loaded_pipeline
    if loaded_pipeline is not None:
        return loaded_pipeline

    if not MODEL_PATH.exists():
        print(f"⚠️ Artefato {MODEL_PATH.name} não encontrado. Executando treinamento automático...")
        if train_and_export_model is not None:
            pipeline, _ = train_and_export_model(output_dir=CURRENT_DIR)
            loaded_pipeline = pipeline
        else:
            raise FileNotFoundError(
                f"Arquivo de modelo '{MODEL_PATH}' não encontrado e módulo de treino indisponível."
            )
    else:
        loaded_pipeline = joblib.load(MODEL_PATH)
        print(f"✅ Modelo de Churn carregado com sucesso a partir de: {MODEL_PATH.name}")

    return loaded_pipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação (startup e shutdown)."""
    # Inicializa e pré-carrega o modelo durante a inicialização
    get_model()
    yield
    # Limpeza opcional no encerramento
    global loaded_pipeline
    loaded_pipeline = None


app = FastAPI(
    title="Churn Prediction Engine API",
    description=(
        "API corporativa de Machine Learning para inferência de risco e "
        "probabilidade de Churn (cancelamento de clientes)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


class CustomerData(BaseModel):
    """Esquema de validação dos atributos do cliente para predição."""

    idade: int = Field(
        ...,
        ge=18,
        le=100,
        description="Idade do cliente em anos completos.",
        json_schema_extra={"example": 45},
    )
    tempo_contrato: int = Field(
        ...,
        ge=1,
        le=120,
        description="Tempo de contrato ativo do cliente em meses.",
        json_schema_extra={"example": 6},
    )
    uso_mensal: float = Field(
        ...,
        ge=0.0,
        description="Volume de uso mensal do serviço (horas de acesso ou GB de dados).",
        json_schema_extra={"example": 85.5},
    )
    chamados_suporte: int = Field(
        ...,
        ge=0,
        le=50,
        description="Quantidade de tickets/chamados abertos no suporte técnico nos últimos 90 dias.",
        json_schema_extra={"example": 4},
    )


class PredictionResponse(BaseModel):
    """Esquema estruturado da resposta da inferência preditiva."""

    churn_prediction: int = Field(
        ..., description="Rótulo binário previsto (0 = Fiel/Retido, 1 = Churn/Cancelamento)."
    )
    churn_label: str = Field(
        ..., description="Rótulo textual legível para relatórios e dashboards."
    )
    churn_probability: float = Field(
        ..., description="Probabilidade estimada de churn (valor contínuo entre 0.0 e 1.0)."
    )
    churn_probability_pct: str = Field(
        ..., description="Probabilidade formatada em percentual amigável."
    )
    risk_level: str = Field(
        ..., description="Classificação de risco: Baixo, Médio, Alto ou Crítico."
    )
    retention_action: str = Field(
        ..., description="Ação sugerida para mitigação de perda do cliente."
    )


def categorize_risk(prob: float) -> tuple[str, str]:
    """Classifica o nível de risco e prescreve a ação recomendada.

    Args:
        prob: Probabilidade de churn entre 0 e 1.

    Returns:
        tuple[str, str]: (Nível de Risco, Ação Recomendada)
    """
    if prob < 0.25:
        return (
            "Baixo",
            "Cliente satisfeito e engajado. Manter rotina padrão de comunicação e pós-venda.",
        )
    elif prob < 0.50:
        return (
            "Médio",
            "Atenção moderada. Enviar pesquisas de satisfação e oferecer conteúdos de onboarding/adoção.",
        )
    elif prob < 0.75:
        return (
            "Alto",
            "Risco iminente. Acionar equipe de Customer Success para contato consultivo e verificação de dores.",
        )
    else:
        return (
            "Crítico",
            "Perda quase certa. Ofertar desconto de retenção, suporte prioritário imediato e plano de fidelização.",
        )


@app.get("/", tags=["Diagnóstico"])
def root() -> Dict[str, Any]:
    """Retorna metadados gerais da API e links úteis de documentação."""
    return {
        "service": "02_churn_predict_engine",
        "status": "online",
        "version": "1.0.0",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
        "model_loaded": loaded_pipeline is not None or MODEL_PATH.exists(),
    }


@app.get("/health", tags=["Diagnóstico"])
def health_check() -> Dict[str, Any]:
    """Verifica a integridade do serviço e disponibilidade do pipeline treinado."""
    try:
        model = get_model()
        return {
            "status": "healthy",
            "model_ready": model is not None,
            "model_path": str(MODEL_PATH.name),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço degradado: falha ao verificar modelo - {exc}",
        )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    tags=["Inferência"],
)
def predict_churn(customer: CustomerData) -> PredictionResponse:
    """Recebe as métricas de um cliente em JSON e retorna a predição e probabilidade de Churn."""
    try:
        pipeline = get_model()

        # Monta DataFrame com as mesmas colunas utilizadas no treinamento
        input_df = pd.DataFrame(
            [
                {
                    "idade": customer.idade,
                    "tempo_contrato": customer.tempo_contrato,
                    "uso_mensal": customer.uso_mensal,
                    "chamados_suporte": customer.chamados_suporte,
                }
            ]
        )

        # Inferência de probabilidade e classe
        proba_array = pipeline.predict_proba(input_df)[0]
        churn_prob = float(proba_array[1])
        prediction = int(pipeline.predict(input_df)[0])

        risk_level, retention_action = categorize_risk(churn_prob)
        churn_label = "Churn (Risco de Cancelamento)" if prediction == 1 else "Fiel (Retido)"

        return PredictionResponse(
            churn_prediction=prediction,
            churn_label=churn_label,
            churn_probability=round(churn_prob, 4),
            churn_probability_pct=f"{churn_prob * 100:.2f}%",
            risk_level=risk_level,
            retention_action=retention_action,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro interno durante a predição: {str(exc)}",
        )


if __name__ == "__main__":
    import uvicorn

    print("🚀 Iniciando servidor FastAPI Churn Predict Engine em http://127.0.0.1:8000")
    print("📖 Documentação Swagger interativa em: http://127.0.0.1:8000/docs")
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
