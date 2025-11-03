from datetime import datetime
from typing import Optional
import pandas as pd

from src.domain.smart_meter.repository import ISmartMeterRepository
from src.domain.forecasting.service import ForecastingService

class ForecastingUseCase:
    """
    Caso de Uso (Application Service) para orquestrar a previsão de demanda.
    Depende de interfaces (ISmartMeterRepository) e serviços de domínio (ForecastingService).
    """

    def __init__(self, repository: ISmartMeterRepository, service: ForecastingService):
        # Injeção de dependência (Princípio de Inversão de Dependência - D do SOLID)
        self.repository = repository
        self.service = service

    def execute(self, start_date: datetime, end_date: datetime, steps: int) -> pd.Series:
        """
        Executa o fluxo de trabalho de previsão:
        1. Obtém dados históricos agregados do repositório.
        2. Treina o modelo de previsão.
        3. Realiza a previsão.
        4. Retorna a série temporal da previsão.
        """
        try:
            # 1. Obter dados históricos agregados
            # A camada de infraestrutura (repositório) é responsável por transformar
            # os dados brutos do DB em um formato utilizável pelo domínio.
            historical_data_dict = self.repository.get_total_consumption_by_hour(start_date, end_date)
            
            # Converte para pd.Series, o formato esperado pelo ForecastingService
            historical_data = pd.Series(
                data=[item['consumption'] for item in historical_data_dict],
                index=[item['timestamp'] for item in historical_data_dict]
            )
            
            if historical_data.empty:
                raise ValueError("No historical data found for the specified period.")

            # 2. Treinar o modelo de previsão
            self.service.train_model(historical_data)

            # 3. Realizar a previsão
            forecast_series = self.service.predict_demand(steps)

            return forecast_series

        except Exception as e:
            # Logar o erro e relançar uma exceção de aplicação
            print(f"Erro no caso de uso de previsão: {e}")
            raise RuntimeError(f"Falha ao executar a previsão de demanda: {e}")
