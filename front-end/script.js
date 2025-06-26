/**
 * @file script.js
 * @description Lógica do frontend para a plataforma TrIAgem.
 *
 * Responsabilidades:
 * 1. Capturar o texto do usuário e interagir com os elementos da página (DOM).
 * 2. Enviar os sintomas para a API de triagem via requisição assíncrona (fetch).
 * 3. Exibir as mensagens do usuário e do bot dinamicamente na interface.
 * 4. Gerenciar estados da UI (carregamento, erro) para uma melhor experiência.
 */

// Executa o script somente após o carregamento completo da página.
document.addEventListener('DOMContentLoaded', () => {

    // --- 1. SELEÇÃO DE ELEMENTOS GLOBAIS ---
    const symptomInput = document.getElementById('symptom-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    const API_URL = 'http://localhost:8000/triagem';

    // --- 2. FUNÇÕES AUXILIARES ---

    /**
     * Adiciona uma nova mensagem (do usuário ou do bot) na interface do chat.
     * @param {string} texto O conteúdo da mensagem a ser exibida.
     * @param {string} tipo O remetente da mensagem ('usuario' ou 'bot').
     */
    const adicionarMensagemNaTela = (texto, tipo) => {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('msg', tipo);

        const msgInnerHTML = (tipo === 'usuario')
            ? `
                <div class="texto">${texto}</div>
                <img src="assets/icone-triagem.png" alt="Ícone do usuário">
              `
            : `
                <img src="assets/icone-triagem.png" alt="Ícone do assistente TrIAgem">
                <div class="texto">${texto}</div>
              `;
        
        msgDiv.innerHTML = msgInnerHTML;
        chatMessages.appendChild(msgDiv);
        
        // Garante que a visualização do chat sempre role para a mensagem mais recente.
        chatMessages.scrollTop = chatMessages.scrollHeight;
    };

    /**
     * Habilita ou desabilita a interface de input durante a comunicação com a API.
     * @param {boolean} isLoading True para desabilitar (carregando), false para habilitar.
     */
    const gerenciarEstadoDeCarregamento = (isLoading) => {
        symptomInput.disabled = isLoading;
        sendButton.disabled = isLoading;
        symptomInput.placeholder = isLoading ? "Analisando..." : "Digite seus sintomas aqui...";
    };


    // --- 3. FUNÇÃO PRINCIPAL DE PROCESSAMENTO ---

    /**
     * Captura o texto, envia para a API e gerencia a exibição da resposta.
     */
    const processarEnvioDeSintomas = async () => {
        const textoSintoma = symptomInput.value.trim();
        if (!textoSintoma) return;

        // Atualiza a interface com a mensagem do usuário e limpa o campo.
        adicionarMensagemNaTela(textoSintoma, 'usuario');
        symptomInput.value = '';
        
        // Bloqueia a interface para evitar envios duplicados enquanto aguarda a resposta.
        gerenciarEstadoDeCarregamento(true);

        try {
            // Envia a requisição para a API e aguarda a resposta.
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texto_sintomas: textoSintoma })
            });

            if (!response.ok) {
                throw new Error(`Erro na API: ${response.statusText}`);
            }

            const data = await response.json();
            adicionarMensagemNaTela(data.resultado_triagem, 'bot');

        } catch (error) {
            // Em caso de falha, informa o usuário sobre o erro.
            console.error("Falha na comunicação com a API:", error);
            adicionarMensagemNaTela('Desculpe, ocorreu um erro de comunicação. Por favor, tente novamente mais tarde.', 'bot');
        } finally {
            // Independente de sucesso ou falha, reabilita a interface para o usuário.
            gerenciarEstadoDeCarregamento(false);
            symptomInput.focus();
        }
    };


    // --- 4. EVENT LISTENERS ---

    // Associa a função de envio ao evento de clique do botão.
    sendButton.addEventListener('click', processarEnvioDeSintomas);

    // Permite que o usuário envie a mensagem com a tecla 'Enter'.
    symptomInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Previne a quebra de linha no textarea.
            processarEnvioDeSintomas();
        }
    });

});