import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_smart_meter_data(num_meters=10, start_date='2024-01-01', end_date='2024-10-27'):
    """
    Gera um dataset sintético de dados de medidores inteligentes.
    
    Os dados simulam consumo de energia (kWh) em intervalos horários
    para vários medidores, com padrões sazonais e aleatoriedade.
    """
    
    # Gerar a série temporal
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    time_index = pd.date_range(start=start, end=end, freq='H')
    
    all_data = []
    
    # Gerar dados para cada medidor
    for i in range(1, num_meters + 1):
        meter_id = f'METER_{i:03d}'
        
        # Padrão base de consumo (comportamento diário e semanal)
        # Simula picos de manhã e à noite
        base_consumption = np.sin(time_index.hour * 2 * np.pi / 24) * 0.5 + 1.5
        
        # Sazonalidade (simula maior consumo no verão)
        day_of_year = time_index.dayofyear
        seasonal_factor = np.sin(day_of_year * 2 * np.pi / 365) * 0.3 + 1.0
        
        # Fator de aleatoriedade (ruído)
        noise = np.random.normal(0, 0.2, len(time_index))
        
        # Consumo final
        consumption = (base_consumption * seasonal_factor + noise) * np.random.uniform(5, 15)
        consumption = np.where(consumption < 0, 0, consumption) # Garante que o consumo não é negativo
        
        # Simula um evento de pico (ex: dia de muito calor)
        if i == 1: # Apenas para um medidor
            peak_start = datetime.strptime('2024-07-15 14:00:00', '%Y-%m-%d %H:%M:%S')
            peak_end = datetime.strptime('2024-07-16 18:00:00', '%Y-%m-%d %H:%M:%S')
            peak_mask = (time_index >= peak_start) & (time_index <= peak_end)
            consumption[peak_mask] *= 1.5 # Aumenta o consumo em 50%
            
        
        df_meter = pd.DataFrame({
            'timestamp': time_index,
            'meter_id': meter_id,
            'consumption_kwh': consumption.round(2)
        })
        all_data.append(df_meter)
        
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Adicionar colunas de contexto
    final_df['temperature_c'] = (np.sin(final_df['timestamp'].dt.dayofyear * 2 * np.pi / 365) * 10 + 25 + np.random.normal(0, 2, len(final_df))).round(1)
    final_df['is_weekend'] = final_df['timestamp'].dt.dayofweek >= 5
    
    return final_df

if __name__ == '__main__':
    df = generate_smart_meter_data()
    output_path = '/home/ubuntu/smart_meter_guide/data/smart_meter_data.csv'
    df.to_csv(output_path, index=False)
    print(f"Dataset sintético gerado e salvo em: {output_path}")
