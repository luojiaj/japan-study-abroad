(function () {
  const root = document.getElementById('sl-chat');
  if (!root) return;

  const welcome = root.getAttribute('data-welcome') || '您好，我是留学小助手，有什么问题都可以咨询我哦！';
  const humanUrl = root.getAttribute('data-human-url') || '/contact';
  const sessionKey = 'sl_chat_session_id';
  let sessionId = localStorage.getItem(sessionKey);
  if (!sessionId) {
    sessionId = (crypto && crypto.randomUUID)
      ? crypto.randomUUID()
      : `${Date.now().toString(36)}${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem(sessionKey, sessionId);
  }

  root.innerHTML = `
    <button class="sl-chat-fab" aria-label="打开聊天" title="智能助手">
      <span style="font-size:22px; line-height:1">💬</span>
    </button>
    <div class="sl-chat-window" role="dialog" aria-label="智能助手聊天窗口" aria-modal="false">
      <div class="sl-chat-header">
        <div class="title">樱路留学助手</div>
        <button class="sl-chat-close" aria-label="关闭">✕</button>
      </div>
      <div class="sl-chat-body"></div>
      <div class="sl-chat-hint">提示：我只回答常见问题；复杂情况会建议你转人工客服。</div>
      <div class="sl-chat-footer">
        <input class="sl-chat-input" type="text" placeholder="请输入你的问题…" />
        <button class="sl-chat-send">发送</button>
      </div>
    </div>
  `;

  const fab = root.querySelector('.sl-chat-fab');
  const win = root.querySelector('.sl-chat-window');
  const closeBtn = root.querySelector('.sl-chat-close');
  const body = root.querySelector('.sl-chat-body');
  const input = root.querySelector('.sl-chat-input');
  const sendBtn = root.querySelector('.sl-chat-send');

  function appendMsg(role, text) {
    const wrap = document.createElement('div');
    wrap.className = 'sl-chat-msg ' + role;
    const bubble = document.createElement('div');
    bubble.className = 'sl-chat-bubble';
    bubble.textContent = text;
    wrap.appendChild(bubble);
    body.appendChild(wrap);
    body.scrollTop = body.scrollHeight;
  }

  function appendQuickChips() {
    const container = document.createElement('div');
    container.className = 'sl-chat-quick';
    const chips = [
      '你们主要做什么服务？',
      'SGU 是什么？',
      '申请修士需要准备什么？',
      '什么时候开始准备？'
    ];
    chips.forEach(q => {
      const chip = document.createElement('button');
      chip.type = 'button';
      chip.className = 'sl-chat-chip';
      chip.textContent = q;
      chip.addEventListener('click', () => {
        input.value = q;
        input.focus();
        send();
      });
      container.appendChild(chip);
    });
    body.appendChild(container);
  }

  async function askBackend(question) {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, session_id: sessionId })
    });
    if (!res.ok) throw new Error('Network error');
    return await res.json();
  }

  async function send() {
    const q = (input.value || '').trim();
    if (!q) return;
    input.value = '';
    appendMsg('user', q);

    try {
      const data = await askBackend(q);
      appendMsg('bot', data.answer || '我暂时没法回答这个问题。');
      if (data.handoff) {
        const tip = `如需转人工客服，请前往：${humanUrl}`;
        appendMsg('bot', tip);
      }
    } catch (e) {
      appendMsg('bot', '网络开小差了，请稍后再试，或直接转人工客服。');
      appendMsg('bot', `人工入口：${humanUrl}`);
    }
  }

  function open() {
    win.classList.add('open');
    body.innerHTML = '';
    appendMsg('bot', welcome);
    appendQuickChips();
    setTimeout(() => input.focus(), 30);
  }

  function close() {
    win.classList.remove('open');
  }

  fab.addEventListener('click', () => {
    if (win.classList.contains('open')) close();
    else open();
  });
  closeBtn.addEventListener('click', close);

  // 首页自动弹出聊天窗口
  if (window.location.pathname === '/') {
    setTimeout(() => open(), 1500);
  }

  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') send();
    if (e.key === 'Escape') close();
  });
})();
