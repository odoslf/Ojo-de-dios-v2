(() => {
  const form = document.getElementById('laia-chat-form');
  const input = document.getElementById('laia-chat-input');
  const log = document.getElementById('laia-chat-log');
  const status = document.getElementById('laia-chat-status');
  const clearButton = document.getElementById('laia-chat-clear');

  if (!form || !input || !log || !status || !clearButton) {
    return;
  }

  const conversation = [];

  function setStatus(text, kind = 'neutral') {
    status.textContent = text;
    status.dataset.state = kind;
  }

  function appendMessage(role, content) {
    const message = document.createElement('article');
    message.className = `chat-message ${role === 'user' ? 'user-message' : 'assistant-message'}`;
    const speaker = document.createElement('strong');
    speaker.textContent = role === 'user' ? 'Tú' : 'LaIA';
    const body = document.createElement('p');
    body.textContent = content;
    message.append(speaker, body);
    log.appendChild(message);
    log.scrollTop = log.scrollHeight;
  }

  function resetConversation() {
    conversation.length = 0;
    log.replaceChildren();
    appendMessage('assistant', 'Conversación reiniciada. Puedo ayudarte sin ejecutar módulos desde este chat.');
    setStatus('Listo');
    input.focus();
  }

  async function sendMessage(content) {
    const endpoint = form.dataset.chatEndpoint || '/api/ai/laia/chat';
    const messages = [...conversation, { role: 'user', content }];
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages, execute_local_ai: true, context: { source: 'ui_chat_tab' } }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw new Error(payload.detail || `HTTP ${response.status}`);
    }
    if (!payload.chat || typeof payload.chat.answer !== 'string') {
      throw new Error('Respuesta de chat inválida.');
    }
    return payload.chat.answer;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const content = input.value.trim();
    if (!content) {
      return;
    }
    input.value = '';
    appendMessage('user', content);
    conversation.push({ role: 'user', content });
    setStatus('Consultando LaIA local...', 'busy');
    form.querySelector('button[type="submit"]').disabled = true;
    try {
      const answer = await sendMessage(content);
      conversation.push({ role: 'assistant', content: answer });
      appendMessage('assistant', answer);
      setStatus('Respuesta recibida', 'ok');
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Error desconocido';
      appendMessage('assistant', `No pude completar la consulta local: ${message}`);
      setStatus('Error', 'error');
    } finally {
      form.querySelector('button[type="submit"]').disabled = false;
      input.focus();
    }
  });

  clearButton.addEventListener('click', resetConversation);
})();
