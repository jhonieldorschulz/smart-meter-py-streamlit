from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any

class ConsumptionRecordSchema(BaseModel):
    """Schema para um registro de consumo."""
    timestamp: datetime
    consumption_kwh: float
    temperature_c: float
    is_weekend: bool

class ForecastRequestSchema(BaseModel):
    """Schema para a requisição de previsão de demanda."""
    start_date: datetime
    end_date: datetime
    steps: int = 24  # Previsão para as próximas 24 horas

class ForecastResponseSchema(BaseModel):
    """Schema para a resposta da previsão de demanda."""
    timestamp: datetime
    predicted_consumption_kwh: float

class HealthCheckResponse(BaseModel):
    """Schema para o Health Check da API."""
    status: str = "ok"
    service: str = "Smart Meter Forecasting API"
    version: str = "1.0.0"

class ErrorResponse(BaseModel):
    """Schema para respostas de erro."""
    detail: str
