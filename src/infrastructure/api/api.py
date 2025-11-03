from fastapi import FastAPI, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List

from src.infrastructure.api.schemas import ForecastRequestSchema, ForecastResponseSchema, HealthCheckResponse, ErrorResponse
from src.application.services.forecasting_use_case import ForecastingUseCase
from src.domain.smart_meter.repository import ISmartMeterRepository
from src.domain.forecasting.service import ForecastingService
from src.infrastructure.db.in_memory_repository import InMemorySmartMeterRepository

# --- Dependências (Factory Pattern) ---

# Inicializa o repositório em memória com os dados do CSV
REPO_PATH = "/home/ubuntu/smart_meter_guide/data/smart_meter_data.csv"
in_memory_repo = InMemorySmartMeterRepository(initial_data_path=REPO_PATH)

def get_smart_meter_repository() -> ISmartMeterRepository:
    """Dependência para obter a instância do repositório."""
    # Aqui, a Injeção de Dependência permite trocar facilmente para PostgresSmartMeterRepository
    # sem alterar o código da aplicação/domínio (Princípio Aberto/Fechado)
    return in_memory_repo

def get_forecasting_use_case(
    repository: ISmartMeterRepository = Depends(get_smart_meter_repository)
) -> ForecastingUseCase:
    """Dependência para obter a instância do Caso de Uso de Previsão."""
    # Cria a instância do Serviço de Domínio
    forecasting_service = ForecastingService(model_order=(5, 1, 0))
    # Injeta as dependências no Caso de Uso
    return ForecastingUseCase(repository=repository, service=forecasting_service)

# --- Configuração da API ---

app = FastAPI(
    title="Smart Meter Forecasting API",
    description="API para previsão de demanda de energia com arquitetura DDD.",
    version="1.0.0"
)

# --- Endpoints ---

@app.get("/health", response_model=HealthCheckResponse, tags=["Monitoramento"])
def health_check():
    """Verifica a saúde da API."""
    return HealthCheckResponse()

@app.post(
    "/forecast/demand", 
    response_model=List[ForecastResponseSchema], 
    status_code=200, 
    tags=["Previsão"],
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def forecast_demand(
    request: ForecastRequestSchema,
    use_case: ForecastingUseCase = Depends(get_forecasting_use_case)
):
    """
    Realiza a previsão de demanda total de energia para as próximas 'steps' horas.
    """
    try:
        # Validação de datas (exemplo de regra de negócio na camada de Aplicação)
        if request.start_date >= request.end_date:
            raise HTTPException(
                status_code=400, 
                detail="A data de início deve ser anterior à data de fim."
            )

        # Executa o Caso de Uso
        forecast_series = use_case.execute(
            start_date=request.start_date,
            end_date=request.end_date,
            steps=request.steps
        )

        # Converte o resultado (pd.Series) para o Schema de Resposta
        response_data = []
        for timestamp, prediction in forecast_series.items():
            response_data.append(ForecastResponseSchema(
                timestamp=timestamp,
                predicted_consumption_kwh=prediction
            ))

        return response_data

    except RuntimeError as e:
        # Captura exceções lançadas pelo Caso de Uso
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        # Captura exceções de validação de dados
        raise HTTPException(status_code=400, detail=str(e))

# --- Arquivo principal para execução ---
# Este código será movido para main.py para execução
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
