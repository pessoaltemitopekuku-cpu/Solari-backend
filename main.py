from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
from typing import Optional

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

df_chargers = pd.DataFrame([
    {"id": "C1", "name": "Carregador Rápido - Vaga 12", "status": "Disponível", "power_kw": 22},
    {"id": "C2", "name": "Carregador Normal - Vaga 15", "status": "Em Uso", "power_kw": 7},
    {"id": "C3", "name": "Carregador Rápido - Vaga 02", "status": "Offline", "power_kw": 22},
])

df_history = pd.DataFrame([
    {"id": 1, "user": "João Silva", "charger_id": "C2", "date": "2026-06-10", "energy_kwh": 35.5, "cost_coins": 150},
    {"id": 2, "user": "Maria Souza", "charger_id": "C1", "date": "2026-06-11", "energy_kwh": 50.0, "cost_coins": 200},
])

# ---------------------------------------------------------
# MODELOS DE DADOS (À prova de falhas do frontend)
# ---------------------------------------------------------
class SessionStartRequest(BaseModel):
    charger_id: Optional[str] = None
    carregadorId: Optional[str] = None
    user_id: Optional[str] = "U1"

class LoginRequest(BaseModel):
    role: Optional[str] = "admin"  # Padrão seguro para evitar Erro 422

# ---------------------------------------------------------
# ROTAS DA API (Endpoints)
# ---------------------------------------------------------

@app.get("/")
def read_root():
    return {"message": "Bem-vindo aos servidores da Solari!"}

@app.get("/api/chargers")
def get_chargers():
    return df_chargers.to_dict(orient="records")

@app.post("/api/sessions/start")
def start_session(request: SessionStartRequest):
    global df_chargers
    target_id = request.charger_id or request.carregadorId
    
    if not target_id:
        raise HTTPException(status_code=400, detail="ID do carregador não enviado")

    idx = df_chargers.index[df_chargers['id'] == target_id].tolist()
    if not idx:
        raise HTTPException(status_code=404, detail="Carregador não encontrado")
        
    if df_chargers.at[idx[0], 'status'] != "Disponível":
        raise HTTPException(status_code=400, detail="Carregador ocupado ou offline")

    df_chargers.at[idx[0], 'status'] = "Em Uso"
    return {"message": "Recarga iniciada com sucesso", "charger_id": target_id}

@app.get("/api/history")
def get_history():
    return df_history.to_dict(orient="records")

@app.get("/api/admin/metrics")
def get_metrics():
    total_energy = float(df_history['energy_kwh'].sum())
    total_revenue = float(df_history['cost_coins'].sum())
    active_sessions = int(len(df_chargers[df_chargers['status'] == 'Em Uso']))
    
    return {
        "total_energy_kwh": total_energy,
        "total_revenue_coins": total_revenue,
        "active_sessions": active_sessions,
        "cluster_name": "Condomínio Solari Alpha"
    }

@app.get("/api/buildings")
def get_buildings():
    return [{"id": "B1", "name": "Condomínio Solari Alpha"}]

@app.get("/api/users")
def get_users():
    return [{"id": "U1", "name": "João Silva"}]

@app.get("/api/admin/payments")
def get_payments():
    total = float(df_history['cost_coins'].sum())
    usuarios = 2
    return {"total_cluster": total, "cost_per_user": total / usuarios}

# ---------------------------------------------------------
# A SOLUÇÃO DO LOGIN
# ---------------------------------------------------------
@app.post("/api/auth/login")
def login(data: Optional[LoginRequest] = None):
    # O padrão é admin. Se o código do Lovable mandar a requisição "torta", a tela não trava.
    papel = "admin" 
    
    # Se o frontend mandou o JSON bonitinho e ele tem um "role", nós usamos
    if data and getattr(data, "role", None):
        papel = data.role
        
    # Separa os caminhos!
    if papel == "funcionario":
        return {"token": "token-func-123", "user": {"nome": "João Silva", "role": "funcionario"}}
    else:
        return {"token": "token-admin-123", "user": {"nome": "Mariana Admin", "role": "admin"}}
