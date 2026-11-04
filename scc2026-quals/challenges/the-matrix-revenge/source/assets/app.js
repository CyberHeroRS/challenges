// Client-side "auth" is deliberately fake and abusable for the challenge.
// Identity is keyed off a localStorage token: identity_token.
// Players are expected to discover that flipping it to "admin" changes behavior.
const AUTH_TOKEN_KEY = "identity_token";
const AUTH_USERNAME_KEY = "identity_username";
const AUTH_HEADER_TOKEN_KEY = "identity_header_token";

const state = {
  isLoggedIn: false,
  threads: [],
  activeThreadId: null,
};

const elements = {
  threadsBody: document.getElementById("threads-body"),
  postTitle: document.getElementById("post-title"),
  postSubtitle: document.getElementById("post-subtitle"),
  postMeta: document.getElementById("post-meta"),
  postLocked: document.getElementById("post-locked"),
  postBody: document.getElementById("post-body"),
  userName: document.getElementById("user-name"),
  loginBtn: document.getElementById("login-btn"),
  logoutBtn: document.getElementById("logout-btn"),
  newPostBtn: document.getElementById("new-post-btn"),
  syslog: document.getElementById("syslog"),
  registerBtn: document.getElementById("register-btn"),
  terminalModal: document.getElementById("terminal-modal"),
  terminalOutput: document.getElementById("terminal-output"),
  loginForm: document.getElementById("login-form"),
  loginUsername: document.getElementById("login-username"),
  loginToken: document.getElementById("login-token"),
  terminalClose: document.querySelector(".terminal-close"),
  rabbitHitbox: document.querySelector(".rabbit-hitbox"),
  reportBtn: document.getElementById("report-btn"),
  reportModal: document.getElementById("report-modal"),
  reportForm: document.getElementById("report-form"),
  reportUrl: document.getElementById("report-url"),
  reportNotes: document.getElementById("report-notes"),
  reportOutput: document.getElementById("report-output"),
  reportClose: document.getElementById("report-close"),
};

let lastIdentityToken = null;
let syslogQueue = [];
let syslogTyping = false;
let unauthorizedWarningShown = false;

function getIdentityToken() {
  try {
    return window.localStorage.getItem(AUTH_TOKEN_KEY);
  } catch {
    return null;
  }
}

function setIdentityToken(value) {
  try {
    window.localStorage.setItem(AUTH_TOKEN_KEY, value);
  } catch {
    // ignore
  }
}

function setSessionIdentity(username, headerToken) {
  try {
    window.localStorage.setItem(AUTH_USERNAME_KEY, username);
    window.localStorage.setItem(AUTH_HEADER_TOKEN_KEY, headerToken);
  } catch {
    // ignore
  }
}

function getSessionIdentity() {
  try {
    return {
      username: window.localStorage.getItem(AUTH_USERNAME_KEY),
      headerToken: window.localStorage.getItem(AUTH_HEADER_TOKEN_KEY),
    };
  } catch {
    return { username: null, headerToken: null };
  }
}

function isAuthenticated() {
  return getIdentityToken() === "admin";
}

function logToSyslog(message) {
  if (!elements.syslog) return;
  syslogQueue.push(`> ${message}`);
  if (!syslogTyping) {
    processSyslogQueue();
  }
}

const syslogMessages = [
  "connection from 10.0.0.13... ghost handshake incomplete.",
  "connection from 10.0.0.42... candidate flagged for invite.",
  "agent scan detected on port 31337... spoofing noise.",
  "uplink rerouted through 7 chained relays.",
  "identity cache flushed... awaiting trusted token.",
  "traffic spike on /zero-day... entropy rising.",
  "heartbeat from nebuchadnezzar: hull stable.",
  "construct hardware ping: inventory mismatch, ghosts suspected.",
];

function processSyslogQueue() {
  if (!elements.syslog) return;
  if (syslogQueue.length === 0) {
    syslogTyping = false;
    return;
  }
  syslogTyping = true;

  const next = syslogQueue.shift();
  const lineEl = document.createElement("div");
  elements.syslog.appendChild(lineEl);

  let index = 0;
  const interval = setInterval(() => {
    lineEl.textContent = next.slice(0, index + 1);
    index += 1;
    elements.syslog.scrollTop = elements.syslog.scrollHeight;

    if (index >= next.length) {
      clearInterval(interval);
      // keep only the last 5 lines to avoid overflow noise
      while (elements.syslog.children.length > 5) {
        elements.syslog.removeChild(elements.syslog.firstChild);
      }
      // small delay between messages
      setTimeout(processSyslogQueue, 150);
    }
  }, 20);
}

function renderThreads() {
  if (!elements.threadsBody) return;
  elements.threadsBody.innerHTML = "";

  state.threads.forEach((thread, index) => {
    const tr = document.createElement("tr");
    tr.dataset.threadId = String(thread.id);

    const tdStatus = document.createElement("td");
    tdStatus.className = "col-status";
    tdStatus.textContent = index + 1;

    const tdTitle = document.createElement("td");
    tdTitle.className = "col-title";
    const titleMain = document.createElement("div");
    titleMain.className = "thread-title-main";

    const badge = document.createElement("span");
    badge.className = "badge-tag" + (thread.locked ? " badge-locked" : "");
    badge.textContent = thread.tag;

    const titleText = document.createElement("span");
    titleText.className = "thread-title-text";
    titleText.textContent = thread.title;

    titleMain.appendChild(badge);
    titleMain.appendChild(titleText);

    const threadSubmeta = document.createElement("div");
    threadSubmeta.className = "thread-submeta";
    threadSubmeta.textContent = thread.preview;

    tdTitle.appendChild(titleMain);
    tdTitle.appendChild(threadSubmeta);

    const tdMeta1 = document.createElement("td");
    tdMeta1.className = "col-meta";
    tdMeta1.textContent = `${thread.replies} replies`;

    const tdMeta2 = document.createElement("td");
    tdMeta2.className = "col-meta";
    tdMeta2.textContent = thread.lastPing;

    tr.appendChild(tdStatus);
    tr.appendChild(tdTitle);
    tr.appendChild(tdMeta1);
    tr.appendChild(tdMeta2);

    tr.addEventListener("click", () => selectThread(thread.id));

    elements.threadsBody.appendChild(tr);
  });
}

function selectThread(threadId) {
  const thread = state.threads.find((t) => t.id === threadId);
  if (!thread) return;

  state.activeThreadId = threadId;

  document
    .querySelectorAll(".threads-table tbody tr")
    .forEach((row) => row.classList.remove("active-row"));
  const activeRow = document.querySelector(
    `.threads-table tbody tr[data-thread-id="${threadId}"]`,
  );
  if (activeRow) activeRow.classList.add("active-row");

  elements.postTitle.textContent = thread.title;
  elements.postSubtitle.textContent = `${thread.tag} • ${thread.preview}`;
  elements.postMeta.innerHTML = "";

  const authorSpan = document.createElement("span");
  authorSpan.textContent = `by ${thread.author}`;
  const repliesSpan = document.createElement("span");
  repliesSpan.textContent = `${thread.replies} replies`;
  const pingSpan = document.createElement("span");
  pingSpan.textContent = `last ping: ${thread.lastPing}`;

  elements.postMeta.appendChild(authorSpan);
  elements.postMeta.appendChild(repliesSpan);
  elements.postMeta.appendChild(pingSpan);

  renderPostBody(thread);
}

function renderPostBody(thread) {
  const loggedIn = state.isLoggedIn;

  // First challenge: content should not be visible when not logged in.
  if (!loggedIn) {
    elements.postLocked.style.display = "flex";
    elements.postBody.innerHTML = "";
  } else {
    elements.postLocked.style.display = "none";
    elements.postBody.innerHTML = "";

    thread.body.forEach((line) => {
      const div = document.createElement("div");
      if (line.type === "system") {
        div.className = "post-line-system";
      } else if (line.type === "warning") {
        div.className = "post-line-warning";
      }
      div.textContent = line.text;
      elements.postBody.appendChild(div);
    });
  }
}

function updateUserPanel() {
  if (state.isLoggedIn) {
    const { username } = getSessionIdentity();
    elements.userName.textContent = username
      ? `${username}@matrix`
      : "ghost@matrix";
    logToSyslog("session flag updated: authenticated");
    if (elements.logoutBtn) elements.logoutBtn.style.display = "inline-flex";
    if (elements.loginBtn) elements.loginBtn.style.display = "none";
    if (elements.newPostBtn) elements.newPostBtn.style.display = "inline-flex";
    if (elements.reportBtn) elements.reportBtn.style.display = "inline-flex";
  } else {
    elements.userName.textContent = "anonymous@guest";
    if (elements.logoutBtn) elements.logoutBtn.style.display = "none";
    if (elements.loginBtn) elements.loginBtn.style.display = "inline-flex";
    if (elements.newPostBtn) elements.newPostBtn.style.display = "none";
    if (elements.reportBtn) elements.reportBtn.style.display = "none";
  }
}

function startIdentityWatcher() {
  try {
    setInterval(() => {
      const current = getIdentityToken();
      if (current === lastIdentityToken) return;
      const wasLoggedIn = state.isLoggedIn;
      lastIdentityToken = current;
      state.isLoggedIn = isAuthenticated();
      if (state.isLoggedIn !== wasLoggedIn) {
        logToSyslog(
          `session flag updated: ${state.isLoggedIn ? "authenticated" : "unauthenticated"}.`,
        );
      }
      if (!state.isLoggedIn && current === "guest" && !unauthorizedWarningShown) {
        logToSyslog("WARNING: unauthorized identity detected (guest).");
        unauthorizedWarningShown = true;
      }
      updateUserPanel();

      if (state.threads.length > 0) {
        const activeRow = document.querySelector(
          ".threads-table tbody tr.active-row",
        );
        const activeId = activeRow
          ? Number(activeRow.dataset.threadId)
          : state.threads[0].id;
        selectThread(activeId);
      }
    }, 1000);
  } catch {
    // ignore
  }
}

function startSyslogTicker() {
  setInterval(() => {
    const msg =
      syslogMessages[Math.floor(Math.random() * syslogMessages.length)];
    logToSyslog(msg);
  }, 5000);
}

function wireAds() {
  document.querySelectorAll(".panel-ad").forEach((panel) => {
    const closeBtn = panel.querySelector(".ad-close");
    if (!closeBtn) return;
    closeBtn.addEventListener("click", () => {
      panel.style.display = "none";
      const slot = panel.getAttribute("data-ad-slot");
      if (slot) {
        logToSyslog(`ad slot ${slot} closed.`);
      }
    });
  });
}

function openTerminalModal(mode) {
  if (!elements.terminalModal) return;
  elements.terminalModal.classList.add("open");
  elements.terminalModal.setAttribute("data-mode", mode || "login");

  if (elements.terminalOutput) {
    elements.terminalOutput.innerHTML = "";
    const lines = [
      "> invite-only access gate.",
      "> provide identity and token to get access to the forum.",
      "> if you lose the token you have received, you have lost the access for good.",
    ];
    lines.forEach((text) => {
      const div = document.createElement("div");
      div.textContent = text;
      elements.terminalOutput.appendChild(div);
    });
    elements.terminalOutput.scrollTop = elements.terminalOutput.scrollHeight;
  }

  if (elements.loginUsername) {
    elements.loginUsername.value = "";
    elements.loginUsername.focus();
  }
  if (elements.loginToken) {
    elements.loginToken.value = "";
  }

  logToSyslog(`access gate opened via ${mode || "login"} button.`);
}

function closeTerminalModal() {
  if (!elements.terminalModal) return;
  elements.terminalModal.classList.remove("open");
}

function wireTerminalModal() {
  if (elements.loginBtn) {
    elements.loginBtn.addEventListener("click", () => openTerminalModal("login"));
  }

  // register is intentionally disabled (invite-only); no handler wired.

  if (elements.terminalClose) {
    elements.terminalClose.addEventListener("click", () => closeTerminalModal());
  }

  if (elements.terminalModal) {
    elements.terminalModal.addEventListener("click", (event) => {
      if (event.target === elements.terminalModal) {
        closeTerminalModal();
      }
    });
  }

  if (elements.loginForm && elements.terminalOutput) {
    elements.loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const username = elements.loginUsername
        ? elements.loginUsername.value.trim()
        : "";
      const token = elements.loginToken ? elements.loginToken.value.trim() : "";

      const echo = document.createElement("div");
      echo.textContent = `> login ${username || "<empty>"} with token[...]`;
      elements.terminalOutput.appendChild(echo);

      if (!username || !token) {
        const resp = document.createElement("div");
        resp.textContent = "> error: identity and token are both required.";
        elements.terminalOutput.appendChild(resp);
        elements.terminalOutput.scrollTop = elements.terminalOutput.scrollHeight;
        return;
      }

      try {
        const res = await fetch("/api/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, token }),
        });

        if (!res.ok) {
          const resp = document.createElement("div");
          resp.textContent = `> login failed [${res.status}].`;
          elements.terminalOutput.appendChild(resp);
        } else {
          const data = await res.json();
          const resp = document.createElement("div");
          resp.textContent = `> login accepted for ${data.user.username}. client still decides what to trust.`;
          elements.terminalOutput.appendChild(resp);

          // Establish a "session" on the client:
          // - remember username + token for headers
          // - flip the local identity_token to admin so content unlocks
          setSessionIdentity(username, token);
          setIdentityToken("admin");
          lastIdentityToken = "admin";
          state.isLoggedIn = true;
          updateUserPanel();
          if (state.threads.length > 0) {
            selectThread(state.threads[0].id);
          }

          const hint = document.createElement("div");
          hint.textContent =
            "> note: headers and local storage do not always agree. ghosts can abuse that.";
          elements.terminalOutput.appendChild(hint);
        }
      } catch (err) {
        const resp = document.createElement("div");
        resp.textContent = `> network error while calling /api/login`;
        elements.terminalOutput.appendChild(resp);
      }

      elements.terminalOutput.scrollTop = elements.terminalOutput.scrollHeight;
    });
  }
}

function wireLogout() {
  if (!elements.logoutBtn) return;
  elements.logoutBtn.addEventListener("click", async () => {
    try {
      await fetch("/api/logout", { method: "POST" });
    } catch {
      // ignore network errors; we'll still clear client state
    }

    setIdentityToken("guest");
    lastIdentityToken = "guest";
    state.isLoggedIn = false;
    try {
      window.localStorage.removeItem(AUTH_USERNAME_KEY);
      window.localStorage.removeItem(AUTH_HEADER_TOKEN_KEY);
    } catch {
      // ignore
    }
    updateUserPanel();
    if (state.threads.length > 0) {
      selectThread(state.threads[0].id);
    }
    logToSyslog("session terminated. identity reset to guest.");
  });
}

function openReportModal() {
  if (!elements.reportModal) return;
  elements.reportModal.classList.add("open");

  if (elements.reportOutput) {
    elements.reportOutput.innerHTML = "";
    const lines = [
      "> report will be queued to the handler subsystem.",
    ];
    lines.forEach((text) => {
      const div = document.createElement("div");
      div.textContent = text;
      elements.reportOutput.appendChild(div);
    });
  }

  if (elements.reportUrl) {
    const base = window.location.origin || "";
    const id =
      state.activeThreadId != null ? String(state.activeThreadId) : "unknown";
    elements.reportUrl.value = `${base}/thread/${id}`;
    elements.reportUrl.focus();
  }
  if (elements.reportNotes) {
    elements.reportNotes.value = "";
  }
}

function closeReportModal() {
  if (!elements.reportModal) return;
  elements.reportModal.classList.remove("open");
}

function wireReportModal() {
  if (elements.reportBtn) {
    elements.reportBtn.addEventListener("click", () => openReportModal());
  }

  if (elements.reportClose) {
    elements.reportClose.addEventListener("click", () => closeReportModal());
  }

  if (elements.reportModal) {
    elements.reportModal.addEventListener("click", (event) => {
      if (event.target === elements.reportModal) {
        closeReportModal();
      }
    });
  }

  if (elements.reportForm && elements.reportOutput) {
    elements.reportForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const url = elements.reportUrl ? elements.reportUrl.value.trim() : "";
      const notes = elements.reportNotes
        ? elements.reportNotes.value.trim()
        : "";

      const echo = document.createElement("div");
      echo.textContent = `> queued report for ${url || "<empty>"}`;
      elements.reportOutput.appendChild(echo);

      if (!url) {
        const resp = document.createElement("div");
        resp.textContent = "> error: url is required.";
        elements.reportOutput.appendChild(resp);
      } else {
        const resp = document.createElement("div");
        resp.textContent =
          "> report stored locally. in the full challenge, a bot would visit it.";
        elements.reportOutput.appendChild(resp);
        logToSyslog(`report queued for url: ${url} ${notes ? "(" + notes + ")" : ""}`);
      }

      elements.reportOutput.scrollTop = elements.reportOutput.scrollHeight;
    });
  }
}


function init() {
  // Challenge 1: seed identity_token if it's missing.
  let token = getIdentityToken();
  if (!token) {
    setIdentityToken("guest");
    token = "guest";
  }
  lastIdentityToken = token;
  state.isLoggedIn = isAuthenticated();

  if (!state.isLoggedIn && token === "guest") {
    logToSyslog("WARNING: unauthorized identity detected (guest).");
    unauthorizedWarningShown = true;
  } else if (state.isLoggedIn) {
    const { username } = getSessionIdentity();
    if (username) {
      logToSyslog(`session restored for ${username}@matrix.`);
    }
  }

  fetch("/api/posts")
    .then((res) => res.json())
    .then((data) => {
      const posts = Array.isArray(data.posts) ? data.posts : [];
      state.threads = posts.map((post, index) => ({
        id: post.id,
        tag: index === 0 ? "sticky" : "post",
        title: post.title,
        author: post.author || "ghost",
        replies: Math.floor(Math.random() * 40) + 1,
        lastPing: `${Math.floor(Math.random() * 59) + 1} min ago`,
        locked: true,
        // Do NOT leak real content in the preview for logged-out users.
        preview: "content encrypted. valid identity token required.",
        body: [
          {
            type: "system",
            text: `> ${post.content}`,
          },
        ],
      }));

      renderThreads();
      if (state.threads.length > 0) {
        selectThread(state.threads[0].id);
      }
    })
    .catch(() => {
      logToSyslog("error: failed to load posts from /api/posts");
    });
  updateUserPanel();
  startIdentityWatcher();
  startSyslogTicker();
  wireAds();
  wireTerminalModal();
  wireLogout();
  wireReportModal();

  if (elements.rabbitHitbox) {
    elements.rabbitHitbox.addEventListener("click", () => {
      // White Rabbit hint for those inspecting the client.
      // eslint-disable-next-line no-console
      console.log("Follow the cookies...");
    });
  }

}

document.addEventListener("DOMContentLoaded", init);

