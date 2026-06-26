/*
 * Embeddable Web Chat widget (MVP).
 * Usage:
 *   <script src="https://app.example.com/webchat-widget.js"
 *           data-account="<channel_account_id>"
 *           data-api="https://api.example.com"></script>
 */
(function () {
  var script = document.currentScript;
  var accountId = script.getAttribute("data-account");
  var apiBase = script.getAttribute("data-api") || "http://localhost:8000";
  var sessionId = localStorage.getItem("ucaas_webchat_session");
  if (!sessionId) {
    sessionId = "wc_" + Math.random().toString(36).slice(2) + Date.now().toString(36);
    localStorage.setItem("ucaas_webchat_session", sessionId);
  }

  var seenIds = new Set();
  var pollInterval = null;

  var box = document.createElement("div");
  box.style.cssText =
    "position:fixed;bottom:20px;right:20px;width:320px;font-family:sans-serif;z-index:99999;" +
    "border:1px solid #e2e8f0;border-radius:12px;background:#fff;box-shadow:0 10px 30px rgba(0,0,0,.15);overflow:hidden";
  box.innerHTML =
    '<div style="background:#0f172a;color:#fff;padding:12px 16px;font-weight:600;display:flex;align-items:center;justify-content:space-between">' +
    '<span>Chat with us</span><span id="ucaas-status" style="font-size:11px;opacity:0.6">●</span></div>' +
    '<div id="ucaas-log" style="height:240px;overflow:auto;padding:12px;font-size:14px"></div>' +
    '<div style="display:flex;border-top:1px solid #e2e8f0">' +
    '<input id="ucaas-input" placeholder="Type a message..." style="flex:1;border:0;padding:12px;outline:none;font-size:14px"/>' +
    '<button id="ucaas-send" style="border:0;background:#0f172a;color:#fff;padding:0 16px;cursor:pointer;font-size:13px">Send</button>' +
    "</div>";
  document.body.appendChild(box);

  var log = box.querySelector("#ucaas-log");
  var input = box.querySelector("#ucaas-input");
  var statusDot = box.querySelector("#ucaas-status");

  function append(text, direction) {
    var mine = direction === "outbound" || direction === "visitor";
    var el = document.createElement("div");
    el.style.cssText =
      "margin:6px 0;padding:8px 10px;border-radius:8px;max-width:80%;word-break:break-word;" +
      (mine
        ? "background:#0f172a;color:#fff;margin-left:auto;text-align:right"
        : "background:#f1f5f9;color:#0f172a");
    el.textContent = text;
    log.appendChild(el);
    log.scrollTop = log.scrollHeight;
  }

  function send() {
    var content = input.value.trim();
    if (!content) return;
    append(content, "visitor");
    input.value = "";
    fetch(apiBase + "/api/v1/webchat/messages", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        channel_account_id: accountId,
        session_id: sessionId,
        content: content,
      }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.message_id) seenIds.add(data.message_id);
      })
      .catch(function () {
        append("Message send nahi hua. Dobara try karo.", "inbound");
      });
  }

  function pollMessages() {
    fetch(
      apiBase +
        "/api/v1/webchat/messages?channel_account_id=" +
        accountId +
        "&session_id=" +
        encodeURIComponent(sessionId)
    )
      .then(function (r) { return r.json(); })
      .then(function (data) {
        statusDot.style.opacity = "1";
        statusDot.title = "Connected";
        var msgs = data.messages || [];
        msgs.forEach(function (msg) {
          if (!seenIds.has(msg.id)) {
            seenIds.add(msg.id);
            // Only show inbound (agent replies) — visitor's own messages already shown on send
            if (msg.direction === "inbound" && msg.sender_type === "contact") return;
            if (msg.direction === "outbound") {
              append(msg.content, "inbound"); // agent reply → show on left
            }
          }
        });
      })
      .catch(function () {
        statusDot.style.opacity = "0.3";
      });
  }

  box.querySelector("#ucaas-send").addEventListener("click", send);
  input.addEventListener("keydown", function (e) {
    if (e.key === "Enter") send();
  });

  // Start polling for agent replies every 3 seconds
  pollMessages();
  pollInterval = setInterval(pollMessages, 3000);
})();
