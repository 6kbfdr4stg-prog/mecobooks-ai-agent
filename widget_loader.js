(function () {
  // 1. Inject CSS
  const style = document.createElement('style');
  style.textContent = `
#haravan-chat-widget-container * {
    box-sizing: border-box;
  }

  #haravan-chat-widget-btn {
    position: fixed !important;
    bottom: 15px !important;
    /* Moved closer to bottom */
    left: 15px !important;
    /* Moved closer to left */
    right: auto !important;
    z-index: 2147483647 !important;
    /* Max Z-Index */
    width: 60px !important;
    height: 60px !important;
    border-radius: 50% !important;
    background-color: #0084ff !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    cursor: pointer;
    display: flex !important;
    align-items: center;
    justify-content: center;
    transition: transform 0.2s;
  }

  #haravan-chat-widget-btn:hover {
    transform: scale(1.05);
  }

  #haravan-chat-widget-btn svg {
    width: 32px;
    height: 32px;
    fill: white;
  }

  #haravan-chat-window {
    display: none;
    position: fixed;
    bottom: 170px;
    /* Above the button */
    left: 30px;
    /* Match button position */
    right: auto;
    width: 350px;
    height: 500px;
    max-height: 80vh;
    background: white;
    border-radius: 12px;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
    z-index: 2147483647;
    flex-direction: column;
    overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }

  #haravan-chat-header {
    background: #0084ff;
    color: white;
    padding: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
  }

  #haravan-chat-close {
    cursor: pointer;
    font-size: 20px;
    background: none;
    border: none;
    color: white;
  }

  #haravan-chat-messages {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
    background: #f0f2f5;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .h-message {
    max-width: 80%;
    padding: 10px 14px;
    border-radius: 18px;
    font-size: 14px;
    line-height: 1.4;
  }

  .h-bot {
    background: white;
    color: #050505;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
  }

  .h-user {
    background: #0084ff;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
  }

  #haravan-chat-input-area {
    padding: 12px;
    background: white;
    border-top: 1px solid #e4e6eb;
    display: flex;
    gap: 8px;
  }

  #haravan-chat-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 20px;
    outline: none;
    font-size: 14px;
  }

  #haravan-chat-send {
    background: #0084ff;
    color: white;
    border: none;
    border-radius: 20px;
    padding: 0 16px;
    cursor: pointer;
    font-weight: 600;
  }

  #haravan-chat-send:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .h-typing {
    font-style: italic;
    font-size: 12px;
    color: #65676b;
    margin-left: 10px;
    display: none;
  }

  /* Product Card Styles - Horizontal Layout */
  .h-product-card {
    display: flex;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 12px;
    background: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s;
  }

  .h-product-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .h-product-image-container {
    width: 80px;
    height: 80px;
    flex-shrink: 0;
  }

  .h-product-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .h-product-info {
    padding: 10px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-width: 0;
    /* Fix flex text overflow */
  }

  .h-product-title {
    font-weight: 600;
    font-size: 14px;
    margin-bottom: 4px;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .h-product-price {
    color: #d32f2f;
    font-weight: bold;
    font-size: 14px;
    margin-bottom: 6px;
  }

  .h-product-actions {
    display: flex;
    gap: 8px;
  }

  .h-btn {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 11px;
    text-decoration: none;
    font-weight: 500;
    display: inline-block;
    text-align: center;
  }

  .h-btn-view {
    background-color: #f5f5f5;
    color: #333;
    border: 1px solid #ddd;
  }

  .h-btn-buy {
    background-color: #d32f2f;
    color: white;
    border: 1px solid #d32f2f;
  }

  /* New styles for image upload */
  .haravan-chat-input-container {
    display: flex;
    align-items: center;
    border-top: 1px solid #eee;
    padding: 10px;
    background: #fff;
  }

  #haravan-chat-input {
    /* Reusing existing ID, but applying new styles */
    flex: 1;
    border: 1px solid #ddd;
    border-radius: 20px;
    padding: 10px 15px;
    outline: none;
  }

  #haravan-chat-send,
  #haravan-upload-btn {
    /* Reusing existing ID, adding new one */
    background: none;
    border: none;
    cursor: pointer;
    color: #0084ff;
    font-size: 20px;
    margin-left: 10px;
    padding: 5px;
  }

  #haravan-upload-btn {
    color: #555;
  }

  #haravan-image-preview-container {
    display: none;
    padding: 10px;
    background: #f9f9f9;
    border-top: 1px solid #eee;
    position: relative;
  }

  #haravan-image-preview {
    max-height: 100px;
    border-radius: 5px;
    border: 1px solid #ddd;
  }

  #haravan-remove-image-btn {
    position: absolute;
    top: 5px;
    left: 5px;
    background: rgba(0, 0, 0, 0.5);
    color: white;
    border: none;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    cursor: pointer;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  `;
  document.head.appendChild(style);

  // 2. Inject HTML
  const container = document.createElement('div');
  container.id = 'haravan-widget-root';
  container.innerHTML = `
<div id="haravan-chat-widget-container">
  <div id="haravan-chat-widget-btn">
    <img src="https://cdn-icons-png.flaticon.com/512/724/724715.png" alt="Chat"
      style="width: 30px; height: 30px; filter: brightness(0) invert(1);" />
  </div>

  <div id="haravan-chat-window">
    <div id="haravan-chat-header">
      <span>Trợ lý ảo</span>
      <button id="haravan-chat-close">✕</button>
    </div>
    <div id="haravan-chat-messages">
      <div class="h-message h-bot">Xin chào! Tôi có thể giúp gì cho bạn hôm nay?</div>
    </div>
    <div class="h-typing" id="h-typing">Đang trả lời...</div>

    
    <div id="haravan-image-preview-container">
      <img id="haravan-image-preview" src="#" alt="Image Preview" style="display: block;" />
      <button id="haravan-remove-image-btn">×</button>
    </div>

    <div class="haravan-chat-input-container">
      
      <input type="file" id="haravan-image-input" accept="image/*" style="display: none;">

      
      <button id="haravan-upload-btn">📎</button>
      <input type="text" id="haravan-chat-input" placeholder="Nhập tin nhắn...">
      <button id="haravan-chat-send">➤</button>
    </div>
  </div>
</div>
  `;
  document.body.appendChild(container);

  // 3. Run Logic
  const API_URL = "https://mecobooks-ai-agent.onrender.com/chat";
  const IMAGE_UPLOAD_API_URL = "https://mecobooks-ai-agent.onrender.com/chat";

  // Image Upload Elements
  const haravanUploadBtn = document.getElementById('haravan-upload-btn');
  const haravanImageInput = document.getElementById('haravan-image-input');
  const haravanImagePreviewContainer = document.getElementById('haravan-image-preview-container');
  const haravanImagePreview = document.getElementById('haravan-image-preview');
  const haravanRemoveImageBtn = document.getElementById('haravan-remove-image-btn');

  // Add Event Listeners (Fix for inline onclick warnings)
  document.getElementById('haravan-chat-widget-btn').addEventListener('click', toggleHaravanChat);
  document.getElementById('haravan-chat-close').addEventListener('click', toggleHaravanChat);
  document.getElementById('haravan-chat-send').addEventListener('click', sendHMessage);

  document.getElementById('haravan-chat-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendHMessage();
  });

  let selectedImageFile = null;

  function toggleHaravanChat() {
    const w = document.getElementById('haravan-chat-window');
    const input = document.getElementById('haravan-chat-input');
    if (w.style.display === 'flex') {
      w.style.display = 'none';
    } else {
      w.style.display = 'flex';
      setTimeout(() => input.focus(), 100);
    }
  }

  function handleHKeyPress(e) {
    if (e.key === 'Enter') sendHMessage();
  }

  function appendHMessage(text, isUser) {
    const container = document.getElementById('haravan-chat-messages');
    const div = document.createElement('div');
    div.className = `h-message ${isUser ? 'h-user' : 'h-bot'}`;
    // User innerHTML to render links and images from bot
    div.innerHTML = text;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
  }

  // Handle File Selection
  haravanUploadBtn.addEventListener('click', () => haravanImageInput.click());

  haravanImageInput.addEventListener('change', (e) => {
    if (e.target.files) {
      if (e.target.files[0]) {
        handleImageSelect(e.target.files[0]);
      }
    }
  });

  // Handle Paste (Clipboard)
  document.getElementById('haravan-chat-input').addEventListener('paste', (e) => {
    const items = (e.clipboardData || e.originalEvent.clipboardData).items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const blob = items[i].getAsFile();
        handleImageSelect(blob);
        e.preventDefault(); // Prevent pasting the image binary text
        break;
      }
    }
  });

  function handleImageSelect(file) {
    selectedImageFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      haravanImagePreview.src = e.target.result;
      haravanImagePreviewContainer.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }

  haravanRemoveImageBtn.addEventListener('click', () => {
    selectedImageFile = null;
    haravanImageInput.value = '';
    haravanImagePreviewContainer.style.display = 'none';
  });

  async function sendHMessage() {
    const input = document.getElementById('haravan-chat-input');
    const text = input.value.trim();
    if (!text) {
      if (!selectedImageFile) return;
    }

    // Display User Message
    if (selectedImageFile) {
      appendHMessage(text + " [Đang gửi ảnh...]", true);
      // Could display the image in chat history here too
    } else {
      appendHMessage(text, true);
    }

    input.value = '';
    const currentImageFile = selectedImageFile; // Snapshot for sending

    // Clear preview after sending
    selectedImageFile = null;
    haravanImageInput.value = '';
    haravanImagePreviewContainer.style.display = 'none';

    document.getElementById('h-typing').style.display = 'block';
    const sendBtn = document.getElementById('haravan-chat-send');
    sendBtn.disabled = true;

    try {
      const formData = new FormData();
      // If there's text, send it. If only image, send placeholder text "Gửi ảnh" so backend validation passes
      // If there's text AND image, send the text.
      let messageContent = text;
      if (!text) {
        if (selectedImageFile) {
          messageContent = "Gửi ảnh";
        }
      }

      // Generate or retrieve Session ID
      let sessionId = localStorage.getItem('haravan_chat_session_id');
      if (!sessionId) {
        sessionId = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
          var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
          return v.toString(16);
        });
        localStorage.setItem('haravan_chat_session_id', sessionId);
      }

      formData.append('message', messageContent);
      formData.append('user_id', sessionId);

      if (currentImageFile) {
        formData.append('file', currentImageFile);
      }

      const res = await fetch(API_URL, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      appendHMessage(data.response, false);
    } catch (err) {
      console.error(err);
      appendHMessage("Lỗi kết nối server!", false);
    } finally {
      document.getElementById('h-typing').style.display = 'none';
      sendBtn.disabled = false;
    }
  }

})();
