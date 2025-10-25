// AI Chat JavaScript Functionality
class AIChat {
  constructor() {
    this.currentChatId = null;
    this.chatHistory = JSON.parse(
      localStorage.getItem("ai_chat_history") || "[]"
    );
    this.uploadedFiles = [];
    this.selectedTool = null;
    this.codeMode = false;

    this.initializeEventListeners();
    this.loadChatHistory();
    this.initializeAutoResize();
    this.checkForQuickQuestion();
  }

  initializeEventListeners() {
    const chatInput = document.getElementById("chatInput");
    const sendBtn = document.querySelector(".send-btn");

    // Send message on Enter (but allow Shift+Enter for new line)
    chatInput.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        this.sendMessage();
      }
    });

    // Auto-resize textarea
    chatInput.addEventListener("input", () => {
      this.autoResizeTextarea(chatInput);
    });

    // Send button click
    sendBtn.addEventListener("click", () => this.sendMessage());

    // File input change
    const fileInput = document.getElementById("fileInput");
    if (fileInput) {
      fileInput.addEventListener("change", (e) => this.handleFileUpload(e));
    }
  }

  initializeAutoResize() {
    const textarea = document.getElementById("chatInput");
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = textarea.scrollHeight + "px";
    }
  }

  autoResizeTextarea(textarea) {
    textarea.style.height = "auto";
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + "px";
  }

  async sendMessage() {
    const input = document.getElementById("chatInput");
    const message = input.value.trim();

    if (!message) return;

    // Add user message to chat
    this.addMessage("user", message);

    // Clear input
    input.value = "";
    this.autoResizeTextarea(input);

    // Show loading
    this.showLoading();

    try {
      // Prepare request data
      const requestData = {
        message: message,
        chat_id: this.currentChatId,
        files: this.uploadedFiles,
        tool: this.selectedTool,
        code_mode: this.codeMode,
      };

      console.log("📤 Sending message with code_mode:", this.codeMode);

      // Send to backend
      const response = await fetch("/ai-chat/send", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from AI");
      }

      const data = await response.json();

      // Add AI response to chat
      this.addMessage("assistant", data.response, data.code_blocks);

      // Update chat ID if new chat
      if (data.chat_id && !this.currentChatId) {
        this.currentChatId = data.chat_id;
        this.updateChatHistory();
      }
    } catch (error) {
      console.error("Error:", error);
      this.addMessage(
        "assistant",
        "Sorry, I encountered an error. Please try again."
      );
    } finally {
      this.hideLoading();
    }
  }

  addMessage(sender, content, codeBlocks = []) {
    const chatMessages = document.getElementById("chatMessages");
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${sender}`;

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.innerHTML =
      sender === "user"
        ? '<i class="fas fa-user"></i>'
        : '<i class="fas fa-robot"></i>';

    const messageContent = document.createElement("div");
    messageContent.className = "message-content";

    // Add copy button for assistant messages
    if (sender === "assistant") {
      const copyBtn = document.createElement("button");
      copyBtn.className = "copy-btn";
      copyBtn.innerHTML = '<i class="fas fa-copy"></i>';
      copyBtn.onclick = () => this.copyToClipboard(content);
      messageContent.appendChild(copyBtn);
    }

    const messageText = document.createElement("div");
    messageText.className = "message-text";

    // Process content for bullet points and code blocks
    let processedContent = this.processMessageContent(content);
    messageText.innerHTML = processedContent;

    // Add code blocks if any
    if (codeBlocks && codeBlocks.length > 0) {
      codeBlocks.forEach((block) => {
        const codeDiv = this.createCodeBlock(block.code, block.language);
        messageText.appendChild(codeDiv);
      });
    }

    messageContent.appendChild(messageText);

    const messageTime = document.createElement("div");
    messageTime.className = "message-time";
    messageTime.textContent = new Date().toLocaleTimeString();

    messageContent.appendChild(messageTime);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Highlight code if Prism is available
    if (typeof Prism !== "undefined") {
      Prism.highlightAll();
    }
  }

  processMessageContent(content) {
    // Convert bullet points to HTML
    let processed = content.replace(/\n• /g, "\n<li>");
    processed = processed.replace(/^• /gm, "<li>");

    // Wrap consecutive list items in ul tags
    processed = processed.replace(
      /(<li>.*<\/li>)/gs,
      '<ul class="bullet-points">$1</ul>'
    );

    // Convert line breaks to HTML
    processed = processed.replace(/\n/g, "<br>");

    return processed;
  }

  createCodeBlock(code, language = "") {
    const codeDiv = document.createElement("div");
    codeDiv.className = "code-block";

    const codeHeader = document.createElement("div");
    codeHeader.className = "code-header";

    const languageSpan = document.createElement("span");
    languageSpan.className = "code-language";
    languageSpan.textContent = language || "Code";

    const copyBtn = document.createElement("button");
    copyBtn.className = "code-copy-btn";
    copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy';
    copyBtn.onclick = () => this.copyToClipboard(code);

    codeHeader.appendChild(languageSpan);
    codeHeader.appendChild(copyBtn);

    const codeContent = document.createElement("pre");
    codeContent.className = "code-content";
    codeContent.textContent = code;

    codeDiv.appendChild(codeHeader);
    codeDiv.appendChild(codeContent);

    return codeDiv;
  }

  async copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      this.showToast("Copied to clipboard!");
    } catch (err) {
      console.error("Failed to copy: ", err);
      this.showToast("Failed to copy to clipboard");
    }
  }

  showToast(message) {
    const toast = document.createElement("div");
    toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
      toast.remove();
    }, 3000);
  }

  showNotification(message, type = "info") {
    const notification = document.createElement("div");
    const bgColor =
      type === "success" ? "#10b981" : type === "error" ? "#ef4444" : "#3b82f6";

    notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${bgColor};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 10000;
            font-size: 14px;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            max-width: 300px;
        `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      if (document.body.contains(notification)) {
        notification.remove();
      }
    }, 3000);
  }

  showLoading() {
    const loadingOverlay = document.getElementById("loadingOverlay");
    loadingOverlay.style.display = "flex";
  }

  hideLoading() {
    const loadingOverlay = document.getElementById("loadingOverlay");
    loadingOverlay.style.display = "none";
  }

  startNewChat() {
    this.currentChatId = null;
    this.uploadedFiles = [];
    this.selectedTool = null;
    this.codeMode = false;

    // Clear chat messages
    const chatMessages = document.getElementById("chatMessages");
    chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-content">
                    <i class="fas fa-robot"></i>
                    <h2>Welcome to AI Mentor!</h2>
                    <p>I'm here to help you with your lab issues, coding problems, and academic questions.</p>
                    <div class="quick-actions">
                        <button class="quick-btn" onclick="askQuickQuestion('How to fix Python import errors?')">
                            <i class="fas fa-code"></i> Python Help
                        </button>
                        <button class="quick-btn" onclick="askQuickQuestion('How to troubleshoot network connectivity?')">
                            <i class="fas fa-network-wired"></i> Network Issues
                        </button>
                        <button class="quick-btn" onclick="askQuickQuestion('How to optimize database queries?')">
                            <i class="fas fa-database"></i> Database Help
                        </button>
                    </div>
                </div>
            </div>
        `;

    this.updateToolStates();
  }

  toggleChatHistory() {
    const sidebar = document.getElementById("chatHistorySidebar");
    sidebar.classList.toggle("active");
  }

  loadChatHistory() {
    const historyList = document.getElementById("historyList");
    historyList.innerHTML = "";

    this.chatHistory.forEach((chat, index) => {
      const historyItem = document.createElement("div");
      historyItem.className = "history-item";
      if (chat.id === this.currentChatId) {
        historyItem.classList.add("active");
      }

      historyItem.innerHTML = `
                <div class="history-content" onclick="window.aiChat.loadChat('${
                  chat.id
                }')">
                  <div class="history-title">${chat.title}</div>
                  <div class="history-preview">${chat.preview}</div>
                  <div class="history-time">${new Date(
                    chat.timestamp
                  ).toLocaleString()}</div>
                </div>
                <div class="history-actions">
                  <button class="delete-chat-btn" onclick="event.stopPropagation(); window.aiChat.deleteChat('${
                    chat.id
                  }')" title="Delete chat">
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
            `;

      historyList.appendChild(historyItem);
    });
  }

  loadChat(chatId) {
    const chat = this.chatHistory.find((c) => c.id === chatId);
    if (!chat) return;

    this.currentChatId = chatId;

    // Clear current chat
    const chatMessages = document.getElementById("chatMessages");
    chatMessages.innerHTML = "";

    // Load chat messages
    chat.messages.forEach((msg) => {
      this.addMessage(msg.sender, msg.content, msg.code_blocks || []);
    });

    // Update history UI
    this.loadChatHistory();
    this.toggleChatHistory();
  }

  updateChatHistory() {
    if (!this.currentChatId) return;

    const chatMessages = document.querySelectorAll(".message");
    const messages = Array.from(chatMessages).map((msg) => ({
      sender: msg.classList.contains("user") ? "user" : "assistant",
      content: msg.querySelector(".message-text").textContent,
      code_blocks: [],
    }));

    const chatIndex = this.chatHistory.findIndex(
      (c) => c.id === this.currentChatId
    );
    const chatData = {
      id: this.currentChatId,
      title: messages[0]?.content.substring(0, 50) + "..." || "New Chat",
      preview:
        messages[0]?.content.substring(0, 100) + "..." || "New conversation",
      timestamp: new Date().toISOString(),
      messages: messages,
    };

    if (chatIndex >= 0) {
      this.chatHistory[chatIndex] = chatData;
    } else {
      this.chatHistory.unshift(chatData);
    }

    // Keep only last 50 chats
    if (this.chatHistory.length > 50) {
      this.chatHistory = this.chatHistory.slice(0, 50);
    }

    localStorage.setItem("ai_chat_history", JSON.stringify(this.chatHistory));
    this.loadChatHistory();
  }

  toggleFileUpload() {
    const fileUploadArea = document.getElementById("fileUploadArea");
    const isVisible = fileUploadArea.style.display !== "none";
    fileUploadArea.style.display = isVisible ? "none" : "block";
  }

  handleFileUpload(event) {
    const files = Array.from(event.target.files);
    files.forEach((file) => {
      if (file.size > 10 * 1024 * 1024) {
        // 10MB limit
        this.showToast("File too large. Maximum size is 10MB.");
        return;
      }

      this.uploadedFiles.push({
        name: file.name,
        size: file.size,
        type: file.type,
        content: null, // Will be populated when file is read
      });

      this.readFileContent(file, this.uploadedFiles.length - 1);
    });

    this.updateUploadedFilesDisplay();
  }

  readFileContent(file, index) {
    const reader = new FileReader();
    reader.onload = (e) => {
      this.uploadedFiles[index].content = e.target.result;
    };
    reader.readAsText(file);
  }

  updateUploadedFilesDisplay() {
    const uploadedFilesDiv = document.getElementById("uploadedFiles");
    uploadedFilesDiv.innerHTML = "";

    this.uploadedFiles.forEach((file, index) => {
      const fileDiv = document.createElement("div");
      fileDiv.className = "uploaded-file";
      fileDiv.innerHTML = `
                <i class="fas fa-file"></i>
                <span>${file.name}</span>
                <button class="remove-file" onclick="removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
      uploadedFilesDiv.appendChild(fileDiv);
    });
  }

  removeFile(index) {
    this.uploadedFiles.splice(index, 1);
    this.updateUploadedFilesDisplay();
  }

  toggleCodeMode() {
    this.codeMode = !this.codeMode;
    this.updateToolStates();
  }

  toggleGeminiTools() {
    const toolsPanel = document.getElementById("geminiToolsPanel");
    const isVisible = toolsPanel.style.display !== "none";
    toolsPanel.style.display = isVisible ? "none" : "block";
  }

  selectTool(tool) {
    this.selectedTool = tool;
    this.updateToolStates();
    this.toggleGeminiTools();
  }

  updateToolStates() {
    // Update code mode button
    const codeBtn = document.querySelector('[onclick="toggleCodeMode()"]');
    if (codeBtn) {
      codeBtn.classList.toggle("active", this.codeMode);
    }

    // Update tool selection
    document.querySelectorAll(".tool-option").forEach((btn) => {
      btn.classList.remove("active");
    });

    if (this.selectedTool) {
      const selectedBtn = document.querySelector(
        `[onclick="selectTool('${this.selectedTool}')"]`
      );
      if (selectedBtn) {
        selectedBtn.classList.add("active");
      }
    }
  }

  clearChat() {
    if (confirm("Are you sure you want to clear the current chat?")) {
      this.startNewChat();
    }
  }

  async deleteChat(chatId) {
    if (!chatId) return;

    if (
      confirm(
        "Are you sure you want to delete this chat? This action cannot be undone."
      )
    ) {
      try {
        const response = await fetch(`/ai-chat/delete/${chatId}`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          // Remove from chat history
          this.chatHistory = this.chatHistory.filter(
            (chat) => chat.id !== chatId
          );
          this.loadChatHistory();

          // If this was the current chat, start a new one
          if (this.currentChatId === chatId) {
            this.startNewChat();
          }

          this.showNotification("Chat deleted successfully", "success");
        } else {
          const error = await response.json();
          this.showNotification(
            error.error || "Failed to delete chat",
            "error"
          );
        }
      } catch (error) {
        console.error("Error deleting chat:", error);
        this.showNotification("Failed to delete chat", "error");
      }
    }
  }

  async deleteAllChats() {
    if (
      confirm(
        "Are you sure you want to delete ALL your chat history? This action cannot be undone."
      )
    ) {
      try {
        const response = await fetch("/ai-chat/delete-all", {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          },
        });

        if (response.ok) {
          const result = await response.json();
          this.chatHistory = [];
          this.loadChatHistory();
          this.startNewChat();
          this.showNotification(result.message, "success");
        } else {
          const error = await response.json();
          this.showNotification(
            error.error || "Failed to delete chats",
            "error"
          );
        }
      } catch (error) {
        console.error("Error deleting all chats:", error);
        this.showNotification("Failed to delete chats", "error");
      }
    }
  }

  checkForQuickQuestion() {
    const quickQuestion = localStorage.getItem("ai_quick_question");
    const codeMode = localStorage.getItem("ai_code_mode");

    if (quickQuestion) {
      // Clear the stored question
      localStorage.removeItem("ai_quick_question");

      // Enable code mode if specified
      if (codeMode === "true") {
        console.log("🔧 Enabling code mode from quick question");
        localStorage.removeItem("ai_code_mode");
        this.toggleCodeMode();
        console.log("💻 Code mode enabled:", this.codeMode);
      }

      // Set the input value and send the message
      setTimeout(() => {
        const chatInput = document.getElementById("chatInput");
        if (chatInput) {
          chatInput.value = quickQuestion;
          this.sendMessage();
        }
      }, 500);
    }
  }
}

// Global functions for HTML onclick handlers
function startNewChat() {
  window.aiChat.startNewChat();
}

function toggleChatHistory() {
  window.aiChat.toggleChatHistory();
}

function toggleFileUpload() {
  window.aiChat.toggleFileUpload();
}

function toggleCodeMode() {
  window.aiChat.toggleCodeMode();
}

function toggleGeminiTools() {
  window.aiChat.toggleGeminiTools();
}

function selectTool(tool) {
  window.aiChat.selectTool(tool);
}

function removeFile(index) {
  window.aiChat.removeFile(index);
}

function clearChat() {
  window.aiChat.clearChat();
}

function askQuickQuestion(question) {
  document.getElementById("chatInput").value = question;
  window.aiChat.sendMessage();
}

// Initialize AI Chat when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.aiChat = new AIChat();
});
