from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.domain.smart_meter.repository import ISmartMeterRepository
from src.domain.smart_meter.entities import ConsumptionRecord

# Configuração de conexão (usando as variáveis do docker-compose)
DATABASE_URL = "postgresql://user:password@db:5432/smart_meter_db"

class PostgresSmartMeterRepository(ISmartMeterRepository):
    """
    Implementação concreta para PostgreSQL.
    """

    def __init__(self, db_url: str = DATABASE_URL):
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self._create_tables()

    def _create_tables(self):
        """Cria as tabelas necessárias no banco de dados, se não existirem."""
        # Em um projeto real, usaríamos um ORM como SQLAlchemy ou Alembic para migrações.
        # Aqui, usamos SQL puro para simplificar a demonstração da infraestrutura.
        with self.engine.connect() as connection:
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS consumption_records (
                    id SERIAL PRIMARY KEY,
                    meter_id VARCHAR(50) NOT NULL,
                    timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
                    consumption_kwh REAL NOT NULL,
                    temperature_c REAL,
                    is_weekend BOOLEAN
                );
            """))
            connection.commit()

    def get_all_meters(self) -> List[str]:
        """Retorna todos os IDs de medidores."""
        with self.SessionLocal() as session:
            result = session.execute(text("SELECT DISTINCT meter_id FROM consumption_records"))
            return [row[0] for row in result]

    def get_consumption_data(self, start_date: datetime, end_date: datetime, meter_id: Optional[str] = None) -> List[ConsumptionRecord]:
        """Retorna dados de consumo para um período."""
        # Implementação omitida para manter o foco na estrutura, mas seguiria a lógica de consulta SQL
        raise NotImplementedError("Método get_consumption_data não implementado para PostgreSQL neste guia.")

    def save_consumption_record(self, record: ConsumptionRecord, meter_id: str):
        """Salva um novo registro de consumo."""
        with self.SessionLocal() as session:
            session.execute(text("""
                INSERT INTO consumption_records (meter_id, timestamp, consumption_kwh, temperature_c, is_weekend)
                VALUES (:meter_id, :timestamp, :consumption_kwh, :temperature_c, :is_weekend)
            """), {
                "meter_id": meter_id,
                "timestamp": record.timestamp,
                "consumption_kwh": record.consumption_kwh,
                "temperature_c": record.temperature_c,
                "is_weekend": record.is_weekend
            })
            session.commit()

    def get_total_consumption_by_hour(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Retorna o consumo total agregado por hora para o período."""
        # Implementação omitida para manter o foco na estrutura, mas seguiria a lógica de consulta SQL
        # Exemplo de consulta:
        # SELECT date_trunc('hour', timestamp) as ts, SUM(consumption_kwh) as total_consumption
        # FROM consumption_records
        # WHERE timestamp BETWEEN :start_date AND :end_date
        # GROUP BY 1 ORDER BY 1
        return [] # Retorna vazio, pois usaremos o repositório em memória para a execução.

