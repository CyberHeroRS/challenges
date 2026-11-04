"use strict";

let username = "";
let rooms = {};
let currentRoom = null;
let messages = {};
let pendingDeleteSlug = null;
let socket = null;
let isEditingUsername = false;

const STORAGE_KEY = "room-squatters";

function loadStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const data = JSON.parse(raw);
    username = data.username || "";
    rooms = data.rooms || {};
    const last = data.lastRoom;
    if (last && rooms[last]) currentRoom = last;
  } catch {}
}

function saveStorage() {
  const data = { username, rooms, lastRoom: currentRoom };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function esc(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function fmtTime(iso) {
  const d = new Date(iso || Date.now());
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function avatarLetter(name) {
  return (name || "?")[0].toUpperCase();
}

function toast(text, type = "info", duration = 3000) {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = text;
  document.getElementById("toasts").appendChild(el);
  requestAnimationFrame(() => {
    requestAnimationFrame(() => el.classList.add("show"));
  });
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.remove(), 250);
  }, duration);
}

let activeModal = null;

function openModal(id) {
  if (activeModal) closeModal(activeModal, false);
  activeModal = id;
  const overlay = document.getElementById("overlay");
  const modal = document.getElementById(id);
  overlay.classList.add("open");
  modal.classList.add("visible");
  setTimeout(() => {
    const inp = modal.querySelector("input");
    if (inp) inp.focus();
  }, 60);
}

function closeModal(id, clearActive = true) {
  const overlay = document.getElementById("overlay");
  const modal = document.getElementById(id);
  modal.classList.remove("visible");
  overlay.classList.remove("open");
  if (clearActive) activeModal = null;
  clearModalError(id);
}

function clearModalError(id) {
  const errEl = document.querySelector(`#${id} .modal-error`);
  if (errEl) {
    errEl.textContent = "";
    errEl.classList.remove("show");
  }
}

function showModalError(modalId, text) {
  const errEl = document.querySelector(`#${modalId} .modal-error`);
  if (errEl) {
    errEl.textContent = text;
    errEl.classList.add("show");
  }
}

function setConnStatus(state) {
  const dot = document.getElementById("conn-dot");
  dot.className = "";
  dot.classList.add(state);
  dot.title = state.charAt(0).toUpperCase() + state.slice(1);
}

function initSocket() {
  if (socket) return;
  socket = io({ autoConnect: true });
  setConnStatus("connecting");

  socket.on("connect", () => {
    setConnStatus("connected");
    if (currentRoom && rooms[currentRoom]) {
      socketJoinRoom(currentRoom, rooms[currentRoom].password, false);
    }
  });

  socket.on("disconnect", () => {
    setConnStatus("disconnected");
  });

  socket.on("connect_error", () => {
    setConnStatus("disconnected");
  });

  socket.on("room:event", (payload) => {
    const slug = currentRoom;
    if (!slug) return;
    addMessage(slug, {
      type: "event",
      text: payload.message,
      time: new Date().toISOString(),
    });
  });

  socket.on("room:message", (payload) => {
    const slug = payload.room_slug;
    if (!slug) return;
    addMessage(slug, {
      type: "message",
      sender: payload.sender,
      text: payload.message,
      time: payload.sent_at || new Date().toISOString(),
    });
  });
}

function socketJoinRoom(slug, password, showErrors = true) {
  return new Promise((resolve) => {
    if (!socket) {
      resolve({ ok: false, error: "Not connected" });
      return;
    }
    socket.emit("room:join", { room_slug: slug, password, username }, (ack) => {
      if (!ack) {
        resolve({ ok: false, error: "No response" });
        return;
      }
      resolve(ack);
    });
  });
}

function renderRoomList() {
  const list = document.getElementById("rooms-list");
  const empty = document.getElementById("rooms-empty");
  const slugs = Object.keys(rooms);

  list.innerHTML = "";

  if (slugs.length === 0) {
    list.appendChild(empty);
    return;
  }

  slugs.forEach((slug) => {
    const room = rooms[slug];
    const item = document.createElement("div");
    item.className = "room-item" + (slug === currentRoom ? " active" : "");
    item.dataset.slug = slug;

    const actionTitle = room.owned ? "Delete room" : "Remove from sidebar";
    const actionClass = room.owned ? "danger" : "muted";
    const actionIcon = room.owned
      ? `<svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor"><path d="M11 1.75V3h2.25a.75.75 0 0 1 0 1.5H2.75a.75.75 0 0 1 0-1.5H5V1.75C5 .784 5.784 0 6.75 0h2.5C10.216 0 11 .784 11 1.75ZM4.496 6.675l.66 6.6a.25.25 0 0 0 .249.225h5.19a.25.25 0 0 0 .249-.225l.66-6.6a.75.75 0 0 1 1.49.149l-.66 6.6A1.748 1.748 0 0 1 10.595 15h-5.19a1.75 1.75 0 0 1-1.741-1.575l-.66-6.6a.75.75 0 1 1 1.49-.15ZM6.5 1.75V3h3V1.75a.25.25 0 0 0-.25-.25h-2.5a.25.25 0 0 0-.25.25Z"/></svg>`
      : `<svg width="13" height="13" viewBox="0 0 16 16" fill="currentColor"><path d="M3.72 3.72a.75.75 0 0 1 1.06 0L8 6.94l3.22-3.22a.75.75 0 1 1 1.06 1.06L9.06 8l3.22 3.22a.75.75 0 1 1-1.06 1.06L8 9.06l-3.22 3.22a.75.75 0 0 1-1.06-1.06L6.94 8 3.72 4.78a.75.75 0 0 1 0-1.06Z"/></svg>`;

    item.innerHTML = `
      <span class="room-hash">#</span>
      <span class="room-slug">${esc(slug)}</span>
      ${room.owned ? '<span class="owned-badge">owner</span>' : ""}
      <button class="room-action-btn ${actionClass}" data-action="${room.owned ? "delete" : "remove"}" data-slug="${esc(slug)}" title="${actionTitle}">
        ${actionIcon}
      </button>
    `;

    item.addEventListener("click", (e) => {
      if (e.target.closest(".room-action-btn")) {
        e.stopPropagation();
        const btn = e.target.closest(".room-action-btn");
        if (btn.dataset.action === "delete") {
          openDeleteModal(btn.dataset.slug);
        } else {
          removeRoom(btn.dataset.slug);
        }
        return;
      }
      switchToRoom(slug);
    });

    list.appendChild(item);
  });
}

async function switchToRoom(slug) {
  if (!rooms[slug]) return;

  currentRoom = slug;
  saveStorage();
  renderRoomList();
  showChatPanel(slug);

  const res = await socketJoinRoom(slug, rooms[slug].password);
  if (!res.ok) {
    toast(`Could not join #${slug}: ${res.error}`, "error");
  }
}

function showChatPanel(slug) {
  const room = rooms[slug];
  const panel = document.getElementById("chat-panel");
  const welcome = document.getElementById("welcome");

  document.getElementById("chat-room-slug").textContent = slug;

  const ownedBadge = document.getElementById("chat-room-owned");
  const deleteBtn = document.getElementById("btn-delete-current");
  if (room && room.owned) {
    ownedBadge.classList.remove("hidden");
    deleteBtn.classList.remove("hidden");
  } else {
    ownedBadge.classList.add("hidden");
    deleteBtn.classList.add("hidden");
  }

  welcome.classList.add("hidden");
  panel.classList.remove("hidden");
  renderMessages(slug);
  scrollToBottom();

  document.getElementById("message-input").focus();
}

function showWelcome() {
  document.getElementById("chat-panel").classList.add("hidden");
  document.getElementById("welcome").classList.remove("hidden");
}

function addMessage(slug, msg) {
  if (!messages[slug]) messages[slug] = [];
  messages[slug].push(msg);

  if (slug === currentRoom) {
    appendMessageToDOM(msg);
    const empty = document.getElementById("messages-empty");
    if (empty) empty.style.display = "none";
    scrollToBottom();
  }
}

function renderMessages(slug) {
  const list = document.getElementById("messages-list");
  const empty = document.getElementById("messages-empty");
  list.innerHTML = "";

  const msgs = messages[slug] || [];
  if (msgs.length === 0) {
    empty.style.display = "flex";
    return;
  }
  empty.style.display = "none";

  let prevSender = null;
  msgs.forEach((msg) => {
    const el = buildMessageEl(msg, prevSender);
    list.appendChild(el);
    if (msg.type === "message") prevSender = msg.sender;
    else prevSender = null;
  });
}

function appendMessageToDOM(msg) {
  const list = document.getElementById("messages-list");
  const lastMsg = list.lastElementChild;
  let prevSender = null;
  if (lastMsg && lastMsg.classList.contains("msg-row")) {
    prevSender = lastMsg.dataset.sender || null;
  }
  const el = buildMessageEl(msg, prevSender);
  list.appendChild(el);
}

function buildMessageEl(msg, prevSender) {
  if (msg.type === "event") {
    const div = document.createElement("div");
    div.className = "msg-event";
    div.textContent = msg.text;
    return div;
  }

  const isOwn = msg.sender === username;
  const isFirstInGroup = msg.sender !== prevSender;
  const row = document.createElement("div");
  row.className = `msg-row${isOwn ? " own" : ""}${isFirstInGroup ? " first-in-group" : ""}`;
  row.dataset.sender = msg.sender;

  const avatarHtml = isOwn
    ? ""
    : isFirstInGroup
      ? `<div class="msg-avatar">${esc(avatarLetter(msg.sender))}</div>`
      : `<div class="msg-avatar-placeholder"></div>`;

  const senderHtml =
    !isOwn && isFirstInGroup
      ? `<div class="msg-sender-name">${esc(msg.sender)}</div>`
      : "";

  const content = document.createElement("div");
  content.className = "msg-content";
  content.innerHTML = `
    ${senderHtml}
    <div class="msg-bubble"></div>
    <div class="msg-time">${esc(fmtTime(msg.time))}</div>
  `;

  content.querySelector(".msg-bubble").textContent = msg.text;

  row.innerHTML = avatarHtml;
  row.appendChild(content);
  return row;
}

function scrollToBottom() {
  const wrap = document.getElementById("messages-wrap");
  wrap.scrollTop = wrap.scrollHeight;
}

function updateUsernameUI() {
  const avatar = document.getElementById("user-avatar");
  const name = document.getElementById("sidebar-username");
  avatar.textContent = avatarLetter(username);
  name.textContent = username || "Not set";

  const welcomeTitle = document.getElementById("welcome-title");
  welcomeTitle.textContent = username ? `Welcome, ${username}!` : "Welcome!";
}

async function handleCreateRoom() {
  const slugEl = document.getElementById("input-create-slug");
  const passEl = document.getElementById("input-create-password");
  const slug = slugEl.value.trim();
  const password = passEl.value;

  if (!slug) {
    showModalError("modal-create", "Room name is required.");
    return;
  }
  if (!/^[a-z0-9_-]+$/i.test(slug)) {
    showModalError(
      "modal-create",
      "Room name may only contain letters, digits, hyphens and underscores.",
    );
    return;
  }

  const btn = document.getElementById("btn-create-room");
  btn.disabled = true;
  btn.textContent = "Creating…";

  try {
    const res = await fetch("/api/rooms", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ room_slug: slug, password }),
    });
    const data = await res.json();

    if (!data.ok) {
      showModalError("modal-create", data.error || "Failed to create room.");
      return;
    }

    rooms[slug] = { password, owned: true };
    if (!messages[slug]) messages[slug] = [];
    saveStorage();
    closeModal("modal-create");
    slugEl.value = "";
    passEl.value = "";
    renderRoomList();
    toast(`Room #${slug} created!`, "success");
    await switchToRoom(slug);
  } catch {
    showModalError("modal-create", "Network error. Please try again.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Create Room";
  }
}

async function handleJoinRoom() {
  const slugEl = document.getElementById("input-join-slug");
  const passEl = document.getElementById("input-join-password");
  const slug = slugEl.value.trim();
  const password = passEl.value;

  if (!slug) {
    showModalError("modal-join", "Room name is required.");
    return;
  }

  const btn = document.getElementById("btn-join-room");
  btn.disabled = true;
  btn.textContent = "Joining…";

  try {
    rooms[slug] = { password, owned: false };
    if (!messages[slug]) messages[slug] = [];

    const res = await socketJoinRoom(slug, password);
    if (!res.ok) {
      delete rooms[slug];
      showModalError("modal-join", res.error || "Failed to join room.");
      return;
    }

    saveStorage();
    currentRoom = slug;
    saveStorage();
    closeModal("modal-join");
    slugEl.value = "";
    passEl.value = "";
    renderRoomList();
    showChatPanel(slug);
    toast(`Joined #${slug}!`, "success");
  } catch {
    delete rooms[slug];
    showModalError("modal-join", "Network error. Please try again.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Join Room";
  }
}

function openDeleteModal(slug) {
  pendingDeleteSlug = slug;
  document.getElementById("delete-confirm-text").textContent =
    `Are you sure you want to delete #${slug}? This cannot be undone.`;
  clearModalError("modal-delete");
  openModal("modal-delete");
}

async function handleDeleteRoom() {
  const slug = pendingDeleteSlug;
  if (!slug) return;

  const btn = document.getElementById("btn-confirm-delete");
  btn.disabled = true;
  btn.textContent = "Deleting…";

  try {
    const res = await fetch(`/api/rooms/${encodeURIComponent(slug)}`, {
      method: "DELETE",
    });
    const data = await res.json();

    if (!data.ok) {
      showModalError("modal-delete", data.error || "Failed to delete room.");
      return;
    }

    removeRoom(slug);
    closeModal("modal-delete");
    toast(`Room #${slug} deleted.`, "info");
  } catch {
    showModalError("modal-delete", "Network error. Please try again.");
  } finally {
    btn.disabled = false;
    btn.textContent = "Delete";
    pendingDeleteSlug = null;
  }
}

function removeRoom(slug) {
  delete rooms[slug];
  delete messages[slug];
  if (currentRoom === slug) {
    currentRoom = null;
    showWelcome();
  }
  saveStorage();
  renderRoomList();
}

async function handleSendMessage() {
  const input = document.getElementById("message-input");
  const text = input.value.trim();
  if (!text || !currentRoom) return;
  if (!socket || !socket.connected) {
    toast("Not connected to server.", "error");
    return;
  }

  input.value = "";
  autoResizeTextarea(input);

  socket.emit(
    "room:message",
    { room_slug: currentRoom, message: text },
    (ack) => {
      if (ack && !ack.ok) toast(ack.error || "Message failed.", "error");
    },
  );
}

function autoResizeTextarea(el) {
  el.style.height = "auto";
  el.style.height = Math.min(el.scrollHeight, 120) + "px";
}

function handleSaveUsername() {
  const input = document.getElementById("input-username");
  const value = input.value.trim().slice(0, 32);
  if (!value) {
    showModalError("modal-username", "Please enter a username.");
    return;
  }

  username = value;
  saveStorage();
  updateUsernameUI();
  closeModal("modal-username");

  if (!socket) {
    initSocket();
  }
  if (currentRoom && rooms[currentRoom]) {
    switchToRoom(currentRoom);
  }
  renderRoomList();
}

function init() {
  loadStorage();

  document.getElementById("overlay").addEventListener("click", (e) => {
    if (e.target === e.currentTarget && activeModal) {
      if (activeModal === "modal-username" && !isEditingUsername) return;
      closeModal(activeModal);
    }
  });

  document
    .getElementById("btn-open-join")
    .addEventListener("click", () => openModal("modal-join"));
  document
    .getElementById("btn-open-create")
    .addEventListener("click", () => openModal("modal-create"));
  document
    .getElementById("btn-welcome-join")
    .addEventListener("click", () => openModal("modal-join"));
  document
    .getElementById("btn-welcome-create")
    .addEventListener("click", () => openModal("modal-create"));

  document.getElementById("btn-edit-username").addEventListener("click", () => {
    isEditingUsername = true;
    document.getElementById("input-username").value = username;
    document.getElementById("modal-username-close").classList.remove("hidden");
    openModal("modal-username");
  });
  document
    .getElementById("btn-save-username")
    .addEventListener("click", handleSaveUsername);
  document.getElementById("input-username").addEventListener("keydown", (e) => {
    if (e.key === "Enter") handleSaveUsername();
  });
  document
    .getElementById("modal-username-close")
    .addEventListener("click", () => {
      if (isEditingUsername) closeModal("modal-username");
    });

  document
    .getElementById("btn-create-room")
    .addEventListener("click", handleCreateRoom);
  document
    .getElementById("modal-create-cancel")
    .addEventListener("click", () => closeModal("modal-create"));
  document
    .getElementById("modal-create-close")
    .addEventListener("click", () => closeModal("modal-create"));
  document
    .getElementById("input-create-slug")
    .addEventListener("keydown", (e) => {
      if (e.key === "Enter")
        document.getElementById("input-create-password").focus();
    });
  document
    .getElementById("input-create-password")
    .addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleCreateRoom();
    });

  document
    .getElementById("btn-join-room")
    .addEventListener("click", handleJoinRoom);
  document
    .getElementById("modal-join-cancel")
    .addEventListener("click", () => closeModal("modal-join"));
  document
    .getElementById("modal-join-close")
    .addEventListener("click", () => closeModal("modal-join"));
  document
    .getElementById("input-join-slug")
    .addEventListener("keydown", (e) => {
      if (e.key === "Enter")
        document.getElementById("input-join-password").focus();
    });
  document
    .getElementById("input-join-password")
    .addEventListener("keydown", (e) => {
      if (e.key === "Enter") handleJoinRoom();
    });

  document
    .getElementById("btn-confirm-delete")
    .addEventListener("click", handleDeleteRoom);
  document
    .getElementById("modal-delete-cancel")
    .addEventListener("click", () => closeModal("modal-delete"));

  document
    .getElementById("btn-delete-current")
    .addEventListener("click", () => {
      if (currentRoom) openDeleteModal(currentRoom);
    });
  document.getElementById("btn-leave-room").addEventListener("click", () => {
    if (currentRoom) removeRoom(currentRoom);
  });

  const msgInput = document.getElementById("message-input");
  msgInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });
  msgInput.addEventListener("input", () => autoResizeTextarea(msgInput));
  document
    .getElementById("send-btn")
    .addEventListener("click", handleSendMessage);

  updateUsernameUI();
  renderRoomList();

  if (!username) {
    isEditingUsername = false;
    document.getElementById("modal-username-close").classList.add("hidden");
    openModal("modal-username");
  } else {
    initSocket();
    if (currentRoom && rooms[currentRoom]) {
      showChatPanel(currentRoom);
    }
  }
}

document.addEventListener("DOMContentLoaded", init);
