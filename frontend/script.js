let isTyping = false;
let hasMessages = false;

async function sendMessage() {
  const questionInput = document.getElementById("question");
  const sendBtn = document.getElementById("send-btn");
  const chatBox = document.getElementById("chat-box");
  const question = questionInput.value.trim();
  if (!question || isTyping) return;

  // first message => hide welcome
  if (!hasMessages) {
    document.getElementById("welcome-section").classList.add("hidden");
    chatBox.classList.remove("hidden");
    hasMessages = true;
  }

  questionInput.disabled = true;
  sendBtn.disabled = true;
  isTyping = true;

  addMessage(question, "user");
  showTypingIndicator();

  questionInput.value = "";

  try {
    let res = await fetch("/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ question })
    });
    let data = await res.json();
    hideTypingIndicator();
    addMessage(data.answer, "bot", data.source);
  } catch (err) {
    hideTypingIndicator();
    addMessage("⚠ Server not responding. Please try again.", "bot", null, true);
  } finally {
    questionInput.disabled = false;
    sendBtn.disabled = false;
    isTyping = false;
    questionInput.focus();
  }
}

function addMessage(text, sender, source=null, isError=false) {
  const chatBox = document.getElementById("chat-box");
  const div = document.createElement("div");
  div.classList.add("fade-in");

  if (sender==="user") {
    div.innerHTML = `
      <div class="flex justify-end mb-6">
        <div class="max-w-xs lg:max-w-2xl">
          <div class="bg-gray-800 rounded-2xl rounded-br-md px-4 py-3">${text}</div>
        </div>
      </div>`;
  } else {
    const iconClass = isError?"bg-red-500":"bg-blue-600";
    const msgClass = isError?"bg-red-900 text-red-100":"bg-gray-900 border border-gray-700";
    const icon = '<img src="Logo/NTB-logo.png" alt="Norton Logo">';
    div.innerHTML = `
      <div class="flex items-start space-x-3 mb-6">
        <!-- Avatar / Icon -->
        <div class="w-8 h-8 ${iconClass} rounded-full flex items-center justify-center">
          ${icon}
        </div>
         
        <!-- Message Box -->
        <div class="max-w-xs lg:max-w-2xl">
          <div class="${msgClass} inline-block rounded-2xl rounded-bl-md px-4 py-3">
            ${text}
            ${source ? `
              <div class="mt-2 text-xs text-gray-400 italic">
                Source: ${source}
              </div>` : ""}
          </div>
        </div>
      </div>
    `;
  }
  chatBox.appendChild(div);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function showTypingIndicator() {
  const typing = document.getElementById("typing-indicator");
  typing.classList.remove("hidden");
  typing.scrollIntoView({behavior:"smooth"});
}

function hideTypingIndicator() {
  document.getElementById("typing-indicator").classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", ()=> {
  document.getElementById("question").focus();
});