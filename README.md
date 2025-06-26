# Plataforma de Teleorientação Médica Comunitária - TrIAgem

Este repositório contém o código-fonte do projeto da disciplina de Sistemas Distribuídos, que visa desenvolver uma plataforma de triagem e encaminhamento para consultas em comunidades remotas.

---

## 1. O Problema: A Distância que Custa Vidas

> "Imagine uma aldeia rural onde os pacientes percorrem dezenas de quilômetros para falar com um médico. Muitas vezes, em casos de urgência, esse deslocamento salva ou custa vidas."

Em muitas comunidades remotas, a falta de acesso imediato a serviços de saúde é um problema crítico. O diagnóstico tardio, causado por longas filas e transporte precário, agrava condições de saúde e sobrecarrega os postos de saúde urbanos com casos que poderiam ser triados remotamente.

---

## 2. A Solução: Uma Ponte Digital para a Saúde

Nossa solução é uma plataforma web que realiza uma triagem inicial através de um chatbot inteligente. Com base na descrição dos sintomas do usuário, o sistema classifica a urgência e pode sugerir os próximos passos ou o contato com profissionais adequados.

### Fluxo do usuário:

1. O paciente acessa o portal via celular ou computador.
2. Um chatbot interativo o recebe e solicita a descrição dos seus sintomas.
3. Nossos agentes de Inteligência Artificial analisam as respostas para classificar a urgência do caso.
4. Com base na análise, o sistema fornece uma orientação sobre o nível de urgência e as ações recomendadas.

---

## 3. Arquitetura (Estado Atual)

No momento, o projeto possui dois componentes principais desenvolvidos e funcionais, prontos para serem integrados ao restante do sistema:

- **Frontend:** Uma interface de chat desenvolvida em HTML, CSS e JavaScript, onde o usuário interage e descreve seus sintomas.
- **Agente de IA de Triagem:** Um microserviço independente desenvolvido em Python com FastAPI. Ele utiliza um modelo de Machine Learning (treinado com `scikit-learn`) para receber o texto dos sintomas e retornar uma classificação de urgência (Baixa, Média ou Alta).

---

## 4. Tecnologias Utilizadas

| Categoria           | Tecnologias                                                              |
|---------------------|---------------------------------------------------------------------------|
| **Frontend**        | HTML5, CSS3, JavaScript                                                  |
| **Agente de IA**    | Python 3.13, FastAPI, Uvicorn, Pandas, Scikit-learn                      |
| **Containerização** | Docker, Docker Compose                                                   |
| **Controle de Versão** | Git, [GitHub](https://github.com/SamueelAbreu/TrIAgem-BOT)            |

> **Obs:** Todas as versões exatas das bibliotecas Python utilizadas estão listadas no arquivo [`/agent-triage/requirements.txt`](agent-triage/requirements.txt).

---

## 5. Como Executar (Estado Atual)

As instruções abaixo permitem testar os componentes já finalizados de forma isolada.

### ✅ Pré-requisitos

- Docker e Docker Compose  
- Python 3.13+  
- Git  
- VS Code com a extensão **Live Server**

---

### 🚀 Passos para Execução

#### Clone o repositório:

```bash
git clone https://github.com/SamueelAbreu/TrIAgem-BOT.git
cd TrIAgem-BOT
```

# Execute o Agente de IA de Triagem (Backend)

1. Navegue até a pasta do agente:

    ```bash
    cd agent-triage
    ```
    
2. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

3. Inicie o servidor da IA:

    ```bash
    uvicorn main:app --reload --port 8000
    ```

    O terminal deverá exibir a mensagem:
    ```
    Uvicorn running on http://127.0.0.1:8000
    ```

    Deixe este terminal aberto.

## Execute o Frontend

1. Abra a pasta `TrIAgem-BOT` no VS Code.

2. Navegue até a subpasta `frontend`.

3. Clique com o botão direito no arquivo `index.html`.

4. Selecione a opção "Open with Live Server".

---

### 🔄 Testando a Integração

Com o servidor da IA rodando no terminal e o frontend aberto no navegador, você pode usar o chat digitando os sintomas. As mensagens serão enviadas para o agente de IA e a classificação de urgência retornada por ele será exibida na tela.

---

Projeto desenvolvido para fins acadêmicos na disciplina de **Sistemas Distribuídos**.

