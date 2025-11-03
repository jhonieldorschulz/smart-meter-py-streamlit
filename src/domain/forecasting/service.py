from typing import List, Tuple
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from datetime import datetime, timedelta

class ForecastingService:
    """
    Serviço de Domínio responsável pela lógica de previsão de demanda.
    Utiliza o padrão Strategy (implícito) para escolher o modelo de previsão.
    """

    def __init__(self, model_order: Tuple[int, int, int] = (5, 1, 0)):
        self.model_order = model_order
        self._model = None
        self._last_train_data = None

    def train_model(self, historical_data: pd.Series):
        """
        Treina o modelo de previsão com os dados históricos.
        Assume que historical_data é uma série temporal (pd.Series) com índice de tempo.
        """
        if historical_data.empty:
            raise ValueError("Historical data cannot be empty for training.")

        # Usando SARIMAX para permitir sazonalidade (embora o protótipo usasse ARIMA)
        # Manteremos o ARIMA simples por enquanto para refletir o protótipo.
        try:
            # O ideal seria usar SARIMAX, mas para manter a simplicidade do protótipo
            # e a transição do notebook, usaremos ARIMA.
            model = ARIMA(historical_data, order=self.model_order)
            self._model = model.fit()
            self._last_train_data = historical_data
            print(f"Modelo ARIMA treinado com sucesso. Ordem: {self.model_order}")
        except Exception as e:
            print(f"Erro ao treinar o modelo ARIMA: {e}")
            raise

    def predict_demand(self, steps: int) -> pd.Series:
        """
        Realiza a previsão de demanda para um número de passos (horas) futuros.
        """
        if self._model is None:
            raise RuntimeError("Model must be trained before making predictions.")

        # Realiza a previsão
        forecast = self._model.forecast(steps=steps)

        # Cria um índice de tempo futuro
        last_time = self._last_train_data.index[-1]
        future_index = pd.date_range(start=last_time + timedelta(hours=1), periods=steps, freq='H')
        
        # Cria a série de previsão com o índice de tempo correto
        forecast_series = pd.Series(forecast.values, index=future_index)

        return forecast_series

    def get_model_summary(self) -> str:
        """Retorna o sumário do modelo treinado."""
        if self._model:
            return self._model.summary().as_text()
        return "Model not trained."
