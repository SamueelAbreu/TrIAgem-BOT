/**
 * @file script.js
 * @description Lógica do frontend para a plataforma TrIAgem.
 */

document.addEventListener('DOMContentLoaded', () => {

    const symptomInput = document.getElementById('symptom-input');
    const sendButton = document.getElementById('send-button');
    const chatMessages = document.getElementById('chat-messages');
    
    // Aponta para o endpoint do Gateway, que será redirecionado pelo Nginx.
    const API_URL = '/api/triagem-completa';

    /**
     * Adiciona uma nova mensagem (do usuário ou do bot) na interface do chat.
     */
    const adicionarMensagemNaTela = (htmlContent, tipo) => {
        const msgDiv = document.createElement('div');
        msgDiv.classList.add('msg', tipo);

        const msgInnerHTML = (tipo === 'usuario')
            ? `
                <div class="texto">${htmlContent}</div>
                <img src="assets/icone-triagem.png" alt="Ícone do usuário">
              `
            : `
                <img src="assets/icone-triagem.png" alt="Ícone do assistente TrIAgem">
                <div class="texto">${htmlContent}</div>
              `;
        
        msgDiv.innerHTML = msgInnerHTML;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll
        return msgDiv;
    };
    
    /**
     * Formata a resposta completa da API em um HTML legível.
     */
    const formatarRespostaCompleta = (data) => {
        let htmlResponse = `<p><strong>Resultado da Triagem:</strong> ${data.resultado_triagem}</p>`;
        
        const rec = data.recomendacoes;
        if (rec) {
            htmlResponse += `<p><em>${rec.observacoes || ''}</em></p>`;
            
            if (rec.recomendacoes_gerais) {
                htmlResponse += `<h4>Orientações Gerais</h4><ul>`;
                Object.values(rec.recomendacoes_gerais).forEach(category => {
                    if (Array.isArray(category)) {
                        category.forEach(item => { htmlResponse += `<li>${item}</li>`; });
                    }
                });
                htmlResponse += `</ul>`;
            }

            if (rec.recomendacoes_especificas && rec.recomendacoes_especificas.length > 0) {
                htmlResponse += `<h4>Dicas para seus sintomas</h4><ul>`;
                rec.recomendacoes_especificas.forEach(item => { htmlResponse += `<li>${item}</li>`; });
                htmlResponse += `</ul>`;
            }
            
            if (rec.medicos_recomendados && rec.medicos_recomendados.length > 0) {
                 htmlResponse += `<h4>Sugestões de Atendimento</h4>`;
                 rec.medicos_recomendados.forEach(medico => {
                     htmlResponse += `
                        <div class="medico-card">
                            <strong>${medico.nome_local}</strong><br>
                            <small>${medico.especialidade}</small><br>
                            <span>${medico.endereco}</span><br>
                            <span>Tel: ${medico.telefone || 'Não informado'}</span>
                        </div>`;
                 });
            }
        }
        return htmlResponse;
    }


    /**
     * Habilita ou desabilita a interface de input durante a comunicação com a API.
     */
    const gerenciarEstadoDeCarregamento = (isLoading) => {
        symptomInput.disabled = isLoading;
        sendButton.disabled = isLoading;
        symptomInput.placeholder = isLoading ? "Analisando..." : "Digite seus sintomas aqui...";
    };

    /**
     * Captura o texto, envia para a API e gerencia a exibição da resposta.
     */
    const processarEnvioDeSintomas = async () => {
        const textoSintoma = symptomInput.value.trim();
        if (!textoSintoma) return;

        // O conteúdo da mensagem do usuário é apenas o texto, não mais HTML.
        adicionarMensagemNaTela(textoSintoma, 'usuario');
        symptomInput.value = '';
        
        gerenciarEstadoDeCarregamento(true);
        // Adiciona um indicador de "digitando" para melhor feedback visual.
        const typingIndicator = adicionarMensagemNaTela(`<div class="typing-indicator"><span></span><span></span><span></span></div>`, 'bot');

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ texto_sintomas: textoSintoma })
            });

            chatMessages.removeChild(typingIndicator);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Erro na API: ${response.statusText}`);
            }

            const data = await response.json();
            const respostaFormatada = formatarRespostaCompleta(data);
            adicionarMensagemNaTela(respostaFormatada, 'bot');

        } catch (error) {
            if (chatMessages.contains(typingIndicator)) {
                chatMessages.removeChild(typingIndicator);
            }
            console.error("Falha na comunicação com a API:", error);
            adicionarMensagemNaTela(`Desculpe, ocorreu um erro de comunicação. Por favor, tente novamente mais tarde. <br><small>${error.message}</small>`, 'bot');
        } finally {
            gerenciarEstadoDeCarregamento(false);
            symptomInput.focus();
        }
    };

    const style = document.createElement('style');
    style.innerHTML = `
        .typing-indicator span { height: 8px; width: 8px; background-color: #9BAEC9; border-radius: 50%; display: inline-block; animation: bounce 1.4s infinite ease-in-out both; }
        .typing-indicator span:nth-of-type(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-of-type(2) { animation-delay: -0.16s; }
        @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1.0); } }
        .medico-card { border-left: 3px solid var(--cor-enviar); padding-left: 10px; margin-top: 10px; font-size: 0.95rem; }
        .medico-card small { color: #ccc; }
    `;
    document.head.appendChild(style);

    sendButton.addEventListener('click', processarEnvioDeSintomas);

    symptomInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            processarEnvioDeSintomas();
        }
    });
});