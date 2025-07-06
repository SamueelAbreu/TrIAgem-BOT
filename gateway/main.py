import uvicorn
import httpx
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("Iniciando o Gateway de Comunicação entre Agentes...")

AGENTE_TRIAGEM_URL = "http://agente-triagem:8000"
AGENTE_RECOMENDACOES_URL = "http://agente-recomendacoes:8001"

app = FastAPI(
    title="Gateway de Comunicação - Sistema TrIAgem",
    description="Gateway que orquestra a comunicação entre os agentes de IA do sistema de triagem médica.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SintomasInput(BaseModel):
    texto_sintomas: str

class TriagemCompleta(BaseModel):
    sintomas_originais: str
    resultado_triagem: str
    urgencia: str
    recomendacoes: Dict[str, Any]
    tempo_processamento: float
    agentes_consultados: list

class HealthStatus(BaseModel):
    gateway_status: str
    agente_triagem_status: str
    agente_recomendacoes_status: str
    timestamp: str

async def verificar_saude_agente(url: str, endpoint: str = "/docs") -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{url}{endpoint}")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Erro ao verificar saúde do agente {url}: {e}")
        return False

async def chamar_agente_triagem(sintomas: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AGENTE_TRIAGEM_URL}/triagem",
                json={"texto_sintomas": sintomas}
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Erro HTTP ao chamar agente de triagem: {e}")
        raise HTTPException(status_code=503, detail="Agente de triagem indisponível")
    except Exception as e:
        logger.error(f"Erro inesperado ao chamar agente de triagem: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no agente de triagem")

async def chamar_agente_recomendacoes(urgencia: str, sintomas: str, resultado_triagem: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{AGENTE_RECOMENDACOES_URL}/recomendacoes",
                json={
                    "urgencia": urgencia,
                    "sintomas_texto": sintomas,
                    "resultado_triagem": resultado_triagem
                }
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"Erro HTTP ao chamar agente de recomendações: {e}")
        raise HTTPException(status_code=503, detail="Agente de recomendações indisponível")
    except Exception as e:
        logger.error(f"Erro inesperado ao chamar agente de recomendações: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no agente de recomendações")

def extrair_urgencia_do_resultado(resultado: str) -> str:
    resultado_lower = resultado.lower()
    if "alta" in resultado_lower:
        return "alta"
    elif "média" in resultado_lower or "media" in resultado_lower:
        return "media"
    else:
        return "baixa"

@app.post("/triagem-completa", response_model=TriagemCompleta, summary="Executa triagem completa com recomendações")
async def executar_triagem_completa(sintomas: SintomasInput):
    import time
    inicio = time.time()
    logger.info(f"Iniciando triagem completa para: {sintomas.texto_sintomas[:50]}...")
    agentes_consultados = []

    try:
        logger.info("Consultando Agente de Triagem...")
        resultado_triagem = await chamar_agente_triagem(sintomas.texto_sintomas)
        agentes_consultados.append("agente_triagem")
        
        urgencia = extrair_urgencia_do_resultado(resultado_triagem["resultado_triagem"])
        logger.info(f"Urgência identificada: {urgencia}")
        
        logger.info("Consultando Agente de Recomendações...")
        recomendacoes = await chamar_agente_recomendacoes(
            urgencia=urgencia,
            sintomas=sintomas.texto_sintomas,
            resultado_triagem=resultado_triagem["resultado_triagem"]
        )
        agentes_consultados.append("agente_recomendacoes")
        
        tempo_processamento = time.time() - inicio
        
        resposta_consolidada = TriagemCompleta(
            sintomas_originais=sintomas.texto_sintomas,
            resultado_triagem=resultado_triagem["resultado_triagem"],
            urgencia=urgencia,
            recomendacoes=recomendacoes,
            tempo_processamento=round(tempo_processamento, 3),
            agentes_consultados=agentes_consultados
        )
        
        logger.info(f"Triagem completa finalizada em {tempo_processamento:.3f}s")
        return resposta_consolidada
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado na triagem completa: {e}")
        raise HTTPException(status_code=500, detail="Erro interno no gateway")

@app.get("/health", response_model=HealthStatus, summary="Verifica o status de todos os componentes")
async def verificar_saude_sistema():
    from datetime import datetime
    tarefas = [
        verificar_saude_agente(AGENTE_TRIAGEM_URL),
        verificar_saude_agente(AGENTE_RECOMENDACOES_URL, "/health")
    ]
    resultados = await asyncio.gather(*tarefas, return_exceptions=True)
    status_triagem = "healthy" if resultados[0] is True else "unhealthy"
    status_recomendacoes = "healthy" if resultados[1] is True else "unhealthy"
    
    return HealthStatus(
        gateway_status="healthy",
        agente_triagem_status=status_triagem,
        agente_recomendacoes_status=status_recomendacoes,
        timestamp=datetime.now().isoformat()
    )

@app.get("/", summary="Informações do Gateway")
async def informacoes_gateway():
    return {
        "service": "Gateway TrIAgem", "version": "1.0.0",
        "description": "Gateway que orquestra a comunicação entre agentes de IA",
        "agentes_conectados": {
            "agente_triagem": AGENTE_TRIAGEM_URL,
            "agente_recomendacoes": AGENTE_RECOMENDACOES_URL
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)