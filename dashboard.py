import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configurações do Streamlit
st.set_page_config(
    page_title="Dashboard de Previsão de Demanda de Energia",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL da API FastAPI (executada localmente)
API_URL = "http://localhost:8000/forecast/demand"
HEALTH_URL = "http://localhost:8000/health"

# --- Funções de Serviço ---

@st.cache_data(ttl=60) # Cache para evitar chamadas repetidas à API
def get_api_health():
    """Verifica a saúde da API."""
    try:
        response = requests.get(HEALTH_URL)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False

def get_forecast(start_date: datetime, end_date: datetime, steps: int) -> pd.DataFrame:
    """Chama a API para obter a previsão de demanda."""
    payload = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "steps": steps
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status() # Levanta exceção para códigos de status ruins (4xx ou 5xx)
        
        data = response.json()
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        return df

    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar ou obter dados da API: {e}")
        return pd.DataFrame()

# --- Layout do Dashboard ---

st.title("⚡️ Dashboard de Previsão de Demanda de Energia")
st.markdown("Este painel interativo consome a API FastAPI (baseada em DDD) para gerar previsões de demanda de energia.")

# 1. Sidebar para Controles
st.sidebar.header("Controles de Previsão")

# Data de fim da janela de dados históricos (para simular "agora")
end_date_default = datetime.now().replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
end_date_input = st.sidebar.date_input(
    "Data Final dos Dados Históricos", 
    value=end_date_default.date(), 
    max_value=end_date_default.date()
)
end_time_input = st.sidebar.time_input(
    "Hora Final dos Dados Históricos", 
    value=end_date_default.time()
)
end_datetime = datetime.combine(end_date_input, end_time_input)

# Data de início (janela histórica de 30 dias)
start_date_default = end_datetime - timedelta(days=30)
start_date_input = st.sidebar.date_input(
    "Data Inicial dos Dados Históricos", 
    value=start_date_default.date(), 
    min_value=datetime(2024, 1, 1).date()
)
start_time_input = st.sidebar.time_input(
    "Hora Inicial dos Dados Históricos", 
    value=start_date_default.time()
)
start_datetime = datetime.combine(start_date_input, start_time_input)

# Número de horas para previsão
steps = st.sidebar.slider(
    "Horas de Previsão (Steps)", 
    min_value=1, 
    max_value=72, 
    value=24, 
    step=1
)

# 2. Status da API
api_status = get_api_health()
st.sidebar.markdown("---")
st.sidebar.subheader("Status do Serviço")
if api_status:
    st.sidebar.success("✅ API FastAPI Online")
else:
    st.sidebar.error("❌ API FastAPI Offline. Por favor, inicie o servidor.")

# 3. Execução da Previsão
if st.sidebar.button("Gerar Previsão de Demanda") and api_status:
    
    st.info(f"Buscando dados históricos de {start_datetime.strftime('%Y-%m-%d %H:%M')} até {end_datetime.strftime('%Y-%m-%d %H:%M')} e prevendo as próximas {steps} horas...")
    
    forecast_df = get_forecast(start_datetime, end_datetime, steps)
    
    if not forecast_df.empty:
        st.success("Previsão gerada com sucesso!")
        
        # 3.1. Visualização
        st.header("Gráfico de Previsão de Carga")
        st.line_chart(forecast_df, use_container_width=True)
        
        # 3.2. Insights para Otimização
        st.header("Insights para Otimização")
        
        max_demand = forecast_df['predicted_consumption_kwh'].max()
        time_of_max_demand = forecast_df['predicted_consumption_kwh'].idxmax()
        
        st.metric(
            label="Pico de Demanda Previsto", 
            value=f"{max_demand:.2f} kWh", 
            delta=f"Ocorrência: {time_of_max_demand.strftime('%Y-%m-%d %H:%M')}"
        )
        
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 5px;">
            <p><strong>Recomendação de Otimização:</strong></p>
            <p>O pico de demanda de <strong>{max_demand:.2f} kWh</strong> está previsto para <strong>{time_of_max_demand.strftime('%d/%m/%Y às %H:%M')}</strong>.</p>
            <p>Este insight é crucial para o <strong>Planejamento de Alocação de Transformadores</strong> e <strong>Geração Distribuída</strong>. A empresa deve considerar:
            <ul>
                <li><strong>Alocação de Transformadores:</strong> Verificar a capacidade dos transformadores na área afetada e planejar o remanejamento ou reforço preventivo para evitar sobrecarga.</li>
                <li><strong>Geração Distribuída:</strong> Programar a ativação de fontes de geração distribuída (ex: baterias, pequenos geradores) para injetar energia na rede e aliviar a demanda no horário de pico.</li>
            </ul>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # 3.3. Dados Brutos
        st.subheader("Dados Brutos da Previsão")
        st.dataframe(forecast_df)

    else:
        st.warning("Não foi possível gerar a previsão. Verifique o status da API e os parâmetros de entrada.")

elif not api_status:
    st.warning("A API FastAPI precisa estar online para gerar a previsão. Por favor, inicie o servidor.")
