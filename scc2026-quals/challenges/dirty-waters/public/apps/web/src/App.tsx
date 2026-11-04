import type { FormEvent, ReactNode } from "react";
import { useEffect, useState } from "react";
import { Link, Navigate, Route, Routes, useNavigate } from "react-router-dom";

type Viewer = {
  username: string;
  role: "admin" | "user";
  displayName: string;
  bio: string;
  preferences: {
    theme: {
      cardStyle: string;
      accentColor: string;
    };
    dashboard: {
      compact: boolean;
    };
  };
};

type Post = {
  id: string;
  author: string;
  title: string;
  body: string;
  createdAt: string;
};

type Report = {
  id: string;
  reporter: string;
  url: string;
  reason: string;
  createdAt: string;
};

async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => ({}))) as { error?: string };
    throw new Error(payload.error ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

function Shell({
  viewer,
  children
}: {
  viewer: Viewer | null;
  children: ReactNode;
}) {
  return (
    <div className="shell">
      <header className="topbar">
        <Link to="/" className="brand">
          <span className="brand-logo">TB</span>
          <span>
            <strong>ThreadBoard</strong>
            <small>Micro-forums for tiny communities</small>
          </span>
        </Link>
        <nav className="topnav">
          <Link to="/">Posts</Link>
          {viewer ? <Link to="/dashboard">Dashboard</Link> : <Link to="/login">Login</Link>}
          {viewer ? <a href="/api/auth/logout">Logout</a> : <Link to="/register">Register</Link>}
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}

function FeedPage({ viewer }: { viewer: Viewer | null }) {
  const [posts, setPosts] = useState<Post[]>([]);

  useEffect(() => {
    void api<{ posts: Post[] }>("/api/posts")
      .then((payload) => setPosts(payload.posts))
      .catch(() => setPosts([]));
  }, []);

  return (
    <section className="layout">
      <div className="main-column">
        <section className="hero">
          <p className="eyebrow">Quiet spaces, loud opinions</p>
          <h1>Post updates, tweak your profile, and flag weird threads for review.</h1>
          <p>
            ThreadBoard is a tiny community platform with member bios, live profile previews, and a
            lightweight moderation queue.
          </p>
          <div className="hero-actions">
            <Link className="primary-button" to={viewer ? "/dashboard" : "/login"}>
              {viewer ? "Open dashboard" : "Sign in"}
            </Link>
            <Link className="secondary-button" to="/register">
              Create account
            </Link>
          </div>
        </section>
        <section className="panel">
          <div className="section-head">
            <h2>Recent posts</h2>
            <p>Normal forum noise, a couple little hints, and somewhere to attach a report flow.</p>
          </div>
          <div className="post-list">
            {posts.map((post) => (
              <article key={post.id} className="post-card">
                <div className="post-meta">
                  <strong>@{post.author}</strong>
                  <span>{new Date(post.createdAt).toLocaleString()}</span>
                </div>
                <h3>{post.title}</h3>
                <p>{post.body}</p>
              </article>
            ))}
          </div>
        </section>
      </div>
      <aside className="side-column">
        <section className="panel">
          <h3>About moderation</h3>
          <p>
            Reported URLs are stored for moderator review. You can wire your bot to consume them
            later.
          </p>
        </section>
      </aside>
    </section>
  );
}

function LoginPage({
  viewer,
  onLogin
}: {
  viewer: Viewer | null;
  onLogin: (username: string, password: string) => Promise<void>;
}) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("guest");
  const [password, setPassword] = useState("guestpass123");
  const [error, setError] = useState("");

  if (viewer) {
    return <Navigate to="/dashboard" replace />;
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await onLogin(username, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    }
  }

  return (
    <section className="auth-wrap">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">Login</p>
        <h1>Sign into ThreadBoard</h1>
        <label>
          Username
          <input value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error ? <div className="notice error">{error}</div> : null}
        <button className="primary-button" type="submit">
          Login
        </button>
      </form>
    </section>
  );
}

function RegisterPage({
  viewer,
  onRegister
}: {
  viewer: Viewer | null;
  onRegister: (username: string, password: string) => Promise<void>;
}) {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  if (viewer) {
    return <Navigate to="/dashboard" replace />;
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await onRegister(username, password);
      navigate("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Register failed");
    }
  }

  return (
    <section className="auth-wrap">
      <form className="auth-card" onSubmit={submit}>
        <p className="eyebrow">Register</p>
        <h1>Start a new account</h1>
        <label>
          Username
          <input value={username} onChange={(event) => setUsername(event.target.value)} />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error ? <div className="notice error">{error}</div> : null}
        <button className="primary-button" type="submit">
          Register
        </button>
      </form>
    </section>
  );
}

function DashboardPage({
  viewer,
  refreshViewer
}: {
  viewer: Viewer | null;
  refreshViewer: () => Promise<void>;
}) {
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [displayName, setDisplayName] = useState(viewer?.displayName ?? "");
  const [bio, setBio] = useState(viewer?.bio ?? "");
  const [reportUrl, setReportUrl] = useState("http://example.com/report-me");
  const [reportReason, setReportReason] = useState("Suspicious content, please review.");
  const [reports, setReports] = useState<Report[]>([]);
  const [message, setMessage] = useState("");
  const [cardStyle, setCardStyle] = useState(viewer?.preferences.theme.cardStyle ?? "clean");
  const [accentColor, setAccentColor] = useState(viewer?.preferences.theme.accentColor ?? "orange");
  const [compactMode, setCompactMode] = useState(viewer?.preferences.dashboard.compact ?? false);

  useEffect(() => {
    if (!viewer) {
      return;
    }

    setDisplayName(viewer.displayName);
    setBio(viewer.bio);
    setCardStyle(viewer.preferences.theme.cardStyle);
    setAccentColor(viewer.preferences.theme.accentColor);
    setCompactMode(viewer.preferences.dashboard.compact);
  }, [viewer]);

  useEffect(() => {
    window.ThreadBoardPreview.renderDisplayNamePreview("profile-preview", displayName);
  }, [displayName]);

  useEffect(() => {
    if (!viewer) {
      return;
    }

    void api<{ reports: Report[] }>("/api/reports")
      .then((payload) => setReports(payload.reports))
      .catch(() => setReports([]));
  }, [viewer]);

  if (!viewer) {
    return <Navigate to="/login" replace />;
  }

  async function submitPost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await api("/api/posts", {
      method: "POST",
      body: JSON.stringify({ title, body })
    });
    setTitle("");
    setBody("");
    setMessage("Post published.");
  }

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await api("/api/settings/profile", {
      method: "POST",
      body: JSON.stringify({ displayName, bio })
    });
    await refreshViewer();
    setMessage("Profile saved.");
  }

  async function sendReport(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const payload = await api<{ ok: boolean; report: Report }>("/api/reports", {
      method: "POST",
      body: JSON.stringify({ url: reportUrl, reason: reportReason })
    });
    setReports((current) => [payload.report, ...current]);
    setMessage(`Queued report ${payload.report.id}.`);
  }

  async function syncThemeSettings(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await api("/api/settings/import", {
      method: "POST",
      body: JSON.stringify({
        config: {
          theme: {
            cardStyle,
            accentColor
          },
          dashboard: {
            compact: compactMode
          }
        }
      })
    });
    await refreshViewer();
    setMessage("Theme settings synced.");
  }

  return (
    <section className="layout">
      <div className="main-column">
        <section className="panel">
          <p className="eyebrow">Dashboard</p>
          <h1>Welcome, {viewer.username}</h1>
          <p className="muted">
            Update your profile, preview your public badge, drop a post, or send a moderator report.
          </p>
          {message ? <div className="notice">{message}</div> : null}
        </section>

        <section className="panel">
          <div className="section-head">
            <h2>Create post</h2>
          </div>
          <form className="stack-form" onSubmit={submitPost}>
            <label>
              Title
              <input value={title} onChange={(event) => setTitle(event.target.value)} />
            </label>
            <label>
              Body
              <textarea value={body} onChange={(event) => setBody(event.target.value)} rows={5} />
            </label>
            <button className="primary-button" type="submit">
              Publish post
            </button>
          </form>
        </section>
      </div>

      <aside className="side-column">
        <section className="panel">
          <div className="section-head">
            <h2>Settings</h2>
          </div>
          <form className="stack-form" onSubmit={saveProfile}>
            <label>
              Display name
              <input value={displayName} onChange={(event) => setDisplayName(event.target.value)} />
            </label>
            <label>
              Bio
              <textarea value={bio} onChange={(event) => setBio(event.target.value)} rows={4} />
            </label>
            <button className="primary-button" type="submit">
              Save profile
            </button>
          </form>
          <div className="preview-shell">
            <div className="preview-title">Live badge preview</div>
            <div id="profile-preview" />
          </div>
          <div className="preview-shell">
            <div className="preview-title">
              Active preset: {viewer.preferences.theme.cardStyle} / {viewer.preferences.theme.accentColor}
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="section-head">
            <h2>Theme sync</h2>
            <p className="muted">Apply style preferences from your dashboard controls.</p>
          </div>
          <form className="stack-form" onSubmit={syncThemeSettings}>
            <label>
              Card style
              <select value={cardStyle} onChange={(event) => setCardStyle(event.target.value)}>
                <option value="clean">Clean</option>
                <option value="soft">Soft</option>
                <option value="flat">Flat</option>
              </select>
            </label>
            <label>
              Accent color
              <input value={accentColor} onChange={(event) => setAccentColor(event.target.value)} />
            </label>
            <label className="checkbox-row">
              <input
                type="checkbox"
                checked={compactMode}
                onChange={(event) => setCompactMode(event.target.checked)}
              />
              <span>Compact dashboard mode</span>
            </label>
            <button className="primary-button" type="submit">
              Sync theme
            </button>
          </form>
        </section>

        <section className="panel">
          <div className="section-head">
            <h2>Report a URL</h2>
          </div>
          <form className="stack-form" onSubmit={sendReport}>
            <label>
              Link for moderator
              <input value={reportUrl} onChange={(event) => setReportUrl(event.target.value)} />
            </label>
            <label>
              Reason
              <textarea
                value={reportReason}
                onChange={(event) => setReportReason(event.target.value)}
                rows={3}
              />
            </label>
            <button className="primary-button" type="submit">
              Send report
            </button>
          </form>
        </section>

        <section className="panel">
          <div className="section-head">
            <h2>Queued reports</h2>
          </div>
          <div className="report-list">
            {reports.map((report) => (
              <div key={report.id} className="report-row">
                <strong>{report.url}</strong>
                <span>{report.reason}</span>
              </div>
            ))}
          </div>
        </section>
      </aside>
    </section>
  );
}

export default function App() {
  const [viewer, setViewer] = useState<Viewer | null>(null);
  const [ready, setReady] = useState(false);

  async function refreshViewer() {
    const payload = await api<Viewer>("/api/me");
    setViewer(payload);
  }

  useEffect(() => {
    void api<Viewer>("/api/me")
      .then((payload) => setViewer(payload))
      .catch(() => setViewer(null))
      .finally(() => setReady(true));
  }, []);

  async function login(username: string, password: string) {
    await api("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
    await refreshViewer();
  }

  async function register(username: string, password: string) {
    await api("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ username, password })
    });
    await refreshViewer();
  }

  if (!ready) {
    return <div className="loading">Loading ThreadBoard...</div>;
  }

  return (
    <Shell viewer={viewer}>
      <Routes>
        <Route path="/" element={<FeedPage viewer={viewer} />} />
        <Route path="/login" element={<LoginPage viewer={viewer} onLogin={login} />} />
        <Route path="/register" element={<RegisterPage viewer={viewer} onRegister={register} />} />
        <Route
          path="/dashboard"
          element={<DashboardPage viewer={viewer} refreshViewer={refreshViewer} />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Shell>
  );
}
