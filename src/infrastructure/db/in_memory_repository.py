from datetime import datetime
from typing import List, Optional, Dict
import pandas as pd

from src.domain.smart_meter.repository import ISmartMeterRepository
from src.domain.smart_meter.entities import ConsumptionRecord

# Repositório de Infraestrutura (Implementação Concreta)
class InMemorySmartMeterRepository(ISmartMeterRepository):
    """
    Implementação em memória (Mock) do repositório para desenvolvimento e testes.
    Em um ambiente real, esta classe seria substituída pela implementação PostgreSQL.
    (Princípio Aberto/Fechado: Aberto para extensão (nova implementação DB), Fechado para modificação (a interface não muda))
    """
    
    def __init__(self, initial_data_path: str = None):
        self._data: List[ConsumptionRecord] = []
        self._meters: Dict[str, bool] = {} # Simplesmente para rastrear IDs de medidores
        
        if initial_data_path:
            self._load_initial_data(initial_data_path)

    def _load_initial_data(self, path: str):
        """Carrega dados do CSV inicial para a simulação."""
        try:
            df = pd.read_csv(path)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            for index, row in df.iterrows():
                record = ConsumptionRecord(
                    timestamp=row['timestamp'],
                    consumption_kwh=row['consumption_kwh'],
                    temperature_c=row['temperature_c'],
                    is_weekend=row['is_weekend']
                )
                self._data.append(record)
                self._meters[row['meter_id']] = True
            print(f"Dados iniciais carregados: {len(self._data)} registros.")
        except Exception as e:
            print(f"Erro ao carregar dados iniciais: {e}")

    def get_all_meters(self) -> List[str]:
        """Retorna todos os IDs de medidores."""
        return list(self._meters.keys())

    def get_consumption_data(self, start_date: datetime, end_date: datetime, meter_id: Optional[str] = None) -> List[ConsumptionRecord]:
        """Retorna dados de consumo para um período."""
        # Simulação de consulta ao DB
        filtered_data = [
            r for r in self._data 
            if start_date <= r.timestamp <= end_date
        ]
        # A simulação em memória não filtra por meter_id, mas a implementação real faria.
        return filtered_data

    def save_consumption_record(self, record: ConsumptionRecord, meter_id: str):
        """Salva um novo registro de consumo."""
        self._data.append(record)
        self._meters[meter_id] = True

    def get_total_consumption_by_hour(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Retorna o consumo total agregado por hora para o período."""
        
        # 1. Filtrar os dados
        filtered_data = [
            r for r in self._data 
            if start_date <= r.timestamp <= end_date
        ]
        
        # 2. Agregação em memória (simulando a agregação do DB)
        consumption_map = {}
        for record in filtered_data:
            key = record.timestamp.replace(minute=0, second=0, microsecond=0)
            consumption_map[key] = consumption_map.get(key, 0) + record.consumption_kwh
            
        # 3. Formatar o resultado
        result = [
            {'timestamp': ts, 'consumption': round(consumption, 2)}
            for ts, consumption in sorted(consumption_map.items())
        ]
        
        return result

# Estrutura para o Repositório PostgreSQL (apenas para referência na documentação)
class PostgresSmartMeterRepository(ISmartMeterRepository):
    """
    Implementação concreta para PostgreSQL (a ser desenvolvida na fase 5).
    """
    def __init__(self, db_connection_string: str):
        # Configuração da conexão com o banco de dados
        pass
    
    # Implementar todos os métodos abstratos de ISmartMeterRepository
    def get_all_meters(self) -> List[str]:
        raise NotImplementedError
    
    def get_consumption_data(self, start_date: datetime, end_date: datetime, meter_id: Optional[str] = None) -> List[ConsumptionRecord]:
        raise NotImplementedError

    def save_consumption_record(self, record: ConsumptionRecord, meter_id: str):
        raise NotImplementedError

    def get_total_consumption_by_hour(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        raise NotImplementedError
