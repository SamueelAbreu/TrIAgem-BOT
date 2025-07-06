# Plataforma de Teleorientação Médica Comunitária - TrIAgem

Este repositório contém o código-fonte do projeto da disciplina de **Sistemas Distribuídos**, que visa desenvolver uma plataforma de triagem e encaminhamento para consultas em comunidades remotas.

**Instituição:** Universidade Federal de Lavras (UFLA)  
**Autores:**
* André Araújo
* Luiz Carlos de Paiva Silva
* Samuel Moreira Abreu
* Sandy Karolina Maciel

---

## 1. O Problema: A Distância que Custa Vidas

> "Imagine uma aldeia rural onde os pacientes percorrem dezenas de quilômetros para falar com um médico. Muitas vezes, em casos de urgência, esse deslocamento salva ou custa vidas."

Em muitas comunidades remotas, a falta de acesso imediato a serviços de saúde é um problema crítico. O diagnóstico tardio, causado por longas filas e transporte precário, agrava condições de saúde e sobrecarrega os postos de saúde urbanos com casos que poderiam ser triados remotamente.

## Referências

A relevância do problema abordado por este projeto é sustentada por políticas públicas, dados oficiais e estudos que evidenciam os desafios no acesso à saúde em regiões remotas do Brasil.

* **Portaria GM/MS nº 1.348, de 2 de junho de 2022:** Documento do Ministério da Saúde que regulamenta a prática da Telessaúde no Brasil, validando a abordagem tecnológica do projeto como uma política de saúde atual. Disponível em: [https://www.in.gov.br/en/web/dou/-/portaria-gm/ms-n-1.348-de-2-de-junho-de-2022-405902354](https://www.in.gov.br/en/web/dou/-/portaria-gm/ms-n-1.348-de-2-de-junho-de-2022-405902354)

* **Pesquisa Nacional de Saúde (PNS) - IBGE:** A mais completa pesquisa sobre a saúde dos brasileiros, cujos dados demonstram a disparidade no acesso a serviços médicos entre zonas urbanas e rurais. Disponível em: [https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html](https://www.ibge.gov.br/estatisticas/sociais/saude/9160-pesquisa-nacional-de-saude.html)

* **Acesso e cobertura da Atenção Primária à Saúde para populações rurais e urbanas:** Estudo científico que analisa e comprova as barreiras enfrentadas por populações rurais para acessar serviços de saúde na região norte do Brasil. Publicado na revista "Saúde em Debate". Disponível em: [https://www.scielo.br/j/sdeb/a/hFrUcLr3dYV9k8pWw8j5zfg/](https://www.scielo.br/j/sdeb/a/hFrUcLr3dYV9k8pWw8j5zfg/)

* **Estudo revela vazios assistenciais e dificuldade de acesso à saúde (Agência Brasil):** Reportagem que ilustra com dados e relatos a existência de "vazios assistenciais" no país, tornando o problema abordado pelo projeto mais tangível. Disponível em: [https://agenciabrasil.ebc.com.br/saude/noticia/2023-05/estudo-revela-vazios-assistenciais-e-dificuldade-de-acesso-saude](https://agenciabrasil.ebc.com.br/saude/noticia/2023-05/estudo-revela-vazios-assistenciais-e-dificuldade-de-acesso-saude)

---

## 2. A Solução: Uma Ponte Digital para a Saúde

Nossa solução é uma plataforma web que realiza uma triagem inicial através de um chatbot inteligente. O sistema utiliza uma arquitetura de microserviços para analisar os sintomas do usuário, classificar a urgência e fornecer orientações detalhadas.

### Fluxo do usuário:

1.  O paciente acessa o portal via celular ou computador.
2.  Um chatbot interativo o recebe e solicita a descrição dos seus sintomas.
3.  Nossos agentes de Inteligência Artificial analisam as respostas para classificar a urgência do caso.
4.  Com base na análise, o sistema fornece orientações sobre o nível de urgência, cuidados imediatos e sugestões de locais para atendimento.

---
## 3. Arquitetura Detalhada: Da Concepção à Implementação

A seguir, detalhamos a evolução da arquitetura do projeto, desde a concepção inicial até a versão final implementada, que visa mitigar os riscos e garantir maior robustez e escalabilidade.

### Visão Arquitetônica Inicial (Pré-Modelagem de Ameaças)

Nesta fase inicial, o sistema foi concebido como uma aplicação monolítica, priorizando a simplicidade e a rapidez no desenvolvimento para validar a ideia central.

* **Componentes:**
    * **Aplicação Frontend:** Uma interface de usuário única (Single Page Application) construída com HTML, CSS e JavaScript.
    * **Aplicação Backend Monolítica:** Um único servidor em Python com FastAPI que conteria todas as responsabilidades:
        * Receber as requisições da API.
        * Carregar e executar o modelo de Machine Learning para triagem.
        * Conter a lógica de regras para as recomendações médicas.
        * Servir a própria aplicação frontend.

* **Comunicação:**
    * A comunicação seria direta entre o navegador do cliente e o servidor monolítico via chamadas de API REST.

* **Fluxo de Dados:**
    1.  O usuário digita os sintomas no Frontend.
    2.  Uma chamada de API é feita para um endpoint `/analisar` no Backend.
    3.  O Backend executa o modelo de triagem e, em seguida, a lógica de recomendação na mesma requisição.
    4.  A resposta consolidada é devolvida ao Frontend.

* **Pontos Fracos (Ameaças Identificadas):**
    * **Ponto Único de Falha:** Se qualquer parte do backend falhasse (ex: erro no carregamento do modelo de ML), toda a aplicação ficaria indisponível.
    * **Baixa Escalabilidade:** Seria difícil escalar apenas uma parte do sistema (ex: a triagem) sem escalar a aplicação inteira.
    * **Complexidade Acoplada:** Manutenção e desenvolvimento de novas funcionalidades se tornariam progressivamente mais difíceis.
    * **Exposição Direta:** O serviço principal ficaria diretamente exposto à internet, aumentando a superfície de ataque.

---

### Visão Arquitetônica Final (Pós-Implementação e Mitigação)

Após a análise dos riscos, o sistema foi reimaginado como uma arquitetura de microserviços distribuídos, orquestrada por um API Gateway e servida através de um proxy reverso.

* **Componentes:**
    * **Frontend (Client-Side Application):** Interface de usuário desacoplada, servida como arquivos estáticos.
    * **Proxy Reverso (Nginx):** Atua como a porta de entrada para todo o tráfego, servindo os arquivos do frontend e redirecionando as chamadas de API.
    * **API Gateway:** Ponto de entrada para a lógica de backend, orquestrando as chamadas para os microserviços internos.
    * **Agente de Triagem (Microserviço):** Serviço autônomo com a única responsabilidade de classificar a urgência.
    * **Agente de Recomendações (Microserviço):** Serviço autônomo para gerar recomendações e consultar seu banco de dados SQLite.
    * **Rede Privada (Docker Network):** Rede virtual que isola os serviços de backend do acesso externo direto.

* **Comunicação e Fluxo:**
    1.  O usuário interage com o **Frontend**.
    2.  O **Nginx** recebe a requisição e a encaminha para o **API Gateway**.
    3.  O **Gateway** chama o **Agente de Triagem**.
    4.  Com a resposta, o **Gateway** chama o **Agente de Recomendações**.
    5.  O **Gateway** consolida a resposta e a retorna ao usuário.

* **Medidas de Mitigação Implementadas:**
    * **Disponibilidade:** A falha em um agente não derruba o sistema todo.
    * **Escalabilidade:** Cada microserviço pode ser escalado de forma independente.
    * **Segurança:** A infraestrutura interna é protegida pela rede privada do Docker e pelo Gateway, minimizando a superfície de ataque.
    * **Manutenibilidade:** Cada serviço pode ser atualizado e implantado de forma independente.

---

## 4. Arquitetura de Microserviços

O projeto é construído sobre uma arquitetura de microserviços, garantindo escalabilidade e separação de responsabilidades. Os componentes principais são:

-   **Frontend:** Uma interface de chat desenvolvida em HTML, CSS e JavaScript, servida por um contêiner Nginx que também atua como proxy reverso para as APIs.

-   **API Gateway:** O ponto de entrada único para o backend. Ele recebe as requisições do frontend e orquestra a comunicação entre os outros agentes, garantindo que a informação flua na ordem correta.

-   **Agente de Triagem:** Um microserviço de IA que utiliza um modelo de Machine Learning (`scikit-learn`) para analisar o texto dos sintomas e classificar a urgência em Baixa, Média ou Alta.

-   **Agente de Recomendações:** Após a triagem, este serviço recebe o nível de urgência e os sintomas para:
    -   Fornecer orientações detalhadas e cuidados específicos.
    -   Consultar um banco de dados **SQLite** para sugerir médicos e postos de saúde fictícios na região.

---

## 5. Tecnologias Utilizadas

| Categoria | Tecnologias |
| :--- | :--- |
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend (Microserviços)** | Python, FastAPI, Pandas, Scikit-learn, SQLite |
| **Gateway** | Python, FastAPI, HTTPX |
| **Servidor Web / Proxy** | Nginx |
| **Containerização** | Docker, Docker Compose |
| **Controle de Versão** | Git, GitHub |

---

## 6. Como Executar o Projeto Completo

As instruções abaixo explicam como executar a plataforma completa, com todos os microserviços, utilizando Docker. Este é o único método recomendado, pois gerencia todas as dependências e redes automaticamente.

### ✅ Pré-requisitos

-   **Docker e Docker Compose:** Essencial. [Instale o Docker Desktop](https://docs.docker.com/engine/install/), que já inclui o Compose.
-   **Git:** Para clonar o repositório.
-   **Python:** Necessário apenas para executar um script de setup inicial.

---

### 🚀 Passos para Execução

#### 1. Clone o Repositório
Abra seu terminal e clone o projeto para a sua máquina.

```bash
git clone [https://github.com/SamueelAbreu/TrIAgem-BOT.git](https://github.com/SamueelAbreu/TrIAgem-BOT.git)
cd TrIAgem-BOT
```

#### 2. Crie o Banco de Dados (Setup Único)
O Agente de Recomendações precisa de um banco de dados com uma lista de médicos. Incluímos um script para gerar este arquivo para você.

```bash
# Entre na pasta do agente de recomendações
cd agente_recomendações

# Execute o script Python para criar o banco
python create_database.py

# Volte para a pasta raiz do projeto
cd ..
```
Você verá a mensagem "Banco de dados 'medicos.db' criado e populado com sucesso."

#### 3. Construa e Inicie os Contêineres
Este é o comando principal que "liga" todo o sistema.

```bash
docker-compose up --build
```
O terminal ficará ocupado, mostrando os logs de todos os serviços sendo construídos e iniciados. Aguarde até que as mensagens se estabilizem e você veja os servidores rodando (ex: `Uvicorn running on http://0.0.0.0:8080`).

**Importante:** Não feche esta janela do terminal! Ela mantém a aplicação no ar.

#### 4. Acesse a Aplicação
Com os contêineres rodando, abra seu navegador e acesse:

**`http://localhost`**

A interface do chat da TrIAgem estará pronta para uso. Digite os sintomas, envie e veja a plataforma em ação!

#### 5. Como Parar a Aplicação
Para desligar todos os serviços, volte ao terminal e pressione **`Ctrl + C`**. Para remover os contêineres, execute `docker-compose down`.

---



