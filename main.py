import uvicorn
from src.infrastructure.api.api import app

if __name__ == "__main__":
    # Configuração para rodar a API
    # host="0.0.0.0" permite acesso externo (necessário para o Streamlit acessar)
    # reload=True é útil em desenvolvimento, mas omitido aqui para ambiente de produção simulado
    uvicorn.run(app, host="0.0.0.0", port=8000)

