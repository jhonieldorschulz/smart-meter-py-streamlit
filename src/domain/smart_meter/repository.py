from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .entities import SmartMeter, ConsumptionRecord

class ISmartMeterRepository(ABC):
    """
    Interface (Contrato) para o Repositório de Medidores Inteligentes.
    Define as operações que a camada de infraestrutura deve implementar.
    """

    @abstractmethod
    def get_all_meters(self) -> List[SmartMeter]:
        """Retorna todos os medidores inteligentes."""
        pass

    @abstractmethod
    def get_consumption_data(self, start_date: datetime, end_date: datetime, meter_id: Optional[str] = None) -> List[ConsumptionRecord]:
        """Retorna dados de consumo para um período e opcionalmente para um medidor específico."""
        pass

    @abstractmethod
    def save_consumption_record(self, record: ConsumptionRecord, meter_id: str):
        """Salva um novo registro de consumo."""
        pass

    @abstractmethod
    def get_total_consumption_by_hour(self, start_date: datetime, end_date: datetime) -> dict:
        """Retorna o consumo total agregado por hora para o período."""
        pass
