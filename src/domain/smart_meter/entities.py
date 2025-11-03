from datetime import datetime
from typing import List, Optional

# Value Object
class ConsumptionRecord:
    def __init__(self, timestamp: datetime, consumption_kwh: float, temperature_c: float, is_weekend: bool):
        if consumption_kwh < 0:
            raise ValueError("Consumption cannot be negative.")
        self.timestamp = timestamp
        self.consumption_kwh = consumption_kwh
        self.temperature_c = temperature_c
        self.is_weekend = is_weekend

# Aggregate Root
class SmartMeter:
    def __init__(self, meter_id: str, location: Optional[str] = None):
        if not meter_id:
            raise ValueError("Meter ID is required.")
        self.meter_id = meter_id
        self.location = location
        self._records: List[ConsumptionRecord] = []

    def add_record(self, record: ConsumptionRecord):
        self._records.append(record)

    def get_records(self) -> List[ConsumptionRecord]:
        # Retorna uma cópia para garantir a imutabilidade da lista interna
        return list(self._records)

    @property
    def total_records(self) -> int:
        return len(self._records)

    def __repr__(self):
        return f"SmartMeter(id='{self.meter_id}', records={self.total_records})"
