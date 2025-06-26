# =================================================================================
# main.py - Agente de IA de Triagem com Machine Learning
#
# Lógica Principal:
# 1. Na inicialização, carrega um dataset de um CSV e treina um modelo de ML.
# 2. Expõe um endpoint de API que:
#    a. Filtra saudações e entradas inválidas.
#    b. Usa uma abordagem HÍBRIDA (regras + IA) para classificar a urgência.
# =================================================================================

import uvicorn
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer

SAUDACOES = ["oi", "ola", "olá"]

print("Iniciando o processo de treinamento do modelo de IA...")

try:
    # Carrega o dataset de treino a partir do arquivo CSV, usando ';' como separador.
    df_treino = pd.read_csv('dados_triagem.csv', sep=';')
    print(f"Arquivo 'dados_triagem.csv' carregado: {len(df_treino)} exemplos encontrados.")
except FileNotFoundError:
    print("ERRO CRÍTICO: 'dados_triagem.csv' não encontrado. Certifique-se de que ele está na mesma pasta que o main.py.")
    exit()

# Define o pipeline de ML: transforma o texto em vetores e depois aplica um classificador.
modelo_ia = Pipeline([
    ('vectorizer', TfidfVectorizer()),
    ('classifier', LogisticRegression(max_iter=1000))
])

# Treina o modelo com os dados do CSV.
modelo_ia.fit(df_treino['texto'], df_treino['urgencia'])

print("Modelo de IA treinado e pronto!")


app = FastAPI(
    title="API do Agente de Triagem Médica",
    description="Uma API que utiliza Machine Learning para classificar a urgência de sintomas.",
    version="1.2.0"
)

# Configura o CORS para permitir que o frontend (rodando em outra porta) acesse esta API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

class SintomasInput(BaseModel):
    texto_sintomas: str


def classificar_sintomas(texto: str) -> str:
    """Usa uma abordagem HÍBRIDA (regras + IA) para classificar o texto do sintoma."""
    
    texto_lower = texto.lower()
    
    # 1. Pré-filtro de regras para casos críticos que exigem urgência ALTA imediata.
    palavras_chave_alta = [
        "acidente", "avc", "boca torta", "convulsao", "convulsão", 
        "confusão mental", "coração acelerado", "corte profundo", "derrame", 
        "desmaio", "dor no peito", "dor excruciante", "engasgado", 
        "envenenamento", "facada", "fala arrastada", "falta de ar", 
        "fratura", "hemorragia", "infarto", "não consigo respirar", 
        "pancada na cabeça", "paralisia", "perda de consciência", 
        "pressão no peito", "queimadura grave", "rosto torto", 
        "sangramento", "sufocando", "traumatismo", "visão dupla",
        "baleado", "veneno", "suicidio"
    ]
    if any(keyword in texto_lower for keyword in palavras_chave_alta):
        return "Urgência ALTA. Sintoma crítico detectado. Busque atendimento presencial imediatamente!."

    # 2. Se não for um caso crítico, usa o modelo de Machine Learning treinado.
    previsao = modelo_ia.predict([texto_lower])[0]
    
    if previsao == "alta":
        return "Urgência ALTA. A análise sugere a necessidade de atendimento presencial imediato!"
    elif previsao == "media":
        return "Urgência MÉDIA. A análise sugere que uma teleconsulta ou consulta seja realizada para avaliação!"
    else: # previsao == "baixa"
        return "Urgência BAIXA. A análise sugere monitorar os sintomas. Se persistirem, procure um especialista."

@app.post("/triagem", summary="Executa a triagem de sintomas")
def executar_triagem(sintomas: SintomasInput):
    """Endpoint principal que filtra entradas antes de chamar a classificação."""
    
    texto_usuario = sintomas.texto_sintomas.lower().strip()
    palavras = texto_usuario.split()
    
    # Filtra saudações para uma resposta mais natural.
    if texto_usuario in SAUDACOES:
        return {"resultado_triagem": "Olá! Sou o assistente TrIAgem. Por favor, descreva seus sintomas para que eu possa ajudar."}

    # Filtra entradas de palavra única e muito curta.
    if len(palavras) == 1 and len(palavras[0]) < 4:
        return {"resultado_triagem": "Para fazer uma análise melhor, por favor, descreva seus sintomas com um pouco mais de detalhes."}

    # Se a entrada for válida, chama a função de classificação.
    resultado = classificar_sintomas(texto_usuario)
    return {"resultado_triagem": resultado}

# Bloco que permite a execução direta do script com "python main.py".
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)