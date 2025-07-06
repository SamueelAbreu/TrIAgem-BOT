import uvicorn
import json
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List, Any, Optional

print("Iniciando o Agente de Recomendações Médicas...")

# --- Conexão com o Banco de Dados ---
DB_FILE = "medicos.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# Mapeamento de sintomas para especialidades (para urgência média)
SINTOMA_ESPECIALIDADE_MAP = {
    "tosse": "Otorrinolaringologista",
    "febre": "Clínico Geral",
    "dor_cabeca": "Neurologista",
    "nausea": "Gastroenterologista",
    "dor_garganta": "Otorrinolaringologista",
    "dor_abdominal": "Gastroenterologista"
}

BASE_RECOMENDACOES = {
    "alta": {
        "orientacoes": [
            "Procure imediatamente um pronto-socorro ou ligue para o SAMU (192)",
            "Não tome medicamentos por conta própria",
            "Se possível, tenha alguém para acompanhá-lo ao hospital",
            "Mantenha-se calmo e evite esforços físicos"
        ],
        "cuidados_imediatos": [
            "Mantenha as vias aéreas desobstruídas",
            "Afrouxe roupas apertadas",
            "Posicione-se de forma confortável",
            "Monitore sinais vitais se possível"
        ],
        "nao_fazer": [
            "Não dirija veículos",
            "Não tome medicamentos sem orientação médica",
            "Não ignore os sintomas",
            "Não demore para buscar ajuda"
        ]
    },
    "media": {
        "orientacoes": [
            "Agende uma consulta médica nas próximas 24-48 horas",
            "Considere uma teleconsulta se disponível",
            "Monitore a evolução dos sintomas",
            "Procure um posto de saúde se os sintomas piorarem"
        ],
        "cuidados_gerais": [
            "Mantenha-se hidratado",
            "Descanse adequadamente",
            "Evite atividades físicas intensas",
            "Mantenha uma alimentação leve"
        ],
        "medicamentos_basicos": [
            "Paracetamol para dor e febre (conforme bula)",
            "Soro fisiológico para congestão nasal",
            "Chás naturais (camomila, gengibre)",
            "Sempre consulte um farmacêutico antes de tomar qualquer medicamento"
        ],
        "sinais_alerta": [
            "Febre persistente acima de 39°C",
            "Dificuldade para respirar",
            "Vômitos persistentes",
            "Piora significativa dos sintomas"
        ]
    },
    "baixa": {
        "orientacoes": [
            "Monitore os sintomas por alguns dias",
            "Procure um médico se os sintomas persistirem por mais de uma semana",
            "Mantenha cuidados básicos de saúde",
            "Considere medidas preventivas"
        ],
        "autocuidado": [
            "Beba bastante líquido",
            "Descanse quando necessário",
            "Mantenha uma alimentação equilibrada",
            "Pratique atividades relaxantes"
        ],
        "remedios_caseiros": [
            "Chá de mel e limão para garganta",
            "Inalação com vapor d'água",
            "Gargarejos com água morna e sal",
            "Compressas mornas para dores musculares"
        ],
        "prevencao": [
            "Lave as mãos frequentemente",
            "Evite aglomerações se estiver resfriado",
            "Mantenha ambientes ventilados",
            "Use máscara se necessário"
        ]
    }
}

RECOMENDACOES_SINTOMAS = {
    "tosse": {
        "dicas": [
            "Mantenha-se hidratado para fluidificar secreções",
            "Evite ambientes com fumaça ou poluição",
            "Use umidificador de ar se possível",
            "Chá de mel pode ajudar a acalmar a tosse"
        ]
    },
    "febre": {
        "dicas": [
            "Monitore a temperatura regularmente",
            "Use roupas leves e mantenha o ambiente fresco",
            "Beba líquidos em abundância",
            "Compressas frias na testa podem ajudar"
        ]
    },
    "dor_cabeca": {
        "dicas": [
            "Descanse em ambiente escuro e silencioso",
            "Aplique compressas frias na testa",
            "Mantenha-se hidratado",
            "Evite telas de computador e celular"
        ]
    },
    "nausea": {
        "dicas": [
            "Coma alimentos leves e em pequenas quantidades",
            "Evite alimentos gordurosos ou muito condimentados",
            "Chá de gengibre pode ajudar",
            "Mantenha-se hidratado com pequenos goles"
        ]
    }
}

app = FastAPI(
    title="API do Agente de Recomendações Médicas",
    description="Uma API que fornece recomendações médicas e sugere locais de atendimento baseados no resultado da triagem.",
    version="1.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TriagemInput(BaseModel):
    urgencia: str
    sintomas_texto: str
    resultado_triagem: str

class MedicoRecomendado(BaseModel):
    nome_local: str
    especialidade: str
    endereco: str
    telefone: Optional[str]

class RecomendacaoResponse(BaseModel):
    urgencia: str
    recomendacoes_gerais: Dict
    recomendacoes_especificas: List[str]
    medicos_recomendados: List[MedicoRecomendado]
    observacoes: str

def extrair_sintomas_chave(texto: str) -> List[str]:
    texto_lower = texto.lower()
    sintomas_encontrados = []
    mapeamento_sintomas = {
        "tosse": ["tosse", "tossir", "pigarro"],
        "febre": ["febre", "febril", "temperatura"],
        "dor_cabeca": ["dor de cabeça", "cefaleia", "enxaqueca", "cabeça doendo"],
        "nausea": ["nausea", "náusea", "enjoo", "vomito", "vômito"]
    }
    for sintoma, palavras_chave in mapeamento_sintomas.items():
        if any(palavra in texto_lower for palavra in palavras_chave):
            sintomas_encontrados.append(sintoma)
    return sintomas_encontrados

def gerar_recomendacoes_especificas(sintomas: List[str]) -> List[str]:
    recomendacoes = []
    for sintoma in sintomas:
        if sintoma in RECOMENDACOES_SINTOMAS:
            recomendacoes.extend(RECOMENDACOES_SINTOMAS[sintoma]["dicas"])
    return recomendacoes

def recomendar_medicos(urgencia: str, sintomas_chave: List[str]) -> List[MedicoRecomendado]:
    recomendacoes = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if urgencia == 'media' and sintomas_chave:
            for sintoma in sintomas_chave:
                if sintoma in SINTOMA_ESPECIALIDADE_MAP:
                    especialidade = SINTOMA_ESPECIALIDADE_MAP[sintoma]
                    cursor.execute(
                        "SELECT nome_local, especialidade, endereco, telefone FROM medicos WHERE especialidade = ? AND nivel_urgencia = 'media' ORDER BY RANDOM() LIMIT 1",
                        (especialidade,)
                    )
                    especialista = cursor.fetchone()
                    if especialista:
                        recomendacoes.append(MedicoRecomendado(**dict(especialista)))
                    break 

        limit = 2 - len(recomendacoes)
        if limit > 0:
            cursor.execute(
                "SELECT nome_local, especialidade, endereco, telefone FROM medicos WHERE nivel_urgencia = ? ORDER BY RANDOM() LIMIT ?",
                (urgencia, limit)
            )
            rows = cursor.fetchall()
            for row in rows:
                if not any(rec.nome_local == row['nome_local'] for rec in recomendacoes):
                    recomendacoes.append(MedicoRecomendado(**dict(row)))
        conn.close()
    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return []
    
    return recomendacoes

@app.post("/recomendacoes", response_model=RecomendacaoResponse, summary="Gera recomendações médicas e sugere locais de atendimento")
def gerar_recomendacoes(triagem: TriagemInput):
    urgencia = triagem.urgencia.lower()
    if urgencia not in BASE_RECOMENDACOES:
        urgencia = "baixa"

    recomendacoes_gerais = BASE_RECOMENDACOES[urgencia]
    sintomas_identificados = extrair_sintomas_chave(triagem.sintomas_texto)
    recomendacoes_especificas = gerar_recomendacoes_especificas(sintomas_identificados)
    medicos = recomendar_medicos(urgencia, sintomas_identificados)

    if urgencia == "alta":
        observacoes = "⚠️ ATENÇÃO: Esta é uma situação de urgência. Busque atendimento médico imediatamente!"
    elif urgencia == "media":
        observacoes = "⚡ Recomenda-se acompanhamento médico. Monitore os sintomas e procure ajuda se piorarem."
    else:
        observacoes = "💡 Situação de baixa urgência. Cuidados básicos podem ser suficientes, mas monitore a evolução."

    return RecomendacaoResponse(
        urgencia=urgencia,
        recomendacoes_gerais=recomendacoes_gerais,
        recomendacoes_especificas=recomendacoes_especificas,
        medicos_recomendados=medicos,
        observacoes=observacoes
    )

@app.get("/health", summary="Verifica o status do serviço")
def health_check():
    return {"status": "healthy", "service": "Agente de Recomendações Médicas"}

@app.get("/sintomas-suportados", summary="Lista sintomas com recomendações específicas")
def listar_sintomas_suportados():
    return {
        "sintomas_suportados": list(RECOMENDACOES_SINTOMAS.keys()),
        "total": len(RECOMENDACOES_SINTOMAS)
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)