import uvicorn
import json
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List

print("Iniciando o Agente de Recomendações Médicas...")

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

# Recomendações específicas por sintomas
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
    description="Uma API que fornece recomendações médicas baseadas no resultado da triagem.",
    version="1.0.0"
)

# Configura o CORS para permitir comunicação entre microserviços
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar origens específicas
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TriagemInput(BaseModel):
    urgencia: str  # "alta", "media", "baixa"
    sintomas_texto: str
    resultado_triagem: str

class RecomendacaoResponse(BaseModel):
    urgencia: str
    recomendacoes_gerais: Dict
    recomendacoes_especificas: List[str]
    observacoes: str

def extrair_sintomas_chave(texto: str) -> List[str]:
    """Extrai sintomas-chave do texto para recomendações específicas."""
    texto_lower = texto.lower()
    sintomas_encontrados = []
    
    # Mapeamento de palavras-chave para sintomas
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
    """Gera recomendações específicas baseadas nos sintomas identificados."""
    recomendacoes = []
    
    for sintoma in sintomas:
        if sintoma in RECOMENDACOES_SINTOMAS:
            recomendacoes.extend(RECOMENDACOES_SINTOMAS[sintoma]["dicas"])
    
    return recomendacoes

@app.post("/recomendacoes", response_model=RecomendacaoResponse, summary="Gera recomendações médicas")
def gerar_recomendacoes(triagem: TriagemInput):
    """Endpoint principal que gera recomendações baseadas no resultado da triagem."""
    
    urgencia = triagem.urgencia.lower()
    
    # Valida o nível de urgência
    if urgencia not in BASE_RECOMENDACOES:
        urgencia = "baixa"  # Default para urgência baixa se não reconhecida
    
    # Obtém recomendações gerais baseadas na urgência
    recomendacoes_gerais = BASE_RECOMENDACOES[urgencia]
    
    # Extrai sintomas específicos do texto
    sintomas_identificados = extrair_sintomas_chave(triagem.sintomas_texto)
    
    # Gera recomendações específicas
    recomendacoes_especificas = gerar_recomendacoes_especificas(sintomas_identificados)
    
    # Gera observações personalizadas
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
        observacoes=observacoes
    )

@app.get("/health", summary="Verifica o status do serviço")
def health_check():
    """Endpoint para verificar se o serviço está funcionando."""
    return {"status": "healthy", "service": "Agente de Recomendações Médicas"}

@app.get("/sintomas-suportados", summary="Lista sintomas com recomendações específicas")
def listar_sintomas_suportados():
    """Retorna a lista de sintomas que possuem recomendações específicas."""
    return {
        "sintomas_suportados": list(RECOMENDACOES_SINTOMAS.keys()),
        "total": len(RECOMENDACOES_SINTOMAS)
    }

# Bloco que permite a execução direta do script
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)

