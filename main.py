from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from datetime import datetime

app = FastAPI(title="Solari API")

# Configuração de Segurança (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# SIMULAÇÃO DE BANCO DE DADOS COM PANDAS
# ---------------------------------------------------------

# Tabela de Carregadores
df_chargers = pd.DataFrame([
    {"id": "C1", "name": "Carregador Rápido - Vaga 12", "status": "Disponível", "power_kw": 22},
    {"id": "C2", "name": "Carregador Normal - Vaga 15", "status": "Em Uso", "power_kw": 7},
    {"id": "C3", "name": "Carregador Rápido - Vaga 02", "status": "Offline", "power_kw": 22},
])

# Tabela de Histórico
df_history = pd.DataFrame([
    {"id": 1, "user": "João Silva", "charger_id": "C2", "date": "2026-06-10", "energy_kwh": 35.5, "cost_coins": 150},
    {"id": 2, "user": "Maria Souza", "charger_id": "C1", "date": "2026-06-11", "energy_kwh": 50.0, "cost_coins": 200},
])

# Modelo para receber dados do Frontend (Start Session)
class SessionStartRequest(BaseModel):
    charger_id: str
    user_id: str

# ---------------------------------------------------------
# ROTAS DA API (Endpoints)
# ---------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "Bem-vindo aos servidores da Solari!"}

@app.get("/api/chargers")
def get_chargers():
    # Converte o DataFrame do Pandas para um formato que a API entende (Dicionário)
    return df_chargers.to_dict(orient="records")

@app.post("/api/sessions/start")
def start_session(request: SessionStartRequest):
    global df_chargers
    
    # Verifica se o carregador existe e está disponível
    idx = df_chargers.index[df_chargers['id'] == request.charger_id].tolist()
    if not idx:
        raise HTTPException(status_code=404, detail="Carregador não encontrado")
        
    if df_chargers.at[idx[0], 'status'] != "Disponível":
        raise HTTPException(status_code=400, detail="Carregador ocupado ou offline")

    # Atualiza o status no Pandas
    df_chargers.at[idx[0], 'status'] = "Em Uso"
    
    return {"message": "Recarga iniciada com sucesso", "charger_id": request.charger_id}

@app.get("/api/history")
def get_history():
    return df_history.to_dict(orient="records")

@app.get("/api/admin/metrics")
def get_metrics():
    # Usa o Pandas para calcular algumas estatísticas da simulação
    total_energy = df_history['energy_kwh'].sum()
    total_revenue = df_history['cost_coins'].sum()
    active_sessions = len(df_chargers[df_chargers['status'] == 'Em Uso'])
    
    return {
        "total_energy_kwh": total_energy,
        "total_revenue_coins": total_revenue,
        "active_sessions": active_sessions,
        "cluster_name": "Condomínio Solari Alpha"
    }

# Endpoints auxiliares vazios apenas para o Lovable não dar erro
@app.post("/api/auth/login")
def login():
    return {"token": "fake-jwt-token-123", "user": {"name": "Visitante Solari", "role": "admin"}}

@app.get("/api/buildings")
def get_buildings():
    return [{"id": "B1", "name": "Condomínio Solari Alpha"}]

@app.get("/api/users")
def get_users():
    return [{"id": "U1", "name": "João Silva"}]

@app.get("/api/admin/payments")
def get_payments():
    # Simula a divisão igualitária que você pediu nas regras
    total = df_history['cost_coins'].sum()
    usuarios = 2
    return {"total_cluster": total, "cost_per_user": total / usuarios}
